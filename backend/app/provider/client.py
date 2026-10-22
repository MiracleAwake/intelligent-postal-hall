"""按档案调用模型。超时和连续失败会熔断。密钥只从环境变量读。"""

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field

from app.provider.profiles import ModelProfile, default_profile, load_profiles


class CircuitOpen(Exception):
    """连续失败后熔断，不再发请求。"""


class ModelCallError(Exception):
    """这一次调用没有拿到正文。"""


@dataclass
class Breaker:
    limit: int
    failures: int = 0
    open: bool = False

    def before(self) -> None:
        if self.open:
            raise CircuitOpen(self.limit)

    def ok(self) -> None:
        self.failures = 0

    def fail(self) -> None:
        self.failures += 1
        if self.failures >= self.limit:
            self.open = True


def strip_think(text: str) -> str:
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return cleaned.strip()


def parse_json_object(text: str) -> dict | None:
    visible = strip_think(text)
    match = re.search(r"\{.*\}", visible, flags=re.DOTALL)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    return data


def parse_intent_reply(text: str) -> dict:
    data = parse_json_object(text)
    if not data:
        visible = strip_think(text)
        return {"intent": "", "summary": visible[:200], "parsed": False}
    return {
        "intent": str(data.get("intent") or ""),
        "summary": str(data.get("summary") or ""),
        "parsed": True,
    }


@dataclass
class Provider:
    profiles: dict[str, ModelProfile] = field(default_factory=load_profiles)
    breakers: dict[str, Breaker] = field(default_factory=dict)
    transport: callable = None

    def __post_init__(self) -> None:
        if self.transport is None:
            self.transport = post_json
        for profile in self.profiles.values():
            self.breakers.setdefault(profile.id, Breaker(profile.failure_limit))

    def profile(self, profile_id: str | None = None) -> ModelProfile:
        if profile_id:
            return self.profiles[profile_id]
        return default_profile(self.profiles)

    def complete(self, prompt: str, *, profile_id: str | None = None) -> str:
        profile = self.profile(profile_id)
        breaker = self.breakers[profile.id]
        breaker.before()
        try:
            text = self._complete(profile, prompt)
        except CircuitOpen:
            raise
        except Exception as exc:
            breaker.fail()
            raise ModelCallError(str(exc)) from exc
        breaker.ok()
        return text

    def recognize_intent(self, appointment: dict, *, profile_id: str | None = None) -> dict:
        prompt = (
            "你是邮政厅堂柜面助手。根据预约只判断客户要办的一类。"
            "只能从这些里选 intent：改存期、取息、加钱、换储种、接着存。"
            "只输出一行 JSON，不要解释："
            '{"intent":"改存期","summary":"一句短话"}\n'
            f"预约：{json.dumps(appointment, ensure_ascii=False)}"
        )
        reply = self.complete(prompt, profile_id=profile_id)
        parsed = parse_intent_reply(reply)
        parsed["executor"] = "model"
        parsed["profile_id"] = self.profile(profile_id).id
        return parsed

    def _complete(self, profile: ModelProfile, prompt: str) -> str:
        if profile.protocol == "ollama":
            url = f"{profile.base_url}/api/chat"
            body = {
                "model": profile.model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            }
            payload = self.transport(url, body, profile.timeout_seconds, {})
            return str(payload["message"]["content"])
        if profile.protocol == "openai_compat":
            key_name = profile.api_key_env or ""
            key = os.getenv(key_name, "")
            if not key:
                raise ModelCallError(f"缺少环境变量 {key_name}")
            url = f"{profile.base_url}/chat/completions"
            body = {
                "model": profile.model,
                "messages": [{"role": "user", "content": prompt}],
            }
            payload = self.transport(
                url,
                body,
                profile.timeout_seconds,
                {"Authorization": f"Bearer {key}"},
            )
            return str(payload["choices"][0]["message"]["content"])
        raise ModelCallError(profile.protocol)


def post_json(url: str, body: dict, timeout: float, headers: dict) -> dict:
    data = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        raise ModelCallError(f"{exc.code} {detail}") from exc
    except urllib.error.URLError as exc:
        raise ModelCallError(str(exc.reason)) from exc

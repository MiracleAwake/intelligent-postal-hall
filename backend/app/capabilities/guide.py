"""新建会话的导引。说完或转写之后，匹配到一项业务才进入工作页。

对不上，或同时像两扇门，就留在导引页。不办结。
"""

from app.assembly.alignment import from_shell
from app.capabilities.speech import SPEECH_HOOK, accept_speech

# 后端岗位 → 壳上的那一页。壳的 P1 不是后端的 P1。
_SHELL_FOR_ROLE = {"P1": "P2", "P2": "P3", "P3": "P1", "P4": "P4"}

# 短语长的先匹配。同一岗位的多项意图可以进同一页。
_PHRASES = (
    ("到期转存", "到期转存", "P1", "time_deposit_rollover", True),
    ("改存期", "改存期", "P1", "time_deposit_rollover", True),
    ("转存", "到期转存", "P1", "time_deposit_rollover", True),
    ("再存", "到期转存", "P1", "time_deposit_rollover", True),
    ("取息", "取息", "P1", "teller_intent", False),
    ("加钱", "加钱", "P1", "teller_intent", False),
    ("再加", "加钱", "P1", "teller_intent", False),
    ("换储种", "换储种", "P1", "teller_intent", False),
    ("接着存", "接着存", "P1", "teller_intent", False),
    ("转活期", "转活期", "P1", "teller_intent", False),
    ("收寄", "收寄", "P2", "accept_mail", False),
    ("寄件", "收寄", "P2", "accept_mail", False),
    ("验视", "收寄", "P2", "accept_mail", False),
    ("授权", "授权", "P3", "authorize", False),
    ("分流", "分流", "P4", "lobby", False),
    ("叫号", "叫号", "P4", "lobby", False),
    ("预约", "预约", "P4", "lobby", False),
)


def _page(role_code: str) -> dict:
    shell = from_shell(_SHELL_FOR_ROLE[role_code])
    return {"role_code": role_code, "home": shell["home"], "post_name": shell["label"]}


def match_business(text: str) -> dict:
    spoken = (text or "").strip()
    base = {"speech": SPEECH_HOOK["id"], "completes": False, "printed": False}
    if not spoken:
        return {**base, "status": "guide", "mode": "guide", "text": "", "hits": []}
    found = []
    seen = set()
    for phrase, name, role, flow, starts in _PHRASES:
        if phrase not in spoken or name in seen:
            continue
        seen.add(name)
        found.append({"name": name, "role_code": role, "flow": flow, "starts_chain": starts})
    roles = {item["role_code"] for item in found}
    if len(roles) != 1:
        return {**base, "status": "guide", "mode": "guide", "text": spoken, "hits": found}
    role = found[0]["role_code"]
    page = _page(role)
    starts = any(item["starts_chain"] for item in found)
    flow = next(item["flow"] for item in found if item["starts_chain"]) if starts else found[0]["flow"]
    return {
        **base,
        "status": "work",
        "mode": "work",
        "text": spoken,
        "business": found[0]["name"] if len(found) == 1 else "、".join(item["name"] for item in found),
        "intents": [item["name"] for item in found],
        "flow": flow,
        "starts_chain": starts,
        "hits": found,
        **page,
    }


def recognize(text: str | None = None, *, audio_ref: str | None = None) -> dict:
    """文字直接匹配。只有声音时先走语音入口，没有转写就不跳页。"""
    if (text or "").strip():
        return match_business(text)
    heard = accept_speech(audio_ref=audio_ref)
    if heard["status"] != "ready":
        stayed = match_business("")
        stayed["voice"] = heard["status"]
        return stayed
    matched = match_business(heard["text"])
    matched["voice"] = heard["status"]
    return matched

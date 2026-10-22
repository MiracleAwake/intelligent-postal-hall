"""读取模型档案。不连接模型。"""

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class ModelProfile:
    id: str
    display_name: str
    protocol: str
    base_url: str
    model: str
    timeout_seconds: float
    failure_limit: int
    api_key_env: str | None = None
    is_default: bool = False


def example_path() -> Path:
    return Path(__file__).with_name("models.example.yaml")


def load_profiles(path: Path | None = None) -> dict[str, ModelProfile]:
    raw = yaml.safe_load((path or example_path()).read_text(encoding="utf-8")) or {}
    profiles = {}
    for item in raw.get("profiles") or []:
        profile = ModelProfile(
            id=item["id"],
            display_name=item.get("display_name") or item["id"],
            protocol=item["protocol"],
            base_url=item["base_url"].rstrip("/"),
            model=item["model"],
            timeout_seconds=float(item.get("timeout_seconds") or 60),
            failure_limit=int(item.get("failure_limit") or 3),
            api_key_env=item.get("api_key_env"),
            is_default=bool(item.get("is_default")),
        )
        profiles[profile.id] = profile
    return profiles


def default_profile(profiles: dict[str, ModelProfile] | None = None) -> ModelProfile:
    found = profiles or load_profiles()
    for profile in found.values():
        if profile.is_default:
            return profile
    return next(iter(found.values()))

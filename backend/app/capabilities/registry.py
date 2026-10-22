"""能力注册表。岗位差异＝调用的能力不同，不按岗位复制实现。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Capability:
    name: str
    kind: str
    summary: str


REGISTRY: dict[str, Capability] = {}


def register(cap: Capability) -> None:
    REGISTRY[cap.name] = cap


def get(name: str) -> Capability:
    return REGISTRY[name]


def names() -> tuple[str, ...]:
    return tuple(REGISTRY)

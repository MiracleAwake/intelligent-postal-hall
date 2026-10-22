"""主页上的窗。统计窗、复核窗、侧栏窗各一具，打开期间不能再点底下的格子。

口径来自 2026-10-19 的原型：统计窗六段、调岗双人复核、侧栏五种内容、岗位牌回工作台。
"""

from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP


STAT_SECTIONS = ("head", "lead", "kpi", "table", "note", "foot")
CLOSE_WAYS = ("mask", "button", "escape")
FIVE = ("撤旧岗", "授新岗", "任务随岗位原地保留", "系统接入切换", "客户关系解绑")
SIDE_KINDS = ("task", "list", "notice", "session", "logout")
_UNIT = ("笔", "人", "台", "分钟", "元", "%")
_CENT = Decimal("0.01")


def check_stat(spec: dict) -> list[str]:
    """六段要齐。去路必须带页和锚点。不能相加的三格必须写明原因。"""
    missing = []
    for key in ("title", "caliber", "lead", "kpi", "cols", "rows", "note", "source", "to", "to_name"):
        if not spec.get(key) and spec.get(key) != 0:
            missing.append(key)
    if spec.get("to") and "#" not in str(spec["to"]):
        missing.append("anchor")
    kpi = spec.get("kpi") or []
    if kpi and len(kpi) != 3:
        missing.append("kpi")
    cols = spec.get("cols") or []
    if cols and len(cols) != 3:
        missing.append("cols")
    if spec.get("part") is False:
        cap = str(spec.get("cap") or "")
        if not any(word in cap for word in ("不可加", "不能加", "不计入", "最低")):
            missing.append("cap")
    for row in spec.get("rows") or []:
        if len(row) != 3:
            missing.append("row")
            break
        cell = str(row[2])
        if any(unit in cell for unit in _UNIT):
            missing.append("unit_in_value")
            break
    total = spec.get("sum")
    if total is not None and len(total) != 3:
        missing.append("sum")
    return missing


class DeskShell:
    def __init__(self) -> None:
        self.stat_key: str | None = None
        self.stat_focus: str | None = None
        self.review_open = False
        self.side: str | None = None
        self.role = ""

    def open_stat(self, key: str, spec: dict) -> dict:
        gaps = check_stat(spec)
        if gaps:
            return {"status": "blocked", "need": gaps}
        if self.stat_key is not None or self.review_open or self.side is not None:
            return {"status": "blocked", "need": "close_first"}
        self.stat_key = key
        self.stat_focus = key
        return {
            "status": "open",
            "key": key,
            "sections": STAT_SECTIONS,
            "warn": spec.get("part") is False,
            "to": spec["to"],
        }

    def close_stat(self, how: str) -> dict:
        if how not in CLOSE_WAYS:
            raise ValueError(how)
        focus = self.stat_focus
        self.stat_key = None
        return {"status": "closed", "how": how, "focus": focus}

    def open_review(self) -> dict:
        if self.stat_key is not None or self.side is not None:
            return {"status": "blocked", "need": "close_first"}
        self.review_open = True
        return {"status": "open", "events": FIVE}

    def confirm_review(self, *, initiator: str, reviewer: str) -> dict:
        if initiator.strip() == reviewer.strip() or not reviewer.strip():
            return {"status": "blocked", "need": "second_person"}
        self.review_open = False
        return {
            "status": "done",
            "events": FIVE,
            "undo": False,
            "audit": {"kind": "变更", "reviewer": reviewer},
        }

    def return_for_more(self, gaps: list[str]) -> dict:
        items = [item.strip() for item in gaps if item.strip()]
        vague = {"不合格", "不行", "退回", "有问题"}
        if not items or all(item in vague for item in items):
            return {"status": "blocked", "need": "gaps"}
        return {"status": "returned", "gaps": items}

    def open_side(self, kind: str, *, go: str | None = None, module: str | None = None) -> dict:
        if kind not in SIDE_KINDS:
            raise ValueError(kind)
        if self.stat_key is not None or self.review_open or self.side is not None:
            return {"status": "blocked", "need": "close_first"}
        self.side = kind
        if kind == "task":
            return {
                "status": "open",
                "kind": kind,
                "transfer": False,
                "trace": "看过这一条",
                "go": go,
                "module": module,
            }
        if kind == "notice":
            return {"status": "open", "kind": kind, "keeps": "today"}
        if kind == "session":
            return {"status": "open", "kind": kind, "carries_chat": False, "role": self.role}
        return {
            "status": "open",
            "kind": kind,
            "tasks_follow": "post",
            "session_follows": "org",
        }

    def close_side(self) -> dict:
        kind = self.side
        self.side = None
        return {"status": "closed", "kind": kind}

    def post_pin(self, *, on_home: bool, back_href: str | None, scroll_top: int) -> dict:
        """牌子回到当前岗位的工作台，不改登录身份。"""
        role = self.role
        closed = self.stat_key is not None or self.review_open
        self.stat_key = None
        self.review_open = False
        self.side = None
        if not on_home:
            return {"go": back_href, "role": role}
        moved = scroll_top > 0 or closed
        return {
            "role": role,
            "scroll": 0,
            "message": "已回到工作台顶部" if moved else "已经在工作台顶部了",
        }

    def logout(self, *, post_id: int, org_id: int) -> dict:
        self.stat_key = None
        self.review_open = False
        self.side = None
        return {
            "login_cleared": True,
            "tasks_post_id": post_id,
            "session_org_id": org_id,
        }


def visible_rows(rows: list[dict], minimum: int = 5) -> dict:
    """不足下限的网点不进表，避免从合计倒推出个别人。"""
    shown = [row for row in rows if int(row["count"]) >= minimum]
    return {"shown": shown, "withheld": len(rows) - len(shown)}


def add_same_unit(parts: list[dict]) -> dict:
    units = {part["unit"] for part in parts}
    if len(units) != 1:
        return {"ok": False, "reason": "不同单位不相加"}
    return {"ok": True, "total": sum(int(part["count"]) for part in parts), "unit": units.pop()}


def service_status(alerts: list[str]) -> str:
    if len(alerts) >= 2:
        return "告警"
    if len(alerts) == 1:
        return "注意"
    return "正常"


def fleet(services: list[dict]) -> dict:
    marks = [service_status(item["alerts"]) for item in services]
    rates = [Decimal(str(item["availability"])) for item in services]
    return {
        "normal": marks.count("正常"),
        "watch": marks.count("注意"),
        "alert_rules": sum(len(item["alerts"]) for item in services),
        "lowest": f"{min(rates):.2f}" if rates else None,
    }


def weighted_fail(rows: list[dict]) -> str | None:
    total = sum(int(row["calls"]) for row in rows)
    if total == 0:
        return None
    weighted = sum(int(row["calls"]) * Decimal(str(row["rate"])) for row in rows) / Decimal(total)
    return f"{weighted.quantize(_CENT, rounding=ROUND_HALF_UP):.2f}"


def rollback_open(*, released_at: datetime, now: datetime, latest: bool, hours: int = 72) -> dict:
    """窗口只罩住刚发的那一次。到期不会自己退回去。"""
    if not latest or now > released_at + timedelta(hours=hours):
        return {"ok": False, "auto": False}
    return {"ok": True, "auto": False}


def allow_plaintext(name: str) -> dict:
    blocked = {"身份证查得", "客户摘要", "交易明细", "影像原文"}
    if name in blocked:
        return {"status": "masked", "body": None}
    return {"status": "ready", "name": name}

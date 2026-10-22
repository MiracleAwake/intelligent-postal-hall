"""本日业务的归集与统计。不连库。

数字和点开后的名单读同一批事实。同一 ref 再送一次只保留最后一笔。
新增储蓄、流失储蓄只加带金额的事实，办结一笔业务不会被算进储蓄。
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP


KINDS = (
    "visit",
    "business",
    "savings_in",
    "savings_out",
    "revisit",
    "appointment",
    "arrival",
    "new_customer",
    "task_open",
    "task_done",
)

LABELS = {
    "visit": "到访客户",
    "business": "办理业务",
    "savings_in": "新增储蓄",
    "savings_out": "流失储蓄",
    "revisit": "回访客户",
    "appointment": "预约",
    "arrival": "预约到店",
    "new_customer": "开发新客户",
    "task_progress": "待办完成",
    "arrival_rate": "预约到店率",
}

PEOPLE = {"visit", "revisit", "new_customer"}
MONEY = {"savings_in", "savings_out"}
_CENT = Decimal("0.01")


@dataclass
class Fact:
    ref: str
    org_id: int
    post_id: int
    role_code: str
    kind: str
    occurred_at: datetime
    staff_id: int | None = None
    customer_ref: str | None = None
    display_name: str | None = None
    amount: str | None = None
    note: str | None = None
    link_ref: str | None = None

    def line(self) -> dict:
        return {
            "ref": self.ref,
            "org_id": self.org_id,
            "post_id": self.post_id,
            "role_code": self.role_code,
            "kind": self.kind,
            "occurred_at": self.occurred_at.isoformat(sep=" ", timespec="seconds"),
            "staff_id": self.staff_id,
            "customer_ref": self.customer_ref,
            "display_name": self.display_name,
            "amount": _money(self.amount) if self.amount is not None else None,
            "note": self.note,
            "link_ref": self.link_ref,
        }


class DailyBook:
    def __init__(self) -> None:
        self._rows: dict[str, Fact] = {}

    def collect(self, fact: Fact) -> Fact:
        if not fact.ref:
            raise ValueError("ref")
        if fact.kind not in KINDS:
            raise ValueError(fact.kind)
        if fact.kind in MONEY:
            _money(fact.amount)
        elif fact.amount is not None:
            _money(fact.amount)
        self._rows[fact.ref] = fact
        return fact

    def summary(self, org_id: int, day: date, role_code: str | None = None) -> dict:
        prior = day - timedelta(days=1)
        items = []
        for key in (
            "visit",
            "business",
            "savings_in",
            "savings_out",
            "task_progress",
            "revisit",
            "appointment",
            "arrival",
            "arrival_rate",
            "new_customer",
        ):
            items.append(self._item(org_id, day, prior, key, role_code))
        return {
            "org_id": org_id,
            "day": day.isoformat(),
            "role_code": role_code,
            "items": items,
        }

    def lines(self, org_id: int, day: date, key: str, role_code: str | None = None) -> list[dict]:
        if key == "task_progress":
            rows = [
                fact
                for fact in self._on(org_id, day, role_code)
                if fact.kind in ("task_open", "task_done")
            ]
        elif key == "arrival_rate":
            rows = [fact for fact in self._on(org_id, day, role_code) if fact.kind == "appointment"]
        elif key in KINDS:
            rows = [fact for fact in self._on(org_id, day, role_code) if fact.kind == key]
        else:
            raise ValueError(key)
        rows.sort(key=lambda fact: fact.occurred_at)
        arrived = self._arrived_refs(org_id, day, role_code)
        out = []
        for fact in rows:
            line = fact.line()
            if key == "arrival_rate":
                line["arrived"] = fact.ref in arrived
            out.append(line)
        return out

    def recent(self, org_id: int, key: str, limit: int = 10, role_code: str | None = None) -> list[dict]:
        if key not in KINDS:
            raise ValueError(key)
        rows = [
            fact
            for fact in self._rows.values()
            if fact.org_id == org_id and fact.kind == key and _role_ok(fact, role_code)
        ]
        rows.sort(key=lambda fact: fact.occurred_at, reverse=True)
        return [fact.line() for fact in rows[:limit]]

    def _item(self, org_id: int, day: date, prior: date, key: str, role_code: str | None) -> dict:
        current = self._measure(org_id, day, key, role_code)
        previous = self._measure(org_id, prior, key, role_code)
        return {
            "key": key,
            "label": LABELS[key],
            "count": current["count"],
            "amount": current["amount"],
            "rate": current["rate"],
            "prior_count": previous["count"],
            "prior_amount": previous["amount"],
            "prior_rate": previous["rate"],
        }

    def _measure(self, org_id: int, day: date, key: str, role_code: str | None) -> dict:
        rows = self._on(org_id, day, role_code)
        if key == "task_progress":
            done = [fact for fact in rows if fact.kind == "task_done"]
            opened = [fact for fact in rows if fact.kind == "task_open"]
            total = len(done) + len(opened)
            return {"count": len(done), "amount": None, "rate": _rate(len(done), total)}
        if key == "arrival_rate":
            appointments = [fact for fact in rows if fact.kind == "appointment"]
            arrived = self._arrived_refs(org_id, day, role_code)
            hit = sum(1 for fact in appointments if fact.ref in arrived)
            return {"count": hit, "amount": None, "rate": _rate(hit, len(appointments))}
        chosen = [fact for fact in rows if fact.kind == key]
        if key in MONEY:
            total = sum((_money(fact.amount) for fact in chosen), Decimal("0.00"))
            return {"count": len(chosen), "amount": f"{total:.2f}", "rate": None}
        if key in PEOPLE:
            people = {fact.customer_ref or fact.ref for fact in chosen}
            return {"count": len(people), "amount": None, "rate": None}
        return {"count": len(chosen), "amount": None, "rate": None}

    def _on(self, org_id: int, day: date, role_code: str | None) -> list[Fact]:
        return [
            fact
            for fact in self._rows.values()
            if fact.org_id == org_id and fact.occurred_at.date() == day and _role_ok(fact, role_code)
        ]

    def _arrived_refs(self, org_id: int, day: date, role_code: str | None) -> set[str]:
        return {
            fact.link_ref
            for fact in self._on(org_id, day, role_code)
            if fact.kind == "arrival" and fact.link_ref
        }


def _role_ok(fact: Fact, role_code: str | None) -> bool:
    return role_code is None or fact.role_code == role_code


def _money(value: str | None) -> Decimal:
    if value is None:
        raise ValueError("amount")
    return Decimal(value).quantize(_CENT, rounding=ROUND_HALF_UP)


def _rate(hit: int, total: int) -> str | None:
    if total == 0:
        return None
    return f"{(Decimal(hit) / Decimal(total)).quantize(_CENT, rounding=ROUND_HALF_UP):.2f}"

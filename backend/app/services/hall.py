"""厅堂公有服务。页面以后把动作送到这里。

模型只留槽。打印、授权、签字、交付停在人。
库未启动，结果先写入 MemoryBiz。
"""

from datetime import datetime

from app.capabilities.units import (
    auth_decision,
    fill_from,
    intent_from,
    materials_for,
    take_ticket,
)
from app.gateway import begin
from app.services.chain import (
    ChainBlocked,
    build_steps,
    complete_current,
    current_id,
    revise,
)
from app.services.model_part import for_view, judge
from app.services.step_prompt import temporary_prompt
from app.threshold import DEFAULT_THRESHOLD
from app.services.daily import DailyBook, Fact
from app.session.hub import SessionHub
from app.storage.biz import MemoryBiz


def _owner(progress: dict) -> str | None:
    current = current_id(progress.get("steps") or [])
    for step in progress.get("steps") or []:
        if step.get("id") == current:
            return step.get("owner")
    return None


def _seat(role: str, step_id: str) -> None:
    """引导在大堂，办理在柜员，授权在支局长。管理员沿用原来的整链。"""
    if role == "admin":
        return
    if step_id == "ask" and role != "P4":
        raise ChainBlocked(step_id)
    if step_id == "authorize" and role != "P3":
        raise ChainBlocked(step_id)
    if step_id in {"recognize", "queue"} and role not in {"P1", "P4"}:
        raise ChainBlocked(step_id)
    if step_id in {
        "print_forms",
        "submit_credentials",
        "scan_fill",
        "password",
        "materials",
        "issue",
        "sign",
        "archive",
        "handover",
    } and role != "P1":
        raise ChainBlocked(step_id)


class HallDesk:
    def __init__(
        self,
        biz: MemoryBiz | None = None,
        hub: SessionHub | None = None,
        daily: DailyBook | None = None,
    ) -> None:
        self.biz = biz or MemoryBiz()
        self.hub = hub or SessionHub()
        self.daily = daily or DailyBook()
        self._ticket = 0

    def handoff(
        self,
        role: str,
        *,
        org_id: int,
        post_id: int,
        appointment: dict,
        seats_free: int,
        threshold: str = DEFAULT_THRESHOLD,
        trace_id: str | None = None,
        linked: bool = False,
    ) -> dict:
        ctx = begin(role, "hall.handoff", write=True, trace_id=trace_id)
        intent = intent_from(appointment)
        forms = materials_for(intent["intent"])
        self._ticket += 1
        ticket = take_ticket(self._ticket, seats_free)
        amount = str(appointment.get("amount") or "0")
        steps = build_steps(amount, threshold, need_print=bool(forms["forms"]))
        if not linked:
            for step_id in ("ask", "recognize", "queue"):
                complete_current(steps, step_id)
        state = self.hub.open(
            org_id=org_id,
            post_id=post_id,
            external_customer_ref=appointment.get("customer_ref"),
        )
        progress = {
            "flow": "time_deposit_rollover",
            "intent": intent,
            "ticket": ticket["ticket"],
            "seats_free": seats_free,
            "print_option": {"forms": forms["forms"], "printed": False},
            "fields_by_step": {},
            "password_locked": False,
            "amount": amount,
            "auth_threshold": threshold,
            "auth": auth_decision(amount, threshold),
            "appointment": dict(appointment),
            "steps": steps,
            "trace_id": ctx.trace_id,
        }
        self.hub.save_progress(state.id, progress, org_id=org_id)
        return self._view(state.id, org_id, ctx.trace_id, ctx.op_id)

    def complete_step(
        self,
        role: str,
        *,
        org_id: int,
        session_id: str,
        step_id: str,
        payload: dict | None = None,
        staff_id: int | None = None,
        trace_id: str | None = None,
    ) -> dict:
        ctx = begin(role, "hall.step", write=True, trace_id=trace_id)
        payload = payload or {}
        progress = self._progress(session_id, org_id)
        self._check_payload(progress, step_id, payload, role)
        owner = next(step["owner"] for step in progress["steps"] if step["id"] == step_id)
        if owner == "model":
            judgment = judge(progress, step_id)
            if judgment["stop"]:
                raise ChainBlocked(tuple(judgment["missing"]))
            progress["fields_by_step"][step_id] = {
                "business": judgment["business"],
                "missing": "、".join(judgment["missing"]),
            }
        if step_id == "scan_fill":
            filled = fill_from(progress["appointment"], payload)
            if filled["human_required"]:
                raise ChainBlocked(tuple(filled["human_required"]))
            progress["fields_by_step"]["scan_fill"] = filled["fields"]
        if step_id == "password":
            progress["password_locked"] = True
        if step_id == "print_forms":
            progress["print_option"]["printed"] = True
        if step_id == "archive":
            self._archive(progress, session_id, staff_id, ctx.trace_id, ctx.op_id)
        complete_current(progress["steps"], step_id)
        if step_id == "handover":
            self.hub.set_status(session_id, "completed", org_id=org_id)
        progress["trace_id"] = ctx.trace_id
        self.hub.save_progress(session_id, progress, org_id=org_id)
        return self._view(session_id, org_id, ctx.trace_id, ctx.op_id)

    def revise_step(
        self,
        role: str,
        *,
        org_id: int,
        session_id: str,
        step_id: str,
        trace_id: str | None = None,
    ) -> dict:
        ctx = begin(role, "hall.revise", write=True, trace_id=trace_id)
        progress = self._progress(session_id, org_id)
        revise(progress["steps"], step_id, password_locked=progress["password_locked"])
        order = [step["id"] for step in progress["steps"]]
        drop_ids = set(order[order.index(step_id):])
        progress["fields_by_step"] = {
            key: value for key, value in progress["fields_by_step"].items() if key not in drop_ids
        }
        self.hub.save_progress(session_id, progress, org_id=org_id)
        return self._view(session_id, org_id, ctx.trace_id, ctx.op_id)

    def _check_payload(self, progress: dict, step_id: str, payload: dict, role: str) -> None:
        if current_id(progress["steps"]) != step_id:
            raise ChainBlocked(step_id)
        _seat(role, step_id)
        owner = next(step["owner"] for step in progress["steps"] if step["id"] == step_id)
        if owner == "human" and payload.get("confirmed") is not True:
            raise ChainBlocked(step_id)
        if step_id == "authorize" and progress["auth"]["required"] and payload.get("confirmed") is not True:
            raise ChainBlocked(step_id)

    def _archive(self, progress: dict, session_id: str, staff_id: int | None, trace_id: str, op_id: str | None) -> None:
        if staff_id is None or op_id is None:
            raise ChainBlocked("archive")
        now = datetime.now()
        self.biz.add_audit(trace_id, op_id, "hall.archive", staff_id)
        self.biz.add_performance(staff_id, "到期转存", progress["amount"], now, note=session_id)
        state = self.hub.load(session_id)
        post_id = state.post_id
        role_code = ""
        if post_id is not None:
            self.biz.add_task(post_id, "到期转存", session_id, status="done")
            for post in self.biz.post:
                if post["id"] == post_id:
                    role_code = post["role_code"]
        self.daily.collect(
            Fact(
                ref=f"business:{session_id}",
                org_id=state.org_id,
                post_id=post_id or 0,
                role_code=role_code,
                kind="business",
                occurred_at=now,
                staff_id=staff_id,
                customer_ref=progress.get("appointment", {}).get("customer_ref"),
                amount=progress.get("amount"),
                note="到期转存",
            )
        )

    def _progress(self, session_id: str, org_id: int) -> dict:
        state = self.hub.load(session_id)
        if state is None or state.org_id != org_id:
            raise KeyError(session_id)
        return state.progress

    def _view(self, session_id: str, org_id: int, trace_id: str, op_id: str | None) -> dict:
        state = self.hub.load(session_id)
        progress = state.progress
        return {
            "trace_id": trace_id,
            "op_id": op_id,
            "session_id": session_id,
            "org_id": org_id,
            "status": state.status,
            "current": current_id(progress["steps"]),
            "steps": progress["steps"],
            "ticket": progress["ticket"],
            "seats_free": progress["seats_free"],
            "print_option": progress["print_option"],
            "intent": progress["intent"],
            "auth": progress["auth"],
            "password_locked": progress["password_locked"],
            "fields_by_step": progress["fields_by_step"],
            "temporary_prompt": temporary_prompt(progress),
            "model_part": for_view(progress, current_id(progress["steps"]), _owner(progress)),
        }

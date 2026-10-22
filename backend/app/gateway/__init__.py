"""请求管道：trace_id、写操作 ID、fail-closed。"""

import uuid
from dataclasses import dataclass

from app.auth.can import can


def attach_trace(request_id: str | None = None) -> str:
    return request_id or uuid.uuid4().hex


def new_op_id() -> str:
    return uuid.uuid4().hex


@dataclass(frozen=True)
class RequestContext:
    trace_id: str
    op_id: str | None
    role: str
    action: str


class GateClosed(Exception):
    def __init__(self, ctx: RequestContext):
        self.ctx = ctx
        super().__init__(f"fail-closed: {ctx.role} {ctx.action}")


def begin(
    role: str,
    action: str,
    *,
    write: bool = False,
    trace_id: str | None = None,
) -> RequestContext:
    ctx = RequestContext(
        trace_id=attach_trace(trace_id),
        op_id=new_op_id() if write else None,
        role=role,
        action=action,
    )
    if not can(role, action):
        raise GateClosed(ctx)
    return ctx

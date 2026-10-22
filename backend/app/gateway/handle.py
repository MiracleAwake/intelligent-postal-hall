"""写会话进度：先过门，再进会话中枢。"""

from app.gateway import RequestContext, begin
from app.session.hub import SessionHub, SessionState

_hub = SessionHub()


def session_hub() -> SessionHub:
    return _hub


def sync_progress(
    role: str,
    *,
    org_id: int,
    session_id: str,
    progress: dict,
    trace_id: str | None = None,
    hub: SessionHub | None = None,
) -> dict:
    ctx = begin(role, "session.sync", write=True, trace_id=trace_id)
    state = (hub or _hub).save_progress(session_id, progress, org_id=org_id)
    return _receipt(ctx, state)


def _receipt(ctx: RequestContext, state: SessionState) -> dict:
    return {
        "trace_id": ctx.trace_id,
        "op_id": ctx.op_id,
        "session_id": state.id,
        "org_id": state.org_id,
        "progress": state.progress,
    }

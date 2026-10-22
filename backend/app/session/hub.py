"""会话中枢。同步的是会话进度，不是业务底库。库未启动时走内存。"""

import uuid
from dataclasses import dataclass


@dataclass
class SessionState:
    id: str
    org_id: int
    post_id: int | None
    external_customer_ref: str | None
    progress: dict
    status: str = "active"


class OrgLocked(Exception):
    """会话留在原网点，不能改 org_id。"""


class MemorySessionStore:
    def __init__(self) -> None:
        self._rows: dict[str, SessionState] = {}

    def get(self, session_id: str) -> SessionState | None:
        return self._rows.get(session_id)

    def put(self, state: SessionState) -> None:
        self._rows[state.id] = state


class SessionHub:
    def __init__(self, store: MemorySessionStore | None = None) -> None:
        self.store = store or MemorySessionStore()

    def open(
        self,
        *,
        org_id: int,
        post_id: int | None = None,
        external_customer_ref: str | None = None,
        session_id: str | None = None,
    ) -> SessionState:
        state = SessionState(
            id=session_id or str(uuid.uuid4()),
            org_id=org_id,
            post_id=post_id,
            external_customer_ref=external_customer_ref,
            progress={},
        )
        self.store.put(state)
        return state

    def load(self, session_id: str) -> SessionState | None:
        return self.store.get(session_id)

    def set_status(self, session_id: str, status: str, *, org_id: int) -> SessionState:
        current = self.store.get(session_id)
        if current is None:
            raise KeyError(session_id)
        if current.org_id != org_id:
            raise OrgLocked(session_id)
        current.status = status
        self.store.put(current)
        return current

    def save_progress(self, session_id: str, progress: dict, *, org_id: int) -> SessionState:
        current = self.store.get(session_id)
        if current is None:
            raise KeyError(session_id)
        if current.org_id != org_id:
            raise OrgLocked(session_id)
        current.progress = dict(progress)
        self.store.put(current)
        return current

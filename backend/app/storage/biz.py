"""业务库的内存仓储。导入不会去连 MySQL。

业绩挂人，管户和任务挂岗位。调岗只关闭旧任职、打开新任职。
"""

from dataclasses import dataclass, field
from datetime import datetime


def _copy(row: dict) -> dict:
    return dict(row)


@dataclass
class MemoryBiz:
    org: list[dict] = field(default_factory=list)
    staff: list[dict] = field(default_factory=list)
    post: list[dict] = field(default_factory=list)
    assignment: list[dict] = field(default_factory=list)
    performance_entry: list[dict] = field(default_factory=list)
    customer_binding: list[dict] = field(default_factory=list)
    task_item: list[dict] = field(default_factory=list)
    audit_event: list[dict] = field(default_factory=list)
    _seq: int = 0

    def _id(self) -> int:
        self._seq += 1
        return self._seq

    def add_org(self, code: str, name: str) -> dict:
        row = {"id": self._id(), "code": code, "name": name}
        self.org.append(row)
        return _copy(row)

    def add_staff(self, employee_no: str, name: str) -> dict:
        row = {"id": self._id(), "employee_no": employee_no, "name": name}
        self.staff.append(row)
        return _copy(row)

    def add_post(self, org_id: int, role_code: str, title: str) -> dict:
        row = {"id": self._id(), "org_id": org_id, "role_code": role_code, "title": title}
        self.post.append(row)
        return _copy(row)

    def open_assignment(self, staff_id: int, post_id: int, started_at: datetime) -> dict:
        row = {
            "id": self._id(),
            "staff_id": staff_id,
            "post_id": post_id,
            "started_at": started_at,
            "ended_at": None,
        }
        self.assignment.append(row)
        return _copy(row)

    def transfer(self, staff_id: int, post_id: int, at: datetime) -> dict:
        for row in self.assignment:
            if row["staff_id"] == staff_id and row["ended_at"] is None:
                row["ended_at"] = at
        return self.open_assignment(staff_id, post_id, at)

    def add_performance(
        self,
        staff_id: int,
        subject: str,
        amount: str | None,
        occurred_at: datetime,
        note: str | None = None,
    ) -> dict:
        row = {
            "id": self._id(),
            "staff_id": staff_id,
            "subject": subject,
            "amount": amount,
            "note": note,
            "occurred_at": occurred_at,
        }
        self.performance_entry.append(row)
        return _copy(row)

    def bind_customer(
        self,
        post_id: int,
        source_system: str,
        external_id: str,
        display_name: str | None = None,
    ) -> dict:
        for row in self.customer_binding:
            if (
                row["post_id"] == post_id
                and row["source_system"] == source_system
                and row["external_id"] == external_id
            ):
                return _copy(row)
        row = {
            "id": self._id(),
            "post_id": post_id,
            "source_system": source_system,
            "external_id": external_id,
            "display_name": display_name,
        }
        self.customer_binding.append(row)
        return _copy(row)

    def add_task(self, post_id: int, title: str, session_id: str | None = None, status: str = "open") -> dict:
        row = {
            "id": self._id(),
            "post_id": post_id,
            "title": title,
            "status": status,
            "session_id": session_id,
        }
        self.task_item.append(row)
        return _copy(row)

    def add_audit(self, trace_id: str, op_id: str, action: str, actor_staff_id: int | None) -> dict:
        row = {
            "id": self._id(),
            "trace_id": trace_id,
            "op_id": op_id,
            "action": action,
            "actor_staff_id": actor_staff_id,
        }
        self.audit_event.append(row)
        return _copy(row)

    def performances_of(self, staff_id: int) -> list[dict]:
        return [_copy(row) for row in self.performance_entry if row["staff_id"] == staff_id]

    def bindings_of(self, post_id: int) -> list[dict]:
        return [_copy(row) for row in self.customer_binding if row["post_id"] == post_id]

    def tasks_of(self, post_id: int) -> list[dict]:
        return [_copy(row) for row in self.task_item if row["post_id"] == post_id]

    def open_post_of(self, staff_id: int) -> dict | None:
        for row in self.assignment:
            if row["staff_id"] == staff_id and row["ended_at"] is None:
                for post in self.post:
                    if post["id"] == row["post_id"]:
                        return _copy(post)
        return None

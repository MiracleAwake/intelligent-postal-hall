"""统一权限门。开发期管理员可恒真；禁止在业务里散落 if admin。"""


def can(role: str, action: str) -> bool:
    if role == "admin":
        return True
    if action in {"hall.handoff", "hall.step", "hall.revise"} and role in {"P1", "P3", "P4"}:
        return True
    if action.startswith("tool."):
        from app.assembly.roles import assemble

        return action.split(".", 1)[1] in assemble(role)
    return False

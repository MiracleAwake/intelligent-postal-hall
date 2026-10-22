"""业务链的亮灭。密码锁定后不能沿原链修改。"""

from decimal import Decimal

STEPS = (
    ("ask", "human", "大堂问询"),
    ("recognize", "model", "预约转流程"),
    ("queue", "system", "叫号与空位"),
    ("print_forms", "human", "一键打印"),
    ("submit_credentials", "human", "提交凭证"),
    ("scan_fill", "rpa", "扫描填写"),
    ("password", "human", "输入密码"),
    ("authorize", "human", "人工授权"),
    ("materials", "model", "其余材料"),
    ("issue", "rpa", "出单"),
    ("sign", "human", "签字确认"),
    ("archive", "system", "收录入库"),
    ("handover", "human", "交付结果"),
)


class ChainBlocked(Exception):
    """当前步还没做完，不能往下走。"""


class ChainLocked(Exception):
    """密码已确认，要改就重开这笔交易。"""


def build_steps(amount: str, threshold: str, *, need_print: bool) -> list[dict]:
    steps = []
    for step_id, owner, title in STEPS:
        status = "pending"
        if step_id == "authorize" and Decimal(amount) < Decimal(threshold):
            status = "skipped"
        if step_id == "print_forms" and not need_print:
            status = "skipped"
        steps.append({"id": step_id, "owner": owner, "title": title, "status": status})
    activate(steps)
    return steps


def activate(steps: list[dict]) -> None:
    if any(step["status"] == "current" for step in steps):
        return
    for step in steps:
        if step["status"] == "pending":
            step["status"] = "current"
            return


def current_id(steps: list[dict]) -> str | None:
    for step in steps:
        if step["status"] == "current":
            return step["id"]
    return None


def complete_current(steps: list[dict], step_id: str) -> None:
    if current_id(steps) != step_id:
        raise ChainBlocked(step_id)
    for step in steps:
        if step["id"] == step_id:
            step["status"] = "done"
    activate(steps)


def revise(steps: list[dict], step_id: str, *, password_locked: bool) -> None:
    if password_locked:
        raise ChainLocked(step_id)
    seen = False
    for step in steps:
        if step["id"] == step_id:
            seen = True
        if seen and step["status"] != "skipped":
            step["status"] = "pending"
    if not seen:
        raise ChainBlocked(step_id)
    activate(steps)

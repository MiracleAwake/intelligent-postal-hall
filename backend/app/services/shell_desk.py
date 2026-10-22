"""壳上的待办、气泡和实数。只认名册、客户库和已经发生的转交。

没有记录就不给数字。管理员不拿客户名单，也不拿客户人数。
"""

_CUSTOMER_ROLES = {"P1", "P2", "P3", "P4"}
_LABEL = {"P1": "支局经理", "P2": "普通柜员", "P3": "邮政营业", "P4": "大堂经理", "P5": "系统管理员"}


def snapshot(shell_role: str, staff: list, customers: list, handoffs: list) -> dict:
    notices: dict[str, dict] = {}
    if shell_role in _CUSTOMER_ROLES:
        focus = [row for row in customers if row.get("focus")]
        if focus:
            notices["客户"] = {"n": len(focus), "tip": f"重点客户 {len(focus)} 人"}
    names = {shell_role, _LABEL.get(shell_role, "")}
    mine = [
        row for row in handoffs
        if row.get("to_owner") in names and row.get("status", "requested") == "requested"
    ]
    pins = []
    tasks = []
    board = []
    for row in mine:
        title = str(row.get("business") or "待收转交")
        pins.append({"title": title, "text": title})
        tasks.append({"i": "g-take", "t": title, "sn": "转交", "tm": "今日"})
        group = str(row.get("group") or "业务")
        slot = notices.setdefault(group, {"n": 0, "tip": ""})
        slot["n"] += 1
        slot["tip"] = f"{slot['tip']} · {title}" if slot["tip"] else title
        board.append([str(row.get("from") or "—"), title, "待收"])
    enter = [row for row in staff if row.get("account_state") == "enter"]
    figures = [
        {"t": "在册员工", "i": "g-users", "v": str(len(staff)), "u": "人", "s": f"可进门 {len(enter)} 人"},
    ]
    if shell_role in _CUSTOMER_ROLES:
        marked = sum(1 for row in customers if row.get("focus"))
        figures.append({
            "t": "在册客户",
            "i": "g-user",
            "v": str(len(customers)),
            "u": "人",
            "s": f"重点 {marked} 人",
        })
    if pins:
        figures.append({"t": "待处理", "i": "g-bell", "v": str(len(pins)), "u": "项", "s": pins[0]["title"]})
    return {"pins": pins, "notices": notices, "tasks": tasks, "figures": figures, "board": board}

"""三套岗位代号对照。入库和模型只用后端 role_code。

壳（2026-10-20）和登录页、组织花名册各用各的代号。这里不改那三处，也不改 assembly/roles.py。
"""

from app.assembly.roles import ROLE_LABELS

GUARD_REASON = "保安岗不建员工账号"

# 岗位名 → 后端 role_code。系统管理员是壳上的叫法，库里的标签是管理员。
_NAME_TO_ROLE = {
    "普通柜员": "P1",
    "邮政营业": "P2",
    "支局经理": "P3",
    "大堂经理": "P4",
    "管理员": "P5",
    "系统管理员": "P5",
}

# 壳上的 role 字段。P1 是支局经理，不是后端的普通柜员。
SHELL = {
    "P1": {"name": "支局经理", "home": "06_支局经理页.html", "cells": 22},
    "P2": {"name": "普通柜员", "home": "05_普通柜员页.html", "cells": 22},
    "P3": {"name": "邮政营业", "home": "07_邮政营业页.html", "cells": 26},
    "P4": {"name": "大堂经理", "home": "09_大堂经理页.html", "cells": 19},
    "P5": {"name": "系统管理员", "home": "08_管理员端.html", "cells": 22},
}

# 登录页 post。管理员在这张表上是 P0，理财经理是 P5。
LOGIN = {
    "P0": {"name": "系统管理员", "account": "enter"},
    "P1": {"name": "支局经理", "account": "enter"},
    "P2": {"name": "普通柜员", "account": "enter"},
    "P3": {"name": "邮政营业", "account": "enter"},
    "P4": {"name": "大堂经理", "account": "enter"},
    "P5": {"name": "理财经理", "account": "no_page", "note": "本版并入代理金融台，未单独成页"},
    "P6": {"name": "综合柜员", "account": "no_page", "note": "本版并入代理金融台，未单独成页"},
    "P7": {"name": "保安", "account": "refuse", "note": GUARD_REASON},
}

# 组织花名册。这里的 P0 是职能，不是登录页上的管理员。P7 不写入 post.role_code。
ROSTER = {
    "P0": {"name": "职能 / 后勤", "account": "no_counter"},
    "P1": {"name": "支局经理", "account": "enter"},
    "P2": {"name": "普通柜员", "account": "enter"},
    "P3": {"name": "邮政营业", "account": "enter"},
    "P4": {"name": "大堂经理", "account": "enter"},
    "P5": {"name": "理财经理", "account": "no_page", "note": "本版并入代理金融台，未单独成页"},
    "P6": {"name": "综合柜员", "account": "no_page", "note": "本版并入代理金融台，未单独成页"},
    "P7": {"name": "保安", "account": "refuse", "note": GUARD_REASON},
    "ADM": {"name": "系统管理员", "account": "enter"},
}

# 工号只记人和登录页代号。口令不在这里。
STAFF = (
    {"no": "1001", "name": "王××", "login": "P1"},
    {"no": "1002", "name": "钱××", "login": "P2"},
    {"no": "1003", "name": "赵××", "login": "P2"},
    {"no": "1017", "name": "秦××", "login": "P3"},
    {"no": "1004", "name": "孙××", "login": "P4"},
    {"no": "9001", "name": "区管理员", "login": "P0"},
    {"no": "1018", "name": "尤××", "login": "P5"},
    {"no": "1010", "name": "褚××", "login": "P6"},
    {"no": "1022", "name": "施××", "login": "P7"},
)


class RoleMapError(ValueError):
    pass


def role_for_name(name: str) -> str:
    """按岗位名取后端代号。理财经理、综合柜员、保安、职能岗没有这一格。"""
    code = _NAME_TO_ROLE.get(name)
    if code is None:
        raise RoleMapError(name)
    return code


def from_shell(code: str) -> dict:
    row = SHELL[code]
    role = role_for_name(row["name"])
    return {
        "source": "shell",
        "code": code,
        "name": row["name"],
        "role_code": role,
        "label": ROLE_LABELS[role],
        "home": row["home"],
        "cells": row["cells"],
    }


def from_login(code: str) -> dict:
    return _from_named("login", LOGIN, code)


def from_roster(code: str) -> dict:
    return _from_named("roster", ROSTER, code)


def _from_named(source: str, table: dict, code: str) -> dict:
    row = table[code]
    account = row["account"]
    out = {
        "source": source,
        "code": code,
        "name": row["name"],
        "account": account,
        "role_code": None,
        "note": row.get("note", ""),
    }
    if account == "enter":
        role = role_for_name(row["name"])
        out["role_code"] = role
        out["label"] = ROLE_LABELS[role]
    if account == "refuse":
        out["note"] = GUARD_REASON
    return out


def identify(staff_no: str) -> dict:
    """工号 → 身份。不核对口令，也不保存口令。"""
    found = next((row for row in STAFF if row["no"] == staff_no), None)
    if found is None:
        return {"kind": "unknown", "no": staff_no, "role_code": None}
    door = from_login(found["login"])
    out = {
        "kind": door["account"] if door["account"] != "enter" else "enter",
        "no": found["no"],
        "name": found["name"],
        "post_name": door["name"],
        "role_code": door["role_code"],
        "note": door["note"],
    }
    if out["kind"] == "refuse":
        out["reason"] = GUARD_REASON
    if out["kind"] == "enter":
        shell_code = _shell_code_for(door["name"])
        shell = from_shell(shell_code)
        out["home"] = shell["home"]
        out["cells"] = shell["cells"]
        out["session"] = "会话留在原网点"
    return out


def _shell_code_for(name: str) -> str:
    for code, row in SHELL.items():
        if row["name"] == name:
            return code
    raise RoleMapError(name)

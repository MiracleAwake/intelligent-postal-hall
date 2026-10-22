"""装配机制。五岗同一壳，工具表来自原型，不在这里写页面。"""

from app.capabilities.tools.catalog import tools_for

ROLES = ("P1", "P2", "P3", "P4", "P5")

ROLE_LABELS = {
    "P1": "普通柜员",
    "P2": "邮政营业",
    "P3": "支局经理",
    "P4": "大堂经理",
    "P5": "管理员",
}


def assemble(role: str) -> list[str]:
    return [tool.id for tool in tools_for(role)]

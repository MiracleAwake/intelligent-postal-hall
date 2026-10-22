"""小D里用过的优化策略。这里只留名字，检索和反思先不跑。"""

STRATEGIES = (
    ("query_rewrite", "查询改写"),
    ("crag", "检索质量评估后纠错重查"),
    ("self_rag", "先判断要不要检索，再自评答案"),
    ("instruction_isolate", "用户内容和系统指令隔开"),
)


def list_strategies() -> list[dict]:
    return [{"id": name, "label": label, "status": "standby"} for name, label in STRATEGIES]

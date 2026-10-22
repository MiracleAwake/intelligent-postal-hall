"""上下文按会话记。迭代提示词按岗位存一份现行正文，不挂在这台电脑上。

岗位口吻是另一份文档。这里的基础设定只写这个岗位要守住的做法。
合并时钉住基础设定和已经留下的规则，新经验接在后面。测试经过和重复句不进正文。
"""

from datetime import datetime


# 和「你是一位前辈」分开。P1 的基础来自今天下午柜面口述抽取里要留下来的规则。
FOUNDATION = {
    "P1": "\n".join(
        (
            "意图只从这几类里选，可以多选：改存期、取息、加钱、换储种、接着存、转活期。",
            "利息只标连本带息、取息、未说。",
            "「这笔」后面的金额记入原存单；「新增」「再加」的金额才记入追加。",
            "说了新增，意图里必须有加钱。",
            "没说新存期就列入缺失，不要编存期和金额。",
            "只有明确说打印新存单，才记为要打印。",
            "材料只认身份证、定期存单、定期存款凭条、利息支取单。",
            "没说代理就按本人；明确代办才标代理。",
            "一句里同时出现的改存期、取息、加钱都要留下。",
            "缺存期就停在这一步，打印入口亮着也不打印。",
            "人未到，先点出缺的材料和人，再停。",
        )
    ),
    "P2": "\n".join(
        (
            "收寄前三件要齐：实名、当面验视、禁限寄告知。",
            "重量只记同事或秤给出的读数。",
            "证件号码进系统，不抄上详情单。",
            "代交寄要核委托和受托两边的证件；姓名和证件不一致就不收寄。",
            "三件缺一件，就点出缺的那一件，不放行面单。",
            "详情单和实物不符，对方又拒绝修改的，不收寄。",
        )
    ),
    "P3": "\n".join(
        (
            "报表数字和点开的名单来自同一份归集。",
            "授权停在人。",
            "较昨日只用当天和前一天已经归集的数。",
            "退回必须写明缺的那一项。",
            "归集缺笔时不改报表上的显示数。",
            "没做的收寄验视不能在日终改成已做。",
        )
    ),
    "P4": "\n".join(
        (
            "进门先分流。",
            "预约收成办理顺序。",
            "回访到期就列出名单。",
            "客户四项不齐，日终只点出处理该条的同事。",
            "没做完的预约、分流、回访不提前勾成已做。",
            "人没到，不记到店。",
            "没指定到名册上的人，不把号叫进窗口。",
            "收寄客户领到营业窗口，门口不称重。",
        )
    ),
    "P5": "\n".join(
        (
            "这个阶段只观测。",
            "不改岗位，不改参数，不破玻璃。",
            "待确认的参数继续用现行值。",
            "破玻璃的复核人必须是另一个人。",
            "不打开客户正文，也不把告警改成正常。",
            "任务留在原岗位。",
        )
    ),
}

_LEDGER = ("测了", "测试", "这次跑", "本次跑", "超时", "GLM")


def summarize_work(items: list[str]) -> str:
    """把一段时间的工作收成一句。不写存储。"""
    return "；".join(item for item in items if item)


def _clauses(text: str) -> list[str]:
    parts = []
    for chunk in text.replace("；", "\n").splitlines():
        line = chunk.strip(" -\t")
        if line:
            parts.append(line)
    return parts


def _ledger(line: str) -> bool:
    if any(word in line for word in _LEDGER):
        return True
    if line.startswith(("今天", "今日", "上午", "下午", "昨天")) and not any(
        word in line for word in ("必须", "不要", "只", "停在", "记下")
    ):
        return True
    return False


def merge_iteration(existing: str, additions: list[str], role_code: str | None) -> str:
    pinned = _clauses(FOUNDATION.get(role_code or "", ""))
    kept: list[str] = []
    seen: set[str] = set()
    incoming = [line for item in additions for line in _clauses(item)]
    for line in pinned + _clauses(existing) + incoming:
        if _ledger(line) or line in seen:
            continue
        seen.add(line)
        kept.append(line)
    ordered: list[str] = []
    placed: set[str] = set()
    for line in pinned + kept:
        if line in placed:
            continue
        placed.add(line)
        ordered.append(line)
    return "\n".join(ordered)


class MemoryBook:
    def __init__(self) -> None:
        self.notes: list[dict] = []
        self.iteration: dict[int, dict] = {}

    def add(self, kind: str, text: str, *, session_id: str | None = None, post_id: int | None = None) -> dict:
        if kind in ("requirement", "summary") and post_id is None:
            raise ValueError("迭代记忆必须绑定岗位")
        if kind == "requirement":
            return self.iterate(post_id, [text])
        if kind == "summary":
            return self.iterate(post_id, [text])
        row = {
            "id": len(self.notes) + 1,
            "kind": kind,
            "text": text,
            "session_id": session_id,
            "post_id": post_id,
            "at": datetime.now().isoformat(timespec="seconds"),
        }
        self.notes.append(row)
        return dict(row)

    def context_of(self, session_id: str) -> list[dict]:
        return [dict(row) for row in self.notes if row["kind"] == "context" and row["session_id"] == session_id]

    def record_context(self, session_id: str, text: str) -> dict:
        return self.add("context", text, session_id=session_id)

    def record_requirement(self, post_id: int, text: str, *, role_code: str | None = None) -> dict:
        if post_id is None:
            raise ValueError("迭代记忆必须绑定岗位")
        return self.iterate(post_id, [text], role_code=role_code)

    def record_summary(self, post_id: int, items: list[str], *, role_code: str | None = None) -> dict:
        if post_id is None:
            raise ValueError("迭代记忆必须绑定岗位")
        return self.iterate(post_id, [summarize_work(items)], role_code=role_code)

    def iterate(self, post_id: int, additions: list[str], *, role_code: str | None = None) -> dict:
        if post_id is None:
            raise ValueError("迭代记忆必须绑定岗位")
        current = self.iteration.get(post_id)
        role = role_code or (current or {}).get("role_code") or ""
        body = merge_iteration("" if current is None else current["body"], additions, role or None)
        row = {
            "post_id": post_id,
            "role_code": role,
            "body": body,
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        }
        self.iteration[post_id] = row
        return dict(row)

    def current(self, post_id: int) -> str:
        row = self.iteration.get(post_id)
        return "" if row is None else row["body"]

    def prompts_for_post(self, post_id: int) -> list[dict]:
        body = self.current(post_id)
        if not body:
            return []
        return [{"kind": "iteration", "text": body, "post_id": post_id}]

    def row_for_save(self, post_id: int) -> tuple | None:
        """现行一份，对应 prompt_iteration 表。不连库。"""
        row = self.iteration.get(post_id)
        if row is None or not row["body"]:
            return None
        return (row["post_id"], row["role_code"], row["body"], row["updated_at"])


def apply_live_rule(book: MemoryBook, post_id: int, rule: str, *, role_code: str | None = None) -> dict:
    """办业务的当次调用。一句新规则才写入；重复或流水账不写。重复说明技能该改。"""
    line = (rule or "").strip()
    body = book.current(post_id)
    if not line or _ledger(line):
        return {"action": "drop", "body": body}
    held = _clauses(FOUNDATION.get(role_code or "", "")) + _clauses(body)
    if line in held:
        return {"action": "revise_skill", "body": body}
    row = book.iterate(post_id, [line], role_code=role_code)
    return {"action": "kept", "body": row["body"]}


def iteration_for_model(book: MemoryBook, post_id: int, role_code: str | None = None) -> str:
    """调用模型时只拿当前岗位的现行迭代提示词。没有迭代过则给该岗位的基础设定。"""
    body = book.current(post_id)
    if body:
        return body
    if role_code:
        return FOUNDATION.get(role_code, "")
    return ""


UPSERT_ITERATION = """
INSERT INTO prompt_iteration (post_id, role_code, body, updated_at)
VALUES (%s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
  role_code = VALUES(role_code),
  body = VALUES(body),
  updated_at = VALUES(updated_at)
""".strip()


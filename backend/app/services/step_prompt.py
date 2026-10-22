"""这一笔的临时提示词。只带上一步已经发生的业务事实，给下一步用。

不进岗位迭代，不进向量库，不带客户身份正文。
"""

import re

_ID_NO = re.compile(r"\d{17}[\dXx]")
_KEEP = ("intent", "new_term", "old_term", "amount", "party", "weight", "notice", "item_name", "missing", "printed")
_LABELS = {
    "intent": "意图",
    "new_term": "存期",
    "old_term": "原存期",
    "amount": "金额",
    "party": "办理人",
    "weight": "重量",
    "notice": "禁限寄告知",
    "item_name": "物品",
    "missing": "缺的一项",
    "printed": "已打印",
}


def _kept(key: str, value) -> str:
    if key not in _KEEP or value in (None, ""):
        return ""
    text = str(value).strip()
    if _ID_NO.search(text) or "crm:" in text:
        return ""
    return f"{_LABELS[key]}：{text}"


def temporary_prompt(progress: dict) -> dict:
    steps = progress.get("steps") or []
    done = [step for step in steps if step.get("status") == "done"]
    current = next((step for step in steps if step.get("status") == "current"), None)
    base = {"layer": "temporary", "persist": False, "session_only": True}
    if current is None:
        return {**base, "status": "none", "text": "", "for_model": False}
    lines = []
    if done:
        previous = done[-1]
        lines.append(f"上一步：{previous.get('title') or previous.get('id')}，已完成。")
        fields = (progress.get("fields_by_step") or {}).get(previous.get("id"), {})
        if isinstance(fields, dict):
            for key in _KEEP:
                line = _kept(key, fields.get(key))
                if line:
                    lines.append(line)
    intent = progress.get("intent") if isinstance(progress.get("intent"), dict) else {}
    facts = {
        "intent": intent.get("intent"),
        "new_term": intent.get("new_term"),
        "amount": progress.get("amount"),
    }
    for key, value in facts.items():
        line = _kept(key, value)
        if line and line not in lines:
            lines.append(line)
    lines.append(f"下一步只做：{current.get('title') or current.get('id')}。")
    owner = current.get("owner")
    for_model = owner == "model"
    if owner == "model":
        lines.append("这一步只判断要办什么、缺什么、该不该停。")
    elif owner == "rpa":
        lines.append("这一步按已知内容抄写。")
    elif owner == "system":
        lines.append("这一步由系统完成。")
    else:
        lines.append("这一步停在人。")
    return {**base, "status": "ready", "text": "\n".join(lines), "for_model": for_model}

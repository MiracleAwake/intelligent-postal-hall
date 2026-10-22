"""办理台口径。页面定稿后按这些函数接入。

业务、账户、活动三页共用这一套：模型只填它该填的，停等和分工停在人。
不读页面，不调用模型。
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Field:
    key: str
    source: str
    step: int
    value: str | None = None


@dataclass(frozen=True)
class ImageDoc:
    name: str
    step: int
    stored: bool = False
    skip_reason: str | None = None


def prepare_fields(fields: list[Field], known: dict, at: int) -> dict:
    """走到这一步才填。口述项留给柜员，模型不代答。"""
    filled: dict[str, str] = {}
    human_required: list[str] = []
    for field in fields:
        if field.step > at:
            continue
        if field.source == "manual":
            human_required.append(field.key)
            continue
        value = known.get(field.key)
        if value not in (None, ""):
            filled[field.key] = str(value)
        elif field.value not in (None, ""):
            filled[field.key] = str(field.value)
        else:
            human_required.append(field.key)
    return {"filled": filled, "human_required": human_required}


def blockers(fields: list[Field], docs: list[ImageDoc], at: int, *, handed: bool) -> list[str]:
    """不齐就不能完成这一步。口述项在转人工之后才算缺。影像缺了任何阶段都算。"""
    missing: list[str] = []
    for field in fields:
        if field.step != at:
            continue
        if field.source == "manual" and not handed:
            continue
        if field.value in (None, ""):
            missing.append(field.key)
    for doc in docs:
        if doc.step != at or doc.skip_reason:
            continue
        if not doc.stored:
            missing.append(doc.name)
    return missing


def mark_skip(reason: str) -> str:
    """不适用必须写理由。留空不算第三态。"""
    text = reason.strip()
    if not text:
        raise ValueError("reason")
    return text


def hand_to_human(steps: list[dict]) -> list[dict]:
    """转人工不是重置。已完成的步骤保持原负责人。"""
    out = []
    for step in steps:
        row = dict(step)
        if row.get("status") != "done":
            row["owner"] = "human"
        out.append(row)
    return out


def run_state(*, model_entered: bool, any_value: bool, waiting: bool, handed: bool) -> str:
    """待办是第四态：模型没进来、也没填过，不能显示成模型已经办过。"""
    if waiting:
        return "auth"
    if handed:
        return "human"
    if not model_entered and not any_value:
        return "todo"
    return "doing"


def gate_label(*, waiting: bool, owner: str) -> str:
    """停等要先于转人工，否则送审按钮出不来。"""
    if waiting:
        return "送主管审批"
    if owner == "human":
        return "办理"
    return "让模型走下一步"


def evidence_lines(library: dict[str, list[str]], step_name: str) -> list[str]:
    """步骤详情和依据抽屉读同一份。"""
    return list(library.get(step_name, []))


def propose_evidence(step_name: str, line: str) -> dict:
    """模型可以提出一条依据，同事确认前不算已入库。"""
    text = line.strip()
    if not text:
        raise ValueError("line")
    return {"step": step_name, "line": text, "source": "model", "accepted": False}


def assign_person(name: str, roster: list[tuple[str, str]]) -> dict:
    """活动分工指定到人。岗位名不算指定。"""
    people = {person for person, _title in roster}
    titles = {title for _person, title in roster}
    if name in titles and name not in people:
        return {"ok": False, "reason": "指定岗位等于没指定"}
    if name not in people:
        return {"ok": False, "reason": "不在本网点名册"}
    return {"ok": True, "name": name}


def effective_value(item: dict) -> str:
    """待确认的参数仍用旧值。规则只引用参数键，不抄数字。"""
    if item.get("status") == "wait":
        return str(item["value"])
    return str(item.get("effective", item["value"]))


def speak(templates: list[dict], key: str) -> dict:
    """只取已启用的话术。未启用的不进对客路径。"""
    found = next((row for row in templates if row["key"] == key), None)
    if found is None or not found.get("enabled"):
        return {"status": "blocked", "key": key}
    return {"status": "ready", "key": key, "text": found["text"]}


def agent_trace(*, authorizer: str, action: str, target: str, result: str) -> dict:
    """智能体代操作的责任挂在授权人身上。留痕不写被查看的内容。"""
    if not authorizer.strip():
        raise ValueError("authorizer")
    if result not in ("完成", "拒绝", "等待"):
        raise ValueError(result)
    return {
        "who": "智能体",
        "post": f"← {authorizer} 授权",
        "action": action,
        "target": target,
        "result": result,
    }

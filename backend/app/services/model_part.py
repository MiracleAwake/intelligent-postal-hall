"""模型在业务链上只做判断。不抄写，不按打印、密码、授权、签字、交付，不写文件，不调设备。

不调用正在跑的模型。库没开，判断用已经知道的事实。
"""

_DOES = ("要办什么", "缺什么", "该不该停")
_LEAVES = ("抄写已知字段", "打印", "输入密码", "授权", "签字", "交付", "写文件", "调用第三方设备")


def participation(owner: str | None) -> dict:
    if owner == "model":
        return {
            "participates": True,
            "does": list(_DOES),
            "leaves": list(_LEAVES),
            "calls_provider": False,
        }
    if owner == "rpa":
        return {
            "participates": False,
            "does": ["按已知内容抄写"],
            "leaves": ["调用模型"],
            "calls_provider": False,
        }
    if owner == "system":
        return {
            "participates": False,
            "does": ["系统记账或叫号"],
            "leaves": ["调用模型"],
            "calls_provider": False,
        }
    return {
        "participates": False,
        "does": ["停在人"],
        "leaves": ["调用模型"],
        "calls_provider": False,
    }


def for_view(progress: dict, current: str | None, owner: str | None) -> dict:
    part = participation(owner)
    if owner == "model" and current:
        part["judgment"] = judge(progress, current)
    return part


def judge(progress: dict, step_id: str) -> dict:
    """只复述已经出现的意图和缺项。不补存期、金额、重量。"""
    intent = progress.get("intent") if isinstance(progress.get("intent"), dict) else {}
    known = _known(progress)
    missing: list[str] = []
    if step_id == "recognize" and not intent.get("intent"):
        missing.append("intent")
    if progress.get("flow") == "time_deposit_rollover" and step_id in ("recognize", "materials"):
        if not known.get("new_term"):
            missing.append("new_term")
    return {
        "executor": "model-slot",
        "business": intent.get("intent") or "",
        "missing": missing,
        "stop": bool(missing),
        "calls_provider": False,
    }


def _known(progress: dict) -> dict:
    found = {}
    intent = progress.get("intent") if isinstance(progress.get("intent"), dict) else {}
    if intent.get("new_term"):
        found["new_term"] = intent["new_term"]
    appointment = progress.get("appointment") if isinstance(progress.get("appointment"), dict) else {}
    if appointment.get("new_term"):
        found["new_term"] = appointment["new_term"]
    for fields in (progress.get("fields_by_step") or {}).values():
        if isinstance(fields, dict) and fields.get("new_term"):
            found["new_term"] = fields["new_term"]
    return found

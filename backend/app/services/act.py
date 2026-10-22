"""写文件和第三方设备的三段。判断、抄已知字段、停在人。

不调用模型，不编读数，抄完不自动提交。
"""

from app.services.model_part import judge

_COPY_KEYS = ("intent", "new_term", "old_term", "amount", "party", "item_name", "weight", "notice")


def run_act(stage: str, payload: dict | None = None) -> dict:
    payload = payload or {}
    if stage == "judge":
        known = payload.get("known") if isinstance(payload.get("known"), dict) else {}
        intent = payload.get("intent") if isinstance(payload.get("intent"), dict) else {}
        if not intent and payload.get("business"):
            intent = {"intent": payload.get("business")}
        progress = {
            "flow": payload.get("flow") or "",
            "intent": intent,
            "appointment": known,
            "fields_by_step": {},
        }
        judged = judge(progress, str(payload.get("step") or "recognize"))
        return {"stage": "judge", **judged}
    if stage == "copy":
        known = payload.get("known") if isinstance(payload.get("known"), dict) else {}
        fields = {}
        for key in _COPY_KEYS:
            value = known.get(key)
            if value not in (None, ""):
                text = str(value).strip()
                if text:
                    fields[key] = text
        return {
            "stage": "copy",
            "executor": "rpa",
            "fields": fields,
            "stop": not fields,
            "calls_provider": False,
            "submitted": False,
        }
    if stage == "device":
        kind = str(payload.get("kind") or "scale")
        reading = payload.get("reading")
        base = {"stage": "device", "owner": "human", "kind": kind, "model_supplied": False}
        if reading in (None, ""):
            return {**base, "status": "waiting"}
        return {**base, "status": "read", "reading": str(reading), "source": "human"}
    return {"stage": stage, "status": "rejected"}

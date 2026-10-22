"""公有能力。模型动作返回 model-slot，这一步不调用模型。"""

from decimal import Decimal

from app.capabilities.registry import Capability, register
from app.capabilities.tools.catalog import all_tools
from app.storage.biz import MemoryBiz

_LOADED = False


def intent_from(appointment: dict) -> dict:
    return {
        "executor": "model-slot",
        "intent": appointment.get("intent") or "改存期",
        "product": "定期到期转存",
        "customer_ref": appointment.get("customer_ref"),
    }


def materials_for(intent: str) -> dict:
    forms = {
        "改存期": ["定期存款凭条"],
        "取息": ["定期存款凭条", "利息支取单"],
    }.get(intent, ["定期存款凭条"])
    return {"executor": "model-slot", "forms": forms}


def fill_from(appointment: dict, scanned: dict) -> dict:
    fields: dict[str, str] = {}
    for key in ("customer_ref", "amount", "old_term", "new_term"):
        value = scanned.get(key) or appointment.get(key)
        if value:
            fields[key] = value
    missing = [key for key in ("new_term",) if key not in fields]
    return {"executor": "rpa", "fields": fields, "human_required": missing}


def take_ticket(number: int, seats_free: int) -> dict:
    return {
        "executor": "system",
        "ticket": f"A{number:03d}",
        "seats_free": seats_free,
    }


def auth_decision(amount: str, threshold: str) -> dict:
    if Decimal(amount) < Decimal(threshold):
        return {"required": False, "status": "skipped", "executor": "system"}
    return {
        "required": True,
        "status": "waiting",
        "owner": "human",
        "executor": "system",
        "targets": ["综合柜员", "支局经理"],
    }


def retrieve() -> dict:
    return {"executor": "system", "hits": [], "connected": False}


def staff_post(biz: MemoryBiz, staff_id: int) -> dict:
    post = biz.open_post_of(staff_id)
    return {"executor": "system", "post": post}


def load() -> None:
    global _LOADED
    if _LOADED:
        return
    catalog = (
        Capability("session", "system", "会话进度，留在原网点"),
        Capability("intent", "model", "预约转成办理意图"),
        Capability("retrieve", "system", "检索；向量库未连接"),
        Capability("notify", "system", "叫号或授权通知"),
        Capability("audit", "system", "审计留痕"),
        Capability("staff_post_query", "system", "当前岗位"),
        Capability("material_list", "model", "需填材料清单"),
        Capability("fill_fields", "rpa", "已知字段按固定步骤抄写，缺项停住"),
        Capability("print_option", "human", "人到打印机后才打印"),
        Capability("auth_request", "human", "达到额度才等人授权"),
        Capability("archive", "system", "办结写入业务库"),
        Capability("daily_rollup", "system", "本日业务归集；数字与明细同一份"),
        Capability("step_prepare", "model", "办理台回填；口述项留给柜员"),
        Capability("step_block", "system", "缺项不推进；停等先于转人工"),
        Capability("evidence_sheet", "model", "依据按步提出，确认前不算入库"),
        Capability("activity_assign", "human", "活动分工指定到人"),
        Capability("script_pick", "model", "只用已启用的话术"),
        Capability("param_read", "system", "待确认参数仍用旧值"),
        Capability("agent_trace", "system", "代操作留痕挂在授权人"),
        Capability("stat_window", "system", "统计窗一份壳；关窗才能再开"),
        Capability("dual_review", "human", "调岗复核两人；确认后五件事一起落"),
        Capability("side_shell", "system", "侧栏五种内容共用一具窗"),
        Capability("report_floor", "system", "报表只给汇总量，不足下限的行不列出"),
        Capability("service_health", "system", "服务状态由告警条数推出"),
        Capability("context_memory", "system", "会话上下文备用"),
        Capability("prompt_memory", "system", "迭代总结能力；记忆按岗位取，不挂在机器上"),
        Capability("optimize", "system", "检索改写与反思策略备用"),
        Capability("multimodal", "system", "图像入口备用，未接视觉模型"),
        Capability("speech_input", "system", "语音转成文字后再进入口述；未接识别引擎"),
    )
    for cap in catalog:
        register(cap)
    for tool in all_tools():
        register(Capability(f"tool.{tool.id}", tool.kind, tool.label))
    _LOADED = True

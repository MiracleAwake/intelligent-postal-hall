"""能用提示词完成的 skill。硬件和核心系统不在这里假装办完。"""

import json

from app.provider.client import Provider, parse_json_object


ALLOWED_FORMS = ("身份证", "定期存单", "定期存款凭条", "利息支取单")
FILL_KEYS = ("customer_ref", "amount", "old_term", "new_term")


def _ask(provider: Provider, prompt: str, *, profile_id: str | None = None) -> dict:
    reply = provider.complete(prompt, profile_id=profile_id)
    data = parse_json_object(reply) or {}
    data["executor"] = "model"
    data["parsed"] = bool(parse_json_object(reply))
    data["profile_id"] = provider.profile(profile_id).id
    return data


def materials_for_intent(provider: Provider, intent: str, *, profile_id: str | None = None) -> dict:
    prompt = (
        "邮政柜面。客户意图是「"
        + intent
        + "」。forms 只能从下面名单里选，不能新造名称："
        + "、".join(ALLOWED_FORMS)
        + '。只输出 JSON：{"forms":["身份证"],"summary":"一句"}'
    )
    data = _ask(provider, prompt, profile_id=profile_id)
    forms = data.get("forms")
    picked = [str(item) for item in forms] if isinstance(forms, list) else []
    data["forms"] = [name for name in picked if name in ALLOWED_FORMS]
    return data


def fill_known_fields(provider: Provider, known: dict, *, profile_id: str | None = None) -> dict:
    prompt = (
        "把已知信息抄进 fields。只能使用这些键："
        + "、".join(FILL_KEYS)
        + "。值必须来自已知，不能编。已知里没有的键放进 missing。"
        '只输出 JSON：{"fields":{},"missing":[]}\n'
        f"已知：{json.dumps(known, ensure_ascii=False)}"
    )
    data = _ask(provider, prompt, profile_id=profile_id)
    fields = data.get("fields") if isinstance(data.get("fields"), dict) else {}
    kept = {}
    for key in FILL_KEYS:
        if key in known and known[key] not in ("", None):
            if str(fields.get(key) or "") == str(known[key]):
                kept[key] = str(known[key])
    data["fields"] = kept
    data["missing"] = [key for key in FILL_KEYS if key not in known or known[key] in ("", None)]
    return data


ALLOWED_INTENTS = ("改存期", "取息", "加钱", "换储种", "接着存", "转活期")
INTERESTS = ("连本带息", "取息", "未说")


def understand_request(provider: Provider, text: str, *, profile_id: str | None = None) -> dict:
    allowed = "、".join(ALLOWED_INTENTS)
    prompt = f"""你是邮政储蓄柜面的字段抽取器。把工作人员的一句话收成 JSON。
intents 只能从这里选，可多选：{allowed}。
interest 只能是：连本带息、取息、未说。连息、连本带息都写「连本带息」。
new_term 写成「3年」「1年」「2年」「5年」，没说就 null。
金额写成数字字符串，五万元是 "50000"，两万是 "20000"。没说的金额是 null。
base_amount 是原存单金额，add_amount 是这次新增的钱。
print_new_certificate：明确说打印新存单才 true，说先别打印或没提就是 false。
party：本人没说就写「本人」，明确是代理人写「代理」。
missing：客户还没定的字段名，例如没定存期就包含 new_term。不要编造没说的存期和金额。
只输出 JSON，不要解释。
示例：
话：连息转成三年，不追加资金，也不打印
JSON：{{"intents":["改存期"],"interest":"连本带息","new_term":"3年","base_amount":null,"add_amount":null,"print_new_certificate":false,"party":"本人","missing":[],"summary":"连息改三年"}}
话：利息支取，本金续存两年
JSON：{{"intents":["取息","改存期"],"interest":"取息","new_term":"2年","base_amount":null,"add_amount":null,"print_new_certificate":false,"party":"本人","missing":[],"summary":"取息后续存两年"}}
工作人员说：{text}
JSON："""
    data = _ask(provider, prompt, profile_id=profile_id)
    intents = data.get("intents")
    picked = [str(item) for item in intents] if isinstance(intents, list) else []
    data["intents"] = [name for name in picked if name in ALLOWED_INTENTS]
    if data.get("interest") not in INTERESTS:
        data["interest"] = "未说"
    data["new_term"] = _term(data.get("new_term"))
    data["base_amount"] = _money(data.get("base_amount"))
    data["add_amount"] = _money(data.get("add_amount"))
    flag = data.get("print_new_certificate")
    data["print_new_certificate"] = flag is True or flag == "true"
    if data.get("party") not in ("本人", "代理"):
        data["party"] = "本人"
    missing = data.get("missing")
    data["missing"] = [str(item) for item in missing] if isinstance(missing, list) else []
    data["summary"] = str(data.get("summary") or "")
    return data


def _term(value) -> str | None:
    if value in (None, "", "null"):
        return None
    text = str(value).replace(" ", "")
    aliases = {"三年": "3年", "一年": "1年", "两年": "2年", "五年": "5年", "三年期": "3年", "一年期": "1年"}
    return aliases.get(text, text)


def _money(value) -> str | None:
    if value in (None, "", "null", 0, "0"):
        return None
    digits = "".join(ch for ch in str(value) if ch.isdigit() or ch == ".")
    if not digits:
        return None
    if "." in digits:
        whole, frac = digits.split(".", 1)
        digits = whole + "." + frac[:2]
        if digits.endswith(".00"):
            digits = digits[:-3]
        elif digits.endswith(".0"):
            digits = digits[:-2]
    return digits.lstrip("0") or "0"


def precheck_materials(
    provider: Provider,
    required: list[str],
    have: list[str],
    *,
    profile_id: str | None = None,
) -> dict:
    prompt = (
        "对照应带材料和客户已有材料，指出还缺什么。不要把没有的说成已有。"
        '只输出 JSON：{"missing":[],"ready":false}\n'
        f"应带：{json.dumps(required, ensure_ascii=False)}\n"
        f"已有：{json.dumps(have, ensure_ascii=False)}"
    )
    data = _ask(provider, prompt, profile_id=profile_id)
    missing = data.get("missing")
    data["missing"] = [str(item) for item in missing] if isinstance(missing, list) else []
    data["ready"] = bool(data.get("ready")) and not data["missing"]
    return data

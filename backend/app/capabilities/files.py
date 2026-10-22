"""按已知内容起草一份文本，并导出成文件。

不编没给的金额和存期，不把身份证号写进文件。导出不是打印，也不办结。
"""

import hashlib
import re
from pathlib import Path

_ID_NO = re.compile(r"\d{17}[\dXx]")

KINDS = {
    "办理摘要": ("intent", "new_term", "note"),
    "定期存款凭条": ("intent", "new_term", "amount", "party"),
    "收寄说明": ("item_name", "weight", "notice"),
    "交接单": ("from_post", "to_post", "missing"),
}

LABELS = {
    "intent": "意图",
    "new_term": "存期",
    "amount": "金额",
    "party": "办理人",
    "note": "说明",
    "item_name": "物品",
    "weight": "重量",
    "notice": "禁限寄告知",
    "from_post": "交出岗位",
    "to_post": "接收岗位",
    "missing": "缺的一项",
}


def _clean(value) -> str:
    text = "" if value is None else str(value).strip()
    if not text or _ID_NO.search(text):
        return ""
    return text


def draft_document(kind: str, known: dict | None = None, body: str | None = None) -> dict:
    base = {"printed": False, "completes": False, "kind": kind}
    fields = KINDS.get(kind)
    if fields is None:
        return {**base, "status": "rejected", "text": ""}
    known = known or {}
    lines = [kind]
    for key in fields:
        lines.append(f"{LABELS[key]}：{_clean(known.get(key))}")
    spoken = _clean(body)
    if spoken:
        lines.extend(["", spoken])
    text = "\n".join(lines) + "\n"
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]
    return {
        **base,
        "status": "draft",
        "text": text,
        "filename": f"{kind}-{digest}.txt",
        "body_kept": bool(spoken),
    }


def export_document(draft: dict, directory: str) -> dict:
    if draft.get("status") != "draft" or not draft.get("filename"):
        return {"status": "rejected", "printed": False, "completes": False}
    root = Path(directory).resolve()
    root.mkdir(parents=True, exist_ok=True)
    path = (root / draft["filename"]).resolve()
    if path.parent != root:
        return {"status": "rejected", "printed": False, "completes": False}
    path.write_text(draft["text"], encoding="utf-8")
    return {
        "status": "exported",
        "path": str(path),
        "filename": draft["filename"],
        "printed": False,
        "completes": False,
    }

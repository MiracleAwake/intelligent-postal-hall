"""扫描后的文字提取，以及证件照和现场照的下位比对。

文字用本机已有的 RapidOCR。不调用国家身份核验接口。
没有人脸识别权重时，只给一张像素相似度，不能当成核验通过。
二维码和电子秤不在这里。
"""

import re

import cv2
import numpy as np

_ID_NO = re.compile(r"\d{17}[\dXx]")
_IMAGE_HEADS = (b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n", b"BM")


def _image(data: bytes) -> bool:
    return any(data.startswith(head) for head in _IMAGE_HEADS)


def mask_id(number: str) -> str:
    if len(number) < 8:
        return ""
    return number[:4] + "**********" + number[-4:]


def fields_from_lines(lines: list[str], doc_kind: str) -> dict:
    """从提取出的行里收证件字段。身份证号另给掩码，明文只留在当次的 id_no。"""
    if doc_kind != "身份证":
        return {}
    name = ""
    for line in lines:
        if line.startswith("姓名"):
            name = line.removeprefix("姓名").strip(" ：:")
            break
    found = _ID_NO.search("".join(lines))
    number = found.group(0).upper() if found else ""
    return {
        "name": name,
        "id_no": number,
        "id_masked": mask_id(number) if number else "",
    }


class PageReader:
    def __init__(self, ocr=None) -> None:
        self._ocr = ocr if ocr is not None else _rapid_lines

    def read(self, image: bytes, doc_kind: str = "") -> dict:
        if not image or not _image(image):
            return {"status": "unreadable", "doc_kind": doc_kind, "lines": [], "fields": {}}
        try:
            lines = [line for line in self._ocr(image) if line.strip()]
        except Exception:
            return {"status": "unreadable", "doc_kind": doc_kind, "lines": [], "fields": {}}
        return {
            "status": "read" if lines else "empty",
            "doc_kind": doc_kind,
            "engine": "RapidOCR",
            "lines": lines,
            "fields": fields_from_lines(lines, doc_kind),
            "persist_id": False,
        }


def _rapid_lines(image: bytes) -> list[str]:
    from rapidocr_onnxruntime import RapidOCR

    engine = _rapid_lines.engine
    if engine is None:
        engine = RapidOCR()
        _rapid_lines.engine = engine
    result, _elapsed = engine(image)
    if not result:
        return []
    return [str(item[1]) for item in result if len(item) > 1]


_rapid_lines.engine = None


def pixel_hint(left: bytes, right: bytes) -> float | None:
    """两张图缩成小块后的相似度。不是人脸识别模型，也不是国家核验。"""
    first = cv2.imdecode(np.frombuffer(left, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
    second = cv2.imdecode(np.frombuffer(right, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
    if first is None or second is None:
        return None
    first = cv2.resize(first, (32, 32)).astype(np.float32)
    second = cv2.resize(second, (32, 32)).astype(np.float32)
    denom = float(np.linalg.norm(first) * np.linalg.norm(second))
    if denom == 0:
        return None
    return float(np.dot(first.ravel(), second.ravel()) / denom)


def compare_photos(doc: bytes | None, live: bytes | None) -> dict:
    base = {
        "authority": "local-pixel",
        "national": False,
        "verified": False,
        "pass": False,
    }
    if not doc or not live:
        return {**base, "status": "waiting", "need": "doc_and_live", "hint_score": None}
    score = pixel_hint(doc, live)
    if score is None:
        return {**base, "status": "unreadable", "hint_score": None}
    return {**base, "status": "hint", "hint_score": round(score, 4)}

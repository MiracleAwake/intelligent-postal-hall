"""多模态入口。只收图片指针和说明，不加载视觉模型。"""


def accept_image(ref: str, note: str = "") -> dict:
    return {
        "status": "standby",
        "ref": ref,
        "note": note,
        "connected": False,
    }

"""语音入口。页面负责把声音转成文字，这里只收那一句。

不连接识别引擎，不保存声音，不推进办理链。
"""

SPEECH_HOOK = {
    "id": "speech_input",
    "label": "语音输入",
    "panel": "agent",
    "fields": ("text", "audio_ref"),
}


def accept_speech(text: str | None = None, *, audio_ref: str | None = None) -> dict:
    """有文字就交给后续的口述抽取。只有声音指针时停在备用，不编一句。"""
    spoken = (text or "").strip()
    base = {
        "id": SPEECH_HOOK["id"],
        "source": "voice",
        "audio_kept": False,
        "connected": False,
        "completes": False,
    }
    if spoken:
        return {**base, "status": "ready", "text": spoken}
    if (audio_ref or "").strip():
        return {**base, "status": "standby", "text": "", "audio_ref": audio_ref.strip()}
    return {**base, "status": "empty", "text": ""}

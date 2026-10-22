"""采集口：选择导入、扫描仪、电脑摄像头。检测时不打开镜头。"""

import hashlib
import os
import subprocess


def _has_cv2() -> bool:
    try:
        import cv2  # noqa: F401
    except ImportError:
        return False
    return True


def _read_file(path: str) -> bytes:
    with open(path, "rb") as handle:
        return handle.read()


def _windows_image_devices() -> list[dict]:
    if os.name != "nt":
        return []
    script = (
        "Get-PnpDevice -Class Image,Camera -Status OK -ErrorAction SilentlyContinue | "
        "Select-Object -Property Class,FriendlyName | ConvertTo-Csv -NoTypeInformation"
    )
    try:
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            capture_output=True,
            text=True,
            timeout=4,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    devices = []
    for line in completed.stdout.splitlines()[1:]:
        parts = [part.strip('"') for part in line.split(",")]
        if len(parts) < 2 or not parts[1]:
            continue
        kind = "camera" if parts[0].lower() == "camera" else "scanner"
        devices.append({"id": f"{kind}:{parts[1]}", "kind": kind, "label": parts[1]})
    return devices


def _grab_cv2(index: int) -> bytes | None:
    try:
        import cv2
    except ImportError:
        return None
    camera = cv2.VideoCapture(index)
    if not camera.isOpened():
        camera.release()
        return None
    ok, frame = camera.read()
    camera.release()
    if not ok:
        return None
    encoded, buffer = cv2.imencode(".jpg", frame)
    if not encoded:
        return None
    return buffer.tobytes()


class Capture:
    def __init__(self, devices=None, camera_grabber=None, file_reader=None) -> None:
        self._devices = devices if devices is not None else _windows_image_devices
        self._grab = camera_grabber if camera_grabber is not None else _grab_cv2
        self._read = file_reader or _read_file

    def detect(self) -> dict:
        sources = [
            {"id": "import", "kind": "file", "label": "选择导入"},
            {
                "id": "camera:0",
                "kind": "camera",
                "label": "电脑摄像头",
                "driver": "opencv" if _has_cv2() else "missing",
            },
        ]
        sources.extend(self._devices())
        return {"sources": sources}

    def import_file(self, path: str, doc_kind: str) -> dict:
        data = self._read(path)
        return {
            "source": "import",
            "doc_kind": doc_kind,
            "filename": os.path.basename(path),
            "size": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }

    def camera_frame(self, index: int = 0) -> dict:
        data = self._grab(index)
        if not data:
            return {"source": "camera", "status": "unavailable", "index": index}
        return {
            "source": "camera",
            "status": "captured",
            "index": index,
            "size": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }

    def camera_bytes(self, index: int = 0) -> bytes | None:
        data = self._grab(index)
        return data or None

    def file_bytes(self, path: str) -> bytes:
        return self._read(path)

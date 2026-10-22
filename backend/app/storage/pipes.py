"""三条数据管道的地址。描述它们不会去连库。"""

from dataclasses import dataclass

from app.storage.settings import StorageSettings, load_settings


@dataclass(frozen=True)
class Pipe:
    name: str
    target: str
    connected: bool = False


def describe_pipes(settings: StorageSettings | None = None) -> dict[str, Pipe]:
    current = settings or load_settings()
    return {
        "biz": Pipe(
            "biz",
            f"mysql://{current.mysql_host}:{current.mysql_port}/{current.mysql_biz_db}",
        ),
        "session": Pipe(
            "session",
            f"mysql://{current.mysql_host}:{current.mysql_port}/{current.mysql_session_db}",
        ),
        "chroma": Pipe(
            "chroma",
            f"http://{current.chroma_host}:{current.chroma_port}",
        ),
    }

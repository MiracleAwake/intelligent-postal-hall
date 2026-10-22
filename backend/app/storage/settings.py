"""只读连接地址，不打开数据库。"""

import os
from dataclasses import dataclass


def _env(name: str, default: str) -> str:
    return os.getenv(name, default)


@dataclass(frozen=True)
class StorageSettings:
    mysql_host: str
    mysql_port: int
    mysql_user: str
    mysql_password: str
    mysql_biz_db: str
    mysql_session_db: str
    chroma_host: str
    chroma_port: int


def load_settings() -> StorageSettings:
    return StorageSettings(
        mysql_host=_env("MYSQL_HOST", "127.0.0.1"),
        mysql_port=int(_env("MYSQL_PORT", "3306")),
        mysql_user=_env("MYSQL_USER", "zhiyou"),
        mysql_password=_env("MYSQL_PASSWORD", "zhiyou"),
        mysql_biz_db=_env("MYSQL_BIZ_DB", "biz"),
        mysql_session_db=_env("MYSQL_SESSION_DB", "session"),
        chroma_host=_env("CHROMA_HOST", "127.0.0.1"),
        chroma_port=int(_env("CHROMA_PORT", "8000")),
    )

"""试连本机 MySQL。口令只在这一次连接里用，不落盘、不回给页面。"""

import re

import pymysql

_NAME = re.compile(r"^[A-Za-z0-9_]+$")


def try_mysql(host: str, port: int, user: str, password: str, database: str) -> dict:
    if not password:
        return {"status": "closed", "detail": "还没有口令"}
    try:
        conn = pymysql.connect(
            host=host or "127.0.0.1",
            port=int(port or 3306),
            user=user,
            password=password,
            database=database or None,
            connect_timeout=3,
            charset="utf8mb4",
        )
    except Exception as exc:
        detail = str(exc).replace(password, "")
        return {"status": "closed", "detail": detail}
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT VERSION()")
            version = cur.fetchone()[0]
            tables = []
            if database:
                cur.execute("SHOW TABLES")
                names = [row[0] for row in cur.fetchall()]
                for name in names:
                    if not _NAME.match(str(name)):
                        continue
                    cur.execute(f"SELECT COUNT(*) FROM `{name}`")
                    tables.append({"name": name, "rows": int(cur.fetchone()[0])})
        return {
            "status": "open",
            "version": version,
            "database": database,
            "tables": tables,
        }
    finally:
        conn.close()

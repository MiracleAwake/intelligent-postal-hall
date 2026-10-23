"""预约客户。页面上的按键按状态取同一套，岗位只决定看不看得到这一笔。"""

import sqlite3

from app.storage.people import connect

_SEED = (
    {
        "id": "a-zhou",
        "cid": "c009",
        "name": "周××",
        "line": "代理金融",
        "intent": "活期转定期 · 5 万元",
        "slot": "今日 17:10",
        "source": "线上预约",
        "status": "待到店",
        "roles": "P1,P2,P4",
        "actual": "",
    },
    {
        "id": "a-feng",
        "cid": "c010",
        "name": "冯××",
        "line": "政务代办",
        "intent": "交管补换领行驶证",
        "slot": "今日 14:30",
        "source": "大堂代约",
        "status": "已到店",
        "actual": "补换领行驶证 · 材料已核",
        "roles": "P1,P3,P4",
    },
)


def ensure_appointments(path=None) -> None:
    conn = connect(path)
    try:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS appointment (
                 id TEXT PRIMARY KEY,
                 name TEXT NOT NULL,
                 line TEXT NOT NULL,
                 intent TEXT NOT NULL,
                 slot TEXT NOT NULL,
                 source TEXT NOT NULL,
                 status TEXT NOT NULL,
                 roles TEXT NOT NULL,
                 actual TEXT NOT NULL DEFAULT '',
                 reminded INTEGER NOT NULL DEFAULT 0,
                 cid TEXT NOT NULL DEFAULT ''
               )"""
        )
        cols = {r[1] for r in conn.execute("PRAGMA table_info(appointment)").fetchall()}
        if "cid" not in cols:
            conn.execute("ALTER TABLE appointment ADD COLUMN cid TEXT NOT NULL DEFAULT ''")
        for row in _SEED:
            conn.execute(
                """INSERT OR IGNORE INTO appointment
                   (id, name, line, intent, slot, source, status, roles, actual)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    row["id"], row["name"], row["line"], row["intent"], row["slot"],
                    row["source"], row["status"], row["roles"], row.get("actual") or "",
                ),
            )
            conn.execute(
                "UPDATE appointment SET cid = ? WHERE id = ? AND cid = ''",
                (row["cid"], row["id"]),
            )
        conn.commit()
    finally:
        conn.close()


def _public(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "name": row["name"],
        "line": row["line"],
        "intent": row["intent"],
        "slot": row["slot"],
        "source": row["source"],
        "status": row["status"],
        "actual": row["actual"],
        "reminded": bool(row["reminded"]),
        "cid": row["cid"],
    }


def view(role: str, *, path=None) -> dict:
    ensure_appointments(path)
    if role == "P5":
        return {"items": []}
    conn = connect(path)
    try:
        rows = conn.execute(
            "SELECT * FROM appointment ORDER BY slot"
        ).fetchall()
    finally:
        conn.close()
    items = [_public(row) for row in rows if role in str(row["roles"]).split(",")]
    return {"items": items}


def act(role: str, appointment_id: str, action: str, *, path=None) -> dict:
    ensure_appointments(path)
    conn = connect(path)
    try:
        row = conn.execute(
            "SELECT * FROM appointment WHERE id = ?", (appointment_id,)
        ).fetchone()
        if row is None or role not in str(row["roles"]).split(","):
            return {"status": "missing"}
        if action == "remind":
            conn.execute(
                "UPDATE appointment SET reminded = 1 WHERE id = ?", (appointment_id,)
            )
        elif action == "reappoint":
            conn.execute(
                """UPDATE appointment
                   SET status = '待到店', reminded = 0, actual = ''
                   WHERE id = ?""",
                (appointment_id,),
            )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM appointment WHERE id = ?", (appointment_id,)
        ).fetchone()
    finally:
        conn.close()
    return {"status": "ok", "item": _public(row)}

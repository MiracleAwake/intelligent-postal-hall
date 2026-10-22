"""今日必办、任务和通知。

必办有两类：回访单记下的下次到访（含预约办理），以及提前定好的每周固定动作。
个人提醒以后再补。管理员不接收客户到访。

确认只销今天。每周固定的动作，下周同一天再出现。
到了当天才推进通知。转交是另一类系统消息，和必办分开进铃铛。
"""

from datetime import date, timedelta

from app.storage.people import connect

_VISITS = (
    ("c005", "赵文博", "下次回访", "短信未回复，约上午再联系", "2026-10-22", "上午", "P1,P2,P4", "客户"),
    ("c002", "李明远", "定期存款到期转存", "回访时约定三年期，15:44 到店", "2026-10-16", "15:44", "P1,P2,P4", "客户"),
    ("c006", "孙丽娟", "下次回访", "约上午联系", "2026-10-26", "上午", "P1,P2,P4", "客户"),
)
_WEEKLY = (
    ("检查数据", "每周四上午", 3, "09:00", "P5", "数据"),
    ("定期维护", "每周四下午", 3, "16:00", "P5", "系统"),
    ("权限复核", "每周一上午", 0, "09:00", "P1", "人员"),
)


def ensure_duties(path=None) -> None:
    conn = connect(path)
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS duty (
              id INTEGER PRIMARY KEY,
              kind TEXT NOT NULL,
              title TEXT NOT NULL,
              detail TEXT NOT NULL,
              customer_ref TEXT,
              due_on TEXT,
              weekday INTEGER,
              at_time TEXT,
              roles TEXT NOT NULL,
              source TEXT NOT NULL,
              grp TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS duty_confirm (
              duty_id INTEGER NOT NULL,
              on_date TEXT NOT NULL,
              PRIMARY KEY (duty_id, on_date)
            );
            CREATE TABLE IF NOT EXISTS notice (
              id INTEGER PRIMARY KEY,
              role TEXT NOT NULL,
              kind TEXT NOT NULL,
              duty_id INTEGER,
              on_date TEXT,
              title TEXT NOT NULL,
              body TEXT NOT NULL,
              dismissed_at TEXT
            );
            """
        )
        count = conn.execute("SELECT COUNT(*) FROM duty").fetchone()[0]
        if count:
            conn.commit()
            return
        for ref, name, title, detail, due, at, roles, grp in _VISITS:
            conn.execute(
                """INSERT INTO duty
                   (kind, title, detail, customer_ref, due_on, at_time, roles, source, grp)
                   VALUES ('visit', ?, ?, ?, ?, ?, ?, '回访', ?)""",
                (f"{name} · {title}", detail, ref, due, at, roles, grp),
            )
        for title, detail, weekday, at, roles, grp in _WEEKLY:
            conn.execute(
                """INSERT INTO duty
                   (kind, title, detail, weekday, at_time, roles, source, grp)
                   VALUES ('weekly', ?, ?, ?, ?, ?, '每周固定', ?)""",
                (title, detail, weekday, at, roles, grp),
            )
        conn.commit()
    finally:
        conn.close()


def _rows(conn):
    return [dict(row) for row in conn.execute("SELECT * FROM duty ORDER BY id")]


def _seen(conn, duty_id: int, day: str) -> bool:
    return (
        conn.execute(
            "SELECT 1 FROM duty_confirm WHERE duty_id = ? AND on_date = ?",
            (duty_id, day),
        ).fetchone()
        is not None
    )


def _is_due(row: dict, today: date) -> bool:
    if row["kind"] == "weekly":
        return today.weekday() == row["weekday"]
    return row["due_on"] == today.isoformat()


def _is_later(row: dict, today: date) -> bool:
    if row["kind"] != "visit" or not row["due_on"]:
        return False
    return row["due_on"] > today.isoformat()


def _for_role(row: dict, role: str) -> bool:
    return role in str(row["roles"]).split(",")


def _push(conn, role: str, row: dict, day: str) -> None:
    found = conn.execute(
        """SELECT id, dismissed_at FROM notice
           WHERE role = ? AND kind = 'duty' AND duty_id = ? AND on_date = ?""",
        (role, row["id"], day),
    ).fetchone()
    if found:
        return
    conn.execute(
        """INSERT INTO notice (role, kind, duty_id, on_date, title, body)
           VALUES (?, 'duty', ?, ?, ?, ?)""",
        (role, row["id"], day, row["title"], row["detail"]),
    )


def confirm(role: str, duty_id: int, *, today: date | None = None, path=None) -> dict:
    ensure_duties(path)
    day = (today or date.today()).isoformat()
    conn = connect(path)
    try:
        row = conn.execute("SELECT * FROM duty WHERE id = ?", (duty_id,)).fetchone()
        if row is None or role not in str(row["roles"]).split(","):
            return {"status": "missing"}
        conn.execute(
            "INSERT OR IGNORE INTO duty_confirm (duty_id, on_date) VALUES (?, ?)",
            (duty_id, day),
        )
        conn.execute(
            """UPDATE notice SET dismissed_at = ?
               WHERE role = ? AND duty_id = ? AND on_date = ? AND dismissed_at IS NULL""",
            (day, role, duty_id, day),
        )
        conn.commit()
    finally:
        conn.close()
    return {"status": "confirmed", "id": duty_id, "on": day}


def view(role: str, handoffs: list | None = None, *, today: date | None = None, path=None) -> dict:
    ensure_duties(path)
    today = today or date.today()
    day = today.isoformat()
    conn = connect(path)
    try:
        pins = []
        later = []
        due = 0
        badges: dict[str, int] = {}
        owned = False
        for row in _rows(conn):
            if not _for_role(row, role):
                continue
            owned = True
            if _is_later(row, today):
                later.append(_item(row))
                continue
            if not _is_due(row, today):
                continue
            due += 1
            if _seen(conn, row["id"], day):
                continue
            _push(conn, role, row, day)
            pins.append(_item(row))
            if row["grp"] == "客户":
                badges["客户"] = badges.get("客户", 0) + 1
        notices = [
            {
                "id": row["id"],
                "duty_id": row["duty_id"],
                "kind": row["kind"],
                "title": row["title"],
                "body": row["body"],
                "group": row["grp"] or "",
            }
            for row in conn.execute(
                """SELECT n.id, n.duty_id, n.kind, n.title, n.body, IFNULL(d.grp, '') AS grp
                   FROM notice n
                   LEFT JOIN duty d ON d.id = n.duty_id
                   WHERE n.role = ? AND n.dismissed_at IS NULL AND (n.on_date IS NULL OR n.on_date = ?)
                   ORDER BY n.id""",
                (role, day),
            )
        ]
        conn.commit()
    finally:
        conn.close()
    for row in handoffs or []:
        if row.get("to_owner") not in {role, _LABEL.get(role, "")}:
            continue
        if row.get("status", "requested") != "requested":
            continue
        notices.append(
            {
                "id": f"handoff-{row.get('id')}",
                "duty_id": None,
                "kind": "system",
                "title": str(row.get("business") or "待收转交"),
                "body": "转交",
                "group": "转交",
            }
        )
    if "客户" not in badges and any(_for_role(row, role) and row["grp"] == "客户" for row in _customer_rows(path)):
        badges["客户"] = 0
    return {"applies": owned, "pins": pins, "due": due, "later": later, "notices": notices, "badges": badges}


def _customer_rows(path):
    conn = connect(path)
    try:
        return _rows(conn)
    finally:
        conn.close()


def _item(row: dict) -> dict:
    when = row["at_time"] or ""
    return {
        "id": row["id"],
        "title": row["title"],
        "text": row["title"] + (f" · {when}" if when else ""),
        "detail": row["detail"],
        "source": row["source"],
        "group": row["grp"],
    }


_LABEL = {"P1": "支局经理", "P2": "普通柜员", "P3": "邮政营业", "P4": "大堂经理", "P5": "系统管理员"}


def next_week(today: date) -> date:
    return today + timedelta(days=7)

"""大堂经理首页的厅堂态势。块的顺序跟原型 09 主栏一致。

窗口、自助机、等候、预约、客流、平板都从这张库读。叫号改的是同一行。
"""

import sqlite3

from app.storage.people import connect

_WINDOWS = (
    ("w1", "01 号台", "代理金融", "办理中", "busy", "李×× · 定期转存", "已 6 分", 1),
    ("w2", "02 号台", "代理金融", "空闲", "free", "—", "—", 2),
    ("w3", "04 号台", "邮政营业", "办理中", "busy", "周×× · 寄包裹", "已 2 分", 3),
)
_KIOSKS = (
    ("k1", "自助机 A", "使用中", "busy", "客户自助办理", "已 3 分", 1),
    ("k2", "自助机 B", "空闲", "free", "—", "—", 2),
    ("k3", "自助机 C", "维护中", "off", "—", "巡检中", 3),
)
_QUEUE = (
    ("q1", "A021", "社保参保证明", "等候 3 分", "邮政营业", 0, 1),
    ("q2", "F007", "定期存款转存", "等候 7 分", "代理金融", 0, 2),
    ("q3", "A022", "寄递包裹", "等候 1 分", "邮政营业", 0, 3),
)
_APPTS = (
    ("p1", "10:30", "陈××", "定期存款转存", "待进门", "wait"),
    ("p2", "14:00", "刘××", "社保参保证明", "已到店", "ok"),
    ("p3", "15:30", "周××", "新开卡", "未到店", "warn"),
)
_BARS = ((9, 6), (10, 11), (11, 13), (12, 4), (13, 7), (14, 9), (15, 9), (16, 0))

# 业务决定条线。页面上不给人选「代理金融 / 邮政营业」。
_LINE = {
    "定期存款转存": "代理金融",
    "活期转定期": "代理金融",
    "理财赎回": "代理金融",
    "寄递包裹": "邮政营业",
    "社保参保证明": "邮政营业",
}
# 壳岗位：P2 普通柜员只拿代理金融，P3 邮政营业只拿邮政营业。
_OWN = {"P2": "代理金融", "P3": "邮政营业"}
_SERVE = (
    "一杯水", "糖果零食", "厅堂微沙龙", "报刊阅览",
    "手机充电", "老花镜", "儿童安抚", "预约提醒卡",
)


def ensure_lobby(path=None) -> None:
    conn = connect(path)
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS lobby_window (
              id TEXT PRIMARY KEY, no TEXT, line TEXT, st TEXT, cls TEXT,
              who TEXT, t TEXT, ord INTEGER
            );
            CREATE TABLE IF NOT EXISTS lobby_kiosk (
              id TEXT PRIMARY KEY, no TEXT, st TEXT, cls TEXT, who TEXT, t TEXT, ord INTEGER
            );
            CREATE TABLE IF NOT EXISTS lobby_queue (
              id TEXT PRIMARY KEY, no TEXT, item TEXT, wait TEXT, dest TEXT,
              called INTEGER NOT NULL DEFAULT 0, ord INTEGER,
              who TEXT NOT NULL DEFAULT '',
              serve TEXT NOT NULL DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS lobby_appt (
              id TEXT PRIMARY KEY, slot TEXT, who TEXT, item TEXT, st TEXT, cls TEXT
            );
            CREATE TABLE IF NOT EXISTS lobby_bar (
              hour INTEGER PRIMARY KEY, n INTEGER NOT NULL
            );
            """
        )
        for row in _WINDOWS:
            conn.execute(
                "INSERT OR IGNORE INTO lobby_window VALUES (?,?,?,?,?,?,?,?)", row
            )
        for row in _KIOSKS:
            conn.execute(
                "INSERT OR IGNORE INTO lobby_kiosk VALUES (?,?,?,?,?,?,?)", row
            )
        cols = [r[1] for r in conn.execute("PRAGMA table_info(lobby_queue)")]
        if "who" not in cols:
            conn.execute("ALTER TABLE lobby_queue ADD COLUMN who TEXT NOT NULL DEFAULT ''")
        if "serve" not in cols:
            conn.execute("ALTER TABLE lobby_queue ADD COLUMN serve TEXT NOT NULL DEFAULT ''")
        for row in _QUEUE:
            conn.execute(
                """INSERT OR IGNORE INTO lobby_queue
                   (id, no, item, wait, dest, called, ord)
                   VALUES (?,?,?,?,?,?,?)""",
                row,
            )
        for row in _APPTS:
            conn.execute(
                "INSERT OR IGNORE INTO lobby_appt VALUES (?,?,?,?,?,?)", row
            )
        for hour, n in _BARS:
            conn.execute(
                "INSERT OR IGNORE INTO lobby_bar (hour, n) VALUES (?, ?)", (hour, n)
            )
        conn.commit()
    finally:
        conn.close()


def _rows(conn: sqlite3.Connection, sql: str) -> list:
    return [dict(row) for row in conn.execute(sql).fetchall()]


def view(role: str, *, path=None) -> dict:
    ensure_lobby(path)
    if role == "P5":
        return {"windows": [], "kiosks": [], "queue": [], "appts": [], "bars": []}
    conn = connect(path)
    try:
        windows = _rows(conn, "SELECT no, line, st, cls, who, t FROM lobby_window ORDER BY ord")
        kiosks = _rows(conn, "SELECT no, st, cls, who, t FROM lobby_kiosk ORDER BY ord")
        queue = _rows(
            conn,
            """SELECT id, no, item, wait, dest, who, serve
               FROM lobby_queue WHERE called = 0 ORDER BY ord""",
        )
        own = _OWN.get(role)
        if own:
            queue = [row for row in queue if row["dest"] == own]
            windows = []
            kiosks = []
        appts = _rows(conn, "SELECT id, slot, who, item, st, cls FROM lobby_appt ORDER BY slot")
        bars = [
            [row["hour"], row["n"]]
            for row in conn.execute("SELECT hour, n FROM lobby_bar ORDER BY hour")
        ]
    finally:
        conn.close()
    return {
        "quick": ["识别客户", "为客户取号", "查看预约", "厅堂巡检"],
        "windows": windows,
        "kiosks": kiosks,
        "queue": queue,
        "waiting": len(queue),
        "appts": appts,
        "bars": bars,
        "barsTitle": "厅堂客流时段分布",
        "barsSub": "按小时 · 单位：人次",
        "tablet": {
            "acts": [
                ["g-scan", "识别客户", "扫证 / 扫码认人，不让客户自证"],
                ["g-seat", "快速叫号", "平板上直接取号、叫号"],
                ["g-cal", "查预约", "今天谁约了、到没到"],
                ["g-flow", "看窗口", "哪台空着、往哪引导"],
            ],
            "note": "大堂经理<b>不在电脑前</b>。这一屏是<b>拿在手里的那部分</b>。与母端是<b>同一条会话</b>：平板上认的人、取的号、引的流，回到电脑前接着看。",
        },
    }


def call_next(role: str, *, path=None) -> dict:
    """把队首叫到第一台空闲窗口。没有空窗就只记已叫。"""
    ensure_lobby(path)
    own = _OWN.get(role)
    if role != "P4" and own is None:
        return {"status": "denied"}
    conn = connect(path)
    try:
        if own:
            ticket = conn.execute(
                """SELECT * FROM lobby_queue
                   WHERE called = 0 AND dest = ? ORDER BY ord LIMIT 1""",
                (own,),
            ).fetchone()
        else:
            ticket = conn.execute(
                "SELECT * FROM lobby_queue WHERE called = 0 ORDER BY ord LIMIT 1"
            ).fetchone()
        if ticket is None:
            return {"status": "empty"}
        window = conn.execute(
            "SELECT * FROM lobby_window WHERE st = '空闲' ORDER BY ord LIMIT 1"
        ).fetchone()
        conn.execute(
            "UPDATE lobby_queue SET called = 1 WHERE id = ?", (ticket["id"],)
        )
        if window is not None:
            conn.execute(
                """UPDATE lobby_window
                   SET st = '办理中', cls = 'busy', who = ?, t = '刚叫到'
                   WHERE id = ?""",
                (ticket["no"] + " · " + ticket["item"], window["id"]),
            )
        conn.commit()
    finally:
        conn.close()
    floor = view(role, path=path)
    floor["called"] = ticket["no"]
    return floor


def touch_appt(role: str, appt_id: str, *, path=None) -> dict:
    """预约行上的确认或回电。只改这一行的状态，不动票池。"""
    ensure_lobby(path)
    if role != "P4":
        return {"status": "denied"}
    conn = connect(path)
    try:
        row = conn.execute(
            "SELECT st FROM lobby_appt WHERE id = ?", (appt_id,)
        ).fetchone()
        if row is None:
            return {"status": "missing"}
        if row["st"] == "待进门":
            conn.execute(
                "UPDATE lobby_appt SET st = '已到店', cls = 'ok' WHERE id = ?",
                (appt_id,),
            )
        elif row["st"] == "未到店":
            conn.execute(
                "UPDATE lobby_appt SET st = '已回电', cls = 'wait' WHERE id = ?",
                (appt_id,),
            )
        conn.commit()
    finally:
        conn.close()
    return view(role, path=path)


def take_ticket(role: str, item: str, who: str = "", *, path=None) -> dict:
    """登记业务后取号。条线由业务类型决定，不接受调用方传入条线。"""
    ensure_lobby(path)
    if role != "P4":
        return {"status": "denied"}
    line = _LINE.get(item)
    if not line:
        return {"status": "unknown"}
    prefix = "F" if line == "代理金融" else "A"
    conn = connect(path)
    try:
        rows = conn.execute(
            "SELECT no, ord FROM lobby_queue"
        ).fetchall()
        seq = 0
        order = 0
        for row in rows:
            order = max(order, int(row["ord"] or 0))
            if str(row["no"]).startswith(prefix) and str(row["no"])[1:].isdigit():
                seq = max(seq, int(str(row["no"])[1:]))
        no = prefix + str(seq + 1).zfill(3)
        conn.execute(
            """INSERT INTO lobby_queue
               (id, no, item, wait, dest, called, ord, who, serve)
               VALUES (?,?,?,?,?,0,?,?,?)""",
            ("q-" + no, no, item, "等候 0 分", line, order + 1, who or "", ""),
        )
        conn.commit()
    finally:
        conn.close()
    floor = view(role, path=path)
    floor["took"] = no
    floor["line"] = line
    return floor


def serve(role: str, ticket_id: str, picks: list, *, path=None) -> dict:
    """等候期服务。只记给了什么，不改排队顺序和等候时长。"""
    ensure_lobby(path)
    if role != "P4":
        return {"status": "denied"}
    chosen = [name for name in _SERVE if name in (picks or [])]
    if not chosen:
        return {"status": "empty"}
    conn = connect(path)
    try:
        row = conn.execute(
            "SELECT ord, wait FROM lobby_queue WHERE id = ? AND called = 0",
            (ticket_id,),
        ).fetchone()
        if row is None:
            return {"status": "missing"}
        conn.execute(
            "UPDATE lobby_queue SET serve = ? WHERE id = ?",
            ("、".join(chosen), ticket_id),
        )
        conn.commit()
        kept = conn.execute(
            "SELECT ord, wait FROM lobby_queue WHERE id = ?", (ticket_id,)
        ).fetchone()
    finally:
        conn.close()
    floor = view(role, path=path)
    floor["served"] = chosen
    floor["samePlace"] = kept["ord"] == row["ord"] and kept["wait"] == row["wait"]
    return floor

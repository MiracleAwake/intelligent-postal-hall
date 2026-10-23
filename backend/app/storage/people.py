"""初步业务库：员工按原型名册，客户存完整资料。

管理员读客户时只给掩码。库里的证件号、手机号、住址不加密。
本机 3306 上的 MySQL 还没有 zhiyou 账号，这一份先用本地文件。
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[3] / "deploy" / "biz.sqlite"

# 后端 role_code 和壳岗位不是同一套，不把库改成壳代号。
# 支局经理=P3，普通柜员=P1，邮政营业=P2，大堂经理=P4，管理员=P5。
# 综合柜员、理财经理、保安没有后端 role_code。网点只记在 post 所属的 org，不另存站点列。
_POSTS = (
    ("df", "P3", "支局经理"),
    ("df", "P1", "普通柜员"),
    ("df", "P2", "邮政营业"),
    ("df", "P4", "大堂经理"),
    ("hq", "P5", "管理员"),
    ("df", "", "综合柜员"),
    ("df", "", "理财经理"),
    ("df", "", "保安"),
)

# 工号、姓名、岗位名、能否进门、派到哪个后端岗位。姓名保持原型写法。
_STAFF = (
    ("1001", "王××", "支局经理", "enter", "P3"),
    ("1003", "赵××", "普通柜员", "enter", "P1"),
    ("1017", "秦××", "邮政营业", "enter", "P2"),
    ("1004", "孙××", "大堂经理", "enter", "P4"),
    ("9001", "区管理员", "管理员", "enter", "P5"),
    ("1002", "钱××", "综合柜员", "no_page", ""),
    ("1010", "褚××", "综合柜员", "no_page", ""),
    ("1018", "尤××", "理财经理", "no_page", ""),
    ("1022", "施××", "保安", "no_page", ""),
)

# 客户页上已经有的人。证件中间十位用序号补齐，掩码仍对得上页面上的前四后四。
_NAMED = (
    ("c001", "陈晓兰", "女", "3301", "1234", "13867230011", "东风路 12 号 3 单元 501", "东风路片区", "个人 · 存量", 1, 0),
    ("c002", "李明远", "男", "3301", "8811", "13846886688", "东风路 12 号 3 单元 501", "东风路片区", "个人 · 存量", 1, 0),
    ("c003", "吴建国", "男", "3301", "2200", "13955000022", "解放路 88 号 1 幢 1203", "解放路片区", "个人 · 存量", 1, 1),
    ("c004", "郑雅琴", "女", "3301", "3344", "13722115566", "中山北路 5 号 1 幢 801", "中山路片区", "个人 · 存量", 1, 1),
    ("c005", "赵文博", "男", "3302", "7711", "13677882211", "城南路 3 号", "城南片区", "个人 · 存量", 1, 0),
    ("c006", "孙丽娟", "女", "3301", "9012", "13711553388", "解放路 66 号", "解放路片区", "个人 · 新客", 1, 0),
    ("c007", "钱海涛", "男", "3301", "5678", "13833449900", "城南路 20 号 2 单元 602", "城南片区", "个人 · 存量", 1, 0),
    ("c008", "刘芳", "女", "3301", "4433", "13599007788", "东风路 30 号 1 单元 201", "东风路片区", "个人 · 存量", 1, 1),
    ("c009", "周凯", "男", "3301", "6655", "13966114433", "光明路 22 号", "光明路片区", "个人 · 存量", 1, 0),
    ("c010", "冯淑珍", "女", "3303", "1188", "13722338811", "光明路 5 号 3 单元 401", "光明路片区", "特殊客群", 1, 1),
    ("c011", "徐强", "男", "3301", "7788", "13677885544", "解放路 25 号 2 幢 601", "解放路片区", "个人 · 存量", 1, 0),
    ("n01", "王磊", "男", "3301", "6621", "13988770011", "东风路 8 号 2 单元 302", "东风路片区", "个人 · 新客", 1, 0),
    ("n02", "韦婷", "女", "3301", "3390", "", "", "城南片区", "个人 · 新客", 0, 0),
    ("n03", "孙浩", "男", "3301", "7745", "13766993388", "解放路 118 号 3 幢 402", "解放路片区", "代发户", 1, 0),
    ("n04", "李俊", "男", "3302", "3456", "13811226699", "", "东风路片区", "对公 · 小微", 0, 0),
    ("n05", "周敏", "女", "3301", "7890", "13655441122", "中山北路 5 号 1 幢 801", "中山路片区", "个人 · 新客", 1, 0),
    ("n06", "章鹏", "男", "3303", "2345", "", "光明路 22 号", "光明路片区", "特殊客群", 0, 0),
)

_EXTRA_SURNAMES = "黄何高林罗梁宋唐许邓冯韩曹彭曾肖田董潘袁蔡蒋余杜叶程魏苏吕丁任卢姚沈钟姜崔谭陆范汪石金贾韦夏"


def _id_no(prefix: str, last4: str, seq: int) -> str:
    return f"{prefix}{seq:010d}{last4}"


def customers() -> list[dict]:
    rows = []
    for seq, item in enumerate(_NAMED, start=1):
        ref, name, sex, prefix, last4, phone, address, area, kind, complete, focus = item
        rows.append({
            "ref": ref,
            "name": name,
            "sex": sex,
            "id_no": _id_no(prefix, last4, seq),
            "phone": phone,
            "address": address,
            "area": area,
            "kind": kind,
            "complete": complete,
            "focus": focus,
        })
    areas = ("东风路片区", "解放路片区", "城南片区", "中山路片区", "光明路片区")
    for n in range(33):
        seq = len(_NAMED) + n + 1
        surname = _EXTRA_SURNAMES[n % len(_EXTRA_SURNAMES)]
        given = f"测{seq:02d}"
        prefix = ("3301", "3302", "3303")[n % 3]
        last4 = f"{(2000 + seq):04d}"[-4:]
        phone = f"139{seq:08d}"[-11:]
        rows.append({
            "ref": f"t{seq:03d}",
            "name": surname + given,
            "sex": "女" if n % 2 else "男",
            "id_no": _id_no(prefix, last4, seq),
            "phone": phone,
            "address": f"测试路 {seq} 号",
            "area": areas[n % len(areas)],
            "kind": "个人 · 存量",
            "complete": 1,
            "focus": 0,
        })
    return rows


def mask_name(name: str) -> str:
    if not name:
        return ""
    return name[0] + "××"


def mask_id(id_no: str) -> str:
    if len(id_no) < 8:
        return ""
    return id_no[:4] + "**********" + id_no[-4:]


def mask_phone(phone: str) -> str:
    if len(phone) < 7:
        return ""
    return phone[:3] + "****" + phone[-4:]


def present(row: dict, role: str) -> dict:
    """柜面可读全文。管理员和未标明岗位只读掩码，住址收到片区。"""
    if role in {"P1", "P2", "P3", "P4"}:
        return {
            "ref": row["ref"],
            "name": row["name"],
            "sex": row["sex"],
            "id_no": row["id_no"],
            "phone": row["phone"],
            "address": row["address"],
            "area": row["area"],
            "kind": row["kind"],
            "complete": bool(row["complete"]),
            "focus": bool(row["focus"]),
        }
    return {
        "ref": row["ref"],
        "name": mask_name(row["name"]),
        "sex": row["sex"],
        "id_no": mask_id(row["id_no"]),
        "phone": mask_phone(row["phone"]),
        "address": "",
        "area": row["area"],
        "kind": row["kind"],
        "complete": bool(row["complete"]),
        "focus": bool(row["focus"]),
    }


def connect(path: Path | None = None) -> sqlite3.Connection:
    target = path or DB_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(target)
    conn.row_factory = sqlite3.Row
    return conn


def ensure(path: Path | None = None) -> None:
    conn = connect(path)
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS org (
              id INTEGER PRIMARY KEY,
              code TEXT NOT NULL UNIQUE,
              name TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS post (
              id INTEGER PRIMARY KEY,
              org_id INTEGER NOT NULL,
              role_code TEXT NOT NULL,
              title TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS staff (
              id INTEGER PRIMARY KEY,
              employee_no TEXT NOT NULL UNIQUE,
              name TEXT NOT NULL,
              title TEXT NOT NULL,
              account_state TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS assignment (
              staff_id INTEGER NOT NULL,
              post_id INTEGER NOT NULL,
              PRIMARY KEY (staff_id, post_id)
            );
            CREATE TABLE IF NOT EXISTS customer (
              id INTEGER PRIMARY KEY,
              ref TEXT NOT NULL UNIQUE,
              name TEXT NOT NULL,
              sex TEXT NOT NULL,
              id_no TEXT NOT NULL,
              phone TEXT NOT NULL,
              address TEXT NOT NULL,
              area TEXT NOT NULL,
              kind TEXT NOT NULL,
              complete INTEGER NOT NULL,
              focus INTEGER NOT NULL
            );
            """
        )
        conn.execute("DELETE FROM assignment")
        conn.execute("DELETE FROM staff")
        conn.execute("DELETE FROM post")
        conn.execute("DELETE FROM org")
        conn.execute("DELETE FROM customer")
        conn.execute("INSERT INTO org (code, name) VALUES ('df', '东风路支局')")
        conn.execute("INSERT INTO org (code, name) VALUES ('hq', '东风区分公司')")
        org = {row["code"]: row["id"] for row in conn.execute("SELECT id, code FROM org")}
        for code, role, title in _POSTS:
            conn.execute(
                "INSERT INTO post (org_id, role_code, title) VALUES (?, ?, ?)",
                (org[code], role, title),
            )
        post_by_role = {}
        post_by_title = {}
        for row in conn.execute("SELECT id, role_code, title FROM post"):
            if row["role_code"]:
                post_by_role[row["role_code"]] = row["id"]
            post_by_title[row["title"]] = row["id"]
        for no, name, title, state, role in _STAFF:
            cur = conn.execute(
                "INSERT INTO staff (employee_no, name, title, account_state) VALUES (?, ?, ?, ?)",
                (no, name, title, state),
            )
            post_id = post_by_role.get(role) if role else post_by_title.get(title)
            if post_id:
                conn.execute(
                    "INSERT INTO assignment (staff_id, post_id) VALUES (?, ?)",
                    (cur.lastrowid, post_id),
                )
        for row in customers():
            conn.execute(
                """INSERT INTO customer
                   (ref, name, sex, id_no, phone, address, area, kind, complete, focus)
                   VALUES (:ref, :name, :sex, :id_no, :phone, :address, :area, :kind, :complete, :focus)""",
                row,
            )
        conn.commit()
    finally:
        conn.close()


def list_customers(role: str, path: Path | None = None) -> list[dict]:
    conn = connect(path)
    try:
        rows = conn.execute(
            "SELECT ref, name, sex, id_no, phone, address, area, kind, complete, focus FROM customer ORDER BY id"
        ).fetchall()
    finally:
        conn.close()
    return [present(dict(row), role) for row in rows]


def list_staff(path: Path | None = None) -> list[dict]:
    conn = connect(path)
    try:
        rows = conn.execute(
            """SELECT s.employee_no, s.name, s.title, s.account_state,
                      p.role_code, o.code AS org_code, o.name AS org_name
               FROM staff s
               LEFT JOIN assignment a ON a.staff_id = s.id
               LEFT JOIN post p ON p.id = a.post_id
               LEFT JOIN org o ON o.id = p.org_id
               ORDER BY s.employee_no"""
        ).fetchall()
    finally:
        conn.close()
    out = []
    for row in rows:
        item = dict(row)
        if item.get("role_code") == "":
            item["role_code"] = None
        out.append(item)
    return out

"""员工端壳的接入。口令不进这里。待办和气泡从名册、客户库、转交来。"""

from hashlib import sha256
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.admin.studio import ORGS, ROLES, Studio
from app.capabilities.speech import accept_speech
from app.services.act import run_act
from app.services.appointments import act as appointment_act
from app.services.appointments import view as appointment_view
from app.services.duties import confirm as confirm_duty
from app.services.duties import view as today_view
from app.services.shell_desk import snapshot
from app.storage.link import try_mysql
from app.storage.people import DB_PATH, ensure, list_customers, list_staff
from app.storage.settings import load_settings

_ROOT = Path(__file__).resolve().parents[2]
_SHELL_DIR = _ROOT / "frontend" / "员工端"
_SHELL = _SHELL_DIR / "挚邮员工端.html"
_WIRE = _SHELL_DIR / "hall-wire.js"
_ACTIONS = _SHELL_DIR / "hall-actions.js"
_GO = _SHELL_DIR / "hall-go.js"
_PAGES = _ROOT.parent / "原型" / "二级页"
# 二级页的「返回工作台」仍指向拆分前的首页。壳合并之后这些地址回到五合一。
_OLD_HOME = {
    "05_普通柜员页.html": "P2",
    "06_支局经理页.html": "P1",
    "07_邮政营业页.html": "P3",
    "08_管理员端.html": "P5",
    "09_大堂经理页.html": "P4",
}


class _Desk:
    def __init__(self) -> None:
        self.files: dict[str, dict] = {}
        self.handoffs: list[dict] = []
        self.sessions: list[dict] = []
        self._seq = 0

    def next_id(self) -> int:
        self._seq += 1
        return self._seq


def create_app() -> FastAPI:
    app = FastAPI()
    app.state.desk = _Desk()
    app.state.studio = Studio()
    app.state.people_db = DB_PATH
    if _PAGES.is_dir():
        app.mount("/二级页", StaticFiles(directory=str(_PAGES)), name="pages")

    @app.get("/")
    def home():
        return FileResponse(_SHELL)

    @app.get("/挚邮员工端.html")
    def shell_file():
        return FileResponse(_SHELL)

    @app.get("/hall-wire.js")
    def wire_js():
        return FileResponse(_WIRE, media_type="application/javascript")

    @app.get("/hall-actions.js")
    def actions_js():
        return FileResponse(_ACTIONS, media_type="application/javascript")

    @app.get("/hall-go.js")
    def go_js():
        return FileResponse(_GO, media_type="application/javascript")

    @app.get("/hall-acts.js")
    def acts_js():
        return FileResponse(_SHELL_DIR / "hall-acts.js", media_type="application/javascript")

    @app.get("/hall-keys.js")
    def keys_js():
        return FileResponse(_SHELL_DIR / "hall-keys.js", media_type="application/javascript")

    @app.get("/hall-live.js")
    def live_js():
        return FileResponse(_SHELL_DIR / "hall-live.js", media_type="application/javascript")

    @app.post("/api/speech")
    def speech(body: dict):
        heard = accept_speech(body.get("text"), audio_ref=body.get("audio_ref"))
        return heard

    @app.post("/api/files")
    async def upload(request: Request, file: UploadFile = File(...)):
        raw = await file.read()
        file_id = sha256(raw).hexdigest()[:12]
        name = file.filename or "未命名"
        request.app.state.desk.files[file_id] = {"name": name, "size": len(raw)}
        return {"file_id": file_id, "name": name, "kept_bytes": False}

    @app.get("/api/files/{file_id}")
    def file_meta(request: Request, file_id: str):
        row = request.app.state.desk.files.get(file_id)
        if row is None:
            return {"status": "missing", "file_id": file_id}
        return {"status": "kept", "file_id": file_id, "name": row["name"], "size": row["size"]}

    @app.post("/api/handoff")
    def handoff(request: Request, body: dict):
        desk: _Desk = request.app.state.desk
        row = {
            "id": desk.next_id(),
            "from": body.get("from"),
            "to_owner": body.get("to_owner"),
            "business": body.get("business"),
            "page": body.get("page"),
            "status": "requested",
        }
        desk.handoffs.append(row)
        return row

    @app.get("/api/handoff")
    def inbox(request: Request, to_owner: str = ""):
        rows = request.app.state.desk.handoffs
        if to_owner:
            rows = [row for row in rows if row["to_owner"] == to_owner]
        return {"items": rows}

    @app.post("/api/act")
    def act(body: dict):
        return run_act(str(body.get("stage") or ""), body)

    @app.get("/api/admin/meta")
    def admin_meta():
        return {"orgs": list(ORGS), "roles": list(ROLES)}

    @app.get("/api/admin/models")
    def admin_models(request: Request):
        return request.app.state.studio.models()

    @app.post("/api/admin/models")
    def admin_add_model(request: Request, body: dict):
        return request.app.state.studio.add_model(body)

    @app.post("/api/admin/models/active")
    def admin_switch(request: Request, body: dict):
        return request.app.state.studio.switch(str(body.get("id") or ""))

    @app.get("/api/admin/prompt")
    def admin_prompt(request: Request, org_id: int, role_code: str):
        return request.app.state.studio.prompt(org_id, role_code)

    @app.post("/api/admin/prompt")
    def admin_save_prompt(request: Request, body: dict):
        return request.app.state.studio.save_prompt(
            int(body.get("org_id")),
            str(body.get("role_code") or ""),
            str(body.get("body") or ""),
        )

    @app.get("/api/admin/docs")
    def admin_docs(request: Request, q: str = ""):
        return request.app.state.studio.find(q)

    @app.post("/api/admin/docs")
    def admin_add_doc(request: Request, body: dict):
        return request.app.state.studio.add_doc(
            str(body.get("title") or ""),
            str(body.get("body") or ""),
            source=str(body.get("source") or "manual"),
        )

    @app.post("/api/admin/docs/{doc_id}")
    def admin_update_doc(request: Request, doc_id: int, body: dict):
        return request.app.state.studio.update_doc(
            doc_id, str(body.get("title") or ""), str(body.get("body") or "")
        )

    @app.get("/api/admin/db")
    def admin_db(request: Request):
        path = request.app.state.people_db
        if not Path(path).exists():
            ensure(path)
        settings = load_settings()
        return {
            "store": "sqlite",
            "file": Path(path).name,
            "mysql": {
                "host": settings.mysql_host,
                "port": settings.mysql_port,
                "user": settings.mysql_user,
                "database": settings.mysql_biz_db,
            },
            "staff": list_staff(path),
            "customers": list_customers("P5", path),
        }

    @app.post("/api/admin/db/connect")
    def admin_db_connect(body: dict):
        password = str(body.get("password") or "")
        result = try_mysql(
            str(body.get("host") or ""),
            int(body.get("port") or 3306),
            str(body.get("user") or ""),
            password,
            str(body.get("database") or ""),
        )
        return result

    @app.get("/api/customers")
    def customers(request: Request, role: str = ""):
        path = request.app.state.people_db
        if not Path(path).exists():
            ensure(path)
        return {"customers": list_customers(role, path)}

    @app.get("/api/desk")
    def desk_view(request: Request, role: str = ""):
        path = request.app.state.people_db
        if not Path(path).exists():
            ensure(path)
        backend = {"P1": "P3", "P2": "P1", "P3": "P2", "P4": "P4", "P5": "P5"}.get(role, "P5")
        customers = [] if role == "P5" else list_customers(backend, path)
        return snapshot(role, list_staff(path), customers, request.app.state.desk.handoffs)

    @app.get("/api/today")
    def today(request: Request, role: str = ""):
        path = request.app.state.people_db
        if not Path(path).exists():
            ensure(path)
        return today_view(role, request.app.state.desk.handoffs, path=path)

    @app.post("/api/today/confirm")
    def today_confirm(request: Request, body: dict):
        path = request.app.state.people_db
        if not Path(path).exists():
            ensure(path)
        return confirm_duty(str(body.get("role") or ""), int(body.get("id") or 0), path=path)

    @app.get("/api/appointments")
    def appointments(request: Request, role: str = ""):
        path = request.app.state.people_db
        if not Path(path).exists():
            ensure(path)
        return appointment_view(role, path=path)

    @app.post("/api/appointments/act")
    def appointments_act(request: Request, body: dict):
        path = request.app.state.people_db
        if not Path(path).exists():
            ensure(path)
        return appointment_act(
            str(body.get("role") or ""),
            str(body.get("id") or ""),
            str(body.get("action") or ""),
            path=path,
        )

    @app.get("/api/staff")
    def staff(request: Request):
        path = request.app.state.people_db
        if not Path(path).exists():
            ensure(path)
        return {"staff": list_staff(path)}

    @app.post("/api/session")
    def session(request: Request, body: dict):
        row = {
            "no": body.get("no"),
            "post": body.get("post"),
            "role": body.get("role"),
            "site": body.get("site"),
        }
        request.app.state.desk.sessions.append(row)
        return {"status": "open", "session": row}

    @app.get("/{page_name}")
    def old_home(page_name: str):
        role = _OLD_HOME.get(page_name)
        if role is None:
            raise HTTPException(status_code=404)
        return RedirectResponse(f"/挚邮员工端.html?role={role}")

    return app

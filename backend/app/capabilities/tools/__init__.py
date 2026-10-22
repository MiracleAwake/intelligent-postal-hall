"""五岗工具封装。壳子按工具 id 调用，不在这里画页面。"""

import hashlib
from decimal import Decimal

from app.capabilities.devices.capture import Capture
from app.capabilities.devices.vision import PageReader, compare_photos
from app.capabilities.files import draft_document, export_document
from app.capabilities.speech import accept_speech
from app.capabilities.tools.catalog import tools_for
from app.gateway import begin
from app.threshold import DEFAULT_THRESHOLD
from app.session.hub import SessionHub
from app.storage.biz import MemoryBiz
from decimal import Decimal


class ToolDesk:
    def __init__(
        self,
        biz: MemoryBiz | None = None,
        hub: SessionHub | None = None,
        capture: Capture | None = None,
        reader: PageReader | None = None,
    ) -> None:
        self.biz = biz or MemoryBiz()
        self.hub = hub or SessionHub()
        self.capture = capture or Capture(devices=lambda: [])
        self.reader = reader or PageReader()
        self.auth_queue: list[dict] = []
        self._ticket = 0
        self._handlers = {
            "read_card": self._read_card,
            "id_card": self._id_card,
            "face_check": self._face_check,
            "scan_voucher": self._scan,
            "print_slip": self._print_slip,
            "dual_record": self._confirm_only,
            "verify_identity": self._verify_identity,
            "auth_request": self._auth_request,
            "trace": self._trace,
            "new_session": self._new_session,
            "takeover": self._takeover,
            "resume": self._resume,
            "to_human": self._to_human,
            "open_account": self._model_form,
            "deposit": self._model_form,
            "wealth": self._model_form,
            "observe": self._observe,
            "inspect": self._scan,
            "weigh": self._weigh,
            "print_waybill": self._print_waybill,
            "insure": self._confirm_only,
            "mail_query": self._mail_query,
            "agency": self._model_form,
            "postal_service": self._model_form,
            "customer_file": self._customer_file,
            "appointment": self._appointment,
            "visit": self._visit,
            "day_end": self._day_end,
            "auth_inbox": self._auth_inbox,
            "auth_approve": self._auth_approve,
            "roster": self._roster,
            "on_duty": self._on_duty,
            "transfer_request": self._transfer_request,
            "handover_note": self._confirm_only,
            "dispatch": self._dispatch,
            "report_counts": self._report_counts,
            "scan_access": self._scan,
            "take_number": self._take_number,
            "appointment_lookup": self._appointment_lookup,
            "divert": self._divert,
            "queue_board": self._queue_board,
            "book": self._appointment,
            "patrol": self._confirm_only,
            "precheck": self._precheck,
            "evaluate": self._evaluate,
            "transfer_counter": self._dispatch,
            "org_chart": self._org_chart,
            "post_template": self._post_template,
            "capability_list": self._capability_list,
            "audit_log": self._audit_log,
            "service_status": self._service_status,
            "adjust_post": self._read_only,
            "set_param": self._read_only,
            "break_glass": self._read_only,
            "speech_input": self._speech,
            "draft_export": self._draft_export,
        }

    def toolbar(self, role: str) -> list[dict]:
        return [{"id": tool.id, "label": tool.label, "kind": tool.kind} for tool in tools_for(role)]

    def call(self, role: str, tool_id: str, payload: dict | None = None, *, trace_id: str | None = None) -> dict:
        ctx = begin(role, f"tool.{tool_id}", write=True, trace_id=trace_id)
        payload = dict(payload or {})
        body = self._handlers[tool_id](tool_id, payload, ctx.trace_id, ctx.op_id)
        body["tool"] = tool_id
        body["role"] = role
        body["trace_id"] = ctx.trace_id
        body["op_id"] = ctx.op_id
        return body

    def _scan(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        mode = payload.get("mode") or "import"
        doc_kind = payload.get("doc_kind") or tool_id
        if mode == "detect":
            return {"status": "ready", "capture": self.capture.detect()}
        if mode in ("camera", "scanner"):
            index = int(payload.get("index") or 0)
            data = self.capture.camera_bytes(index)
            if not data:
                return {"status": "unavailable", "capture": {"source": "camera", "status": "unavailable", "index": index}}
            source = "camera" if mode == "camera" else "camera_as_scanner"
            return {
                "status": "captured",
                "capture": {
                    "source": source,
                    "status": "captured",
                    "index": index,
                    "size": len(data),
                    "sha256": hashlib.sha256(data).hexdigest(),
                },
                "text": self.reader.read(data, doc_kind),
            }
        path = payload.get("path")
        if not path:
            return {"status": "waiting", "need": "path"}
        data = self.capture.file_bytes(path)
        return {
            "status": "captured",
            "capture": self.capture.import_file(path, doc_kind),
            "text": self.reader.read(data, doc_kind),
        }

    def _face_check(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        doc = payload.get("doc") if isinstance(payload.get("doc"), bytes) else None
        live = payload.get("live") if isinstance(payload.get("live"), bytes) else None
        if payload.get("doc_path"):
            doc = self.capture.file_bytes(payload["doc_path"])
        if payload.get("live_path"):
            live = self.capture.file_bytes(payload["live_path"])
        if live is None and payload.get("mode") == "camera":
            live = self.capture.camera_bytes(int(payload.get("index") or 0))
        hint = compare_photos(doc, live)
        hint["national"] = False
        hint["verified"] = False
        hint["pass"] = False
        hint["owner"] = "human"
        if payload.get("confirmed") is True:
            hint["status"] = "confirmed"
            hint["staff_confirmed"] = True
        return hint

    def _read_card(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        ref = payload.get("card_ref")
        if not ref:
            return {"status": "waiting", "need": "card_ref"}
        return {"status": "read", "card_ref": ref}

    def _id_card(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        shot = self._scan(tool_id, {**payload, "doc_kind": "身份证"}, trace_id, op_id)
        if shot["status"] != "captured":
            return shot
        if payload.get("confirmed") is True:
            return {"status": "confirmed", "capture": shot["capture"]}
        return {"status": "waiting", "need": "staff_confirm", "capture": shot["capture"]}

    def _confirm_only(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        if payload.get("confirmed") is True:
            return {"status": "done"}
        return {"status": "waiting", "owner": "human"}

    def _print_slip(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        printed = payload.get("confirmed") is True
        return {"status": "printed" if printed else "ready", "printed": printed}

    def _verify_identity(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        if not payload.get("id_captured"):
            return {"status": "blocked", "need": "id_captured"}
        if payload.get("confirmed") is not True:
            return {"status": "waiting", "owner": "human"}
        return {"status": "verified"}

    def _auth_request(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        amount = str(payload.get("amount") or "0")
        threshold = str(payload.get("threshold") or DEFAULT_THRESHOLD)
        if Decimal(amount) < Decimal(threshold):
            return {"status": "skipped", "required": False}
        item = {
            "id": len(self.auth_queue) + 1,
            "amount": amount,
            "session_id": payload.get("session_id"),
            "status": "waiting",
            "targets": ["综合柜员", "支局经理"],
        }
        self.auth_queue.append(item)
        return {"status": "waiting", "required": True, "request": dict(item)}

    def _trace(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        self.biz.add_audit(trace_id, op_id or "", payload.get("action") or tool_id, payload.get("staff_id"))
        return {"status": "recorded"}

    def _new_session(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        state = self.hub.open(
            org_id=int(payload["org_id"]),
            post_id=payload.get("post_id"),
            external_customer_ref=payload.get("customer_ref"),
        )
        from app.capabilities.guide import recognize

        opened = recognize(payload.get("text"), audio_ref=payload.get("audio_ref"))
        opened["session_id"] = state.id
        opened["org_id"] = state.org_id
        if opened["mode"] == "guide":
            opened["status"] = "guide"
        return opened

    def _takeover(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        state = self.hub.load(payload["session_id"])
        if state is None:
            return {"status": "blocked", "need": "session_id"}
        return {"status": "taken", "session_id": state.id, "org_id": state.org_id}

    def _resume(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        state = self.hub.load(payload["session_id"])
        if state is None or state.org_id != int(payload["org_id"]):
            return {"status": "blocked", "need": "same_org"}
        return {"status": "resumed", "session_id": state.id, "progress": state.progress}

    def _to_human(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        return {"status": "waiting", "owner": "human", "reason": payload.get("reason") or "转人工"}

    def _model_form(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        required = {
            "open_account": ("customer_ref",),
            "deposit": ("customer_ref", "amount"),
            "wealth": ("customer_ref", "product"),
            "agency": ("item",),
            "postal_service": ("item",),
        }.get(tool_id, ())
        fields = {key: payload[key] for key in required if payload.get(key)}
        missing = [key for key in required if key not in fields]
        return {
            "status": "ready" if not missing else "waiting",
            "executor": "model-slot",
            "fields": fields,
            "human_required": missing,
        }

    def _observe(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        return {"status": "ready", "executor": "model-slot", "steps": []}

    def _weigh(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        if payload.get("reading") in (None, ""):
            return {"status": "waiting", "need": "scale_reading", "owner": "human"}
        return {"status": "read", "reading": str(payload["reading"]), "source": "scale"}

    def _print_waybill(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        missing = [key for key in ("inspected", "weight", "notice_confirmed") if not payload.get(key)]
        if missing:
            return {"status": "blocked", "need": missing}
        printed = payload.get("confirmed") is True
        return {"status": "printed" if printed else "ready", "printed": printed}

    def _mail_query(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        ref = payload.get("external_id")
        if not ref:
            return {"status": "waiting", "need": "external_id"}
        return {"status": "pointer", "source_system": payload.get("source_system") or "mail", "external_id": ref}

    def _customer_file(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        row = self.biz.bind_customer(
            int(payload["post_id"]),
            payload.get("source_system") or "crm",
            payload["external_id"],
            payload.get("display_name"),
        )
        return {"status": "bound", "binding_id": row["id"]}

    def _appointment(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        task = self.biz.add_task(int(payload["post_id"]), payload.get("title") or "预约", status="open")
        return {"status": "booked", "task_id": task["id"]}

    def _visit(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        if payload.get("confirmed") is not True:
            task = self.biz.add_task(int(payload["post_id"]), payload.get("title") or "待回访", status="open")
            return {"status": "waiting", "owner": "human", "task_id": task["id"]}
        return {"status": "done"}

    def _day_end(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        if payload.get("confirmed") is not True:
            return {"status": "waiting", "owner": "human", "items": ["结算缴款", "业务补录", "验单处理"]}
        self.biz.add_audit(trace_id, op_id or "", "day_end", payload.get("staff_id"))
        return {"status": "closed"}

    def _auth_inbox(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        waiting = [dict(item) for item in self.auth_queue if item["status"] == "waiting"]
        return {"status": "ready", "items": waiting}

    def _auth_approve(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        if payload.get("confirmed") is not True:
            return {"status": "waiting", "owner": "human"}
        for item in self.auth_queue:
            if item["id"] == payload.get("request_id") and item["status"] == "waiting":
                item["status"] = "approved"
                self.biz.add_audit(trace_id, op_id or "", "auth_approve", payload.get("staff_id"))
                return {"status": "approved", "request_id": item["id"]}
        return {"status": "blocked", "need": "request_id"}

    def _roster(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        return {"status": "ready", "staff": [dict(row) for row in self.biz.staff], "posts": [dict(row) for row in self.biz.post]}

    def _on_duty(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        open_rows = [dict(row) for row in self.biz.assignment if row["ended_at"] is None]
        return {"status": "ready", "assignments": open_rows}

    def _transfer_request(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        self.biz.add_audit(trace_id, op_id or "", "transfer_request", payload.get("staff_id"))
        return {"status": "requested", "applied": False}

    def _dispatch(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        return {"status": "sent", "target_post_id": payload.get("target_post_id")}

    def _report_counts(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        return {
            "status": "ready",
            "tasks": len(self.biz.task_item),
            "audits": len(self.biz.audit_event),
            "performances": len(self.biz.performance_entry),
        }

    def _take_number(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        self._ticket += 1
        return {"status": "called", "ticket": f"A{self._ticket:03d}", "seats_free": payload.get("seats_free")}

    def _appointment_lookup(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        tasks = self.biz.tasks_of(int(payload["post_id"]))
        return {"status": "ready", "tasks": tasks}

    def _divert(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        return {"status": "diverted", "target_role": payload.get("target_role")}

    def _queue_board(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        return {"status": "ready", "waiting": payload.get("waiting", 0), "current": payload.get("current")}

    def _precheck(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        forms = list(payload.get("forms") or [])
        return {"status": "ready", "executor": "model-slot", "forms": forms, "missing": [name for name in forms if not name]}

    def _evaluate(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        if payload.get("score") is None:
            return {"status": "waiting", "owner": "human"}
        return {"status": "recorded", "score": payload["score"]}

    def _org_chart(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        return {"status": "ready", "org": [dict(row) for row in self.biz.org]}

    def _post_template(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        return {"status": "ready", "posts": [dict(row) for row in self.biz.post]}

    def _capability_list(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        from app.capabilities.registry import names

        return {"status": "ready", "names": list(names())}

    def _audit_log(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        return {"status": "ready", "events": [dict(row) for row in self.biz.audit_event]}

    def _service_status(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        from app.storage.pipes import describe_pipes

        pipes = describe_pipes()
        return {"status": "ready", "pipes": {name: {"target": pipe.target, "connected": pipe.connected} for name, pipe in pipes.items()}}

    def _speech(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        return accept_speech(payload.get("text"), audio_ref=payload.get("audio_ref"))

    def _draft_export(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        known = payload.get("known") if isinstance(payload.get("known"), dict) else {}
        draft = draft_document(str(payload.get("kind") or ""), known, payload.get("body"))
        directory = payload.get("directory")
        if draft["status"] != "draft" or not directory:
            return draft
        saved = export_document(draft, str(directory))
        saved["text"] = draft["text"]
        return saved

    def _read_only(self, tool_id: str, payload: dict, trace_id: str, op_id: str | None) -> dict:
        return {"status": "read_only", "tool": tool_id}

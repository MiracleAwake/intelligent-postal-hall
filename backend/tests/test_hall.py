import unittest

from app.capabilities import names
from app.capabilities.units import retrieve
from app.gateway import GateClosed
from app.services.chain import ChainBlocked, ChainLocked
from app.services.hall import HallDesk
from app.storage.biz import MemoryBiz


APPOINTMENT = {
    "customer_ref": "crm:1",
    "intent": "改存期",
    "amount": "20000.00",
    "old_term": "1年",
    "new_term": "3年",
}


class HallFlow(unittest.TestCase):
    def setUp(self):
        self.biz = MemoryBiz()
        self.desk = HallDesk(self.biz)

    def test_capabilities_are_registered(self):
        self.assertIn("intent", names())
        self.assertIn("fill_fields", names())
        self.assertIn("archive", names())
        self.assertEqual(retrieve()["connected"], False)

    def test_handoff_returns_flow_and_skips_auth(self):
        view = self.desk.handoff(
            "admin",
            org_id=7,
            post_id=3,
            appointment=APPOINTMENT,
            seats_free=2,
            trace_id="trace-hall",
        )
        self.assertEqual(view["trace_id"], "trace-hall")
        self.assertEqual(view["ticket"], "A001")
        self.assertEqual(view["seats_free"], 2)
        self.assertEqual(view["current"], "print_forms")
        self.assertFalse(view["print_option"]["printed"])
        self.assertEqual(view["intent"]["executor"], "model-slot")
        self.assertFalse(view["auth"]["required"])
        self.assertEqual(view["intent"]["customer_ref"], "crm:1")
        owners = {step["id"]: step["owner"] for step in view["steps"]}
        self.assertEqual(owners["recognize"], "model")
        self.assertEqual(owners["scan_fill"], "rpa")
        self.assertEqual(owners["issue"], "rpa")
        self.assertEqual(owners["archive"], "system")
        self.assertEqual(owners["password"], "human")
        self.assertFalse(view["model_part"]["participates"])
        self.assertIn("调用模型", view["model_part"]["leaves"])
        self.assertNotIn("model_part", self.desk.hub.load(view["session_id"]).progress)

    def test_missing_term_blocks_fill(self):
        view = self._to_scan({**APPOINTMENT, "new_term": None})
        with self.assertRaises(ChainBlocked):
            self.desk.complete_step(
                "admin",
                org_id=7,
                session_id=view["session_id"],
                step_id="scan_fill",
                payload={"customer_ref": "crm:1"},
            )

    def test_revise_restarts_tail_until_password(self):
        view = self._through_password()
        with self.assertRaises(ChainLocked):
            self.desk.revise_step("admin", org_id=7, session_id=view["session_id"], step_id="scan_fill")

        earlier = self._to_scan(APPOINTMENT)
        self.desk.complete_step(
            "admin",
            org_id=7,
            session_id=earlier["session_id"],
            step_id="scan_fill",
            payload=APPOINTMENT,
        )
        revised = self.desk.revise_step(
            "admin", org_id=7, session_id=earlier["session_id"], step_id="scan_fill"
        )
        self.assertEqual(revised["current"], "scan_fill")
        self.assertEqual(revised["fields_by_step"], {})

    def test_model_only_judges_the_materials_step(self):
        view = self._through_password()
        self.assertEqual(view["current"], "materials")
        part = view["model_part"]
        self.assertTrue(part["participates"])
        self.assertFalse(part["calls_provider"])
        self.assertIn("缺什么", part["does"])
        self.assertIn("写文件", part["leaves"])
        self.assertIn("调用第三方设备", part["leaves"])
        self.assertFalse(part["judgment"]["stop"])
        done = self.desk.complete_step(
            "admin", org_id=7, session_id=view["session_id"], step_id="materials"
        )
        self.assertEqual(done["current"], "issue")
        self.assertFalse(done["model_part"]["participates"])
        self.assertEqual(done["model_part"]["does"], ["按已知内容抄写"])

    def test_archive_writes_staff_performance(self):
        view = self._through_password()
        session_id = view["session_id"]
        for step_id in ("materials", "issue"):
            self.desk.complete_step("admin", org_id=7, session_id=session_id, step_id=step_id)
        self.desk.complete_step(
            "admin", org_id=7, session_id=session_id, step_id="sign", payload={"confirmed": True}
        )
        self.desk.complete_step(
            "admin", org_id=7, session_id=session_id, step_id="archive", staff_id=9
        )
        done = self.desk.complete_step(
            "admin", org_id=7, session_id=session_id, step_id="handover", payload={"confirmed": True}
        )
        self.assertEqual(done["status"], "completed")
        self.assertEqual(len(self.biz.performances_of(9)), 1)
        self.assertEqual(self.biz.audit_event[0]["action"], "hall.archive")
        self.assertEqual(self.biz.tasks_of(3)[0]["status"], "done")

    def test_other_role_stays_closed(self):
        with self.assertRaises(GateClosed):
            self.desk.handoff("P2", org_id=7, post_id=3, appointment=APPOINTMENT, seats_free=1)

    def _to_scan(self, appointment: dict) -> dict:
        view = self.desk.handoff("admin", org_id=7, post_id=3, appointment=appointment, seats_free=1)
        session_id = view["session_id"]
        self.desk.complete_step(
            "admin", org_id=7, session_id=session_id, step_id="print_forms", payload={"confirmed": True}
        )
        return self.desk.complete_step(
            "admin",
            org_id=7,
            session_id=session_id,
            step_id="submit_credentials",
            payload={"confirmed": True},
        )

    def _through_password(self) -> dict:
        view = self._to_scan(APPOINTMENT)
        self.desk.complete_step(
            "admin", org_id=7, session_id=view["session_id"], step_id="scan_fill", payload=APPOINTMENT
        )
        return self.desk.complete_step(
            "admin",
            org_id=7,
            session_id=view["session_id"],
            step_id="password",
            payload={"confirmed": True},
        )

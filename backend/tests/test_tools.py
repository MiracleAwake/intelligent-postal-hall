import os
import tempfile
import unittest

from app.assembly.roles import ROLE_LABELS, assemble
from app.capabilities.devices.capture import Capture
from app.capabilities.tools import ToolDesk
from app.gateway import GateClosed
from app.storage.biz import MemoryBiz


class RoleTools(unittest.TestCase):
    def setUp(self):
        self.biz = MemoryBiz()
        self.capture = Capture(
            devices=lambda: [{"id": "scanner:test", "kind": "scanner", "label": "测试扫描仪"}],
            camera_grabber=lambda index: b"frame",
        )
        self.desk = ToolDesk(self.biz, capture=self.capture)

    def test_five_roles_match_prototypes(self):
        self.assertEqual(ROLE_LABELS["P1"], "普通柜员")
        self.assertIn("scan_voucher", assemble("P1"))
        self.assertIn("print_waybill", assemble("P2"))
        self.assertIn("auth_inbox", assemble("P3"))
        self.assertIn("take_number", assemble("P4"))
        self.assertIn("audit_log", assemble("P5"))
        self.assertNotIn("adjust_post", assemble("P1"))

    def test_teller_can_detect_import_and_camera(self):
        detected = self.desk.call("P1", "scan_voucher", {"mode": "detect"})
        kinds = {item["kind"] for item in detected["capture"]["sources"]}
        self.assertEqual(kinds, {"file", "camera", "scanner"})
        with tempfile.NamedTemporaryFile(delete=False) as handle:
            handle.write(b"voucher")
            path = handle.name
        try:
            imported = self.desk.call("P1", "scan_voucher", {"mode": "import", "path": path, "doc_kind": "存单"})
        finally:
            os.remove(path)
        self.assertEqual(imported["status"], "captured")
        self.assertEqual(imported["capture"]["doc_kind"], "存单")
        shot = self.desk.call("P1", "scan_voucher", {"mode": "camera"})
        self.assertEqual(shot["status"], "captured")

    def test_waybill_stops_without_notice(self):
        blocked = self.desk.call("P2", "print_waybill", {"inspected": True, "weight": "1kg"})
        self.assertEqual(blocked["status"], "blocked")
        self.assertIn("notice_confirmed", blocked["need"])
        ready = self.desk.call(
            "P2",
            "print_waybill",
            {"inspected": True, "weight": "1kg", "notice_confirmed": True},
        )
        self.assertFalse(ready["printed"])

    def test_scale_does_not_invent_weight(self):
        waiting = self.desk.call("P2", "weigh", {})
        self.assertEqual(waiting["need"], "scale_reading")

    def test_lobby_number_and_branch_auth(self):
        called = self.desk.call("P4", "take_number", {"seats_free": 2})
        self.assertEqual(called["ticket"], "A001")
        requested = self.desk.call("P1", "auth_request", {"amount": "80000.00", "session_id": "s1"})
        self.assertTrue(requested["required"])
        inbox = self.desk.call("P3", "auth_inbox")
        approved = self.desk.call(
            "P3",
            "auth_approve",
            {"request_id": inbox["items"][0]["id"], "confirmed": True, "staff_id": 4},
        )
        self.assertEqual(approved["status"], "approved")

    def test_admin_write_stays_read_only(self):
        org = self.biz.add_org("001", "网点")
        person = self.biz.add_staff("1001", "甲")
        post = self.biz.add_post(org["id"], "P1", "柜面")
        self.biz.open_assignment(person["id"], post["id"], __import__("datetime").datetime(2026, 10, 1))
        result = self.desk.call("P5", "adjust_post", {"staff_id": person["id"], "post_id": 9})
        self.assertEqual(result["status"], "read_only")
        self.assertEqual(self.biz.open_post_of(person["id"])["id"], post["id"])

    def test_other_role_cannot_use_teller_scanner(self):
        with self.assertRaises(GateClosed):
            self.desk.call("P4", "scan_voucher", {"mode": "detect"})

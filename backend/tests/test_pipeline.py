import unittest

from app.gateway import GateClosed, begin
from app.gateway.handle import sync_progress
from app.session.hub import OrgLocked, SessionHub
from app.storage.pipes import describe_pipes


class Step02Pipeline(unittest.TestCase):
    def test_pipes_stay_disconnected(self):
        pipes = describe_pipes()
        self.assertEqual(set(pipes), {"biz", "session", "chroma"})
        self.assertTrue(all(pipe.connected is False for pipe in pipes.values()))
        self.assertTrue(pipes["biz"].target.endswith("/biz"))
        self.assertTrue(pipes["session"].target.endswith("/session"))
        self.assertIn(":8000", pipes["chroma"].target)

    def test_admin_sync_keeps_org_and_ids(self):
        hub = SessionHub()
        opened = hub.open(org_id=7, post_id=3, external_customer_ref="crm:1")
        result = sync_progress(
            "admin",
            org_id=7,
            session_id=opened.id,
            progress={"step": "材料"},
            trace_id="trace-fixed",
            hub=hub,
        )
        self.assertEqual(result["trace_id"], "trace-fixed")
        self.assertTrue(result["op_id"])
        self.assertEqual(result["org_id"], 7)
        self.assertEqual(result["progress"], {"step": "材料"})
        self.assertEqual(hub.load(opened.id).external_customer_ref, "crm:1")
        self.assertIsNone(begin("admin", "session.read").op_id)

    def test_org_cannot_move(self):
        hub = SessionHub()
        opened = hub.open(org_id=7)
        with self.assertRaises(OrgLocked):
            sync_progress(
                "admin",
                org_id=9,
                session_id=opened.id,
                progress={"step": "带走"},
                hub=hub,
            )
        self.assertEqual(hub.load(opened.id).progress, {})

    def test_other_roles_fail_closed(self):
        hub = SessionHub()
        opened = hub.open(org_id=7)
        with self.assertRaises(GateClosed):
            sync_progress(
                "P1",
                org_id=7,
                session_id=opened.id,
                progress={"step": "柜员"},
                hub=hub,
            )
        self.assertEqual(hub.load(opened.id).progress, {})

    def test_two_windows_keep_their_own_progress(self):
        hub = SessionHub()
        teller = hub.open(org_id=7, post_id=1, external_customer_ref="crm:a")
        postal = hub.open(org_id=7, post_id=2, external_customer_ref="crm:b")
        hub.save_progress(teller.id, {"step": "到期转存"}, org_id=7)
        hub.save_progress(postal.id, {"step": "收寄"}, org_id=7)
        self.assertEqual(hub.load(teller.id).progress, {"step": "到期转存"})
        self.assertEqual(hub.load(postal.id).progress, {"step": "收寄"})
        self.assertNotEqual(teller.id, postal.id)


if __name__ == "__main__":
    unittest.main()

import unittest

from app.gateway import GateClosed
from app.services.chain import ChainBlocked
from app.services.hall import HallDesk


VISIT = {
    "customer_ref": "crm:9",
    "intent": "改存期",
    "amount": "60000.00",
    "old_term": "1年",
    "new_term": "3年",
}


class LinkedVisit(unittest.TestCase):
    def test_guide_work_auth_work_done(self):
        desk = HallDesk()
        opened = desk.handoff(
            "P4",
            org_id=7,
            post_id=4,
            appointment=VISIT,
            seats_free=2,
            linked=True,
        )
        session_id = opened["session_id"]
        self.assertEqual(opened["current"], "ask")
        self.assertTrue(opened["auth"]["required"])

        guided = desk.complete_step(
            "P4", org_id=7, session_id=session_id, step_id="ask", payload={"confirmed": True}
        )
        self.assertEqual(guided["current"], "recognize")

        view = guided
        for step_id in ("recognize", "queue"):
            view = desk.complete_step("P1", org_id=7, session_id=session_id, step_id=step_id)
        for step_id in ("print_forms", "submit_credentials"):
            view = desk.complete_step(
                "P1",
                org_id=7,
                session_id=session_id,
                step_id=step_id,
                payload={"confirmed": True},
            )
        view = desk.complete_step(
            "P1", org_id=7, session_id=session_id, step_id="scan_fill", payload=VISIT
        )
        view = desk.complete_step(
            "P1",
            org_id=7,
            session_id=session_id,
            step_id="password",
            payload={"confirmed": True},
        )
        self.assertEqual(view["current"], "authorize")
        with self.assertRaises(ChainBlocked):
            desk.complete_step(
                "P1",
                org_id=7,
                session_id=session_id,
                step_id="authorize",
                payload={"confirmed": True},
            )
        granted = desk.complete_step(
            "P3",
            org_id=7,
            session_id=session_id,
            step_id="authorize",
            payload={"confirmed": True},
        )
        self.assertEqual(granted["current"], "materials")
        view = granted
        for step_id in ("materials", "issue"):
            view = desk.complete_step("P1", org_id=7, session_id=session_id, step_id=step_id)
        view = desk.complete_step(
            "P1", org_id=7, session_id=session_id, step_id="sign", payload={"confirmed": True}
        )
        view = desk.complete_step(
            "P1", org_id=7, session_id=session_id, step_id="archive", staff_id=3
        )
        done = desk.complete_step(
            "P1",
            org_id=7,
            session_id=session_id,
            step_id="handover",
            payload={"confirmed": True},
        )
        self.assertEqual(done["status"], "completed")
        self.assertEqual(len(desk.biz.performances_of(3)), 1)

    def test_lobby_cannot_finish_the_counter(self):
        desk = HallDesk()
        opened = desk.handoff(
            "P4", org_id=7, post_id=4, appointment=VISIT, seats_free=1, linked=True
        )
        desk.complete_step(
            "P4",
            org_id=7,
            session_id=opened["session_id"],
            step_id="ask",
            payload={"confirmed": True},
        )
        with self.assertRaises(ChainBlocked):
            desk.complete_step(
                "P4",
                org_id=7,
                session_id=opened["session_id"],
                step_id="print_forms",
                payload={"confirmed": True},
            )

    def test_stranger_stays_closed(self):
        desk = HallDesk()
        with self.assertRaises(GateClosed):
            desk.handoff("P2", org_id=7, post_id=2, appointment=VISIT, seats_free=1, linked=True)


if __name__ == "__main__":
    unittest.main()

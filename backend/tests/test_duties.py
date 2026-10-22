"""今日必办按日子推送。确认只销当天，每周固定的下周再出现。管理员看不到客户到访。"""

import tempfile
import unittest
from datetime import date
from pathlib import Path

from app.services.duties import confirm, view
from app.storage.people import ensure


class DutyTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name) / "biz.sqlite"
        ensure(self.path)
        self.today = date(2026, 10, 22)

    def tearDown(self):
        self.dir.cleanup()

    def test_thursday_pushes_followup_to_counter_and_weekly_to_admin(self):
        teller = view("P2", [], today=self.today, path=self.path)
        self.assertTrue(any("赵文博" in row["text"] for row in teller["pins"]))
        self.assertTrue(any("孙丽娟" in row["text"] for row in teller["later"]))
        self.assertEqual(teller["badges"]["客户"], 1)
        self.assertTrue(any(row["kind"] == "duty" and "赵文博" in row["title"] for row in teller["notices"]))
        admin = view("P5", [], today=self.today, path=self.path)
        titles = [row["title"] for row in admin["pins"]]
        self.assertEqual(titles, ["检查数据", "定期维护"])
        self.assertNotIn("赵文博", str(admin))
        self.assertNotIn("客户", admin["badges"])

    def test_confirm_hides_today_and_weekly_returns_next_week(self):
        admin = view("P5", [], today=self.today, path=self.path)
        check = next(row for row in admin["pins"] if row["title"] == "检查数据")
        self.assertEqual(confirm("P5", check["id"], today=self.today, path=self.path)["status"], "confirmed")
        again = view("P5", [], today=self.today, path=self.path)
        self.assertEqual(again["due"], 2)
        self.assertEqual(len(again["pins"]), 1)
        self.assertFalse(any(row["duty_id"] == check["id"] for row in again["notices"]))
        nxt = view("P5", [], today=date(2026, 10, 29), path=self.path)
        self.assertIn("检查数据", [row["title"] for row in nxt["pins"]])

    def test_handoff_is_a_bell_message_not_a_pin(self):
        told = view("P1", [{
            "id": 3,
            "to_owner": "支局经理",
            "business": "授权复核",
            "status": "requested",
        }], today=self.today, path=self.path)
        self.assertTrue(any(row["kind"] == "system" and row["title"] == "授权复核" for row in told["notices"]))
        self.assertFalse(any("授权复核" in row["text"] for row in told["pins"]))

    def test_postal_counter_is_not_driven_yet(self):
        postal = view("P3", [], today=self.today, path=self.path)
        self.assertFalse(postal["applies"])
        self.assertEqual(postal["pins"], [])


if __name__ == "__main__":
    unittest.main()

"""两条模拟预约按岗位分开，按键动作写回同一条。"""

import tempfile
import unittest
from pathlib import Path

from app.services.appointments import act, view
from app.storage.people import ensure


class AppointmentTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name) / "biz.sqlite"
        ensure(self.path)

    def tearDown(self):
        self.dir.cleanup()

    def test_roles_see_their_own_line(self):
        teller = [row["name"] for row in view("P2", path=self.path)["items"]]
        postal = [row["name"] for row in view("P3", path=self.path)["items"]]
        lobby = [row["name"] for row in view("P4", path=self.path)["items"]]
        admin = view("P5", path=self.path)["items"]
        self.assertEqual(teller, ["周××"])
        self.assertEqual(postal, ["冯××"])
        self.assertEqual(lobby, ["冯××", "周××"])
        by_name = {row["name"]: row["cid"] for row in view("P4", path=self.path)["items"]}
        self.assertEqual(by_name["周××"], "c009")
        self.assertEqual(by_name["冯××"], "c010")
        self.assertEqual(admin, [])

    def test_remind_and_reappoint_stay_on_the_row(self):
        reminded = act("P2", "a-zhou", "remind", path=self.path)
        self.assertTrue(reminded["item"]["reminded"])
        changed = act("P4", "a-feng", "reappoint", path=self.path)
        self.assertEqual(changed["item"]["status"], "待到店")
        self.assertEqual(changed["item"]["actual"], "")

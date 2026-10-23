"""厅堂态势按原型 09 的块给出。叫号改窗口和队列。"""

import tempfile
import unittest
from pathlib import Path

from app.services.lobby import call_next, view


class LobbyTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name) / "biz.sqlite"

    def tearDown(self):
        self.dir.cleanup()

    def test_floor_matches_the_lobby_blocks(self):
        floor = view("P4", path=self.path)
        self.assertEqual([w["no"] for w in floor["windows"]], ["01 号台", "02 号台", "04 号台"])
        self.assertEqual(len(floor["kiosks"]), 3)
        self.assertEqual([q["no"] for q in floor["queue"]], ["A021", "F007", "A022"])
        self.assertEqual(floor["bars"][0], [9, 6])
        self.assertEqual(floor["barsTitle"], "厅堂客流时段分布")
        self.assertEqual(view("P5", path=self.path)["windows"], [])

    def test_call_fills_the_free_window(self):
        floor = call_next("P4", path=self.path)
        self.assertEqual(floor["called"], "A021")
        self.assertEqual([q["no"] for q in floor["queue"]], ["F007", "A022"])
        busy = [w for w in floor["windows"] if w["no"] == "02 号台"][0]
        self.assertEqual(busy["st"], "办理中")
        self.assertIn("A021", busy["who"])
        self.assertEqual(call_next("P1", path=self.path)["status"], "denied")

    def test_business_picks_the_line(self):
        from app.services.lobby import take_ticket
        fin = take_ticket("P4", "定期存款转存", "陈××", path=self.path)
        post = take_ticket("P4", "寄递包裹", "周××", path=self.path)
        self.assertEqual(fin["line"], "代理金融")
        self.assertEqual(post["line"], "邮政营业")
        nos = [q["no"] for q in fin["queue"]]
        self.assertEqual(nos, ["A021", "F007", "A022", fin["took"]])
        nos2 = [q["no"] for q in post["queue"]]
        self.assertEqual(nos2[-1], post["took"])
        self.assertEqual(nos2[-2], fin["took"])
        teller = view("P2", path=self.path)
        postal = view("P3", path=self.path)
        self.assertTrue(all(q["dest"] == "代理金融" for q in teller["queue"]))
        self.assertFalse(any(q["no"].startswith("A") for q in teller["queue"]))
        self.assertTrue(all(q["dest"] == "邮政营业" for q in postal["queue"]))
        self.assertNotIn("F007", [q["no"] for q in postal["queue"]])
        self.assertEqual(
            len(view("P4", path=self.path)["queue"]),
            len(teller["queue"]) + len(postal["queue"]),
        )

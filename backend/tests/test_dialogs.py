import unittest
from datetime import datetime

from app.capabilities import names
from app.services.dialogs import DeskShell, add_same_unit, allow_plaintext, fleet, rollback_open, visible_rows


SPEC = {
    "title": "今日交易",
    "caliber": "渠道口径 · 按笔计",
    "lead": "今日累计办结的笔数。",
    "kpi": [("柜面", "1208", "笔"), ("自助", "1647", "笔"), ("手机银行", "557", "笔")],
    "part": True,
    "cap": "1208 ＋ 1647 ＋ 557 ＝ 3412 笔",
    "cols": ["渠道", "笔数 · 占比", "笔"],
    "rows": [["柜面", "35.4%", "1208"], ["自助", "48.3%", "1647"], ["手机银行", "16.3%", "557"]],
    "sum": ["合计", "3 个渠道", "3412 笔"],
    "note": "调用次数和业务笔数不是同一个单位。",
    "source": "08_报表 · 全局报表",
    "to": "二级页/08_报表.html#全局报表",
    "to_name": "全局报表",
}


class Dialogs(unittest.TestCase):
    def test_stat_window_stays_modal(self):
        shell = DeskShell()
        opened = shell.open_stat("trade", SPEC)
        self.assertEqual(opened["status"], "open")
        self.assertEqual(opened["sections"], ("head", "lead", "kpi", "table", "note", "foot"))
        again = shell.open_stat("sites", SPEC)
        self.assertEqual(again["need"], "close_first")
        closed = shell.close_stat("escape")
        self.assertEqual(closed["focus"], "trade")
        bad = dict(SPEC)
        bad["to"] = "二级页/08_报表.html"
        bad["part"] = False
        bad["cap"] = ""
        blocked = shell.open_stat("trade", bad)
        self.assertIn("anchor", blocked["need"])
        self.assertIn("cap", blocked["need"])

    def test_review_and_return_need_a_second_fact(self):
        shell = DeskShell()
        shell.open_review()
        same = shell.confirm_review(initiator="周××", reviewer="周××")
        self.assertEqual(same["need"], "second_person")
        done = shell.confirm_review(initiator="周××", reviewer="郑××")
        self.assertEqual(len(done["events"]), 5)
        self.assertFalse(done["undo"])
        vague = shell.return_for_more(["不合格"])
        self.assertEqual(vague["need"], "gaps")
        named = shell.return_for_more(["交接清单缺签认栏"])
        self.assertEqual(named["gaps"], ["交接清单缺签认栏"])

    def test_side_shell_and_post_pin(self):
        shell = DeskShell()
        shell.role = "P5"
        task = shell.open_side("task", go="二级页/08_组织.html#调岗与交接", module="组织")
        self.assertFalse(task["transfer"])
        self.assertEqual(task["trace"], "看过这一条")
        self.assertEqual(shell.open_side("logout")["need"], "close_first")
        shell.close_side()
        session = shell.open_side("session")
        self.assertFalse(session["carries_chat"])
        self.assertEqual(session["role"], "P5")
        shell.close_side()
        shell.open_stat("trade", SPEC)
        home = shell.post_pin(on_home=True, back_href=None, scroll_top=0)
        self.assertEqual(home["message"], "已回到工作台顶部")
        self.assertEqual(home["role"], "P5")
        self.assertIsNone(shell.stat_key)
        away = shell.post_pin(on_home=False, back_href="08_管理员端.html", scroll_top=20)
        self.assertEqual(away["go"], "08_管理员端.html")
        self.assertEqual(away["role"], "P5")

    def test_logout_keeps_tasks_on_the_post(self):
        shell = DeskShell()
        out = shell.logout(post_id=4, org_id=1)
        self.assertTrue(out["login_cleared"])
        self.assertEqual(out["tasks_post_id"], 4)
        self.assertEqual(out["session_org_id"], 1)

    def test_report_floor_units_and_service(self):
        rolled = visible_rows([{"name": "甲", "count": 12}, {"name": "乙", "count": 3}])
        self.assertEqual(len(rolled["shown"]), 1)
        self.assertEqual(rolled["withheld"], 1)
        mixed = add_same_unit([{"count": 1, "unit": "项"}, {"count": 2, "unit": "条"}])
        self.assertFalse(mixed["ok"])
        health = fleet(
            [
                {"alerts": [], "availability": "99.99"},
                {"alerts": ["延迟", "积压"], "availability": "99.62"},
            ]
        )
        self.assertEqual(health["watch"], 0)
        self.assertEqual(health["alert_rules"], 2)
        self.assertEqual(health["lowest"], "99.62")
        closed = rollback_open(
            released_at=datetime(2026, 10, 5, 9, 0),
            now=datetime(2026, 10, 20, 16, 0),
            latest=False,
        )
        self.assertFalse(closed["ok"])
        self.assertFalse(closed["auto"])
        self.assertEqual(allow_plaintext("身份证查得")["status"], "masked")
        self.assertIn("stat_window", names())
        self.assertIn("side_shell", names())

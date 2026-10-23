import unittest

from app.assembly.alignment import (
    from_login,
    from_roster,
    from_shell,
    identify,
    role_for_name,
)
from app.assembly.roles import ROLE_LABELS
from app.auth.boundary import admin_effect, customer_body_returned


class RoleAlignment(unittest.TestCase):
    def test_shell_codes_do_not_enter_the_backend_as_is(self):
        shell = from_shell("P1")
        self.assertEqual(shell["name"], "支局经理")
        self.assertEqual(shell["role_code"], "P3")
        self.assertEqual(ROLE_LABELS["P1"], "普通柜员")
        self.assertEqual(from_shell("P2")["role_code"], "P1")
        self.assertEqual(from_shell("P3")["role_code"], "P2")
        self.assertEqual([from_shell(code)["cells"] for code in ("P1", "P2", "P3", "P4", "P5")], [22, 22, 26, 19, 22])

    def test_roster_p0_is_not_the_login_admin(self):
        self.assertIsNone(from_roster("P0")["role_code"])
        self.assertEqual(from_roster("P0")["account"], "no_counter")
        admin = from_login("P0")
        self.assertEqual(admin["role_code"], "P5")
        self.assertEqual(admin["name"], "系统管理员")

    def test_roster_posts_without_a_backend_code(self):
        self.assertEqual(from_roster("P7")["account"], "no_page")
        self.assertIn("默认同意", from_roster("P7")["note"])
        self.assertIsNone(from_roster("P7")["role_code"])
        self.assertEqual(from_roster("P5")["account"], "no_page")
        self.assertEqual(from_roster("P6")["account"], "no_page")
        for name in ("理财经理", "综合柜员", "保安", "职能 / 后勤"):
            with self.assertRaises(ValueError):
                role_for_name(name)

    def test_five_doors_two_missing_pages_and_the_guard(self):
        entered = [identify(no) for no in ("1001", "1003", "1017", "1004", "9001")]
        self.assertEqual([row["role_code"] for row in entered], ["P3", "P1", "P2", "P4", "P5"])
        self.assertEqual(identify("1002")["role_code"], "P1")
        self.assertEqual(identify("1002")["home"], identify("1003")["home"])
        wealth = identify("1018")
        comprehensive = identify("1010")
        self.assertEqual(wealth["kind"], "no_page")
        self.assertEqual(comprehensive["kind"], "no_page")
        self.assertIn("未单独成页", wealth["note"])
        self.assertIn("未单独成页", comprehensive["note"])
        guard = identify("1022")
        self.assertEqual(guard["kind"], "no_page")
        self.assertIn("默认同意", guard["note"])
        self.assertIsNone(guard["role_code"])
        self.assertEqual(identify("1001")["session"], "会话留在原网点")

    def test_admin_writes_stay_read_only(self):
        for action in ("adjust_post", "set_param", "break_glass"):
            self.assertEqual(admin_effect(action), "read_only")
        self.assertFalse(customer_body_returned())


if __name__ == "__main__":
    unittest.main()

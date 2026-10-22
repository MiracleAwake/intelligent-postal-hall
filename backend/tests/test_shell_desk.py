"""壳上的待办只来自名册、客户库和转交。没有的项不出现。"""

import unittest

from fastapi.testclient import TestClient

from app.main import create_app
from app.services.shell_desk import snapshot


class ShellDeskTest(unittest.TestCase):
    def test_empty_handoff_has_no_pin_and_admin_skips_customers(self):
        view = snapshot("P5", [{"account_state": "enter"}, {"account_state": "no_page"}], [{"name": "陈晓兰", "focus": True}], [])
        self.assertEqual(view["pins"], [])
        self.assertEqual(view["notices"], {})
        self.assertEqual(view["tasks"], [])
        self.assertEqual(view["board"], [])
        self.assertEqual(view["figures"][0]["t"], "在册员工")
        self.assertEqual(view["figures"][0]["v"], "2")
        self.assertEqual([item["t"] for item in view["figures"]], ["在册员工"])
        self.assertNotIn("陈晓兰", str(view))

    def test_focus_customers_are_a_notice_for_counter_roles(self):
        customers = [{"focus": True}, {"focus": False}, {"focus": True}]
        view = snapshot("P2", [], customers, [])
        self.assertEqual(view["notices"]["客户"]["n"], 2)
        self.assertEqual(view["pins"], [])
        self.assertEqual(view["figures"][1]["t"], "在册客户")
        self.assertEqual(view["figures"][1]["v"], "3")

    def test_handoff_becomes_pin_task_and_badge(self):
        view = snapshot("P1", [], [], [{
            "to_owner": "P1",
            "from": "大堂",
            "business": "定期转存",
            "group": "授权",
            "status": "requested",
        }])
        self.assertEqual(view["pins"][0]["text"], "定期转存")
        self.assertEqual(view["tasks"][0]["t"], "定期转存")
        self.assertEqual(view["notices"]["授权"]["n"], 1)
        self.assertEqual(view["board"], [["大堂", "定期转存", "待收"]])
        titled = snapshot("P1", [], [], [{
            "to_owner": "支局经理",
            "from": "大堂",
            "business": "授权复核",
            "status": "requested",
        }])
        self.assertEqual(titled["pins"][0]["text"], "授权复核")

    def test_route_hides_admin_customer_body(self):
        client = TestClient(create_app())
        res = client.get("/api/desk", params={"role": "P5"})
        self.assertEqual(res.status_code, 200)
        body = res.text
        self.assertNotIn("陈晓兰", body)
        self.assertNotIn("13867230011", body)
        data = res.json()
        self.assertEqual(data["pins"], [])
        self.assertEqual(data["notices"], {})
        self.assertEqual(data["figures"][0]["v"], "9")
        told = client.get("/api/desk", params={"role": "P2"}).json()
        self.assertEqual(told["notices"]["客户"]["n"], 4)
        self.assertEqual(told["figures"][1]["v"], "50")


if __name__ == "__main__":
    unittest.main()

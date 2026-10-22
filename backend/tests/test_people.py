import tempfile
import unittest
from pathlib import Path

from app.storage.people import ensure, list_customers, list_staff, mask_id


class PeopleTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name) / "biz.sqlite"
        ensure(self.path)

    def tearDown(self):
        self.dir.cleanup()

    def test_fifty_customers_stay_in_the_clear_for_the_counter(self):
        rows = list_customers("P1", self.path)
        self.assertEqual(len(rows), 50)
        chen = next(row for row in rows if row["ref"] == "c001")
        self.assertEqual(chen["name"], "陈晓兰")
        self.assertTrue(chen["id_no"].startswith("3301"))
        self.assertTrue(chen["id_no"].endswith("1234"))
        self.assertNotIn("*", chen["id_no"])
        self.assertEqual(chen["phone"], "13867230011")
        self.assertIn("东风路 12 号", chen["address"])

    def test_admin_only_reads_the_mask(self):
        rows = list_customers("P5", self.path)
        full = next(row for row in list_customers("P1", self.path) if row["ref"] == "c001")
        chen = next(row for row in rows if row["ref"] == "c001")
        self.assertEqual(chen["name"], "陈××")
        self.assertEqual(chen["id_no"], mask_id(full["id_no"]))
        self.assertEqual(chen["phone"], "138****0011")
        self.assertEqual(chen["address"], "")
        self.assertEqual(chen["area"], "东风路片区")
        joined = " ".join(str(value) for value in chen.values())
        self.assertNotIn("陈晓兰", joined)
        self.assertNotIn("13867230011", joined)

    def test_staff_follow_the_prototype_roster(self):
        staff = {row["employee_no"]: row for row in list_staff(self.path)}
        self.assertEqual(staff["1001"]["title"], "支局经理")
        self.assertEqual(staff["1001"]["role_code"], "P3")
        self.assertEqual(staff["1003"]["role_code"], "P1")
        self.assertEqual(staff["9001"]["role_code"], "P5")
        self.assertEqual(staff["1002"]["account_state"], "no_page")
        self.assertIsNone(staff["1002"]["role_code"])
        self.assertEqual(staff["1022"]["account_state"], "refuse")
        self.assertEqual(staff["1018"]["title"], "理财经理")

    def test_admin_route_does_not_return_the_clear_row(self):
        from fastapi.testclient import TestClient

        from app.main import create_app

        app = create_app()
        app.state.people_db = self.path
        client = TestClient(app)
        body = client.get("/api/customers", params={"role": "P5"}).json()
        self.assertEqual(len(body["customers"]), 50)
        text = str(body)
        self.assertNotIn("陈晓兰", text)
        self.assertNotIn("13867230011", text)
        counter = client.get("/api/customers", params={"role": "P1"}).json()
        self.assertIn("陈晓兰", str(counter))

    def test_admin_database_pane_masks_customers_and_drops_the_password(self):
        from fastapi.testclient import TestClient

        from app.main import create_app

        app = create_app()
        app.state.people_db = self.path
        client = TestClient(app)
        view = client.get("/api/admin/db").json()
        self.assertEqual(len(view["customers"]), 50)
        self.assertEqual(view["customers"][0]["name"], "陈××")
        self.assertEqual(view["customers"][0]["address"], "")
        text = str(view)
        self.assertNotIn("陈晓兰", text)
        self.assertNotIn("password", text)
        self.assertEqual(len(view["staff"]), 9)
        secret = "learn-secret-not-for-chat"
        denied = client.post(
            "/api/admin/db/connect",
            json={
                "host": "127.0.0.1",
                "port": 1,
                "user": "zhiyou",
                "password": secret,
                "database": "biz",
            },
        ).json()
        self.assertEqual(denied["status"], "closed")
        self.assertNotIn(secret, str(denied))
        empty = client.post("/api/admin/db/connect", json={"password": ""}).json()
        self.assertEqual(empty["detail"], "还没有口令")


if __name__ == "__main__":
    unittest.main()

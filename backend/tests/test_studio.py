import unittest

from fastapi.testclient import TestClient

from app.main import create_app


class AdminStudio(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(create_app())

    def test_branches_keep_different_prompts(self):
        east = self.client.get("/api/admin/prompt", params={"org_id": 7, "role_code": "P1"}).json()
        west = self.client.get("/api/admin/prompt", params={"org_id": 8, "role_code": "P1"}).json()
        self.assertNotEqual(east["body"], west["body"])
        self.assertIn("本支局另守一句", west["body"])
        saved = self.client.post(
            "/api/admin/prompt",
            json={"org_id": 8, "role_code": "P1", "body": "西城路只办到期转存的授权。"},
        ).json()
        again = self.client.get("/api/admin/prompt", params={"org_id": 7, "role_code": "P1"}).json()
        self.assertEqual(saved["body"], "西城路只办到期转存的授权。")
        self.assertNotEqual(again["body"], saved["body"])

    def test_switch_model_without_a_key(self):
        added = self.client.post(
            "/api/admin/models",
            json={
                "id": "hall_trial",
                "display_name": "试用",
                "model": "demo",
                "base_url": "http://127.0.0.1:9",
                "api_key": "secret",
            },
        ).json()
        self.assertEqual(added["status"], "added")
        self.assertNotIn("api_key", added["item"])
        switched = self.client.post("/api/admin/models/active", json={"id": "hall_trial"}).json()
        self.assertEqual(switched["active"], "hall_trial")

    def test_knowledge_add_find_update(self):
        added = self.client.post(
            "/api/admin/docs",
            json={"title": "寄递安全", "body": "禁限寄要当面告知。", "source": "manual"},
        ).json()
        self.assertEqual(added["status"], "added")
        found = self.client.get("/api/admin/docs", params={"q": "当面"}).json()
        self.assertEqual(len(found["items"]), 1)
        doc_id = found["items"][0]["id"]
        updated = self.client.post(
            f"/api/admin/docs/{doc_id}",
            json={"title": "寄递安全", "body": "禁限寄要当面告知，并留下告知记录。"},
        ).json()
        self.assertIn("告知记录", updated["doc"]["body"])


if __name__ == "__main__":
    unittest.main()

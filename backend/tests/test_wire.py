import unittest

from fastapi.testclient import TestClient

from app.main import create_app


class StaffWire(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(create_app())

    def test_speech_without_text_stays_standby(self):
        res = self.client.post("/api/speech", json={"audio_ref": "mic:0:03"})
        body = res.json()
        self.assertEqual(body["status"], "standby")
        self.assertEqual(body["text"], "")
        self.assertFalse(body["audio_kept"])

    def test_upload_returns_a_file_id(self):
        res = self.client.post(
            "/api/files",
            files={"file": ("身份证正面.png", b"png-bytes", "image/png")},
        )
        body = res.json()
        self.assertEqual(body["name"], "身份证正面.png")
        self.assertEqual(len(body["file_id"]), 12)
        self.assertFalse(body["kept_bytes"])
        self.assertNotIn("png-bytes", res.text)

    def test_handoff_records_a_request(self):
        res = self.client.post(
            "/api/handoff",
            json={"from": "P2", "to_owner": "邮政营业", "business": "收寄与封发", "page": "07_收寄"},
        )
        body = res.json()
        self.assertEqual(body["status"], "requested")
        self.assertEqual(body["to_owner"], "邮政营业")
        self.assertNotIn("url", body)

    def test_inbox_shows_the_request_to_the_owning_post(self):
        self.client.post(
            "/api/handoff",
            json={"from": "P2", "to_owner": "邮政营业", "business": "收寄与封发", "page": "07_收寄"},
        )
        mine = self.client.get("/api/handoff", params={"to_owner": "邮政营业"}).json()
        other = self.client.get("/api/handoff", params={"to_owner": "普通柜员"}).json()
        self.assertEqual(len(mine["items"]), 1)
        self.assertEqual(mine["items"][0]["status"], "requested")
        self.assertEqual(other["items"], [])

    def test_copy_does_not_invent_fields(self):
        empty = self.client.post("/api/act", json={"stage": "copy", "known": {}}).json()
        self.assertTrue(empty["stop"])
        self.assertEqual(empty["fields"], {})
        self.assertFalse(empty["submitted"])
        kept = self.client.post("/api/act", json={"stage": "copy", "known": {"amount": "20000", "weight": ""}}).json()
        self.assertEqual(kept["fields"], {"amount": "20000"})
        self.assertNotIn("weight", kept["fields"])

    def test_device_waits_until_a_person_gives_the_reading(self):
        waiting = self.client.post("/api/act", json={"stage": "device", "kind": "scale"}).json()
        self.assertEqual(waiting["status"], "waiting")
        self.assertEqual(waiting["owner"], "human")
        self.assertFalse(waiting["model_supplied"])
        read = self.client.post("/api/act", json={"stage": "device", "kind": "scale", "reading": "3.2"}).json()
        self.assertEqual(read["reading"], "3.2")
        self.assertEqual(read["source"], "human")
        self.assertFalse(read["model_supplied"])

    def test_file_lookup_returns_the_name_only(self):
        res = self.client.post(
            "/api/files",
            files={"file": ("身份证正面.png", b"png-bytes", "image/png")},
        )
        file_id = res.json()["file_id"]
        meta = self.client.get("/api/files/" + file_id).json()
        self.assertEqual(meta["name"], "身份证正面.png")
        self.assertNotIn("png-bytes", str(meta))

    def test_session_drops_anything_except_the_desk(self):
        res = self.client.post(
            "/api/session",
            json={"no": "1001", "post": "P1", "role": "支局经理", "site": "df", "pw": "123456"},
        )
        body = res.json()["session"]
        self.assertEqual(body["no"], "1001")
        self.assertNotIn("pw", body)

    def test_shell_is_the_renamed_copy(self):
        res = self.client.get("/挚邮员工端.html")
        self.assertEqual(res.status_code, 200)
        self.assertIn("挚邮员工端", res.text[:400])
        self.assertIn("hall-wire.js", res.text)

    def test_old_admin_home_returns_to_the_shell(self):
        res = self.client.get("/08_管理员端.html", follow_redirects=False)
        self.assertEqual(res.status_code, 307)
        self.assertIn("role=P5", res.headers["location"])
        wire = self.client.get("/hall-wire.js")
        self.assertEqual(wire.status_code, 200)


if __name__ == "__main__":
    unittest.main()

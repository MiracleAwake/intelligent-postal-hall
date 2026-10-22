import unittest

from app.services.hall import HallDesk
from app.services.step_prompt import temporary_prompt
from tests.test_hall import APPOINTMENT


class StepPrompt(unittest.TestCase):
    def test_prompt_uses_the_previous_step_and_drops_the_customer_ref(self):
        progress = {
            "amount": "20000.00",
            "intent": {"intent": "改存期", "customer_ref": "crm:1"},
            "fields_by_step": {
                "scan_fill": {"new_term": "3年", "id_no": "110101199001011234", "customer_ref": "crm:1"},
            },
            "steps": [
                {"id": "scan_fill", "title": "扫描填写", "owner": "model", "status": "done"},
                {"id": "password", "title": "输入密码", "owner": "human", "status": "current"},
            ],
        }
        prompt = temporary_prompt(progress)
        self.assertEqual(prompt["layer"], "temporary")
        self.assertFalse(prompt["persist"])
        self.assertFalse(prompt["for_model"])
        self.assertIn("上一步：扫描填写，已完成。", prompt["text"])
        self.assertIn("存期：3年", prompt["text"])
        self.assertIn("这一步停在人。", prompt["text"])
        self.assertNotIn("crm:1", prompt["text"])
        self.assertNotIn("110101199001011234", prompt["text"])

    def test_handoff_view_carries_the_prompt_outside_the_saved_body(self):
        desk = HallDesk()
        view = desk.handoff("admin", org_id=7, post_id=3, appointment=APPOINTMENT, seats_free=1)
        prompt = view["temporary_prompt"]
        self.assertEqual(prompt["status"], "ready")
        self.assertFalse(prompt["for_model"])
        self.assertNotIn("crm:1", prompt["text"])
        saved = desk.hub.load(view["session_id"]).progress
        self.assertNotIn("temporary_prompt", saved)


if __name__ == "__main__":
    unittest.main()

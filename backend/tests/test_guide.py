import unittest

from app.capabilities.guide import match_business, recognize
from app.capabilities.tools import ToolDesk


class NewSessionGuide(unittest.TestCase):
    def test_rollover_opens_the_teller_page_and_the_chain(self):
        heard = match_business("这笔到期了，再存一年，另外再加一笔")
        self.assertEqual(heard["mode"], "work")
        self.assertEqual(heard["home"], "05_普通柜员页.html")
        self.assertEqual(heard["role_code"], "P1")
        self.assertEqual(heard["flow"], "time_deposit_rollover")
        self.assertTrue(heard["starts_chain"])
        self.assertIn("到期转存", heard["intents"])
        self.assertIn("加钱", heard["intents"])
        self.assertFalse(heard["completes"])

    def test_mail_opens_the_postal_page(self):
        heard = match_business("客户要寄件")
        self.assertEqual(heard["home"], "07_邮政营业页.html")
        self.assertEqual(heard["role_code"], "P2")
        self.assertFalse(heard["starts_chain"])

    def test_two_doors_stay_on_the_guide(self):
        heard = match_business("转存之后顺便寄件")
        self.assertEqual(heard["mode"], "guide")
        self.assertNotIn("home", heard)
        names = {item["name"] for item in heard["hits"]}
        self.assertEqual(names, {"到期转存", "收寄"})

    def test_voice_without_text_does_not_jump(self):
        heard = recognize(audio_ref="mic:1")
        self.assertEqual(heard["mode"], "guide")
        self.assertEqual(heard["voice"], "standby")

    def test_new_session_tool_keeps_the_guide_until_a_business_is_clear(self):
        desk = ToolDesk()
        guide = desk.call("P4", "new_session", {"org_id": 7, "post_id": 4})
        self.assertEqual(guide["status"], "guide")
        self.assertEqual(guide["speech"], "speech_input")
        work = desk.call("P1", "new_session", {"org_id": 7, "post_id": 1, "text": "办理授权"})
        self.assertEqual(work["mode"], "work")
        self.assertEqual(work["home"], "06_支局经理页.html")
        self.assertEqual(work["org_id"], 7)


if __name__ == "__main__":
    unittest.main()

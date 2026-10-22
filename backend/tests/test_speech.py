import unittest

from app.assembly.roles import assemble
from app.capabilities.speech import SPEECH_HOOK, accept_speech
from app.capabilities.tools import ToolDesk


class SpeechInput(unittest.TestCase):
    def test_text_is_ready_and_does_not_complete(self):
        heard = accept_speech("这笔再存一年，利息取出来，另外再加一笔")
        self.assertEqual(heard["status"], "ready")
        self.assertEqual(heard["text"], "这笔再存一年，利息取出来，另外再加一笔")
        self.assertFalse(heard["completes"])
        self.assertFalse(heard["audio_kept"])
        self.assertFalse(heard["connected"])
        self.assertEqual(heard["id"], SPEECH_HOOK["id"])

    def test_audio_without_text_stays_standby(self):
        waiting = accept_speech(audio_ref="mic:1")
        self.assertEqual(waiting["status"], "standby")
        self.assertEqual(waiting["text"], "")
        self.assertNotIn("再存", waiting["text"])

    def test_blank_is_empty(self):
        self.assertEqual(accept_speech("  ")["status"], "empty")

    def test_each_role_can_call_the_hook(self):
        desk = ToolDesk()
        for role in ("P1", "P2", "P3", "P4", "P5"):
            self.assertIn("speech_input", assemble(role))
            heard = desk.call(role, "speech_input", {"text": "先分流"})
            self.assertEqual(heard["status"], "ready")
            self.assertEqual(heard["text"], "先分流")
            self.assertFalse(heard["completes"])


if __name__ == "__main__":
    unittest.main()

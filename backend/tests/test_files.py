import tempfile
import unittest
from pathlib import Path

from app.assembly.roles import assemble
from app.capabilities.tools import ToolDesk
from app.gateway import GateClosed


class DraftExport(unittest.TestCase):
    def test_blank_amount_stays_blank_and_id_is_left_out(self):
        desk = ToolDesk()
        draft = desk.call(
            "P1",
            "draft_export",
            {
                "kind": "定期存款凭条",
                "known": {"intent": "改存期", "new_term": "1年", "party": "本人", "id_no": "110101199001011234"},
                "body": "客户身份证 110101199001011234",
            },
        )
        self.assertEqual(draft["status"], "draft")
        self.assertIn("存期：1年", draft["text"])
        self.assertIn("金额：\n", draft["text"])
        self.assertNotIn("110101199001011234", draft["text"])
        self.assertFalse(draft["printed"])
        self.assertFalse(draft["completes"])
        self.assertFalse(draft["body_kept"])

    def test_export_writes_a_text_file(self):
        desk = ToolDesk()
        with tempfile.TemporaryDirectory() as folder:
            saved = desk.call(
                "P2",
                "draft_export",
                {"kind": "收寄说明", "known": {"item_name": "衣物", "weight": "1.2kg"}, "directory": folder},
            )
            path = Path(saved["path"])
            self.assertEqual(saved["status"], "exported")
            self.assertTrue(path.is_file())
            self.assertIn("重量：1.2kg", path.read_text(encoding="utf-8"))
            self.assertEqual(path.parent, Path(folder).resolve())
            self.assertFalse(saved["printed"])

    def test_admin_cannot_export_and_unknown_kind_is_rejected(self):
        desk = ToolDesk()
        self.assertNotIn("draft_export", assemble("P5"))
        with self.assertRaises(GateClosed):
            desk.call("P5", "draft_export", {"kind": "办理摘要"})
        rejected = desk.call("P3", "draft_export", {"kind": "客户明细"})
        self.assertEqual(rejected["status"], "rejected")
        self.assertEqual(rejected["text"], "")


if __name__ == "__main__":
    unittest.main()

import unittest

import cv2
import numpy as np

from app.capabilities.devices.vision import PageReader, compare_photos, fields_from_lines, mask_id
from app.capabilities.tools import ToolDesk
from app.capabilities.devices.capture import Capture


def _png(pattern: str) -> bytes:
    image = np.zeros((40, 40), dtype=np.uint8)
    if pattern == "left":
        image[:, :20] = 255
    elif pattern == "top":
        image[:20, :] = 255
    else:
        image[:, :] = 128
    ok, encoded = cv2.imencode(".png", image)
    assert ok
    return encoded.tobytes()


class PageText(unittest.TestCase):
    def test_id_lines_keep_a_masked_number(self):
        fields = fields_from_lines(["姓名王××", "110101199001011234"], "身份证")
        self.assertEqual(fields["name"], "王××")
        self.assertEqual(fields["id_no"], "110101199001011234")
        self.assertEqual(fields["id_masked"], mask_id(fields["id_no"]))
        self.assertNotEqual(fields["id_masked"], fields["id_no"])
        self.assertEqual(fields_from_lines(["定期存单"], "存单"), {})

    def test_reader_uses_the_given_engine_and_skips_non_images(self):
        reader = PageReader(ocr=lambda image: ["姓名李××", "公民身份号码 110101199001011234"])
        heard = reader.read(_png("flat"), "身份证")
        self.assertEqual(heard["status"], "read")
        self.assertEqual(heard["fields"]["name"], "李××")
        self.assertFalse(heard["persist_id"])
        self.assertEqual(reader.read(b"frame", "身份证")["status"], "unreadable")

    def test_photo_hint_is_not_a_national_pass(self):
        same = compare_photos(_png("left"), _png("left"))
        other = compare_photos(_png("left"), _png("top"))
        self.assertFalse(same["national"])
        self.assertFalse(same["verified"])
        self.assertFalse(same["pass"])
        self.assertGreater(same["hint_score"], other["hint_score"])
        waiting = compare_photos(None, _png("left"))
        self.assertEqual(waiting["need"], "doc_and_live")

    def test_camera_scan_extracts_without_opening_a_real_lens(self):
        picture = _png("flat")
        desk = ToolDesk(
            capture=Capture(devices=lambda: [], camera_grabber=lambda index: picture, file_reader=lambda path: picture),
            reader=PageReader(ocr=lambda image: ["定期存单"]),
        )
        shot = desk.call("P1", "scan_voucher", {"mode": "scanner", "doc_kind": "存单"})
        self.assertEqual(shot["capture"]["source"], "camera_as_scanner")
        self.assertEqual(shot["text"]["lines"], ["定期存单"])
        face = desk.call("P1", "face_check", {"doc": picture, "live": picture})
        self.assertEqual(face["owner"], "human")
        self.assertFalse(face["national"])
        self.assertNotEqual(face["status"], "verified")


if __name__ == "__main__":
    unittest.main()

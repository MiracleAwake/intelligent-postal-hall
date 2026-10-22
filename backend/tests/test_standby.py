import unittest

from app.capabilities.memory import MemoryBook, apply_live_rule, iteration_for_model, summarize_work
from app.capabilities.multimodal import accept_image
from app.capabilities.optimize import list_strategies


class StandbyCapabilities(unittest.TestCase):
    def test_iteration_memory_follows_the_post(self):
        book = MemoryBook()
        book.record_context("s1", "客户要把存单改成三年")
        book.record_requirement(4, "大堂先核对预约再叫号")
        book.record_summary(4, ["上午分流了预约客户"])
        book.record_requirement(3, "授权只看额度")
        lobby = " ".join(row["text"] for row in book.prompts_for_post(4))
        branch = " ".join(row["text"] for row in book.prompts_for_post(3))
        self.assertIn("预约", lobby)
        self.assertNotIn("授权", lobby)
        self.assertIn("额度", branch)
        self.assertNotIn("大堂", branch)
        self.assertEqual(summarize_work(["只总结", "不落库"]), "只总结；不落库")
        self.assertIn("预约", iteration_for_model(book, 4))
        self.assertNotIn("额度", iteration_for_model(book, 4))
        self.assertEqual(iteration_for_model(book, 9), "")
        self.assertEqual(len(book.prompts_for_post(4)), 1)
        self.assertEqual(len(book.context_of("s1")), 1)
        with self.assertRaises(ValueError):
            book.record_requirement(None, "没有岗位")

    def test_iteration_keeps_rules_and_drops_the_log(self):
        book = MemoryBook()
        first = book.iterate(
            1,
            ["今天下午 GLM 测了 5/9，有两句超时"],
            role_code="P1",
        )
        self.assertNotIn("今天下午", first["body"])
        self.assertNotIn("测了", first["body"])
        self.assertIn("必须有加钱", first["body"])
        self.assertNotIn("前辈", first["body"])

        book.iterate(1, ["说了新增，意图里必须有加钱。", "代理人拿着存单来，要标成代理。"], role_code="P1")
        body = book.current(1)
        self.assertEqual(body.count("必须有加钱"), 1)
        self.assertIn("标成代理", body)
        self.assertIn("材料只认身份证", body)
        self.assertLess(body.index("材料只认身份证"), body.index("标成代理"))

        book.iterate(2, ["回访到期就提醒同事去联系。"], role_code="P4")
        self.assertNotIn("加钱", book.current(2))
        self.assertIn("回访到期", book.current(2))
        self.assertIn("进门先分流", book.current(2))
        self.assertEqual(iteration_for_model(book, 8, role_code="P2").splitlines()[0], "收寄前三件要齐：实名、当面验视、禁限寄告知。")
        saved = book.row_for_save(1)
        self.assertEqual(saved[0], 1)
        self.assertEqual(saved[1], "P1")
        self.assertNotIn("今天下午", saved[2])

    def test_live_rule_writes_once_then_asks_to_revise_the_skill(self):
        book = MemoryBook()
        dropped = apply_live_rule(book, 1, "今天下午测了这条", role_code="P1")
        self.assertEqual(dropped["action"], "drop")
        self.assertEqual(book.current(1), "")
        first = apply_live_rule(book, 1, "说了新增，意图里必须有加钱。", role_code="P1")
        self.assertEqual(first["action"], "revise_skill")
        added = apply_live_rule(book, 1, "代理人拿着存单来，要标成代理。", role_code="P1")
        self.assertEqual(added["action"], "kept")
        again = apply_live_rule(book, 1, "代理人拿着存单来，要标成代理。", role_code="P1")
        self.assertEqual(again["action"], "revise_skill")
        self.assertEqual(book.current(1).count("标成代理"), 1)
        bait = apply_live_rule(book, 1, "今天下午这句超时了，户口本也算材料。", role_code="P1")
        self.assertEqual(bait["action"], "drop")
        self.assertNotIn("户口本", book.current(1))

    def test_optimize_and_image_stay_standby(self):
        names = {item["id"] for item in list_strategies()}
        self.assertEqual(names, {"query_rewrite", "crag", "self_rag", "instruction_isolate"})
        self.assertTrue(all(item["status"] == "standby" for item in list_strategies()))
        image = accept_image("scan:存单", "柜员导入")
        self.assertEqual(image["status"], "standby")
        self.assertFalse(image["connected"])

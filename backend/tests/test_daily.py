import unittest
from datetime import date, datetime

from app.capabilities import names
from app.services.daily import DailyBook, Fact


DAY = date(2026, 10, 16)
PRIOR = datetime(2026, 10, 15, 11, 0, 0)
TODAY = datetime(2026, 10, 16, 9, 30, 0)


def fact(ref, kind, at=TODAY, role="P4", customer=None, amount=None, link=None, note=None):
    return Fact(
        ref=ref,
        org_id=1,
        post_id=4,
        role_code=role,
        kind=kind,
        occurred_at=at,
        customer_ref=customer,
        display_name=customer,
        amount=amount,
        note=note,
        link_ref=link,
    )


class DailyRollup(unittest.TestCase):
    def test_revisit_count_and_list_share_rows(self):
        book = DailyBook()
        book.collect(fact("rv-1", "revisit", customer="周", note="电话"))
        book.collect(fact("rv-2", "revisit", customer="周", note="到店", at=datetime(2026, 10, 16, 15, 0, 0)))
        book.collect(fact("rv-old", "revisit", at=PRIOR, customer="王"))

        item = next(row for row in book.summary(1, DAY)["items"] if row["key"] == "revisit")
        lines = book.lines(1, DAY, "revisit")

        self.assertEqual(item["count"], 1)
        self.assertEqual(item["prior_count"], 1)
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0]["note"], "电话")
        recent = book.recent(1, "revisit", limit=1)
        self.assertEqual(recent[0]["ref"], "rv-2")

    def test_same_ref_does_not_double(self):
        book = DailyBook()
        book.collect(fact("rv-1", "revisit", customer="周"))
        book.collect(fact("rv-1", "revisit", customer="周", note="改期"))
        self.assertEqual(len(book.lines(1, DAY, "revisit")), 1)
        self.assertEqual(book.lines(1, DAY, "revisit")[0]["note"], "改期")

    def test_savings_sum_by_role_and_branch(self):
        book = DailyBook()
        book.collect(fact("in-1", "savings_in", role="P1", amount="100.50"))
        book.collect(fact("in-2", "savings_in", role="P2", amount="50.00"))
        book.collect(fact("out-1", "savings_out", role="P1", amount="20.00"))
        book.collect(fact("biz-1", "business", role="P1", amount="20000.00"))

        branch = {row["key"]: row for row in book.summary(1, DAY)["items"]}
        teller = {row["key"]: row for row in book.summary(1, DAY, role_code="P1")["items"]}

        self.assertEqual(branch["savings_in"]["amount"], "150.50")
        self.assertEqual(teller["savings_in"]["amount"], "100.50")
        self.assertEqual(teller["savings_out"]["amount"], "20.00")
        self.assertEqual(branch["business"]["count"], 1)
        self.assertIsNone(branch["business"]["amount"])

    def test_task_and_arrival(self):
        book = DailyBook()
        book.collect(fact("task-1", "task_open"))
        book.collect(fact("task-1", "task_done"))
        book.collect(fact("appt-1", "appointment", customer="李"))
        book.collect(fact("appt-2", "appointment", customer="赵"))
        book.collect(fact("arr-1", "arrival", customer="李", link="appt-1"))

        items = {row["key"]: row for row in book.summary(1, DAY)["items"]}
        self.assertEqual(items["task_progress"]["count"], 1)
        self.assertEqual(items["task_progress"]["rate"], "1.00")
        self.assertEqual(items["arrival_rate"]["count"], 1)
        self.assertEqual(items["arrival_rate"]["rate"], "0.50")
        arrived = {row["ref"]: row["arrived"] for row in book.lines(1, DAY, "arrival_rate")}
        self.assertEqual(arrived, {"appt-1": True, "appt-2": False})

    def test_two_counters_keep_two_facts(self):
        book = DailyBook()
        book.collect(fact("business:w1", "business", role="P1", note="到期转存"))
        book.collect(fact("business:w2", "business", role="P2", note="收寄"))
        book.collect(fact("business:w1", "business", role="P1", note="到期转存-改"))
        notes = {row["ref"]: row["note"] for row in book.lines(1, DAY, "business")}
        self.assertEqual(notes, {"business:w1": "到期转存-改", "business:w2": "收寄"})

    def test_unknown_kind_rejected(self):
        book = DailyBook()
        with self.assertRaises(ValueError):
            book.collect(fact("x", "vip"))

    def test_capability_registered(self):
        self.assertIn("daily_rollup", names())

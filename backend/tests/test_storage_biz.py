import unittest
from datetime import datetime

from app.storage.biz import MemoryBiz


class Ownership(unittest.TestCase):
    def test_transfer_keeps_performance_and_bindings(self):
        biz = MemoryBiz()
        org = biz.add_org("001", "示例网点")
        person = biz.add_staff("1001", "柜员甲")
        counter = biz.add_post(org["id"], "P1", "柜面")
        lobby = biz.add_post(org["id"], "P4", "大堂")
        biz.open_assignment(person["id"], counter["id"], datetime(2026, 10, 1))
        biz.add_performance(person["id"], "到期转存", "20000.00", datetime(2026, 10, 2))
        biz.bind_customer(counter["id"], "crm", "c-1", "客户")
        biz.add_task(counter["id"], "预约到期")

        biz.transfer(person["id"], lobby["id"], datetime(2026, 10, 16))

        self.assertEqual(biz.open_post_of(person["id"])["role_code"], "P4")
        self.assertEqual(len(biz.performances_of(person["id"])), 1)
        self.assertEqual(len(biz.bindings_of(counter["id"])), 1)
        self.assertEqual(biz.bindings_of(lobby["id"]), [])
        self.assertEqual(len(biz.tasks_of(counter["id"])), 1)
        closed = [row for row in biz.assignment if row["ended_at"] is not None]
        self.assertEqual(len(closed), 1)

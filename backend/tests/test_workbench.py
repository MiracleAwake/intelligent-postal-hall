import unittest

from app.capabilities import names
from app.services.workbench import (
    Field,
    ImageDoc,
    agent_trace,
    assign_person,
    blockers,
    effective_value,
    evidence_lines,
    gate_label,
    hand_to_human,
    mark_skip,
    prepare_fields,
    propose_evidence,
    run_state,
    speak,
)


ROSTER = [("王××", "支局经理"), ("赵××", "柜员"), ("全员", "全员")]


class Workbench(unittest.TestCase):
    def test_model_does_not_answer_for_the_customer(self):
        fields = [
            Field("金额", "model", 1),
            Field("用途", "manual", 1),
            Field("存期", "model", 3),
        ]
        out = prepare_fields(fields, {"金额": "20000"}, at=1)
        self.assertEqual(out["filled"], {"金额": "20000"})
        self.assertEqual(out["human_required"], ["用途"])
        self.assertNotIn("存期", out["filled"])

    def test_blockers_wait_for_handoff_on_spoken_fields(self):
        fields = [Field("用途", "manual", 2)]
        docs = [ImageDoc("身份证", 2)]
        self.assertEqual(blockers(fields, docs, 2, handed=False), ["身份证"])
        self.assertEqual(blockers(fields, docs, 2, handed=True), ["用途", "身份证"])
        self.assertEqual(mark_skip("理财赎回沿用凭条，不另填申请书"), "理财赎回沿用凭条，不另填申请书")
        with self.assertRaises(ValueError):
            mark_skip("  ")

    def test_handoff_keeps_finished_steps_and_todo_is_separate(self):
        steps = hand_to_human(
            [
                {"id": "受理", "status": "done", "owner": "model"},
                {"id": "确认", "status": "open", "owner": "model"},
            ]
        )
        self.assertEqual(steps[0]["owner"], "model")
        self.assertEqual(steps[1]["owner"], "human")
        self.assertEqual(run_state(model_entered=False, any_value=False, waiting=False, handed=False), "todo")
        self.assertEqual(run_state(model_entered=True, any_value=False, waiting=True, handed=False), "auth")
        self.assertEqual(gate_label(waiting=True, owner="model"), "送主管审批")

    def test_evidence_assignment_script_and_trace(self):
        library = {"授权": ["双人到场，用后即过期"]}
        self.assertEqual(evidence_lines(library, "授权"), ["双人到场，用后即过期"])
        proposed = propose_evidence("授权", "额度读参数键")
        self.assertFalse(proposed["accepted"])

        self.assertFalse(assign_person("支局经理", ROSTER)["ok"])
        self.assertTrue(assign_person("赵××", ROSTER)["ok"])

        templates = [
            {"key": "M-01", "enabled": True, "text": "请稍等主管确认"},
            {"key": "M-04", "enabled": False, "text": "还没定稿"},
        ]
        self.assertEqual(speak(templates, "M-01")["status"], "ready")
        self.assertEqual(speak(templates, "M-04")["status"], "blocked")
        self.assertEqual(effective_value({"value": "5 分钟", "effective": "3 分钟", "status": "wait"}), "5 分钟")

        line = agent_trace(authorizer="郑××", action="查阅", target="GS-2026-0416", result="完成")
        self.assertEqual(line["who"], "智能体")
        self.assertIn("郑××", line["post"])
        with self.assertRaises(ValueError):
            agent_trace(authorizer="", action="查阅", target="GS-1", result="完成")

    def test_capabilities_registered(self):
        for name in ("step_prepare", "step_block", "evidence_sheet", "activity_assign", "script_pick", "param_read", "agent_trace"):
            self.assertIn(name, names())

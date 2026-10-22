"""五岗工具表，名称对齐原型功能区。页面以后按 id 接入。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Tool:
    id: str
    label: str
    kind: str


def _tools(*rows: tuple[str, str, str]) -> tuple[Tool, ...]:
    return tuple(Tool(*row) for row in rows)


P1_TOOLS = _tools(
    ("read_card", "读卡", "device"),
    ("id_card", "身份证", "device"),
    ("face_check", "人脸核验", "human"),
    ("scan_voucher", "凭证扫描", "device"),
    ("print_slip", "打印凭条", "human"),
    ("dual_record", "双录", "human"),
    ("verify_identity", "身份核验", "human"),
    ("auth_request", "授权与双录", "human"),
    ("trace", "留痕", "system"),
    ("new_session", "新建会话", "system"),
    ("takeover", "接管", "system"),
    ("resume", "断点续办", "system"),
    ("to_human", "转人工", "human"),
    ("open_account", "开户", "model"),
    ("deposit", "存取", "model"),
    ("wealth", "理财", "model"),
    ("observe", "模型观测", "model"),
    ("speech_input", "语音输入", "system"),
    ("draft_export", "起草并导出", "model"),
)

P2_TOOLS = _tools(
    ("inspect", "验视", "device"),
    ("weigh", "称重计费", "human"),
    ("print_waybill", "打印面单", "human"),
    ("insure", "保价", "human"),
    ("mail_query", "邮件查询", "system"),
    ("agency", "政务代办", "model"),
    ("postal_service", "邮务", "model"),
    ("customer_file", "建档", "system"),
    ("appointment", "预约", "system"),
    ("visit", "回访", "human"),
    ("day_end", "日终", "human"),
    ("trace", "操作留痕", "system"),
    ("speech_input", "语音输入", "system"),
    ("draft_export", "起草并导出", "model"),
)

P3_TOOLS = _tools(
    ("auth_inbox", "待我授权", "human"),
    ("auth_approve", "批准授权", "human"),
    ("roster", "岗位名册", "system"),
    ("on_duty", "排班与在岗", "system"),
    ("transfer_request", "调岗申请", "human"),
    ("handover_note", "交接单", "human"),
    ("takeover", "接管", "system"),
    ("resume", "断点续办", "system"),
    ("dispatch", "转派", "system"),
    ("new_session", "新建会话", "system"),
    ("trace", "操作留痕", "system"),
    ("report_counts", "岗位报表", "system"),
    ("speech_input", "语音输入", "system"),
    ("draft_export", "起草并导出", "model"),
)

P4_TOOLS = _tools(
    ("scan_access", "扫码接入", "device"),
    ("take_number", "叫号", "system"),
    ("appointment_lookup", "预约查询", "system"),
    ("divert", "客户分流", "system"),
    ("queue_board", "叫号管理", "system"),
    ("book", "预约登记", "system"),
    ("patrol", "巡检", "human"),
    ("precheck", "材料预检", "model"),
    ("print_slip", "打印凭条", "human"),
    ("evaluate", "评价器", "human"),
    ("transfer_counter", "转台席", "system"),
    ("new_session", "新建会话", "system"),
    ("takeover", "接管", "system"),
    ("resume", "断点续办", "system"),
    ("trace", "留痕", "system"),
    ("observe", "模型观测", "model"),
    ("speech_input", "语音输入", "system"),
    ("draft_export", "起草并导出", "model"),
)

P5_TOOLS = _tools(
    ("org_chart", "组织架构", "system"),
    ("post_template", "岗位模板", "system"),
    ("capability_list", "接口与能力", "system"),
    ("audit_log", "操作留痕", "system"),
    ("service_status", "服务状态", "system"),
    ("adjust_post", "调岗", "human"),
    ("set_param", "业务参数", "human"),
    ("break_glass", "破玻璃记录", "human"),
    ("speech_input", "语音输入", "system"),
)

ROLE_TOOLS = {
    "P1": P1_TOOLS,
    "P2": P2_TOOLS,
    "P3": P3_TOOLS,
    "P4": P4_TOOLS,
    "P5": P5_TOOLS,
}


def tools_for(role: str) -> tuple[Tool, ...]:
    return ROLE_TOOLS.get(role, ())


def all_tools() -> tuple[Tool, ...]:
    seen: dict[str, Tool] = {}
    for group in ROLE_TOOLS.values():
        for tool in group:
            seen.setdefault(tool.id, tool)
    return tuple(seen.values())

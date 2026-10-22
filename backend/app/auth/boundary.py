"""管理员这一轮的边界。处置入口可以出现，写入不落库，客户正文不返回。"""

VISIBLE_WRITES = ("adjust_post", "set_param", "break_glass")
WRITE_RESULT = "read_only"
CUSTOMER_BODY = False


def admin_effect(action: str) -> str:
    if action not in VISIBLE_WRITES:
        raise KeyError(action)
    return WRITE_RESULT


def customer_body_returned() -> bool:
    return CUSTOMER_BODY

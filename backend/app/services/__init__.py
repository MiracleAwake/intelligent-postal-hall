"""公有服务。按业务动作编排，不按岗位页复制。"""

from app.services.hall import HallDesk
from app.threshold import DEFAULT_THRESHOLD
from app.capabilities.units import load

load()

PUBLIC_ACTIONS = (
    "session",
    "intent",
    "retrieve",
    "notify",
    "audit",
    "staff_post_query",
    "material_list",
    "fill_fields",
    "print_option",
    "auth_request",
    "archive",
)

__all__ = ["DEFAULT_THRESHOLD", "HallDesk", "PUBLIC_ACTIONS"]

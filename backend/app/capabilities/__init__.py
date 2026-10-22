"""公有能力。导入时完成登记。"""

from app.capabilities.registry import REGISTRY, get, names
from app.capabilities.units import load

load()

__all__ = ["REGISTRY", "get", "names", "load"]

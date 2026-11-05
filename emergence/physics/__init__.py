from .base import REGISTRY, Physics, physics_from_dict, register
from .controls import NoiseControl, SmoothNoiseControl
from .lenia import Lenia
from .totalistic import OuterTotalistic

__all__ = ["REGISTRY", "Physics", "physics_from_dict", "register", "OuterTotalistic", "NoiseControl", "SmoothNoiseControl", "Lenia", "parse_rule"]


def parse_rule(rule: str) -> Physics:
    """Parse any rule label: B3/S23, B2/S/C3, LENIA/R13/T10/m0.150/s0.0150/b1."""
    if rule.strip().upper().startswith("LENIA/"):
        return Lenia.parse(rule)
    return OuterTotalistic.parse(rule)

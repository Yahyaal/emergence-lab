from .base import REGISTRY, Physics, physics_from_dict, register
from .controls import JitterControl, NoiseControl, SmoothNoiseControl
from .flow_lenia import FlowLenia, FlowLeniaPL
from .gray_scott import GrayScott, GrayScottTracer
from .lenia import Lenia
from .multi_lenia import MKernel, MultiLenia
from .totalistic import OuterTotalistic

__all__ = ["REGISTRY", "Physics", "physics_from_dict", "register", "OuterTotalistic", "NoiseControl", "SmoothNoiseControl", "JitterControl", "Lenia", "MultiLenia", "MKernel", "FlowLenia", "FlowLeniaPL", "GrayScott", "GrayScottTracer", "parse_rule"]


def parse_rule(rule: str) -> Physics:
    """Parse any rule label: B3/S23, B2/S/C3, LENIA/R13/T10/m0.150/s0.0150/b1,
    FLENIA/R13/m0.150/s0.0150/h1/r1/a0.5/b1/w0.15, GS/F0.0367/k0.0649, MLENIA/C2/R13/T10/k0>0,r1,m0.150,s0.0150,h1,b1+..."""
    if rule.strip().upper().startswith("GST/"):
        return GrayScottTracer.parse(rule)
    if rule.strip().upper().startswith("GS/"):
        return GrayScott.parse(rule)
    if rule.strip().upper().startswith("FLENIA-PL/"):
        return FlowLeniaPL.parse(rule)
    if rule.strip().upper().startswith("FLENIA/"):
        return FlowLenia.parse(rule)
    if rule.strip().upper().startswith("MLENIA/"):
        return MultiLenia.parse(rule)
    if rule.strip().upper().startswith("LENIA/"):
        return Lenia.parse(rule)
    return OuterTotalistic.parse(rule)

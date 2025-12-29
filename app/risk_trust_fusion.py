from __future__ import annotations
from dataclasses import dataclass

@dataclass
class FusionResult:
    adjusted_risk: float
    final_level: str   # "safe" | "suspicious" | "critical"
    action: str        # "ALLOW" | "STEP_UP_AUTH" | "DECOY"
    reason: str

def clamp(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, float(x)))

def level_from_score(score: float) -> str:
    if score <= 29:
        return "safe"
    if score <= 69:
        return "suspicious"
    return "critical"

def fuse(risk_score: float, trust_score: float, device_changed: bool = False) -> FusionResult:
    """
    Week 5: Risk–Trust Fusion Layer
    - Higher trust reduces adjusted risk
    - Lower trust increases adjusted risk
    - Device change + low trust escalates to CRITICAL (Decoy)
    """

    r = clamp(risk_score)
    t = clamp(trust_score)

    # Trust adjustment: trust 100 => -20 risk, trust 0 => +20 risk
    # (Simple, explainable mapping)
    trust_adjust = (50.0 - t) / 50.0 * 20.0  # t=50 => 0, t=100 => -20, t=0 => +20
    adjusted = clamp(r + trust_adjust)

    # Escalation rule used in your scrum notes:
    # if adjusted_risk >= 70 or (device_change and trust_score < 40): DECOY
    if adjusted >= 70 or (device_changed and t < 40):
        return FusionResult(
            adjusted_risk=adjusted,
            final_level="critical",
            action="DECOY",
            reason="critical_threshold_or_device_change_low_trust",
        )

    lvl = level_from_score(adjusted)
    if lvl == "suspicious":
        return FusionResult(
            adjusted_risk=adjusted,
            final_level="suspicious",
            action="STEP_UP_AUTH",
            reason="suspicious_adjusted_risk",
        )

    return FusionResult(
        adjusted_risk=adjusted,
        final_level="safe",
        action="ALLOW",
        reason="safe_adjusted_risk",
    )

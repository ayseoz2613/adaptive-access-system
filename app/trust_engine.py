from __future__ import annotations
from dataclasses import dataclass

@dataclass
class TrustResult:
    score: float
    delta: float
    reason: str

def clamp(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, float(x)))

def update_trust(
    current: float,
    success: bool,
    ip_changed: bool = False,
    device_changed: bool = False,
    risk_level: str = "safe",
) -> TrustResult:
    """
    Trust score update (Week 5).
    Simple, explainable rules:
      - successful safe login increases trust slightly
      - anomalies decrease trust
      - suspicious/critical decreases more
    Score range: 0..100
    """
    cur = clamp(current if current is not None else 50.0)

    delta = 0.0
    reason_parts = []

    if success:
        delta += 2.0
        reason_parts.append("success")

        if ip_changed:
            delta -= 6.0
            reason_parts.append("ip_changed")

        if device_changed:
            delta -= 8.0
            reason_parts.append("device_changed")

        lvl = (risk_level or "safe").lower()
        if lvl == "suspicious":
            delta -= 6.0
            reason_parts.append("risk=suspicious")
        elif lvl == "critical":
            delta -= 12.0
            reason_parts.append("risk=critical")

    else:
        # failed login attempts reduce trust
        delta -= 10.0
        reason_parts.append("failed_login")

    new_score = clamp(cur + delta)
    reason = ", ".join(reason_parts) if reason_parts else "no_change"
    return TrustResult(score=new_score, delta=delta, reason=reason)

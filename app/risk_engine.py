"""Rule-based risk scoring (Week 3).

Goal: a working, explainable baseline that can be extended later.
Signals used (available today):
 - IP address
 - User-Agent
 - Login time (hour-of-day)
 - Recent failed attempts counter (User.failed_login_attempts)

Output:
 - risk_score: 0..100
 - risk_level: safe | suspicious | critical
 - reasons: list[str] (stored in DB for debugging/UI)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List

from .models import LoginAttempt, User


@dataclass
class RiskResult:
    score: float
    level: str
    reasons: List[str]


def _level_from_score(score: float) -> str:
    # Thresholds:
    # 0-29  -> safe
    # 30-69 -> suspicious
    # 70+   -> critical
    if score >= 70:
        return "critical"
    if score >= 30:
        return "suspicious"
    return "safe"


def evaluate_login_risk(
    user: User,
    ip_address: str | None,
    user_agent: str | None,
    now: datetime,
    recent_days: int = 30,
    recent_limit: int = 20,
) -> RiskResult:
    score = 0.0
    reasons: List[str] = []

    cutoff = now - timedelta(days=recent_days)
    recent_success = (
        LoginAttempt.query
        .filter(
            LoginAttempt.user_id == user.id,
            LoginAttempt.success.is_(True),
            LoginAttempt.timestamp >= cutoff,
        )
        .order_by(LoginAttempt.timestamp.desc())
        .limit(recent_limit)
        .all()
    )

    known_ips = {la.ip_address for la in recent_success if la.ip_address}
    known_agents = {la.user_agent for la in recent_success if la.user_agent}

    # IP novelty
    if ip_address:
        if known_ips and ip_address not in known_ips:
            score += 40
            reasons.append("New IP address detected")
        elif not known_ips:
            score += 5
            reasons.append("No historical IP data yet")
    else:
        score += 10
        reasons.append("IP address missing")

    # User-Agent novelty
    if user_agent:
        if known_agents and user_agent not in known_agents:
            score += 20
            reasons.append("New device/browser (User-Agent) detected")
        elif not known_agents:
            score += 5
            reasons.append("No historical device data yet")
    else:
        score += 10
        reasons.append("User-Agent missing")

    # Login time anomaly
    hours = [la.timestamp.hour for la in recent_success if la.timestamp]
    if len(hours) >= 5:
        avg_hour = sum(hours) / len(hours)
        dist = min(abs(now.hour - avg_hour), 24 - abs(now.hour - avg_hour))
        if dist >= 6:
            score += 15
            reasons.append("Unusual login time")
    else:
        score += 3
        reasons.append("Not enough historical time data")

    # Failed attempts signal
    if user.failed_login_attempts >= 3:
        score += 15
        reasons.append("Multiple recent failed login attempts")

    score = max(0.0, min(100.0, score))
    level = _level_from_score(score)
    return RiskResult(score=score, level=level, reasons=reasons)

# app/risk_contract.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any, List


# --- Risk thresholds (backend sabitleri) ---
RISK_SAFE_MAX = 29.99
RISK_SUSPICIOUS_MAX = 69.99
# 70+ => CRITICAL


@dataclass(frozen=True)
class RiskDecision:
    # Backend contract: FE'nin okuyacağı tek standart blok
    level: str              # SAFE | SUSPICIOUS | CRITICAL
    ui_state: str           # normal | warning | decoy | locked
    alert_type: Optional[str]   # None | MFA_REQUIRED | WARNING | DECOY | ACCOUNT_LOCKED | EMERGENCY_LOCK
    message_key: str        # i18n key gibi düşün (frontend isterse map'ler)
    action: str             # ALLOW | STEP_UP_AUTH | DECOY | BLOCK
    http_hint: int          # 200 / 401 / 423 / 403 gibi FE için ipucu


def normalize_level(level: str) -> str:
    lvl = (level or "").strip().lower()
    if lvl in ("safe", "normal"):
        return "SAFE"
    if lvl in ("suspicious", "warning"):
        return "SUSPICIOUS"
    if lvl in ("critical", "decoy", "high"):
        return "CRITICAL"
    # bilinmiyorsa safe'e düş
    return "SAFE"


def level_from_score(score: float) -> str:
    try:
        s = float(score)
    except Exception:
        s = 0.0

    if s <= RISK_SAFE_MAX:
        return "SAFE"
    if s <= RISK_SUSPICIOUS_MAX:
        return "SUSPICIOUS"
    return "CRITICAL"


def build_risk_decision(
    *,
    risk_score: float,
    risk_level: Optional[str] = None,
    require_mfa: bool = False,
    account_locked: bool = False,
    emergency_locked: bool = False,
) -> RiskDecision:
    """
    Ayşe Week3+Week4: Risk State Mapping + API Contract + Alert Payload + UI Support Fields
    Tek bir fonksiyon: FE sözleşmesi burada.
    """
    level = normalize_level(risk_level) if risk_level else level_from_score(risk_score)

    if emergency_locked:
        return RiskDecision(
            level="CRITICAL",
            ui_state="locked",
            alert_type="EMERGENCY_LOCK",
            message_key="auth.emergency_lock.active",
            action="BLOCK",
            http_hint=403,
        )

    if account_locked:
        return RiskDecision(
            level="CRITICAL",
            ui_state="locked",
            alert_type="ACCOUNT_LOCKED",
            message_key="auth.account_locked",
            action="BLOCK",
            http_hint=423,
        )

    if level == "SAFE":
        return RiskDecision(
            level="SAFE",
            ui_state="normal",
            alert_type=None,
            message_key="auth.risk.safe",
            action="ALLOW",
            http_hint=200,
        )

    if level == "SUSPICIOUS":
        # mapping: suspicious => MFA / warning
        if require_mfa:
            return RiskDecision(
                level="SUSPICIOUS",
                ui_state="warning",
                alert_type="MFA_REQUIRED",
                message_key="auth.risk.suspicious.mfa_required",
                action="STEP_UP_AUTH",
                http_hint=200,
            )

        return RiskDecision(
            level="SUSPICIOUS",
            ui_state="warning",
            alert_type="WARNING",
            message_key="auth.risk.suspicious",
            action="ALLOW",
            http_hint=200,
        )

    # CRITICAL => decoy
    return RiskDecision(
        level="CRITICAL",
        ui_state="decoy",
        alert_type="DECOY",
        message_key="auth.risk.critical",
        action="DECOY",
        http_hint=200,
    )


def contract_payload(
    *,
    risk_score: float,
    risk_level: str,
    risk_reasons: Optional[str] = None,
    require_mfa: bool = False,
    account_locked: bool = False,
    emergency_locked: bool = False,
) -> Dict[str, Any]:
    """
    FE standard JSON block.
    """
    decision = build_risk_decision(
        risk_score=risk_score,
        risk_level=risk_level,
        require_mfa=require_mfa,
        account_locked=account_locked,
        emergency_locked=emergency_locked,
    )

    return {
        "risk": {
            "score": float(risk_score),
            "level": decision.level,               # SAFE | SUSPICIOUS | CRITICAL
            "reasons": risk_reasons or "",
        },
        "ui": {
            "state": decision.ui_state,            # normal | warning | decoy | locked
            "alert_type": decision.alert_type,     # e.g. MFA_REQUIRED
            "message_key": decision.message_key,   # e.g. auth.risk.suspicious
            "action": decision.action,             # ALLOW | STEP_UP_AUTH | DECOY | BLOCK
            "http_hint": decision.http_hint,
        },
        # Geriye dönük uyumluluk isteyenler için (istersen sonra kaldırırız):
        "risk_level": decision.level.lower(),
        "risk_score": float(risk_score),
        "ui_state": decision.ui_state,
    }

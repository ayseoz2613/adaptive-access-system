from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, List

from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)

from . import db
from .models import User, LoginAttempt

auth_bp = Blueprint("auth", __name__)

# -----------------------------
# Helpers: time, responses
# -----------------------------
def utcnow() -> datetime:
    # DB ile uyum için naive UTC
    return datetime.now(timezone.utc).replace(tzinfo=None)


def ok(data: dict, status: int = 200):
    return jsonify({"ok": True, "data": data}), status


def err(
    code: str,
    message: str,
    status: int = 400,
    *,
    message_key: str = "error.generic",
    details: Optional[dict] = None,
):
    payload = {
        "ok": False,
        "error": {
            "code": code,
            "message": message,
            "message_key": message_key,
        },
    }
    if details:
        payload["error"]["details"] = details
    return jsonify(payload), status


# -----------------------------
# Risk thresholds + UI contract
# -----------------------------
RISK_THRESHOLDS = {
    "SAFE_MAX": 29,
    "SUSPICIOUS_MAX": 69,  # 30-69 suspicious
    # >=70 critical
}

UI_STATE_BY_RISK = {
    "safe": "normal",
    "suspicious": "mfa",
    "critical": "decoy",
}

ALERT_BY_RISK = {
    "safe": ("none", "auth.safe"),
    "suspicious": ("warning", "auth.suspicious"),
    "critical": ("danger", "auth.critical"),
}

# Progressive lock policy (failed_login_attempts hits N -> lock seconds)
LOCK_SCHEDULE = {
    3: 30,
    5: 120,
    7: 86400,
}


def risk_level_from_score(score: float) -> str:
    if score <= RISK_THRESHOLDS["SAFE_MAX"]:
        return "safe"
    if score <= RISK_THRESHOLDS["SUSPICIOUS_MAX"]:
        return "suspicious"
    return "critical"


def is_temporarily_locked(user: User) -> bool:
    return bool(user.locked_until and user.locked_until > utcnow())


def remaining_lock_seconds(user: User) -> int:
    if not user.locked_until:
        return 0
    return max(0, int((user.locked_until - utcnow()).total_seconds()))


def make_tokens(user: User) -> dict:
    claims = {"tv": int(user.token_version or 0), "email": user.email}
    access = create_access_token(identity=str(user.id), additional_claims=claims)
    refresh = create_refresh_token(
        identity=str(user.id),
        additional_claims={"tv": int(user.token_version or 0), "type": "refresh"},
    )
    return {"access_token": access, "refresh_token": refresh, "token_type": "Bearer"}


def ensure_session_valid(user: User, jwt_claims: dict):
    if bool(user.is_locked):
        return err("ACCOUNT_LOCKED", "Account is locked.", 423, message_key="auth.locked")

    if is_temporarily_locked(user):
        return err(
            "TEMP_LOCKED",
            "Account temporarily locked.",
            423,
            message_key="auth.temp_locked",
            details={
                "locked_until": user.locked_until.isoformat() if user.locked_until else None,
                "remaining_seconds": remaining_lock_seconds(user),
            },
        )

    token_tv = jwt_claims.get("tv")
    if token_tv is None or int(token_tv) != int(user.token_version or 0):
        return err(
            "SESSION_INVALID",
            "Session invalidated. Please login again.",
            401,
            message_key="auth.session_invalid",
        )

    return None


# -----------------------------
# Risk scoring (Week 3/5)
# Compare with last successful login attempt
# -----------------------------
def compute_risk_from_last_success(
    user: User,
    ip: str,
    user_agent: str,
    device_info: str,
    location: str,
) -> Tuple[float, str, str]:
    """
    Basit kural tabanlı risk (if/else).
    Son başarılı girişle kıyas:
      - IP değişimi
      - User-Agent değişimi
      - Device değişimi
      - Location değişimi
    """
    risk_score = 0.0
    reasons: List[str] = []

    last_ok = (
        LoginAttempt.query
        .filter_by(user_id=user.id, success=True)
        .order_by(LoginAttempt.id.desc())
        .first()
    )

    if last_ok:
        if last_ok.ip_address and ip and last_ok.ip_address != ip:
            risk_score += 30
            reasons.append("IP changed")

        if last_ok.user_agent and user_agent and last_ok.user_agent != user_agent:
            risk_score += 25
            reasons.append("User-Agent changed")

        if last_ok.device_info and device_info and last_ok.device_info != device_info:
            risk_score += 25
            reasons.append("Device changed")

        if last_ok.location and location and last_ok.location != location:
            risk_score += 20
            reasons.append("Location changed")
    else:
        # ilk başarılı login: çok düşük baseline
        risk_score += 3
        reasons.append("First successful login baseline")

    level = risk_level_from_score(risk_score)
    risk_reasons = "; ".join(reasons) if reasons else None
    return risk_score, level, (risk_reasons or "No notable risk signals")


# -----------------------------
# Routes
# -----------------------------
@auth_bp.post("/register")
def register():
    body = request.get_json(silent=True) or {}
    email = (body.get("email") or "").strip().lower()
    password = body.get("password") or ""

    if not email or "@" not in email:
        return err("VALIDATION", "Geçerli bir email giriniz.", 400, message_key="auth.invalid_email")
    if len(password) < 8:
        return err("VALIDATION", "Şifre en az 8 karakter olmalıdır.", 400, message_key="auth.weak_password")

    existing = User.query.filter_by(email=email).first()
    if existing:
        # enumeration engellemek için tek tip mesaj
        return err("REGISTER_DENIED", "Bu email ile kayıt yapılamıyor.", 400, message_key="auth.register_denied")

    user = User(email=email)
    user.set_password(password)
    user.is_active = True
    user.failed_login_attempts = 0
    user.locked_until = None
    user.is_locked = False
    user.token_version = 0

    db.session.add(user)
    db.session.commit()

    return ok({"message": "Kayıt başarılı.", "message_key": "auth.register_ok"}, 201)


@auth_bp.post("/login")
def login():
    body = request.get_json(silent=True) or {}
    email = (body.get("email") or "").strip().lower()
    password = body.get("password") or ""

    # --- client context ---
    user_agent = request.headers.get("User-Agent", "") or ""
    ip = (request.headers.get("X-Forwarded-For") or request.remote_addr or "unknown").split(",")[0].strip()

    device_info = (body.get("device_info") or "").strip() or user_agent
    location = (body.get("location") or "").strip()

    generic_fail = err(
        "INVALID_CREDENTIALS",
        "Kullanıcı adı veya şifre hatalı.",
        401,
        message_key="auth.invalid_credentials",
    )

    if not email or not password:
        return generic_fail

    user = User.query.filter_by(email=email).first()
    if not user:
        return generic_fail

    # Permanent emergency lock
    if bool(user.is_locked):
        return err("ACCOUNT_LOCKED", "Account is locked.", 423, message_key="auth.locked")

    # Temporary lock window: attempts should NOT increase (your desired behavior)
    if is_temporarily_locked(user):
        return err(
            "TEMP_LOCKED",
            "Account temporarily locked.",
            423,
            message_key="auth.temp_locked",
            details={
                "locked_until": user.locked_until.isoformat() if user.locked_until else None,
                "remaining_seconds": remaining_lock_seconds(user),
            },
        )

    # -------------------------
    # Wrong password
    # -------------------------
    if not user.check_password(password):
        user.failed_login_attempts = int(user.failed_login_attempts or 0) + 1
        fails = int(user.failed_login_attempts or 0)

        # default attempt fields for wrong password
        attempt = LoginAttempt(
            user_id=user.id,
            ip_address=ip,
            user_agent=user_agent,
            device_info=device_info,
            location=location or None,
            success=False,
            risk_score=0.0,
            risk_level="safe",
            risk_reasons="Invalid credentials",
        )

        lock_seconds = LOCK_SCHEDULE.get(fails)
        if lock_seconds:
            user.locked_until = utcnow() + timedelta(seconds=lock_seconds)

            # escalate risk on brute-force thresholds
            attempt.risk_score = 60.0 if lock_seconds < 86400 else 90.0
            attempt.risk_level = "suspicious" if lock_seconds < 86400 else "critical"
            attempt.risk_reasons = f"Brute-force threshold reached ({fails}); lock {lock_seconds}s"

        db.session.add(attempt)
        db.session.commit()

        if lock_seconds:
            return err(
                "TEMP_LOCKED",
                "Account temporarily locked.",
                423,
                message_key="auth.temp_locked",
                details={
                    "locked_until": user.locked_until.isoformat() if user.locked_until else None,
                    "remaining_seconds": remaining_lock_seconds(user),
                },
            )

        return generic_fail

    # -------------------------
    # Correct password
    # -------------------------
    # reset counters
    user.failed_login_attempts = 0
    user.locked_until = None

    # IMPORTANT: defaults (always defined)
    risk_score = 0.0
    risk_level = "safe"
    ui_state = "normal"
    alert_type = "none"
    message_key = "auth.safe"
    risk_reasons = None

    # compute risk BEFORE creating attempt
    risk_score, risk_level, risk_reasons = compute_risk_from_last_success(
        user=user,
        ip=ip,
        user_agent=user_agent,
        device_info=device_info,
        location=location,
    )
    ui_state = UI_STATE_BY_RISK[risk_level]
    alert_type, message_key = ALERT_BY_RISK[risk_level]

    # persist successful attempt
    attempt = LoginAttempt(
        user_id=user.id,
        ip_address=ip,
        user_agent=user_agent,
        device_info=device_info,
        location=location or None,
        success=True,
        risk_score=float(risk_score),
        risk_level=risk_level,
        risk_reasons=risk_reasons,
    )
    db.session.add(attempt)

    # update user baseline
    user.last_login_at = utcnow()

    # CRITICAL: decoy -> no tokens
    if risk_level == "critical":
        db.session.commit()
        return ok(
            {
                "risk_level": risk_level,
                "risk_score": float(risk_score),
                "ui_state": ui_state,
                "alert_type": alert_type,
                "message_key": message_key,
            },
            200,
        )

    # SAFE/SUSPICIOUS: issue tokens
    tokens = make_tokens(user)
    db.session.commit()

    return ok(
        {
            **tokens,
            "risk_level": risk_level,
            "risk_score": float(risk_score),
            "ui_state": ui_state,
            "alert_type": alert_type,
            "message_key": message_key,
        },
        200,
    )


@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()
    claims = get_jwt()
    user = User.query.get(int(user_id)) if user_id else None
    if not user:
        return err("UNAUTHORIZED", "Unauthorized.", 401, message_key="auth.unauthorized")

    invalid = ensure_session_valid(user, claims)
    if invalid:
        return invalid

    return ok(
        {
            "id": user.id,
            "email": user.email,
            "is_active": bool(user.is_active),
            "is_locked": bool(user.is_locked),
            "locked_until": user.locked_until.isoformat() if user.locked_until else None,
            "token_version": int(user.token_version or 0),
        }
    )


@auth_bp.post("/emergency-lock")
@jwt_required()
def emergency_lock():
    user_id = get_jwt_identity()
    claims = get_jwt()
    user = User.query.get(int(user_id)) if user_id else None
    if not user:
        return err("UNAUTHORIZED", "Unauthorized.", 401, message_key="auth.unauthorized")

    invalid = ensure_session_valid(user, claims)
    if invalid:
        return invalid

    user.is_locked = True
    user.token_version = int(user.token_version or 0) + 1
    user.locked_until = None

    db.session.commit()
    return ok(
        {
            "message": "Emergency lock activated.",
            "message_key": "auth.emergency_lock_ok",
            "is_locked": True,
            "token_version": int(user.token_version or 0),
        }
    )


@auth_bp.post("/unlock")
def unlock_account():
    """
    Admin unlock (Week 5 opsiyonel):
      Header: X-ADMIN-UNLOCK-KEY: <Config.ADMIN_UNLOCK_KEY>
      Body: {"email": "..."}
    """
    admin_key_cfg = current_app.config.get("ADMIN_UNLOCK_KEY")
    admin_key = request.headers.get("X-ADMIN-UNLOCK-KEY")

    if not (admin_key_cfg and admin_key and admin_key == admin_key_cfg):
        return err("UNAUTHORIZED", "Admin key required.", 401, message_key="auth.unlock_admin_key_required")

    body = request.get_json(silent=True) or {}
    email = (body.get("email") or "").strip().lower()
    if not email:
        return err("VALIDATION", "email required.", 400, message_key="auth.unlock_validation")

    user = User.query.filter_by(email=email).first()
    if not user:
        return err("NOT_FOUND", "User not found.", 404, message_key="auth.user_not_found")

    user.is_locked = False
    user.locked_until = None
    user.failed_login_attempts = 0
    user.token_version = int(user.token_version or 0) + 1  # eski tokenları invalid et

    db.session.commit()
    return ok(
        {
            "message": "Account unlocked.",
            "message_key": "auth.unlock_ok",
            "email": user.email,
            "token_version": int(user.token_version or 0),
        }
    )

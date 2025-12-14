import os
from flask import Blueprint, request, jsonify
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

from . import db
from .models import User, LoginAttempt
from .risk_engine import evaluate_login_risk
from .auth_utils import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_token_from_header,
)

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    data = request.get_json() or {}

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email ve şifre zorunludur."}), 400

    if "@" not in email:
        return jsonify({"error": "Geçerli bir email giriniz."}), 400

    if len(password) < 8:
        return jsonify({"error": "Şifre en az 8 karakter olmalıdır."}), 400

    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({"error": "Bu email ile kayıt yapılamıyor."}), 400

    user = User(email=email)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Kayıt başarılı."}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email ve şifre zorunludur."}), 400

    user = User.query.filter_by(email=email).first()
    invalid_msg = {"error": "Kullanıcı adı veya şifre hatalı."}

    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    user_agent = request.headers.get("User-Agent", "")
    device_info = ""

    now = datetime.utcnow()

    login_attempt = LoginAttempt(
        user_id=user.id if user else None,
        ip_address=ip,
        user_agent=user_agent,
        device_info=device_info,
        timestamp=now,
    )

    # ❌ Wrong credentials
    if not user or not user.check_password(password):
        login_attempt.success = False
        login_attempt.risk_score = 0.0
        login_attempt.risk_level = "safe"
        login_attempt.risk_reasons = "Invalid credentials"

        db.session.add(login_attempt)

        if user:
            user.failed_login_attempts += 1

            # ✅ Week 5: basic brute-force protection (>=5 failed attempts => lock)
            if user.failed_login_attempts >= 5:
                user.is_locked = True
                user.token_version = int(user.token_version or 0) + 1
                login_attempt.risk_score = 100.0
                login_attempt.risk_level = "critical"
                login_attempt.risk_reasons = "Brute-force protection triggered (>=5 failed attempts)"

        db.session.commit()
        return jsonify(invalid_msg), 401

    # 🔒 Week 4: Emergency Lock - account locked check
    if user.is_locked:
        login_attempt.success = False
        login_attempt.risk_score = 100.0
        login_attempt.risk_level = "critical"
        login_attempt.risk_reasons = "Account is locked (Emergency Lock active)"

        db.session.add(login_attempt)
        db.session.commit()

        return jsonify({"error": "Account is locked. Emergency Lock is active."}), 403

    # ✅ Week 3: Risk calculation
    risk = evaluate_login_risk(
        user=user,
        ip_address=ip,
        user_agent=user_agent,
        now=now
    )

    # ✅ Update user login state
    user.failed_login_attempts = 0
    user.last_login_at = now

    # ✅ Store success + risk info into LoginAttempt
    login_attempt.success = True
    login_attempt.risk_score = float(risk.score)
    login_attempt.risk_level = risk.level
    login_attempt.risk_reasons = "; ".join(risk.reasons)

    db.session.add(login_attempt)

    # ✅ UI state mapping for frontend
    ui_state = "normal"
    if risk.level == "suspicious":
        ui_state = "mfa"
    elif risk.level == "critical":
        ui_state = "decoy"

    # ✅ Week 4: token_version claim for session invalidation
    access_token = create_access_token({
        "sub": user.id,
        "email": user.email,
        "tv": int(user.token_version or 0)
    })
    refresh_token = create_refresh_token({
        "sub": user.id,
        "tv": int(user.token_version or 0)
    })

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Sunucu hatası."}), 500

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "risk_score": float(risk.score),
        "risk_level": risk.level,
        "ui_state": ui_state
    }), 200


@auth_bp.get("/me")
def me():
    token = get_token_from_header()
    if not token:
        return jsonify({"error": "Yetkisiz erişim (token yok)."}), 401

    decoded = decode_token(token)
    if not decoded:
        return jsonify({"error": "Geçersiz veya süresi dolmuş token."}), 401

    user_id = decoded.get("sub")
    user = User.query.get(user_id)
    if not user or not user.is_active:
        return jsonify({"error": "Kullanıcı bulunamadı veya pasif."}), 401

    # ✅ Week 4: token invalidation (tv must match)
    token_version = decoded.get("tv")
    if token_version is None or int(token_version) != int(user.token_version or 0):
        return jsonify({"error": "Session is no longer valid (token invalidated)."}), 401

    # ✅ Week 4: account locked check
    if user.is_locked:
        return jsonify({"error": "Account is locked. Emergency Lock is active."}), 403

    return jsonify({
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at.isoformat(),
        "trust_score": user.trust_score,
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None
    }), 200


@auth_bp.post("/emergency-lock")
def emergency_lock():
    token = get_token_from_header()
    if not token:
        return jsonify({"error": "Unauthorized (missing token)."}), 401

    decoded = decode_token(token)
    if not decoded:
        return jsonify({"error": "Invalid or expired token."}), 401

    user_id = decoded.get("sub")
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404

    # 🔒 Lock account + invalidate existing sessions
    user.is_locked = True
    user.token_version = int(user.token_version or 0) + 1

    db.session.commit()

    return jsonify({"message": "Emergency Lock activated. Sessions invalidated."}), 200


@auth_bp.post("/unlock")
def unlock_account():
    """
    Week 5 helper: unlock account for demo/testing.
    Two modes:
      1) Admin key unlock (recommended for demos when user is locked and cannot login):
         - Header: X-Admin-Key: <ADMIN_UNLOCK_KEY>
         - Body: { "email": "user@example.com" }
      2) Self unlock (needs valid token, useful before lock):
         - Authorization: Bearer <token>
    """

    # --- Mode 1: Admin key unlock ---
    admin_key = request.headers.get("X-Admin-Key")
    env_admin_key = os.getenv("ADMIN_UNLOCK_KEY")

    if env_admin_key and admin_key and admin_key == env_admin_key:
        data = request.get_json() or {}
        email = (data.get("email") or "").strip().lower()
        if not email:
            return jsonify({"error": "Email is required for admin unlock."}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "User not found."}), 404

        user.is_locked = False
        user.failed_login_attempts = 0
        user.token_version = int(user.token_version or 0) + 1  # invalidate old tokens

        db.session.commit()
        return jsonify({"message": "Account unlocked (admin). Sessions invalidated."}), 200

    # --- Mode 2: Self unlock (token required) ---
    token = get_token_from_header()
    if not token:
        return jsonify({"error": "Unauthorized (missing token)."}), 401

    decoded = decode_token(token)
    if not decoded:
        return jsonify({"error": "Invalid or expired token."}), 401

    user_id = decoded.get("sub")
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404

    user.is_locked = False
    user.failed_login_attempts = 0
    user.token_version = int(user.token_version or 0) + 1

    db.session.commit()
    return jsonify({"message": "Account unlocked. Sessions invalidated."}), 200

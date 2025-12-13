# app/auth_routes.py
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError

from . import db
from .models import User, LoginAttempt
from .auth_utils import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_token_from_header,
)

from .risk_data import RiskDataPacket
from .risk_engine import calculate_risk, calculate_trust, decide_action
from .mfa_otp import set_user_otp, verify_user_otp

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

    # Request bilgileri
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    user_agent = request.headers.get("User-Agent", "")
    device_info = user_agent

    # Attempt kaydı (user yoksa user_id None kalır)
    login_attempt = LoginAttempt(
        user_id=user.id if user else None,
        ip_address=ip,
        user_agent=user_agent,
        device_info=device_info,
        timestamp=datetime.utcnow(),
    )

    # Yanlış kullanıcı/şifre
    if not user or not user.check_password(password):
        login_attempt.success = False
        login_attempt.risk_score = 0.0
        login_attempt.risk_level = "safe"

        db.session.add(login_attempt)
        if user:
            user.failed_login_attempts += 1
        db.session.commit()

        return jsonify(invalid_msg), 401

    # ====== Risk packet + history ======
    packet = RiskDataPacket.from_request(user_id=user.id)

    ten_min_ago = datetime.utcnow() - timedelta(minutes=10)

    known_ips = {
        r[0] for r in db.session.query(LoginAttempt.ip_address)
        .filter(LoginAttempt.user_id == user.id, LoginAttempt.success == True)
        .distinct().all()
        if r[0]
    }
    known_devices = {
        r[0] for r in db.session.query(LoginAttempt.device_info)
        .filter(LoginAttempt.user_id == user.id, LoginAttempt.success == True)
        .distinct().all()
        if r[0]
    }
    failed_last_10min = LoginAttempt.query.filter(
        LoginAttempt.user_id == user.id,
        LoginAttempt.success == False,
        LoginAttempt.timestamp >= ten_min_ago
    ).count()

    history = {
        "known_ips": known_ips,
        "known_devices": known_devices,
        "failed_last_10min": failed_last_10min
    }

    risk, reasons = calculate_risk(packet, history)
    trust_now = float(user.trust_score or 0.0)
    action, risk_level = decide_action(risk, trust_now)

    # başarılı login metrikleri
    user.failed_login_attempts = 0
    user.last_login_at = datetime.utcnow()

    login_attempt.success = True
    login_attempt.risk_score = float(risk)
    login_attempt.risk_level = risk_level
    login_attempt.ip_address = packet.ip_address
    login_attempt.device_info = packet.device_info

    db.session.add(login_attempt)

    # Trust update (başarılı giriş sonrası)
    user.trust_score = calculate_trust(user.trust_score, risk, success=True)

    # ====== Action handling ======
    try:
        # SAFE -> token ver
        if action == "SAFE":
            access_token = create_access_token({"sub": user.id, "email": user.email})
            refresh_token = create_refresh_token({"sub": user.id})

            db.session.commit()
            return jsonify({
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "Bearer",
                "risk_score": risk,
                "risk_level": risk_level,
                "risk_action": action,
                "risk_reasons": reasons,
                "trust_score": user.trust_score
            }), 200

        # MFA -> OTP üret (demo için response'a otp koyuyoruz)
        if action == "MFA":
            otp = set_user_otp(user)
            db.session.commit()
            return jsonify({
                "message": "Multi-factor authentication required",
                "require_mfa": True,
                "dev_otp": otp,  # demo amaçlı (prod'da kaldırılır)
                "risk_score": risk,
                "risk_level": risk_level,
                "risk_action": action,
                "risk_reasons": reasons,
                "trust_score": user.trust_score
            }), 200

        # DECOY -> token yok, fake response
        db.session.commit()
        return jsonify({
            "decoy": True,
            "message": "Welcome",
            "fake_dashboard": {
                "balance": "₺12.450",
                "last_login": user.last_login_at.isoformat() if user.last_login_at else None
            },
            "risk_score": risk,
            "risk_level": risk_level,
            "risk_action": action,
            "risk_reasons": reasons,
            "trust_score": user.trust_score
        }), 200

    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Sunucu hatası."}), 500


@auth_bp.post("/mfa/request")
def mfa_request():
    """
    İsteğe bağlı endpoint: email ile OTP üretir.
    Demo amaçlı OTP response'a döndürülür.
    """
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()

    if not email:
        return jsonify({"error": "Email zorunludur."}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    otp = set_user_otp(user)
    db.session.commit()

    return jsonify({"message": "OTP generated", "dev_otp": otp}), 200


@auth_bp.post("/mfa/verify")
def mfa_verify():
    """
    OTP doğrulama başarılıysa token üretir.
    """
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    code = (data.get("code") or "").strip()

    if not email or not code:
        return jsonify({"error": "Email ve code zorunludur."}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not verify_user_otp(user, code):
        return jsonify({"error": "Invalid or expired OTP"}), 401

    user.mfa_pending = False
    db.session.commit()

    access_token = create_access_token({"sub": user.id, "email": user.email})
    refresh_token = create_refresh_token({"sub": user.id})

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer"
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

    return jsonify({
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at.isoformat(),
        "trust_score": user.trust_score,
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None
    }), 200

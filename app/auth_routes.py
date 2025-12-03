from flask import Blueprint, request, jsonify
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

from . import db
from .models import User, LoginAttempt
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

    login_attempt = LoginAttempt(
        user_id=user.id if user else None,
        ip_address=ip,
        user_agent=user_agent,
        device_info=device_info,
        timestamp=datetime.utcnow(),
    )

    if not user or not user.check_password(password):
        login_attempt.success = False
        login_attempt.risk_score = 0.0
        login_attempt.risk_level = "safe"

        db.session.add(login_attempt)
        if user:
            user.failed_login_attempts += 1
        db.session.commit()

        return jsonify(invalid_msg), 401

    # başarılı login
    user.failed_login_attempts = 0
    user.last_login_at = datetime.utcnow()

    login_attempt.success = True
    login_attempt.risk_score = 0.0
    login_attempt.risk_level = "safe"

    db.session.add(login_attempt)

    access_token = create_access_token({"sub": user.id, "email": user.email})
    refresh_token = create_refresh_token({"sub": user.id})

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Sunucu hatası."}), 500

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

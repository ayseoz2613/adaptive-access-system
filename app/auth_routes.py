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
from .lock_utils import check_account_lock, apply_progressive_lock, get_lock_status_message
from .risk_data import RiskDataPacket
from .mfa_utils import should_require_mfa, update_user_device_info
from .error_handlers import (
    error_response,
    invalid_credentials,
    account_locked,
    too_many_attempts,
    mfa_required,
)

auth_bp = Blueprint("auth", __name__)

@auth_bp.post("/register")
def register():
    """
    Kullanıcı kayıt endpoint'i.
    """
    data = request.get_json() or {}

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return error_response(400, "Email ve şifre zorunludur.")

    if "@" not in email:
        return error_response(400, "Geçerli bir email giriniz.")

    if len(password) < 8:
        return error_response(400, "Şifre en az 8 karakter olmalıdır.")

    existing = User.query.filter_by(email=email).first()
    if existing:
        return error_response(409, "Bu email ile kayıt yapılamıyor.")

    user = User(email=email)
    user.set_password(password)

    try:
        db.session.add(user)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return error_response(500, "Sunucu hatası.")

    return jsonify({"message": "Kayıt başarılı."}), 201


@auth_bp.post("/login")
def login():
    """
    Kullanıcı giriş endpoint'i.
    
    Özellikler:
    - Progressive lock kontrolü
    - MFA tetikleme kontrolü
    - RiskDataPacket oluşturma
    - Standart error handling
    """
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return error_response(400, "Email ve şifre zorunludur.")

    user = User.query.filter_by(email=email).first()
    
    # RiskDataPacket oluştur
    risk_packet = RiskDataPacket.from_request(
        user_id=user.id if user else None
    )

    # Progressive lock kontrolü (kullanıcı varsa)
    if user:
        lock_check = check_account_lock(user)
        if lock_check:
            error_resp, status_code = lock_check
            # Kilit durumunu veritabanına kaydet
            try:
                db.session.commit()
            except SQLAlchemyError:
                db.session.rollback()
            return jsonify(error_resp), status_code

    # Login attempt kaydı oluştur
    login_attempt = LoginAttempt(
        user_id=user.id if user else None,
        ip_address=risk_packet.ip_address,
        user_agent=risk_packet.device_info,
        device_info=risk_packet.device_info,
        location=risk_packet.location,
        timestamp=risk_packet.login_time,
    )

    # Şifre kontrolü
    if not user or not user.check_password(password):
        login_attempt.success = False
        login_attempt.risk_score = 0.0
        login_attempt.risk_level = "safe"

        db.session.add(login_attempt)
        
        if user:
            user.failed_login_attempts += 1
            # Progressive lock uygula
            locked_until = apply_progressive_lock(user)
            
            # Hatalı giriş sayısına göre uygun hata mesajı döndür
            failed_count = user.failed_login_attempts
            
            try:
                db.session.commit()
            except SQLAlchemyError:
                db.session.rollback()
                return error_response(500, "Sunucu hatası.")
            
            # Progressive lock uygulandıysa uygun hata kodu döndür
            if locked_until:
                if failed_count >= 7:
                    return account_locked(
                        locked_until.isoformat(),
                        int((locked_until - datetime.utcnow()).total_seconds())
                    )
                elif failed_count >= 5:
                    return account_locked(
                        locked_until.isoformat(),
                        int((locked_until - datetime.utcnow()).total_seconds())
                    )
                elif failed_count >= 3:
                    return too_many_attempts(30)
            
            # Normal hatalı giriş
            return invalid_credentials()
        else:
            # Kullanıcı bulunamadı
            try:
                db.session.commit()
            except SQLAlchemyError:
                db.session.rollback()
            return invalid_credentials()

    # Başarılı login
    user.failed_login_attempts = 0
    user.last_login_at = datetime.utcnow()
    user.locked_until = None  # Başarılı girişte kilidi kaldır

    login_attempt.success = True
    login_attempt.risk_score = 0.0
    login_attempt.risk_level = "safe"

    db.session.add(login_attempt)

    # MFA kontrolü
    requires_mfa = should_require_mfa(user, risk_packet)
    if requires_mfa:
        user.require_mfa = True
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            return error_response(500, "Sunucu hatası.")
        
        # MFA gerektiğini belirten response döndür
        error_resp, status_code = mfa_required()
        return jsonify(error_resp), status_code

    # Normal başarılı giriş
    user.require_mfa = False
    update_user_device_info(user, risk_packet)

    access_token = create_access_token({"sub": user.id, "email": user.email})
    refresh_token = create_refresh_token({"sub": user.id})

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return error_response(500, "Sunucu hatası.")

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "require_mfa": False
    }), 200


@auth_bp.get("/me")
def me():
    """
    Kullanıcı bilgilerini döndüren endpoint.
    """
    token = get_token_from_header()
    if not token:
        return error_response(401, "Yetkisiz erişim (token yok).")

    decoded = decode_token(token)
    if not decoded:
        return error_response(401, "Geçersiz veya süresi dolmuş token.")

    user_id = decoded.get("sub")
    user = User.query.get(user_id)
    if not user or not user.is_active:
        return error_response(401, "Kullanıcı bulunamadı veya pasif.")

    return jsonify({
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at.isoformat(),
        "trust_score": user.trust_score,
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        "require_mfa": user.require_mfa
    }), 200

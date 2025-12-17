# app/mfa_otp.py
from datetime import datetime, timedelta
import random
from . import bcrypt

def generate_otp() -> str:
    return f"{random.randint(0, 999999):06d}"

def set_user_otp(user, minutes=5) -> str:
    code = generate_otp()
    user.mfa_code_hash = bcrypt.generate_password_hash(code).decode("utf-8")
    user.mfa_expires_at = datetime.utcnow() + timedelta(minutes=minutes)
    user.mfa_pending = True
    return code  # demo için response'ta döndürüyoruz

def verify_user_otp(user, code: str) -> bool:
    if not user.mfa_pending or not user.mfa_expires_at:
        return False
    if datetime.utcnow() > user.mfa_expires_at:
        return False
    if not user.mfa_code_hash:
        return False
    return bcrypt.check_password_hash(user.mfa_code_hash, code)

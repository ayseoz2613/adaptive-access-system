import jwt
from datetime import datetime, timedelta
from flask import current_app, request
from typing import Optional


def create_access_token(payload: dict) -> str:
    """Kısa ömürlü access token üretir."""
    exp_minutes = current_app.config["ACCESS_TOKEN_EXPIRES_MIN"]
    to_encode = payload.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(minutes=exp_minutes)
    return jwt.encode(
        to_encode,
        current_app.config["JWT_SECRET_KEY"],
        algorithm=current_app.config["JWT_ALGORITHM"],
    )


def create_refresh_token(payload: dict) -> str:
    """Daha uzun ömürlü refresh token üretir."""
    exp_days = current_app.config["REFRESH_TOKEN_EXPIRES_DAYS"]
    to_encode = payload.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(days=exp_days)
    to_encode["type"] = "refresh"
    return jwt.encode(
        to_encode,
        current_app.config["JWT_SECRET_KEY"],
        algorithm=current_app.config["JWT_ALGORITHM"],
    )


def decode_token(token: str) -> Optional[dict]:
    """Token'ı decode eder, hata varsa None döner."""
    try:
        decoded = jwt.decode(
            token,
            current_app.config["JWT_SECRET_KEY"],
            algorithms=[current_app.config["JWT_ALGORITHM"]],
        )
        return decoded
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_token_from_header() -> Optional[str]:
    """Authorization header içinden 'Bearer <token>' formatındaki token'ı alır."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    return auth_header.split(" ", 1)[1]

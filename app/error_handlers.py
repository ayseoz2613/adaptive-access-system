"""
Backend → UI hata-durum eşleştirme tablosu ve standart error response formatı.

Tüm hatalar tek tip bir JSON error response formatında döndürülür.
"""
from flask import jsonify
from typing import Dict, Tuple


# HTTP status code → UI error message eşleştirmeleri
ERROR_MESSAGES: Dict[int, str] = {
    400: "Bad request",
    401: "Invalid credentials",
    403: "Forbidden",
    404: "Not found",
    409: "Conflict",
    423: "Account temporarily locked",
    429: "Too many attempts, please wait",
    500: "Internal server error",
}


def create_error_response(
    error_code: int,
    custom_message: str = None,
    additional_data: dict = None
) -> Tuple[dict, int]:
    """
    Standart error response oluşturur.
    
    Args:
        error_code: HTTP status code
        custom_message: Özel hata mesajı (opsiyonel)
        additional_data: Ek veri (opsiyonel)
        
    Returns:
        Tuple[dict, int]: (error_response_dict, status_code)
    """
    message = custom_message or ERROR_MESSAGES.get(error_code, "An error occurred")
    
    response = {
        "error": ERROR_MESSAGES.get(error_code, "Unknown error"),
        "message": message,
        "status_code": error_code
    }
    
    if additional_data:
        response.update(additional_data)
    
    return response, error_code


def error_response(error_code: int, custom_message: str = None, additional_data: dict = None):
    """
    Flask jsonify ile standart error response döndürür.
    
    Args:
        error_code: HTTP status code
        custom_message: Özel hata mesajı (opsiyonel)
        additional_data: Ek veri (opsiyonel)
        
    Returns:
        Flask Response: JSON error response
    """
    response, status_code = create_error_response(error_code, custom_message, additional_data)
    return jsonify(response), status_code


# Özel hata response'ları için helper fonksiyonlar
def invalid_credentials(message: str = None) -> Tuple[dict, int]:
    """401 Invalid credentials hatası"""
    return create_error_response(401, message or "Kullanıcı adı veya şifre hatalı.")


def account_locked(locked_until: str = None, remaining_seconds: int = None) -> Tuple[dict, int]:
    """423 Account locked hatası"""
    additional_data = {}
    if locked_until:
        additional_data["locked_until"] = locked_until
    if remaining_seconds is not None:
        additional_data["remaining_seconds"] = remaining_seconds
    
    return create_error_response(
        423,
        "Hesap geçici olarak kilitlendi. Lütfen daha sonra tekrar deneyin.",
        additional_data
    )


def too_many_attempts(wait_seconds: int = None) -> Tuple[dict, int]:
    """429 Too many attempts hatası"""
    additional_data = {}
    if wait_seconds is not None:
        additional_data["wait_seconds"] = wait_seconds
    
    return create_error_response(
        429,
        "Çok fazla deneme yapıldı. Lütfen bekleyin.",
        additional_data
    )


def mfa_required() -> Tuple[dict, int]:
    """MFA gerektiğinde döndürülecek response"""
    return create_error_response(
        401,
        "Multi-factor authentication required",
        {"require_mfa": True}
    )


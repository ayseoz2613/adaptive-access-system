"""
Progressive Lock (İlerlemeli Kilitleme) mekanizması için utility fonksiyonları.

Kurallar:
- 3 hatalı giriş → 30 saniye bekleme süresi
- 5 hatalı giriş → 2 dakika geçici kilit
- 7 hatalı giriş → geçici tam hesap kilidi
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
from flask import jsonify


# Progressive lock eşikleri ve süreleri
LOCK_THRESHOLDS = {
    3: timedelta(seconds=30),   # 3 hatalı → 30 saniye
    5: timedelta(minutes=2),    # 5 hatalı → 2 dakika
    7: timedelta(hours=24),     # 7 hatalı → 24 saat (konfigüre edilebilir)
}


def check_account_lock(user) -> Optional[Tuple[dict, int]]:
    """
    Kullanıcı hesabının kilitli olup olmadığını kontrol eder.
    
    Args:
        user: User model instance
        
    Returns:
        None: Hesap kilitli değil
        Tuple[dict, int]: (error_response, status_code) hesap kilitliyse
    """
    if not user or not user.locked_until:
        return None
    
    if datetime.utcnow() < user.locked_until:
        # Hesap hala kilitli
        remaining_seconds = int((user.locked_until - datetime.utcnow()).total_seconds())
        return (
            {
                "error": "Account temporarily locked",
                "message": f"Hesap geçici olarak kilitlendi. Lütfen {remaining_seconds} saniye sonra tekrar deneyin.",
                "locked_until": user.locked_until.isoformat(),
                "remaining_seconds": remaining_seconds
            },
            423  # 423 Locked
        )
    else:
        # Kilit süresi dolmuş, kilidi kaldır
        user.locked_until = None
        return None


def apply_progressive_lock(user) -> Optional[datetime]:
    """
    Hatalı giriş sayısına göre progressive lock uygular.
    
    Args:
        user: User model instance
        
    Returns:
        datetime: Yeni kilit bitiş zamanı (eğer kilit uygulandıysa)
        None: Kilit uygulanmadı
    """
    failed_count = user.failed_login_attempts
    
    # Eşik değerlerini kontrol et (büyükten küçüğe)
    for threshold in sorted(LOCK_THRESHOLDS.keys(), reverse=True):
        if failed_count >= threshold:
            lock_duration = LOCK_THRESHOLDS[threshold]
            locked_until = datetime.utcnow() + lock_duration
            user.locked_until = locked_until
            return locked_until
    
    return None


def get_lock_status_message(failed_count: int) -> str:
    """
    Hatalı giriş sayısına göre kullanıcıya gösterilecek mesajı döndürür.
    
    Args:
        failed_count: Başarısız giriş denemesi sayısı
        
    Returns:
        str: Kullanıcıya gösterilecek mesaj
    """
    if failed_count >= 7:
        return "Çok fazla hatalı giriş denemesi. Hesabınız 24 saat süreyle kilitlendi."
    elif failed_count >= 5:
        return "5 hatalı giriş denemesi. Hesabınız 2 dakika süreyle kilitlendi."
    elif failed_count >= 3:
        return "3 hatalı giriş denemesi. Lütfen 30 saniye bekleyin."
    else:
        return "Kullanıcı adı veya şifre hatalı."


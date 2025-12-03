"""
MFA (Multi-Factor Authentication) tetikleme koşulları için utility fonksiyonları.

MFA tetikleme kuralları:
- IP değişmişse → require_mfa = True
- Cihaz bilgisi farklıysa → require_mfa = True
- Hiçbir şüpheli durum yoksa → normal girişe izin ver
"""
from typing import Optional
from .risk_data import RiskDataPacket


def should_require_mfa(user, risk_packet: RiskDataPacket) -> bool:
    """
    MFA gerekip gerekmediğini kontrol eder.
    
    Args:
        user: User model instance
        risk_packet: RiskDataPacket instance
        
    Returns:
        bool: MFA gerekiyorsa True, aksi halde False
    """
    if not user:
        return False
    
    # İlk giriş ise MFA gerekmez (henüz kayıt yok)
    if not user.last_ip and not user.last_device_info:
        return False
    
    # IP değişmişse MFA gerekir
    if user.last_ip and user.last_ip != risk_packet.ip_address:
        return True
    
    # Cihaz bilgisi farklıysa MFA gerekir
    if user.last_device_info and user.last_device_info != risk_packet.device_info:
        return True
    
    return False


def update_user_device_info(user, risk_packet: RiskDataPacket):
    """
    Kullanıcının son IP ve cihaz bilgisini günceller.
    
    Args:
        user: User model instance
        risk_packet: RiskDataPacket instance
    """
    user.last_ip = risk_packet.ip_address
    user.last_device_info = risk_packet.device_info


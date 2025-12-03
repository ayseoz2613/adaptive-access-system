"""
RiskDataPacket yapısı - Risk Engine'e aktarılacak veriyi temsil eder.

Bu yapı Week 3'te Risk Engine'e aktarılacak veriyi temsil edecek.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class RiskDataPacket:
    """
    Risk analizi için gerekli veri paketi.
    
    Attributes:
        ip_address: İstek yapan IP adresi
        device_info: Cihaz bilgisi (user agent, device fingerprint vb.)
        login_time: Giriş zamanı
        location: Konum bilgisi (opsiyonel)
        user_id: Kullanıcı ID (opsiyonel)
    """
    ip_address: str
    device_info: str
    login_time: datetime
    location: Optional[str] = None
    user_id: Optional[int] = None
    
    def to_dict(self) -> dict:
        """
        RiskDataPacket'i dictionary formatına dönüştürür.
        
        Returns:
            dict: Packet verilerini içeren dictionary
        """
        return {
            "ip_address": self.ip_address,
            "device_info": self.device_info,
            "login_time": self.login_time.isoformat(),
            "location": self.location,
            "user_id": self.user_id
        }
    
    @classmethod
    def from_request(cls, user_id: Optional[int] = None, location: Optional[str] = None) -> 'RiskDataPacket':
        """
        Flask request'ten RiskDataPacket oluşturur.
        
        Args:
            user_id: Kullanıcı ID (opsiyonel)
            location: Konum bilgisi (opsiyonel)
            
        Returns:
            RiskDataPacket: Oluşturulan packet instance
        """
        from flask import request
        
        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        user_agent = request.headers.get("User-Agent", "")
        
        # Basit device info (ileride daha detaylı fingerprint eklenebilir)
        device_info = user_agent
        
        return cls(
            ip_address=ip,
            device_info=device_info,
            login_time=datetime.utcnow(),
            location=location,
            user_id=user_id
        )


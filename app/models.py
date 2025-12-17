from datetime import datetime
from . import db, bcrypt


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Risk / behavior related
    trust_score = db.Column(db.Float, default=0.0)
    last_login_at = db.Column(db.DateTime, nullable=True)
    failed_login_attempts = db.Column(db.Integer, default=0)

    # ✅ Week 5: Progressive Lock (temporary lock)
    locked_until = db.Column(db.DateTime, nullable=True)

    # Week 4: Emergency Lock + session invalidation
    is_locked = db.Column(db.Boolean, default=False, nullable=False)
    token_version = db.Column(db.Integer, default=0, nullable=False)

    # MFA tetikleme için IP ve cihaz bilgisi takibi
    last_ip = db.Column(db.String(50), nullable=True)  # Son başarılı giriş IP adresi
    last_device_info = db.Column(db.String(255), nullable=True)  # Son başarılı giriş cihaz bilgisi
    require_mfa = db.Column(db.Boolean, default=False, nullable=False)  # MFA gerekip gerekmediği

    def set_password(self, plain_password: str):
        self.password_hash = bcrypt.generate_password_hash(plain_password).decode("utf-8")

    def check_password(self, plain_password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, plain_password)


class LoginAttempt(db.Model):
    """
    Login attempt kayıtları - gelecekte risk analizi için kullanılacak.
    
    Her login denemesi (başarılı/başarısız) bu tabloda kaydedilir.
    Bu kayıtlar risk analizi, anomali tespiti ve güvenlik ihlali tespiti için kullanılır.
    IP, cihaz, konum ve zaman bilgileri risk skorlama ve pattern analizi için saklanır.
    """
    __tablename__ = "login_attempts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    
    # Risk analizi için gerekli veriler - gelecekte risk analizi için kullanılacak
    ip_address = db.Column(db.String(50), nullable=True)  # IP değişimi tespiti için
    user_agent = db.Column(db.String(255), nullable=True)  # Tarayıcı/cihaz değişimi tespiti için
    device_info = db.Column(db.String(255), nullable=True)  # Cihaz değişimi tespiti için
    location = db.Column(db.String(255), nullable=True)  # Konum değişimi tespiti için
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Zaman analizi için
    success = db.Column(db.Boolean, default=False)  # Başarılı/başarısız deneme bilgisi

    # Risk skorlama alanları - gelecekte risk analizi için kullanılacak
    risk_score = db.Column(db.Float, default=0.0)  # Risk skoru (0-100)
    risk_level = db.Column(db.String(50), default="safe")  # safe / suspicious / critical

    # Week 3: explainability - risk nedenlerinin açıklanması
    risk_reasons = db.Column(db.Text, nullable=True)  # Risk skorunun nedenleri

    user = db.relationship("User", backref="login_attempts")

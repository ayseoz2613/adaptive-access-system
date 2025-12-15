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

    # Week 4: Emergency Lock + session invalidation
    is_locked = db.Column(db.Boolean, default=False, nullable=False)
    token_version = db.Column(db.Integer, default=0, nullable=False)

    def set_password(self, plain_password: str):
        self.password_hash = bcrypt.generate_password_hash(plain_password).decode("utf-8")

    def check_password(self, plain_password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, plain_password)


class LoginAttempt(db.Model):
    __tablename__ = "login_attempts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    device_info = db.Column(db.String(255), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    success = db.Column(db.Boolean, default=False)

    risk_score = db.Column(db.Float, default=0.0)
    risk_level = db.Column(db.String(50), default="safe")  # safe / suspicious / critical

    # Week 3: explainability
    risk_reasons = db.Column(db.Text, nullable=True)

    user = db.relationship("User", backref="login_attempts")

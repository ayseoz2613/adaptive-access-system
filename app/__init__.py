from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from .config import Config

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    from datetime import timedelta

    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=app.config.get("ACCESS_TOKEN_EXPIRES_MIN", 15))
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=app.config.get("REFRESH_TOKEN_EXPIRES_DAYS", 7))


    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)


    # CORS desteği - test.html için gerekli
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    # Blueprint'leri register et
    from .auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    # Root path
    @app.get("/")
    def index():
        return {
            "message": "Adaptive Access System API",
            "endpoints": {
                "health": "/api/health",
                "register": "/api/auth/register",
                "login": "/api/auth/login",
                "me": "/api/auth/me"
            }
        }, 200

    # Sağlık kontrolü
    @app.get("/api/health")
    def health():
        return {"status": "ok"}, 200

    return app

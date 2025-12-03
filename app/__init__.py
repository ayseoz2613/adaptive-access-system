from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from .config import Config

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    # Blueprint’leri register et
    from .auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    # Sağlık kontrolü
    @app.get("/api/health")
    def health():
        return {"status": "ok"}, 200

    return app

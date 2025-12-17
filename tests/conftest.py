import os
import pytest

AUTH_BASE = os.getenv("AUTH_BASE", "/api/auth")


def auth_url(path: str) -> str:
    return f"{AUTH_BASE}{path}"

@pytest.fixture(scope="session")
def app():
    from run import app as flask_app
    flask_app.config["TESTING"] = True
    return flask_app

@pytest.fixture()
def client(app):
    return app.test_client()

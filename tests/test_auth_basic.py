import uuid
from .conftest import auth_url

def test_register_and_login_safe(client):
    email = f"test_{uuid.uuid4().hex[:6]}@example.com"
    password = "test12345"

    r = client.post(auth_url("/register"), json={"email": email, "password": password})
    assert r.status_code == 201

    r = client.post(auth_url("/login"), json={"email": email, "password": password})
    assert r.status_code == 200

    data = r.get_json()
    assert "access_token" in data

import uuid
from tests.conftest import auth_url


def test_mfa_request_and_verify(client):
    email = f"mfa_{uuid.uuid4().hex[:6]}@example.com"
    password = "test12345"

    client.post(auth_url("/register"), json={"email": email, "password": password})

    r = client.post(auth_url("/mfa/request"), json={"email": email})
    assert r.status_code == 200
    otp = r.get_json()["dev_otp"]

    r = client.post(auth_url("/mfa/verify"), json={"email": email, "code": otp})
    assert r.status_code == 200
    assert "access_token" in r.get_json()

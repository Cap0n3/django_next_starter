"""
End-to-end tests of the allauth headless *browser* flow as the Next.js
frontend drives it: signup, login, session, logout, email verification.
"""

import pytest
from allauth.account.models import EmailAddress, EmailConfirmationHMAC
from django.contrib.auth import get_user_model
from django.core import mail

from .conftest import EMAIL, PASSWORD

pytestmark = pytest.mark.django_db

BASE = "/_allauth/browser/v1"
User = get_user_model()


def _post(client, path, payload):
    return client.post(f"{BASE}{path}", payload, content_type="application/json")


# --- session bootstrap -------------------------------------------------------


def test_anonymous_session_returns_401_and_sets_csrf_cookie(client):
    res = client.get(f"{BASE}/auth/session")
    assert res.status_code == 401
    assert res.json()["meta"]["is_authenticated"] is False
    assert "csrftoken" in res.cookies


# --- signup -------------------------------------------------------------------


def test_signup_creates_user_and_logs_in(client):
    res = _post(client, "/auth/signup", {"email": EMAIL, "password": PASSWORD})
    assert res.status_code == 200, res.content
    body = res.json()
    assert body["meta"]["is_authenticated"] is True
    assert body["data"]["user"]["email"] == EMAIL
    assert "sessionid" in res.cookies

    assert User.objects.filter(email=EMAIL).exists()
    # Session cookie now authenticates DRF endpoints.
    assert client.get("/api/me/").status_code == 200


def test_signup_sends_verification_email(client):
    _post(client, "/auth/signup", {"email": EMAIL, "password": PASSWORD})
    assert len(mail.outbox) == 1
    assert EMAIL in mail.outbox[0].to
    address = EmailAddress.objects.get(email=EMAIL)
    assert address.verified is False


def test_signup_rejects_duplicate_email(client, user):
    res = _post(client, "/auth/signup", {"email": EMAIL, "password": PASSWORD})
    assert res.status_code == 400
    assert any(e["param"] == "email" for e in res.json()["errors"])


def test_signup_rejects_weak_password(client):
    res = _post(client, "/auth/signup", {"email": EMAIL, "password": "12345678"})
    assert res.status_code == 400
    assert any(e["param"] == "password" for e in res.json()["errors"])
    assert not User.objects.filter(email=EMAIL).exists()


# --- login / logout -----------------------------------------------------------


def test_login_with_valid_credentials(client, user):
    res = _post(client, "/auth/login", {"email": EMAIL, "password": PASSWORD})
    assert res.status_code == 200, res.content
    assert res.json()["meta"]["is_authenticated"] is True
    assert client.get("/api/me/").status_code == 200


def test_login_with_wrong_password_fails(client, user):
    res = _post(client, "/auth/login", {"email": EMAIL, "password": "nope-nope-nope"})
    assert res.status_code == 400
    assert client.get("/api/me/").status_code in (401, 403)


def test_logout_returns_401_and_invalidates_session(auth_client):
    assert auth_client.get("/api/me/").status_code == 200

    # allauth signals a successful logout with 401 (the session is now anonymous).
    res = auth_client.delete(f"{BASE}/auth/session")
    assert res.status_code == 401
    assert res.json()["meta"]["is_authenticated"] is False

    assert auth_client.get("/api/me/").status_code in (401, 403)


# --- email verification -------------------------------------------------------


def test_verify_email_marks_address_verified(client):
    _post(client, "/auth/signup", {"email": EMAIL, "password": PASSWORD})
    address = EmailAddress.objects.get(email=EMAIL)
    key = EmailConfirmationHMAC(address).key

    res = client.get(f"{BASE}/auth/email/verify", HTTP_X_EMAIL_VERIFICATION_KEY=key)
    assert res.status_code == 200
    assert res.json()["data"]["email"] == EMAIL

    res = _post(client, "/auth/email/verify", {"key": key})
    assert res.status_code == 200, res.content
    address.refresh_from_db()
    assert address.verified is True


def test_verify_email_rejects_invalid_key(client):
    res = _post(client, "/auth/email/verify", {"key": "not-a-real-key"})
    assert res.status_code == 400

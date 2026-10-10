"""Tests for the project's own DRF endpoints."""

import pytest

pytestmark = pytest.mark.django_db


def test_ping_is_public(client):
    res = client.get("/api/ping/")
    assert res.status_code == 200
    assert res.json() == {"pong": True}


def test_me_requires_authentication(client):
    res = client.get("/api/me/")
    # DRF SessionAuthentication returns 403 (no WWW-Authenticate scheme) when anonymous.
    assert res.status_code in (401, 403)


def test_me_returns_current_user(auth_client, user):
    res = auth_client.get("/api/me/")
    assert res.status_code == 200
    body = res.json()
    assert body["id"] == user.id
    assert body["email"] == user.email
    assert set(body) == {"id", "email", "first_name", "last_name", "date_joined"}


def test_me_is_read_only(auth_client):
    res = auth_client.post("/api/me/", {"email": "x@example.com"})
    assert res.status_code == 405

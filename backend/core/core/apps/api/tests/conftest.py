import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

EMAIL = "alice@example.com"
PASSWORD = "correct-horse-battery-staple"


@pytest.fixture
def user(db):
    return User.objects.create_user(email=EMAIL, password=PASSWORD)


@pytest.fixture
def auth_client(client, user):
    client.force_login(user)
    return client

"""
Test settings.

Must never be used in production or local development — uses MD5 password
hashing for test speed and an in-memory SQLite database.
"""

import os

# Ensure required env vars exist before importing base (which reads them at
# import time). Tests do not need real secrets or a real database.
os.environ.setdefault("DJANGO_SECRET_KEY", "django-insecure-test-key")
os.environ.setdefault("DJANGO_DEBUG", "0")
os.environ.setdefault("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")
os.environ.setdefault("POSTGRES_DB", "test")
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")

from .base import *  # noqa: E402, F403, F401

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# MD5 is used ONLY here for test speed. Never reuse in local.py / production.py.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

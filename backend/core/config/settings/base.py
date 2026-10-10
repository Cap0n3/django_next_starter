"""
Base settings for the project.
"""

import os
from pathlib import Path

from config.logging import build_logging

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECRET_KEY must be provided via env. No default — fail loud if missing.
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

DEBUG = os.environ.get("DJANGO_DEBUG", "0") == "1"

ALLOWED_HOSTS = [h.strip() for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",") if h.strip()]

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "corsheaders",
    "allauth",
    "allauth.account",
    "allauth.headless",
]

LOCAL_APPS = [
    "core.apps.users",
    "core.apps.api",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["POSTGRES_DB"],
        "USER": os.environ["POSTGRES_USER"],
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST": os.environ.get("POSTGRES_HOST", "db"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom user model (email-as-username)
AUTH_USER_MODEL = "users.User"

# django-allauth
SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
# "optional": users can log in right away, but a verification email is sent
# and `EmailAddress.verified` tracks ownership. Switch to "mandatory" to block
# login until the address is confirmed.
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_UNIQUE_EMAIL = True
# Custom User model has no `username` field — email is the USERNAME_FIELD.
# Without this, allauth's signup form crashes in get_username_max_length().
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
# allauth's built-in rate limits (login failures, signup, email sends, ...)
# are enabled by default and rely on CACHES below. Keep them on.

# Frontend origin(s) — comma-separated. First one is the canonical URL used
# to build links in emails (verify email, password reset).
_frontend_origins = [
    o.strip().rstrip("/") for o in os.environ.get("FRONTEND_URL", "http://localhost:3000").split(",") if o.strip()
]
_frontend_url = _frontend_origins[0]

# allauth headless — frontend drives all UI
HEADLESS_ONLY = True
HEADLESS_FRONTEND_URLS = {
    "account_confirm_email": f"{_frontend_url}/verify-email/{{key}}",
    # Password reset pages are not implemented in the frontend yet.
    "account_reset_password": f"{_frontend_url}/password/reset",
    "account_reset_password_from_key": f"{_frontend_url}/password/reset/key/{{key}}",
    "account_signup": f"{_frontend_url}/signup",
}

# Email — console backend by default so verification emails show up in the
# backend logs during development. Set DJANGO_EMAIL_BACKEND + EMAIL_* in
# production (see docs/environment.md).
EMAIL_BACKEND = os.environ.get("DJANGO_EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "1") == "1"
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@localhost")

# Cache — shared Redis when REDIS_URL is set, otherwise per-process memory.
# allauth's rate limits and DRF throttling both count against this cache, so
# production with more than one worker needs REDIS_URL for limits to hold.
_redis_url = os.environ.get("REDIS_URL", "").strip()
if _redis_url:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": _redis_url,
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "django_next_starter",
        }
    }

# Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": os.environ.get("DRF_THROTTLE_ANON", "60/min"),
        "user": os.environ.get("DRF_THROTTLE_USER", "600/min"),
    },
}

# CORS / CSRF
CORS_ALLOWED_ORIGINS = _frontend_origins
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = _frontend_origins
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_HTTPONLY = False  # frontend reads csrftoken cookie to echo as X-CSRFToken

# Cookie domain. Leave empty when frontend and backend share a host (localhost
# in dev). When deployed on sibling subdomains (app.example.com +
# api.example.com) set DJANGO_COOKIE_DOMAIN=.example.com, otherwise the
# frontend cannot read `csrftoken` and every POST fails with 403.
_cookie_domain = os.environ.get("DJANGO_COOKIE_DOMAIN", "").strip() or None
SESSION_COOKIE_DOMAIN = _cookie_domain
CSRF_COOKIE_DOMAIN = _cookie_domain

# Admin URL prefix — change it via env to keep scanners off /admin/.
ADMIN_URL = os.environ.get("DJANGO_ADMIN_URL", "admin/").strip("/") + "/"

# Logging
LOGGING = build_logging(debug=DEBUG)

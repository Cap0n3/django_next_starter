"""
Production settings.

All secrets, hosts, and origins are read from environment variables in
base.py. This module only hardens security-related flags.

Required env vars (in addition to base.py):
  - DJANGO_SECRET_KEY
  - DJANGO_ALLOWED_HOSTS  (comma-separated)
  - POSTGRES_DB / POSTGRES_USER / POSTGRES_PASSWORD / POSTGRES_HOST / POSTGRES_PORT
  - FRONTEND_URL          (comma-separated if multiple)
  - DJANGO_COOKIE_DOMAIN  (e.g. ".example.com" when frontend and API live on
                           sibling subdomains; see base.py)
  - REDIS_URL             (shared cache so rate limits hold across workers)
  - DJANGO_EMAIL_BACKEND + EMAIL_HOST / EMAIL_HOST_USER / EMAIL_HOST_PASSWORD
                          (verification emails are dropped to stdout otherwise)

Deployment notes:
  - DJANGO_DEBUG must be unset or "0" (enforced below regardless).
  - TLS termination is expected at the proxy/load balancer; SECURE_PROXY_SSL_HEADER
    trusts X-Forwarded-Proto. Make sure the proxy strips any client-supplied
    X-Forwarded-Proto header before forwarding.
"""

from .base import *  # noqa: F403, F401

# Hard override — never allow DEBUG in production regardless of env.
DEBUG = False

# --- HTTPS / transport security ---
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 365  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"

# --- Cookies ---
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
# CSRF_COOKIE_HTTPONLY stays False (inherited from base) so the frontend can
# read csrftoken and echo it as X-CSRFToken. This is the documented allauth
# headless pattern and is safe as long as the frontend origin is trusted.

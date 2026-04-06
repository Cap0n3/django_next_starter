---
name: Auth architecture
description: Full auth and API setup for django_next_starter — framework, session strategy, CORS/CSRF config locations, and known issues from 2026-04-07 audit
type: project
---

Django 6.0.3 backend + Next.js 16 (App Router) frontend.

Auth framework: django-allauth[headless] — all auth UI is owned by Next.js, which calls `/_allauth/browser/v1/auth/*` endpoints. No JWT; uses Django session cookies.

Session strategy: Django database-backed sessions. Session cookie name `sessionid`. CSRF cookie name `csrftoken` (non-HttpOnly so JS can read it for X-CSRFToken header).

DRF auth: `SessionAuthentication` only. Default permission: `IsAuthenticated`.

**Why:** Allauth headless browser mode requires session cookies and CSRF, not token auth.

**How to apply:** Any new API views must explicitly set `permission_classes` or inherit `IsAuthenticated` default. Token-based auth is not in scope.

Key config files:
- `backend/core/config/settings/base.py` — CORS, CSRF, session, allauth, DRF config
- `backend/core/config/settings/local.py` — DEBUG=True, insecure dev SECRET_KEY
- `backend/.env` — env vars (gitignored); values not read into settings (hardcoded in base.py instead)
- `frontend/lib/api.ts` — fetch wrapper, CSRF cookie reader, credentials: include
- `frontend/lib/auth.ts` — allauth headless wrappers (signup, login, logout, getSession)
- `frontend/middleware.ts` — Next.js edge middleware, cookie-presence-based route guard
- `backend/core/core/apps/api/views.py` — PingView (AllowAny), MeView (IsAuthenticated)
- `backend/core/config/urls.py` — root URL conf; index view has no auth
- `backend/docker-compose.yml` — `makemigrations` runs at startup

Sensitive env vars defined in .env: DJANGO_SECRET_KEY, POSTGRES_PASSWORD.
These vars are defined but NOT read by settings — both are hardcoded literals in base.py / local.py.

Known issues confirmed in 2026-04-07 audit:
- [CRITICAL] SECRET_KEY hardcoded in base.py:9 ("change-me-in-production") and local.py:11; not read from DJANGO_SECRET_KEY env var
- [CRITICAL] DB credentials hardcoded in base.py:75-76 (user: "django", password: "django"); not read from env
- [CRITICAL] No production.py settings file; no SECURE_SSL_REDIRECT, SECURE_HSTS_*, SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE
- [HIGH] ACCOUNT_EMAIL_VERIFICATION = "none" — accounts can be created with any email, no ownership proof
- [HIGH] No rate limiting on auth endpoints (/_allauth/browser/v1/auth/login, signup, etc.)
- [HIGH] SESSION_COOKIE_SECURE and CSRF_COOKIE_SECURE not set anywhere — session cookie sent over HTTP
- [HIGH] ALLOWED_HOSTS = [] in base.py — would allow any host if DEBUG=False is ever reached without local.py override
- [MEDIUM] CORS/CSRF only cover localhost; no production origin config exists
- [MEDIUM] `makemigrations` runs at container start in docker-compose (line 19) — unsafe for prod, can auto-generate migrations
- [MEDIUM] No security headers: CSP, X-Content-Type-Options, Referrer-Policy, Permissions-Policy absent
- [MEDIUM] test.py uses MD5PasswordHasher — safe only for tests, but worth noting
- [MEDIUM] Error display on login/signup: JSON.stringify(err.data) renders raw API error body to user
- [LOW] index view at "/" returns JSON but bypasses DRF auth and has no rate limiting
- [LOW] Middleware route guard relies only on cookie presence (documented as UX-only — backend enforces)
- [LOW] No session expiry configured (SESSION_COOKIE_AGE defaults to 2 weeks)
- [LOW] No cookie name prefixes (__Host- / __Secure-) on session or CSRF cookies
- [INFO] .env and .env.example have identical values including placeholder secrets

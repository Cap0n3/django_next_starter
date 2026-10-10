---
name: Auth architecture
description: Auth and API setup for django_next_starter — allauth headless browser flow, session cookies, CORS/CSRF, rate limiting, and the state after the 2026-10-10 hardening pass
type: project
---

Django 6.0.3 backend + Next.js 16 (App Router) frontend.

Auth framework: django-allauth[headless] 65.x — all auth UI is owned by Next.js, which calls `/_allauth/browser/v1/auth/*`. No JWT; Django DB-backed sessions. Cookie names `sessionid` (HttpOnly) and `csrftoken` (readable by JS on purpose, echoed as `X-CSRFToken`).

DRF: `SessionAuthentication` only, default `IsAuthenticated`, `AnonRateThrottle` + `UserRateThrottle` on by default.

Key files:
- `backend/core/config/settings/base.py` — everything env-driven (SECRET_KEY, DB, FRONTEND_URL, DJANGO_COOKIE_DOMAIN, REDIS_URL, email, throttles, ADMIN_URL). `HEADLESS_FRONTEND_URLS` derived from the first FRONTEND_URL.
- `backend/core/config/settings/production.py` — DEBUG hard False, HSTS, SSL redirect, Secure cookies.
- `backend/core/config/logging/config.py` — `build_logging()` → `LOGGING` (stdout).
- `backend/core/core/apps/api/tests/` — pytest coverage of signup/login/logout/verify-email and `/api/me/`.
- `frontend/lib/api.ts` — fetch wrapper (credentials include, CSRF header).
- `frontend/lib/auth.ts` — allauth wrappers; `getSession`/`logout`/`verifyEmail` treat 401 as a valid anonymous state; `formatAuthError()` maps `errors[]` to text.
- `frontend/proxy.ts` — cookie-presence redirect guard (UX only).
- `frontend/app/(auth)/verify-email/[key]/page.tsx` — verification landing page.

Behaviours to remember:
- allauth returns **401 on successful logout**. Any client code must treat that as success.
- `ACCOUNT_EMAIL_VERIFICATION = "optional"`; console email backend in dev.
- Cross-subdomain deployments need `DJANGO_COOKIE_DOMAIN`, otherwise the frontend cannot read `csrftoken` → 403 on every POST.
- Rate limits (allauth + DRF) count in `CACHES["default"]`: LocMem without `REDIS_URL`, so multi-worker prod needs Redis.
- Tests clear the cache between tests (`core/conftest.py`) because allauth's per-email rate limit otherwise suppresses the verification email in later tests.

Remaining known gaps (not fixed, by choice):
- Password reset frontend pages do not exist yet (backend URLs point at `/password/reset`).
- No session idle timeout beyond Django's 2-week `SESSION_COOKIE_AGE`.
- `/admin/` is only protected by the configurable `DJANGO_ADMIN_URL` prefix.

# Architecture

## Stack

| Layer    | Tech |
| -------- | ---- |
| Backend  | Django 6, DRF, django-allauth (headless), django-cors-headers, PostgreSQL |
| Frontend | Next.js 16 (App Router), React 19, TypeScript, Tailwind v4, shadcn/ui |
| Auth     | Session cookies via allauth headless (`HEADLESS_ONLY = True`) — no JWT |
| User     | Custom `users.User` model (email as `USERNAME_FIELD`, no username) |

## Project structure

```
django_next_starter/
├── backend/
│   ├── docker-compose.yml          # db + web + frontend services
│   ├── Dockerfile.web.local        # Python 3.12 dev image
│   ├── .env.example                # all env vars with defaults
│   └── core/
│       ├── manage.py
│       ├── conftest.py             # project-wide pytest fixtures
│       ├── config/
│       │   ├── urls.py             # root router: admin, allauth, api
│       │   ├── wsgi.py
│       │   └── settings/
│       │       ├── base.py         # shared settings (DB, CORS, auth, DRF)
│       │       ├── local.py        # dev overrides (imports base)
│       │       ├── production.py   # HSTS, secure cookies, DEBUG=False
│       │       └── test.py         # in-memory SQLite, fast hasher
│       └── core/apps/
│           ├── users/              # custom User model + admin
│           └── api/                # ping + me endpoints + serializers + tests/
├── frontend/
│   ├── Dockerfile.local            # Node 22 dev image (pnpm)
│   ├── .dockerignore
│   ├── app/
│   │   ├── layout.tsx              # root layout (fonts, globals)
│   │   ├── page.tsx                # landing page + ping test
│   │   ├── (auth)/login/           # login form
│   │   ├── (auth)/signup/          # signup form
│   │   ├── (auth)/verify-email/    # landing page for the verification email link
│   │   └── (app)/dashboard/        # protected — shows current user
│   ├── components/ui/              # shadcn components (button, input, etc.)
│   ├── lib/
│   │   ├── api.ts                  # apiFetch() — credentials + CSRF
│   │   ├── auth.ts                 # allauth headless client
│   │   └── utils.ts                # cn() tailwind helper
│   └── proxy.ts                    # soft route protection (Next.js 16 name for middleware)
├── scripts/bootstrap.sh            # one-shot automated setup
└── Makefile                        # all dev commands
```

## Request lifecycle

```
Browser
  │
  ├─ Static pages ──► Next.js dev server (:3000)
  │
  └─ API / Auth ──► apiFetch() ──► Django (:8001)
                     │                │
                     │ credentials:   ├─ /_allauth/browser/v1/...  (auth)
                     │ "include"      ├─ /api/ping/                (public)
                     │ X-CSRFToken    └─ /api/me/                  (session-protected)
                     │
                     └─ cookies: sessionid + csrftoken
```

1. `apiFetch()` (`lib/api.ts`) sends every request with `credentials: "include"` so the browser attaches `sessionid` and `csrftoken` cookies.
2. For unsafe methods (POST, PUT, PATCH, DELETE), it reads the `csrftoken` cookie and echoes it as the `X-CSRFToken` header — Django's CSRF middleware validates the match.
3. Django responds with session state. On login/signup, it sets `sessionid` via `Set-Cookie`.
4. CORS is configured for `FRONTEND_URL` (default `http://localhost:3000`) with `CORS_ALLOW_CREDENTIALS = True`, so cookies flow between ports.

## Auth flow

```
1. Page load
   GET /_allauth/browser/v1/auth/session
   → Django sets csrftoken cookie (CSRF bootstrap)
   → Returns session state (authenticated or not)

2. Signup / Login
   POST /_allauth/browser/v1/auth/signup   (or .../login)
   Headers: X-CSRFToken: <value from cookie>
   Body: { email, password }
   → Django creates user + session
   → Sets sessionid cookie in response

3. Protected requests
   GET /api/me/
   Cookies: sessionid (sent automatically)
   → DRF SessionAuthentication validates session
   → Returns user data

4. Logout
   DELETE /_allauth/browser/v1/auth/session
   → Django destroys session
   → Clears sessionid cookie
   → Responds 401 (session is now anonymous) — this is the SUCCESS response,
     lib/auth.ts treats it as such

5. Email verification (ACCOUNT_EMAIL_VERIFICATION = "optional")
   Signup sends an email with a link to /verify-email/{key} on the frontend
   (dev: printed to the backend logs — `make backend-logs`).
   GET  /_allauth/browser/v1/auth/email/verify  (X-Email-Verification-Key: key) → which address?
   POST /_allauth/browser/v1/auth/email/verify  { key }                           → verified
   Users can log in before verifying; `EmailAddress.verified` records the state.
   Switch to "mandatory" to require verification before login.

6. Proxy (frontend soft-protection, `proxy.ts`)
   /dashboard without sessionid cookie → redirect to /login
   /login with sessionid cookie → redirect to /dashboard
   (UX convenience only — backend is the source of truth)
```

## Design decisions

- **Session cookies, not JWT** — simpler, no token refresh logic, Django handles expiry and revocation natively.
- **Email-only auth** — custom `User` model removes `username`; allauth configured with `ACCOUNT_LOGIN_METHODS = {"email"}`.
- **`HEADLESS_ONLY = True`** — no Django HTML auth pages; the Next.js frontend fully owns the UI.
- **`CSRF_COOKIE_HTTPONLY = False`** — intentional: the frontend must read `csrftoken` from `document.cookie` to echo it as a header. The CSRF token is not a secret (it prevents cross-site forgery, not token theft).
- **Soft proxy** — `proxy.ts` (Next.js 16's name for middleware) checks cookie presence for UX redirects, but never replaces server-side auth checks.
- **DRF defaults** — `SessionAuthentication` + `IsAuthenticated` globally; public endpoints override with `AllowAny`. Anonymous and per-user throttling is on by default.
- **Rate limits need a shared cache** — allauth's limits and DRF throttles count in `CACHES["default"]`: in-memory in dev, Redis in production (`REDIS_URL`).
- **Cookie domain is explicit** — `DJANGO_COOKIE_DOMAIN` must be set when frontend and API are on sibling subdomains, otherwise the frontend cannot read `csrftoken`. See [environment.md](environment.md#cookie-domain-and-cross-origin-deployments).
- **Errors are mapped, not dumped** — `formatAuthError()` turns allauth's `errors[]` into readable text; raw API bodies never reach the UI.
- **Single compose file** — db, backend, and frontend in one `docker-compose.yml` for one-command startup.

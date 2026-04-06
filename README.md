# django_next_starter

Fullstack boilerplate: **Django + DRF + django-allauth Headless** backend, **Next.js (App Router) + Tailwind + Shadcn-style UI** frontend.

The Django side is bootstrapped from [Cap0n3/barebone](https://github.com/Cap0n3/barebone) and extended with DRF, CORS, and the allauth headless API. The Next.js side talks to it via session cookies — no JWT.

```
.
├── backend/    # Django 6 + DRF + Allauth Headless (Postgres via docker compose)
└── frontend/   # Next.js 16 + Tailwind v4
```

## Stack

| Layer    | Tech                                                                       |
| -------- | -------------------------------------------------------------------------- |
| Backend  | Django 6.0, DRF, django-allauth[headless], django-cors-headers, Postgres   |
| Auth     | Session-cookie auth via `allauth.headless` (`HEADLESS_ONLY = True`)        |
| Frontend | Next.js 16 (App Router, TS), Tailwind v4, shadcn-style components          |
| User     | Custom `users.User` (email as `USERNAME_FIELD`, no username)               |

## Prerequisites

- Docker + Docker Compose (for the backend)
- Node.js 20+ and **pnpm** (for the frontend — enable via `corepack enable` or `npm i -g pnpm`)
- `make`

## Quick start

You have two options.

### Option A — Automated (one command)

```bash
./scripts/bootstrap.sh
```

Runs `make setup`, waits for the backend, pings `/api/ping/`, copies `frontend/.env.local`, and starts the frontend dev server. Handles errors gracefully and is safe to re-run.

### Option B — Manual (step by step)

```bash
cp backend/.env.example backend/.env         # required — Django reads secrets from here
# then edit backend/.env and set a real DJANGO_SECRET_KEY, e.g.:
#   python -c "import secrets; print(secrets.token_urlsafe(50))"
make setup                                   # backend containers + frontend deps
curl http://localhost:8001/api/ping/         # sanity check → {"pong": true}
cp frontend/.env.local.example frontend/.env.local
make frontend-run                            # starts Next.js on :3000
```

Use `make backend-run` / `make backend-stop` to control containers afterwards.

> **Note** — `AUTH_USER_MODEL` is set before the first migration, so the custom `users.User` table is created from scratch. Don't run migrations against an existing barebone DB without resetting it.

Useful Make targets (all run from project root):

| Command                          | What                                          |
| -------------------------------- | --------------------------------------------- |
| `make backend-run` / `backend-stop` | Start / stop backend containers             |
| `make migrate`                   | Apply migrations                              |
| `make mkmigs app=users`          | Make migrations for an app                    |
| `make create-superuser`          | Create a Django superuser                     |
| `make backend-test`              | Run pytest                                    |
| `make app app=foo`               | Scaffold a new app under `core/core/apps/foo` |

Run `make help` to see the full command reference for both stacks.

### 2. Frontend — http://localhost:3000

```bash
cp frontend/.env.local.example frontend/.env.local
make frontend-run
```

Open http://localhost:3000 and click **Ping backend** — you should see `{"pong": true}`. Then sign up, you'll be redirected to `/dashboard` showing your user from `/api/me/`.

## How auth works

- Allauth runs in `HEADLESS_ONLY` mode — there are no Django HTML auth pages. Everything goes through `/_allauth/browser/v1/...`.
- The frontend hits `GET /_allauth/browser/v1/auth/session` first to obtain a `csrftoken` cookie, then POSTs login/signup with `X-CSRFToken` echoed in the header.
- Authentication state lives in Django's `sessionid` cookie. CORS is configured for `http://localhost:3000` with credentials, so the cookie is shared automatically.
- DRF endpoints (`/api/...`) use `SessionAuthentication` and require `IsAuthenticated` by default — see `backend/core/core/apps/api/views.py` for examples.

## Endpoints

| Endpoint                              | Auth | Purpose                              |
| ------------------------------------- | ---- | ------------------------------------ |
| `GET  /api/ping/`                     |  —   | Health check                         |
| `GET  /api/me/`                       |  ✓   | Current user                         |
| `GET  /_allauth/browser/v1/auth/session` | — | Bootstrap CSRF + read session       |
| `POST /_allauth/browser/v1/auth/signup`  | — | Sign up                             |
| `POST /_allauth/browser/v1/auth/login`   | — | Log in                              |
| `DELETE /_allauth/browser/v1/auth/session` | ✓ | Log out                           |

Allauth headless OpenAPI: https://docs.allauth.org/en/latest/headless/openapi-specification/

## Configuration choices

These are the defaults — change in `backend/core/config/settings/base.py`:

- **Login method:** email only (`ACCOUNT_LOGIN_METHODS = {"email"}`)
- **Email verification:** disabled (`ACCOUNT_EMAIL_VERIFICATION = "none"`) — flip to `"optional"` or `"mandatory"` once you wire up an email backend
- **Custom user model:** `users.User` with email as `USERNAME_FIELD`

## Frontend layout

```
frontend/
├── app/
│   ├── (auth)/login/page.tsx
│   ├── (auth)/signup/page.tsx
│   ├── (app)/dashboard/page.tsx     # protected
│   └── page.tsx                     # landing + ping
├── components/ui/                   # button, input, label, card
├── lib/
│   ├── api.ts                       # fetch wrapper (cookies + CSRF)
│   ├── auth.ts                      # allauth headless client
│   └── utils.ts                     # cn() helper
└── middleware.ts                    # soft-protect /dashboard
```

The UI components mirror the shadcn/ui API and structure, so you can drop in real shadcn components later via `npx shadcn@latest add <name>` without breaking imports.

## Caveats

- **Next.js 16** is recent — its `frontend/AGENTS.md` warns about breaking changes vs older docs. If something behaves unexpectedly, check `frontend/node_modules/next/dist/docs/`.
- The frontend is **not** dockerized in this first pass — keep `make frontend-run` (pnpm) local for fast iteration.
- Email verification is off, so passwords are the only credential. Don't ship to prod without turning verification on and configuring an SMTP backend.

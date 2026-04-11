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

- Docker + Docker Compose (backend **and** frontend both run in containers)
- `make`, `curl`

## Quick start

You have two options.

### Option A — Automated (one command)

```bash
./scripts/bootstrap.sh
```

Runs `make setup`, waits for the backend at `/api/ping/`, waits for the frontend at `:3000`, and prints next steps. Safe to re-run.

### Option B — Manual

```bash
cp backend/.env.example backend/.env         # edit DJANGO_SECRET_KEY
make setup                                   # builds & starts db + backend + frontend
```

Then open http://localhost:3000. Use `make backend-stop` to stop everything, `make backend-run` / `make frontend-run` to start individual services.

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

Open http://localhost:3000 and click **Ping backend** — you should see `{"pong": true}`. Sign up and you'll land on `/dashboard` showing your user from `/api/me/`.

## Documentation

- [Architecture overview](docs/architecture.md) — how backend and frontend connect, auth flow, design decisions
- [Development guide](docs/development.md) — daily workflow, common tasks, troubleshooting
- [Environment variables](docs/environment.md) — every env var across backend and frontend

## Do do list

- [ ] Add auth tests
- [ ] Add client-side session refresh
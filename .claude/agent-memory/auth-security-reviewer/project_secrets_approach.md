---
name: Secrets and config management
description: How secrets are loaded (plain os.environ, fail-loud), what is env-driven, and gitignore status as of 2026-10-10
type: project
---

All configuration is read with plain `os.environ` in `backend/core/config/settings/base.py` — no django-environ / decouple. Required vars raise `KeyError` at import if missing (`DJANGO_SECRET_KEY`, `POSTGRES_DB/USER/PASSWORD`). Optional vars have safe dev defaults.

`backend/.env` and `frontend/.env.local` are gitignored; only `*.example` files are committed, with placeholder values. `scripts/bootstrap.sh` generates a random `DJANGO_SECRET_KEY` when creating `.env`.

Production-only env vars (documented in `docs/environment.md`): `DJANGO_COOKIE_DOMAIN`, `REDIS_URL`, `DJANGO_EMAIL_BACKEND` + `EMAIL_*`, `DJANGO_ADMIN_URL`.

`make backend-test` / pytest always use `config.settings.test` thanks to `--ds` in `pyproject.toml`, even though `.env` sets `DJANGO_SETTINGS_MODULE=config.settings.local`.

**How to apply:** when adding a new secret, read it in base.py with `os.environ[...]` (required) or `.get()` (optional), add it to `backend/.env.example` and the table in `docs/environment.md`.

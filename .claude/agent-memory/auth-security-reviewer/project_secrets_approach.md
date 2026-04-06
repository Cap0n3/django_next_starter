---
name: Secrets and config management
description: How secrets are loaded, what is and isn't read from env, and gitignore status
type: project
---

Backend `.env` is gitignored. `.env.example` committed with placeholder values only (identical to `.env` content — placeholder values happen to match, no real secrets committed as of 2026-04-07 audit).

However, `base.py` does NOT read SECRET_KEY or DB credentials from environment — both are hardcoded literals in the settings file itself. The `.env` file defines `DJANGO_SECRET_KEY` and `POSTGRES_PASSWORD` but nothing reads them.

`local.py` overrides SECRET_KEY with another hardcoded insecure literal: `"django-insecure-local-dev-key-change-in-production"`. No `production.py` settings file exists yet.

Frontend `.env.local` is gitignored (`.gitignore` covers `.env*`). The only var is `NEXT_PUBLIC_API_URL=http://localhost:8001` — a non-secret public URL.

No secret management library is installed. `django-environ` or `python-decouple` is NOT in requirements. Settings read env vars via `os.environ` would need manual wiring, or a library added.

**How to apply:** When helping add production settings, must:
1. Add `django-environ` or `python-decouple` to requirements/base.txt
2. Wire `SECRET_KEY = env("DJANGO_SECRET_KEY")` in base.py or production.py
3. Wire DB credentials from POSTGRES_* env vars
4. Add SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE, SECURE_SSL_REDIRECT, SECURE_HSTS_SECONDS in production.py

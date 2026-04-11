# Environment variables

All backend env vars live in `backend/.env` (copied from `backend/.env.example` during setup). Frontend env vars are set in `docker-compose.yml` for Docker, or in `frontend/.env.local` for local dev.

## Docker / Compose

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `COMPOSE_PROJECT_NAME` | `django_next_starter` | Prefix for container names (`<name>_db`, `<name>_web`, `<name>_frontend`) |
| `WEB_PORT` | `8001` | Host port mapped to Django's internal port 8000 |
| `DB_PORT` | `5432` | Host port mapped to PostgreSQL |
| `FRONTEND_PORT` | `3000` | Host port mapped to Next.js dev server |

## Django

| Variable | Default | Required | Description |
| -------- | ------- | -------- | ----------- |
| `DJANGO_SETTINGS_MODULE` | `config.settings.local` | Yes | Which settings file to use. Options: `config.settings.local`, `config.settings.production`, `config.settings.test` |
| `DJANGO_SECRET_KEY` | `change-me-in-production` | Yes | Cryptographic signing key. The bootstrap script generates a random one automatically |
| `DJANGO_DEBUG` | `0` | No | Set to `1` to enable debug mode. Production settings override this to `False` regardless |
| `DJANGO_ALLOWED_HOSTS` | `""` | No | Comma-separated list of allowed hostnames (e.g. `localhost,127.0.0.1`) |

## Database

| Variable | Default | Required | Description |
| -------- | ------- | -------- | ----------- |
| `POSTGRES_DB` | `django_db` | Yes | Database name (must match in both Django and Postgres) |
| `POSTGRES_USER` | `django` | Yes | Database user |
| `POSTGRES_PASSWORD` | `django` | Yes | Database password |
| `POSTGRES_HOST` | `db` | No | Hostname. Use `db` in Docker (service name) or `localhost` outside Docker |
| `POSTGRES_PORT` | `5432` | No | Internal PostgreSQL port |

## CORS / Auth

| Variable | Default | Required | Description |
| -------- | ------- | -------- | ----------- |
| `FRONTEND_URL` | `http://localhost:3000` | No | Frontend origin(s) for CORS and CSRF trusted origins. Comma-separated for multiple origins |

This value is used to set:
- `CORS_ALLOWED_ORIGINS` — which origins can make cross-origin requests
- `CSRF_TRUSTED_ORIGINS` — which origins are trusted for CSRF validation

## Frontend

| Variable | Set in | Default | Description |
| -------- | ------ | ------- | ----------- |
| `NEXT_PUBLIC_API_URL` | `docker-compose.yml` | `http://localhost:8001` | Django API base URL. Prefixed with `NEXT_PUBLIC_` so it's available in browser code |
| `WATCHPACK_POLLING` | `docker-compose.yml` | `true` | Enables file-system polling for hot reload in Docker (required on macOS) |
| `CHOKIDAR_USEPOLLING` | `docker-compose.yml` | `true` | Same as above, for older watchers |

## Production notes

`config/settings/production.py` applies these hardcoded overrides (not controlled by env vars):

- `DEBUG = False` — always off, regardless of `DJANGO_DEBUG`
- `SECURE_SSL_REDIRECT = True` — forces HTTPS
- `SECURE_HSTS_SECONDS = 31536000` — 1 year HSTS with subdomains and preload
- `SESSION_COOKIE_SECURE = True` — session cookie only sent over HTTPS
- `CSRF_COOKIE_SECURE = True` — CSRF cookie only sent over HTTPS
- `SESSION_COOKIE_HTTPONLY = True` — session cookie not readable by JavaScript
- `CSRF_COOKIE_HTTPONLY = False` — stays False (frontend needs to read it for the `X-CSRFToken` header)
- `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")` — trusts reverse proxy for SSL termination

When deploying to production, you must also:
1. Set `DJANGO_SECRET_KEY` to a strong random value
2. Set `DJANGO_ALLOWED_HOSTS` to your domain(s)
3. Set `FRONTEND_URL` to your production frontend origin
4. Configure an email backend if enabling email verification (`ACCOUNT_EMAIL_VERIFICATION = "optional"` or `"mandatory"`)

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
| `DJANGO_COOKIE_DOMAIN` | *(empty)* | No | Domain for `sessionid`/`csrftoken` cookies. Empty = host-only (dev). Set to the parent domain (`.example.com`) when frontend and API are on sibling subdomains |
| `DJANGO_ADMIN_URL` | `admin/` | No | URL prefix of the Django admin |
| `DJANGO_LOG_LEVEL` | `DEBUG` if debug else `INFO` | No | Root log level |
| `REDIS_URL` | *(empty)* | No (prod: yes) | Redis cache URL. Empty = per-process in-memory cache. Needed in production so rate limits are shared across workers |
| `DRF_THROTTLE_ANON` | `60/min` | No | DRF throttle for anonymous requests to `/api/` |
| `DRF_THROTTLE_USER` | `600/min` | No | DRF throttle for authenticated requests to `/api/` |
| `DJANGO_EMAIL_BACKEND` | console backend | No (prod: yes) | Email backend. Default prints emails to backend logs |
| `EMAIL_HOST` / `EMAIL_PORT` / `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` / `EMAIL_USE_TLS` | `""` / `587` / `""` / `""` / `1` | No | SMTP settings, used with the SMTP backend |
| `DEFAULT_FROM_EMAIL` | `noreply@localhost` | No | Sender address for verification emails |

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
2. Set `DJANGO_ALLOWED_HOSTS` to your API domain(s)
3. Set `FRONTEND_URL` to your production frontend origin (first entry is used to build email links)
4. **Set `DJANGO_COOKIE_DOMAIN`** if the frontend and the API are on sibling subdomains — see below
5. Set `REDIS_URL` so allauth rate limits and DRF throttling are shared across workers (without it each worker counts separately)
6. Set `DJANGO_EMAIL_BACKEND` to the SMTP backend and fill in `EMAIL_HOST*` — otherwise verification emails are printed to stdout and never delivered
7. Optionally change `DJANGO_ADMIN_URL` away from `admin/`
8. Run `python manage.py check --deploy` with the production settings module

### Cookie domain and cross-origin deployments

Authentication relies on the browser attaching the `sessionid` cookie **and** on the frontend reading the `csrftoken` cookie from `document.cookie` to echo it as `X-CSRFToken`.

In development both apps are on `localhost` (different ports only), so both cookies are visible to the frontend and nothing extra is needed.

In production you have two options:

| Deployment | What to set |
| ---------- | ----------- |
| Sibling subdomains, e.g. `app.example.com` + `api.example.com` | `DJANGO_COOKIE_DOMAIN=.example.com` so both cookies are scoped to the parent domain and readable by the frontend. `SameSite=Lax` still applies because the two hosts are the same *site*. |
| Same origin via reverse proxy, e.g. `example.com/` → Next.js and `example.com/api/`, `example.com/_allauth/` → Django | Leave `DJANGO_COOKIE_DOMAIN` empty and set `NEXT_PUBLIC_API_URL` to the same origin. |

Completely unrelated domains (`myapp.com` + `api.otherhost.net`) will **not** work with cookie-based auth: the browser blocks `SameSite=Lax` cookies and the CSRF token is unreadable. Put a proxy in front or use allauth's app client with token auth instead.

### Rate limiting

- allauth's built-in `ACCOUNT_RATE_LIMITS` protect the `/_allauth/` endpoints (login failures, signup, verification emails, password resets).
- DRF `AnonRateThrottle` / `UserRateThrottle` protect `/api/` (`DRF_THROTTLE_ANON`, `DRF_THROTTLE_USER`).

Both count against `CACHES["default"]`, hence the `REDIS_URL` requirement above.

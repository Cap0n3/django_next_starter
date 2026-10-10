# Development guide

All commands run from the **project root**. Both backend and frontend are dockerized.

## Starting and stopping

```bash
make setup            # first time: copies .env, builds & starts all containers
make backend-run      # start db + backend + frontend containers
make backend-stop     # stop all containers
make frontend-run     # start just the frontend container
make frontend-stop    # stop just the frontend container
```

After `make setup`, services are available at:

- Backend: http://localhost:8001
- Frontend: http://localhost:3000
- Django admin: http://localhost:8001/admin/

## Viewing logs

```bash
make backend-logs     # stream Django dev server output
make frontend-logs    # stream Next.js dev server output
```

## Shelling into containers

```bash
make docker-bash      # bash into the backend (web) container
make frontend-shell   # sh into the frontend container
make backend-shell    # Django shell (manage.py shell)
```

## Hot reload

Both backend and frontend support live reload via bind-mounted volumes:

- **Backend**: Django's `runserver` watches for Python file changes automatically.
- **Frontend**: Next.js watches via `WATCHPACK_POLLING=true` (reliable on Docker Desktop / macOS). Edit any file under `frontend/app/` or `frontend/components/` and changes appear in ~1-2s.

If hot reload feels stale, rebuild the image:

```bash
docker compose -f backend/docker-compose.yml build frontend
make frontend-run
```

## Common tasks

### Create a Django superuser

```bash
make create-superuser
```

### Add a new Django app

```bash
make app app=myapp
```

This creates `backend/core/core/apps/myapp/`. Register it in `INSTALLED_APPS` (`backend/core/config/settings/base.py`).

### Run migrations

Containers run `migrate` on start but never `makemigrations` — generate migrations explicitly and commit them:

```bash
make mkmigs               # makemigrations
make mkmigs app=users     # makemigrations for a specific app
make migrate              # apply migrations
make showmigrations       # check migration status
```

### Add a frontend dependency

```bash
# 1. Shell into the container and add it
make frontend-shell
pnpm add <package>
exit

# 2. Rebuild the image (bakes the dep into the layer)
docker compose -f backend/docker-compose.yml build frontend
make frontend-run
```

### Add a shadcn/ui component

```bash
make frontend-shell
pnpm dlx shadcn@latest add <component>
exit
```

Components are written to `frontend/components/ui/`. Never hand-write files in that directory.

### Run tests and linting

Backend tests always use `config.settings.test` (in-memory SQLite, fast hasher) via `--ds` in `pyproject.toml`, regardless of what `.env` sets. They cover the full allauth headless flow (signup, login, logout, email verification) and the DRF endpoints.

```bash
make backend-test         # pytest (backend)
make frontend-lint        # eslint (frontend)
make ruff                 # ruff lint (backend)
make ruff-fix             # ruff lint --fix
make ruff-format          # ruff format
```

### Database operations

```bash
make psql                 # PostgreSQL shell
make db-backup            # backup database
make db-restore           # restore from backup
make flush                # delete all data (careful!)
```

### See all commands

```bash
make help
```

## Troubleshooting

**Port already in use**
Another process is using 8001 or 3000. Either kill it or change the port in `backend/.env`:
```
WEB_PORT=8002
FRONTEND_PORT=3001
```
Then `make backend-stop && make backend-run`.

**CORS error in browser console**
The `FRONTEND_URL` env var in `backend/.env` must match the origin the browser is using. Default is `http://localhost:3000`.

**Verification email — where is it?**
Dev uses the console email backend: the email (with the `/verify-email/<key>` link) is printed in `make backend-logs`.

**Login works but /api/me/ returns 401**
Session may have expired or the `sessionid` cookie wasn't sent. Check:
- Browser DevTools > Application > Cookies — `sessionid` should exist for `localhost`.
- `credentials: "include"` must be set on the fetch call (handled by `lib/api.ts`).

**Frontend container keeps restarting**
Check logs with `make frontend-logs`. Common cause: `pnpm-lock.yaml` out of sync with `package.json`. Shell in and run `pnpm install`, then rebuild.

**Stale node_modules after switching branches**
The anonymous Docker volume for `node_modules` persists across restarts. To reset:
```bash
make backend-stop
docker compose -f backend/docker-compose.yml down -v   # removes volumes
make backend-run                                        # fresh install
```

PROJECT_NAME = ./core
DC := docker compose -f backend/docker-compose.yml

.PHONY: setup help \
        backend-run backend-stop backend-build backend-logs backend-shell backend-test backend-lint \
        frontend-run frontend-stop frontend-logs frontend-shell frontend-build frontend-start frontend-lint frontend-test install \
        secret app create-superuser docker-bash \
        mkmigs mkmigs-dry migrate migrate-all showmigrations \
        db-backup db-restore db-table db-columns flush sqlflush psql \
        collect \
        ruff ruff-fix ruff-format djlint djlint-all

# ==============================================================================
#  PROJECT SETUP
# ==============================================================================
setup:
	@echo "Setting up the project..."
	@cp -n backend/.env.example backend/.env 2>/dev/null && echo "Created backend/.env from backend/.env.example" || echo "backend/.env already exists, skipping"
	@echo "Building and starting all containers (db, web, frontend)..."
	@$(DC) up -d --build
	@echo "Waiting for containers to be ready..."
	@sleep 10
	@echo ""
	@echo "Setup complete! (backend migrations are applied automatically on container start)"
	@echo "  - Backend:  http://localhost:$${WEB_PORT:-8001}"
	@echo "  - Frontend: http://localhost:$${FRONTEND_PORT:-3000}"
	@echo ""
	@echo "Next steps:"
	@echo "  make create-superuser    Create a Django admin account"
	@echo "  make frontend-run        Start the Next.js dev server"
	@echo "  make help                See all available commands"
	@echo ""

# ==============================================================================
#  BACKEND — lifecycle (namespaced)
# ==============================================================================
backend-run:
	@echo "Starting backend containers..."
	@$(DC) up -d --build
	@echo "Backend running at http://localhost:$${WEB_PORT:-8001}"

backend-stop:
	@echo "Stopping backend containers..."
	@$(DC) down

backend-logs:
	@$(DC) logs -f --tail 50 web

backend-shell:
	@echo "Running Django shell..."
	@$(DC) exec web python $(PROJECT_NAME)/manage.py shell

backend-test:
	@echo "Running backend tests..."
	@$(DC) exec web pytest $(PROJECT_NAME)/

backend-lint: ruff

# ==============================================================================
#  FRONTEND — lifecycle (dockerized)
# ==============================================================================
frontend-run:
	@echo "Starting frontend container..."
	@$(DC) up -d --build frontend
	@echo "Frontend running at http://localhost:$${FRONTEND_PORT:-3000}"

frontend-stop:
	@echo "Stopping frontend container..."
	@$(DC) stop frontend

frontend-logs:
	@$(DC) logs -f --tail 50 frontend

frontend-shell:
	@echo "Opening shell in frontend container..."
	@$(DC) exec frontend sh

frontend-build:
	@echo "Building frontend (next build) inside container..."
	@$(DC) exec frontend pnpm build

frontend-start:
	@echo "Starting frontend (production build) inside container..."
	@$(DC) exec frontend pnpm start

frontend-lint:
	@echo "Running frontend lint..."
	@$(DC) exec frontend pnpm lint

install:
	@echo "Installing frontend dependencies inside container..."
	@$(DC) exec frontend pnpm install

# ==============================================================================
#  DJANGO — unambiguous commands (no prefix)
# ==============================================================================
secret:
	@echo "Generating Django secret key..."
	@python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

app:
	@if [ -z "$(app)" ]; then \
		echo "Usage: make app app=<app_name>"; \
		exit 1; \
	fi
	@echo "Creating app $(app)..."
	@$(DC) exec web mkdir -p /app/$(PROJECT_NAME)/$(PROJECT_NAME)/apps/$(app)
	@$(DC) exec web python $(PROJECT_NAME)/manage.py startapp $(app) $(PROJECT_NAME)/$(PROJECT_NAME)/apps/$(app)

create-superuser:
	@echo "Creating superuser..."
	@$(DC) exec web python $(PROJECT_NAME)/manage.py createsuperuser

docker-bash:
	@echo "Connecting to web container..."
	@$(DC) exec web bash

# ==============================================================================
#  MIGRATIONS
# ==============================================================================
mkmigs:
	@echo "Making migrations..."
	@$(DC) exec web python $(PROJECT_NAME)/manage.py makemigrations $(app)

mkmigs-dry:
	@echo "Making migrations (dry run)..."
	@$(DC) exec web python $(PROJECT_NAME)/manage.py makemigrations --dry-run

migrate:
	@echo "Migrating..."
	@$(DC) exec web python $(PROJECT_NAME)/manage.py migrate

migrate-all:
	@echo "Making migrations locally, then migrating in container..."
	@cd backend/$(PROJECT_NAME) && python manage.py makemigrations
	@$(DC) exec web python $(PROJECT_NAME)/manage.py migrate

showmigrations:
	@echo "Showing migrations..."
	@$(DC) exec web python $(PROJECT_NAME)/manage.py showmigrations $(app)

# ==============================================================================
#  DATABASE
# ==============================================================================
db-backup:
	@echo "Creating a backup of database..."
	@$(DC) exec web bash -c "cd /app/$(PROJECT_NAME)/utility/db_operations && DOCKER_BACKUP_DIR=/app/db_backups ./db_backup.sh"

db-restore:
	@echo "Restoring database..."
	@$(DC) exec web bash -c "cd /app/$(PROJECT_NAME)/utility/db_operations && DOCKER_BACKUP_DIR=/app/db_backups ./db_restore.sh"

db-table:
	@echo "Searching table..."
	@$(DC) exec web bash -c \
	"echo \"SELECT $(columns) FROM $(table) $(WHERE);\" | python $(PROJECT_NAME)/manage.py dbshell"

db-columns:
	@echo "Listing columns for table: $(table)"
	@$(DC) exec web bash -c \
	"echo \"\
SELECT column_name \
FROM information_schema.columns \
WHERE table_name = '$(table)' \
ORDER BY ordinal_position;\" \
| python $(PROJECT_NAME)/manage.py dbshell"

sqlflush:
	@echo "Showing SQL to flush the database..."
	@$(DC) exec web python $(PROJECT_NAME)/manage.py sqlflush

flush:
	@echo "Flushing the database (deleting all data)..."
	@$(DC) exec web python $(PROJECT_NAME)/manage.py flush

psql:
	@echo "Connecting to PostgreSQL database..."
	@$(DC) exec db psql -U django -d django_db

# ==============================================================================
#  STATIC FILES
# ==============================================================================
collect:
	@echo "Collecting static files..."
	@$(DC) exec web python $(PROJECT_NAME)/manage.py collectstatic

# ==============================================================================
#  CODE QUALITY (backend)
# ==============================================================================
ruff:
	@echo "Running ruff check..."
ifdef path
	@$(DC) exec web ruff check ./$(PROJECT_NAME)/$(path)
else
	@$(DC) exec web ruff check ./$(PROJECT_NAME)/
endif

ruff-fix:
	@echo "Running ruff fix..."
ifdef path
	@$(DC) exec web ruff check --fix ./$(PROJECT_NAME)/$(path)
else
	@$(DC) exec web ruff check --fix ./$(PROJECT_NAME)/
endif

ruff-format:
	@echo "Running ruff format..."
ifdef path
	@$(DC) exec web ruff format ./$(PROJECT_NAME)/$(path)
else
	@$(DC) exec web ruff format ./$(PROJECT_NAME)/
endif

djlint:
ifndef path
	@echo "Error: Please specify a path relative to templates/ directory."
	@echo "Usage: make djlint path=<relative_path_from_templates>"
	@exit 1
endif
	@djlint --check backend/$(PROJECT_NAME)/templates/$(path)

djlint-all:
	@echo "Running djlint check on all HTML templates..."
	@djlint --check backend/$(PROJECT_NAME)/templates/

# ==============================================================================
#  HELP
# ==============================================================================
help:
	@echo ""
	@echo "╔══════════════════════════════════════════════════════════════════════════════╗"
	@echo "║              Django + Next.js Starter — Root Makefile                        ║"
	@echo "╚══════════════════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "┌──────────────────────────────────────────────────────────────────────────────┐"
	@echo "│  PROJECT SETUP                                                               │"
	@echo "└──────────────────────────────────────────────────────────────────────────────┘"
	@echo "  setup               First-time setup (env, backend Docker, frontend deps)"
	@echo ""
	@echo "┌──────────────────────────────────────────────────────────────────────────────┐"
	@echo "│  BACKEND (Django, dockerized)                                                │"
	@echo "└──────────────────────────────────────────────────────────────────────────────┘"
	@echo "  backend-run         Start backend containers"
	@echo "  backend-stop        Stop backend containers"
	@echo "  backend-logs        Stream web container logs"
	@echo "  backend-shell       Open Django shell"
	@echo "  backend-test        Run pytest"
	@echo "  backend-lint        Run ruff (alias)"
	@echo "  docker-bash         Bash into web container"
	@echo "  create-superuser    Create a Django superuser"
	@echo "  app app=<name>      Create a new Django app"
	@echo "  secret              Generate a Django secret key"
	@echo ""
	@echo "  MIGRATIONS:"
	@echo "    mkmigs [app=<n>]  Make migrations"
	@echo "    mkmigs-dry        Make migrations (dry run)"
	@echo "    migrate           Apply migrations"
	@echo "    migrate-all       makemigrations (local) + migrate (docker)"
	@echo "    showmigrations    Show migration status"
	@echo ""
	@echo "  DATABASE:"
	@echo "    psql              PostgreSQL shell"
	@echo "    db-backup         Backup database"
	@echo "    db-restore        Restore database"
	@echo "    db-table          Query a table"
	@echo "    db-columns        List table columns"
	@echo "    flush             Delete all data"
	@echo "    sqlflush          Show flush SQL"
	@echo ""
	@echo "  STATIC / QUALITY:"
	@echo "    collect           Collect static files"
	@echo "    ruff [path=]      Ruff lint"
	@echo "    ruff-fix          Ruff lint --fix"
	@echo "    ruff-format       Ruff format"
	@echo "    djlint path=<p>   djlint a template"
	@echo "    djlint-all        djlint all templates"
	@echo ""
	@echo "┌──────────────────────────────────────────────────────────────────────────────┐"
	@echo "│  FRONTEND (Next.js, dockerized)                                              │"
	@echo "└──────────────────────────────────────────────────────────────────────────────┘"
	@echo "  frontend-run        Start frontend container (Next.js dev server)"
	@echo "  frontend-stop       Stop frontend container"
	@echo "  frontend-logs       Stream frontend container logs"
	@echo "  frontend-shell      Open shell in frontend container"
	@echo "  frontend-build      Build production bundle (next build)"
	@echo "  frontend-start      Start built frontend"
	@echo "  frontend-lint       Run eslint"
	@echo "  install             Install frontend dependencies (pnpm, in container)"
	@echo ""
	@echo "──────────────────────────────────────────────────────────────────────────────"
	@echo "  Backend and frontend both run in Docker (dev)."
	@echo "──────────────────────────────────────────────────────────────────────────────"
	@echo ""

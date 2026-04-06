#!/usr/bin/env bash
#
# bootstrap.sh — one-shot setup for django_next_starter
#
# Runs: make setup → waits for backend → pings /api/ping/ → copies frontend .env.local → starts frontend.
# Idempotent: safe to re-run. Exits non-zero on any unrecoverable error.

set -Eeuo pipefail

# ---- pretty output -----------------------------------------------------------
if [[ -t 1 ]]; then
  BOLD=$'\033[1m'; RED=$'\033[31m'; GREEN=$'\033[32m'; YELLOW=$'\033[33m'; BLUE=$'\033[34m'; RESET=$'\033[0m'
else
  BOLD=""; RED=""; GREEN=""; YELLOW=""; BLUE=""; RESET=""
fi

info()  { printf "%s==>%s %s\n" "${BLUE}${BOLD}" "${RESET}" "$*"; }
ok()    { printf "%s✓%s  %s\n" "${GREEN}${BOLD}" "${RESET}" "$*"; }
warn()  { printf "%s!%s  %s\n" "${YELLOW}${BOLD}" "${RESET}" "$*"; }
err()   { printf "%s✗%s  %s\n" "${RED}${BOLD}"   "${RESET}" "$*" >&2; }

on_error() {
  local line=$1
  err "bootstrap failed at line ${line}."
  err "Inspect backend logs with: make backend-logs"
  exit 1
}
trap 'on_error $LINENO' ERR

# ---- locate project root -----------------------------------------------------
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

# ---- preflight ---------------------------------------------------------------
info "Checking prerequisites..."
missing=()
for cmd in docker make curl; do
  command -v "$cmd" >/dev/null 2>&1 || missing+=("$cmd")
done
if ! docker compose version >/dev/null 2>&1; then
  missing+=("docker compose plugin")
fi
if ! command -v pnpm >/dev/null 2>&1; then
  if command -v corepack >/dev/null 2>&1; then
    warn "pnpm not found — enabling via corepack"
    corepack enable >/dev/null 2>&1 || missing+=("pnpm (corepack failed)")
  else
    missing+=("pnpm")
  fi
fi
if ((${#missing[@]})); then
  err "Missing required tools: ${missing[*]}"
  err "Install them and re-run ./scripts/bootstrap.sh"
  exit 1
fi
ok "All prerequisites present."

# ---- backend .env ------------------------------------------------------------
BE_ENV="backend/.env"
BE_EXAMPLE="backend/.env.example"
if [[ -f "${BE_ENV}" ]]; then
  ok "${BE_ENV} already exists — keeping it."
elif [[ -f "${BE_EXAMPLE}" ]]; then
  cp "${BE_EXAMPLE}" "${BE_ENV}"
  # Replace the placeholder SECRET_KEY with a freshly generated one so the
  # backend is never started with a well-known key, even in dev.
  if command -v python3 >/dev/null 2>&1; then
    NEW_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')"
    # portable in-place sed (BSD + GNU)
    sed -i.bak "s|^DJANGO_SECRET_KEY=.*|DJANGO_SECRET_KEY=${NEW_KEY}|" "${BE_ENV}"
    rm -f "${BE_ENV}.bak"
    ok "Created ${BE_ENV} from ${BE_EXAMPLE} with a generated DJANGO_SECRET_KEY."
  else
    warn "python3 not found — created ${BE_ENV} but DJANGO_SECRET_KEY is still the placeholder. Edit it before deploying."
  fi
else
  err "${BE_EXAMPLE} not found — cannot bootstrap backend env."
  exit 1
fi

# ---- run make setup ----------------------------------------------------------
info "Running 'make setup' (builds backend, installs frontend deps)..."
if ! make setup; then
  err "'make setup' failed. Check output above."
  exit 1
fi

# ---- wait for backend /api/ping/ --------------------------------------------
WEB_PORT="${WEB_PORT:-8001}"
PING_URL="http://localhost:${WEB_PORT}/api/ping/"
info "Waiting for backend at ${PING_URL} ..."
attempts=30
until curl -fsS "${PING_URL}" >/dev/null 2>&1; do
  attempts=$((attempts - 1))
  if (( attempts <= 0 )); then
    err "Backend never responded at ${PING_URL}."
    err "Try: make backend-logs"
    exit 1
  fi
  sleep 1
done
response="$(curl -fsS "${PING_URL}")"
ok "Backend reachable — ${response}"

# ---- frontend .env.local -----------------------------------------------------
FE_ENV="frontend/.env.local"
FE_EXAMPLE="frontend/.env.local.example"
if [[ -f "${FE_ENV}" ]]; then
  ok "${FE_ENV} already exists — keeping it."
elif [[ -f "${FE_EXAMPLE}" ]]; then
  cp "${FE_EXAMPLE}" "${FE_ENV}"
  ok "Created ${FE_ENV} from ${FE_EXAMPLE}."
else
  warn "${FE_EXAMPLE} not found — skipping frontend env copy."
fi

# ---- done --------------------------------------------------------------------
cat <<EOF

${GREEN}${BOLD}Bootstrap complete!${RESET}

  Backend:   http://localhost:${WEB_PORT}
  Frontend:  http://localhost:3000  (starting now...)

Press Ctrl+C to stop the frontend. Backend keeps running in Docker —
use 'make backend-stop' to shut it down.

EOF

info "Starting frontend dev server (make frontend-run)..."
exec make frontend-run

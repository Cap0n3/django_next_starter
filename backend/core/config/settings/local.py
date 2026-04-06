"""
Local development settings.

SECRET_KEY, DEBUG, ALLOWED_HOSTS, DB credentials, and FRONTEND_URL are all
read from environment variables in base.py (loaded from backend/.env by
docker compose). See backend/.env.example for the expected variables.
"""

from .base import *  # noqa: F403, F401

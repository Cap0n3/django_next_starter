"""
Django LOGGING configuration.

Everything goes to stdout so Docker / the platform collects it. Wired into
settings via `LOGGING = build_logging(debug=DEBUG)` in base.py.
"""

import os


def build_logging(*, debug: bool) -> dict:
    level = os.environ.get("DJANGO_LOG_LEVEL", "DEBUG" if debug else "INFO").upper()
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console": {
                "format": "[%(asctime)s] [%(levelname)s] {%(name)s -> %(funcName)s} - %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "console",
            },
        },
        "root": {"handlers": ["console"], "level": level},
        "loggers": {
            "django": {"handlers": ["console"], "level": level, "propagate": False},
            # Queries are extremely noisy at DEBUG; raise them to INFO unless needed.
            "django.db.backends": {"level": "INFO", "propagate": True},
            "core": {"handlers": ["console"], "level": level, "propagate": False},
        },
    }

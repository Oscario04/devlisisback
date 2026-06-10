import logging
from logging.config import dictConfig

from app.core.config import get_settings

settings = get_settings()


class SafeExtraFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        defaults = {
            "request_id": "-",
            "method": "-",
            "path": "-",
            "status_code": "-",
            "duration_ms": "-",
        }
        for field, default_value in defaults.items():
            if not hasattr(record, field):
                setattr(record, field, default_value)
        return True


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s | req_id=%(request_id)s method=%(method)s path=%(path)s status=%(status_code)s duration_ms=%(duration_ms)s",
        },
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "filters": ["safe_extra"],
        },
    },
    "filters": {
        "safe_extra": {
            "()": "app.core.logging.SafeExtraFilter",
        }
    },
    "root": {
        "level": settings.log_level,
        "handlers": ["default"],
    },
    "loggers": {
        "uvicorn.error": {"level": settings.log_level},
        "uvicorn.access": {
            "level": settings.log_level,
            "handlers": ["default"],
            "propagate": False,
        },
    },
}


def configure_logging() -> None:
    dictConfig(LOGGING_CONFIG)
    logging.getLogger(__name__).info(
        "Logging configured",
        extra={"log_level": settings.log_level},
    )
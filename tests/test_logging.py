from logging.config import dictConfig

from typeable import JsonValue, typecast
from typeable.schemas.logging import LoggingConfig


def test_simple():
    data = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {"simple": {"format": "%(levelname)-8s - %(message)s"}},
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "simple",
                "stream": "ext://sys.stdout",
            },
            "stderr": {
                "class": "logging.StreamHandler",
                "level": "ERROR",
                "formatter": "simple",
                "stream": "ext://sys.stderr",
            },
        },
        "root": {"level": "DEBUG", "handlers": ["stderr", "stdout"]},
    }

    config = typecast(LoggingConfig, data)
    dictConfig(typecast(JsonValue, config))  # type: ignore
    dictConfig(typecast(JsonValue, LoggingConfig(version=1)))  # type: ignore

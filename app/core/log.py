import inspect
import logging
import sys

from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger

from app.core.config import settings

LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"


class InterceptHandler(logging.Handler):
    """
    Redirige los logs de la librería estándar `logging` (incluidos los de uvicorn
    y los `logging.getLogger(__name__)` del propio proyecto) hacia loguru.

    Referencia: https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def _default_formatter(record: dict) -> str:
    base_format = settings.LOG_FORMAT if settings.LOG_FORMAT.endswith("\n") else f"{settings.LOG_FORMAT}\n"
    if record.get("exception") is not None:
        base_format += "{exception}\n"
    return base_format


def setup_logging() -> None:
    """Configura el logging estándar para que fluya a través de loguru."""
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(settings.LOG_STD_LEVEL)

    for name in logging.root.manager.loggerDict:
        logging.getLogger(name).handlers = []
        # Evita duplicar logs de acceso/recarga muy verbosos
        logging.getLogger(name).propagate = "uvicorn.access" not in name and "watchfiles.main" not in name

    logger.remove()
    logger.configure(
        handlers=[
            {
                "sink": sys.stdout,
                "level": settings.LOG_STD_LEVEL,
                "format": _default_formatter,
            }
        ]
    )


def set_custom_logfile() -> None:
    """Configura archivos de log rotativos: uno para info/acceso y otro para errores."""
    LOG_DIR.mkdir(exist_ok=True)

    log_access_file = LOG_DIR / settings.LOG_ACCESS_FILENAME
    log_error_file = LOG_DIR / settings.LOG_ERROR_FILENAME

    def _compress(filepath: str) -> None:
        path = Path(filepath)
        date_str = datetime.now().strftime("%Y-%m-%d")
        path.rename(path.with_name(f"{path.stem}_{date_str}{path.suffix}"))

    log_config: dict[str, Any] = {
        "format": _default_formatter,
        "enqueue": True,
        "rotation": "00:00",
        "retention": "7 days",
        "compression": _compress,
    }

    logger.add(
        str(log_access_file),
        level="INFO",
        filter=lambda record: record["level"].no <= 25,
        backtrace=False,
        diagnose=False,
        **log_config,
    )

    logger.add(
        str(log_error_file),
        level="WARNING",
        filter=lambda record: record["level"].no >= 30,
        backtrace=True,
        diagnose=True,
        **log_config,
    )


log = logger

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(
    *,
    app_name: str = "receptor",
    log_level: str | None = None,
    log_dir: str | None = None,
    log_file: str = '',
) -> None:
    level_name = (log_level or os.getenv("LOG_LEVEL") or "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    default_dir = os.getenv("LOG_DIR", "/var/log/receptor")
    dir_path = Path(log_dir or default_dir)
    dir_path.mkdir(parents=True, exist_ok=True)

    file_path = Path(log_file or os.getenv("LOG_FILE", str(dir_path / f"{app_name}.log")))

    fmt = "%(asctime)s | %(levelname)s | %(name)s | %(process)d:%(threadName)s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)

    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(formatter)

    max_bytes = int(os.getenv("LOG_MAX_BYTES", str(10 * 1024 * 1024)))
    backup_count = int(os.getenv("LOG_BACKUP_COUNT", "5"))

    file_handler = RotatingFileHandler(
        filename=str(file_path),
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    root.addHandler(console)
    root.addHandler(file_handler)

    logging.getLogger("aiohttp").setLevel(max(level, logging.WARNING))
    logging.getLogger("asyncio").setLevel(max(level, logging.WARNING))

    for name in (
        "sqlalchemy",
        "sqlalchemy.engine",
        "sqlalchemy.engine.Engine",
        "sqlalchemy.pool",
        "sqlalchemy.dialects",
        "sqlalchemy.orm",
    ):
        logger = logging.getLogger(name)
        logger.setLevel(logging.WARNING)

    sa_engine_logger = logging.getLogger("sqlalchemy.engine.Engine")
    sa_engine_logger.propagate = False
    sa_engine_logger.handlers.clear()

    for name in (
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
    ):
        uv_logger = logging.getLogger(name)
        uv_logger.handlers.clear()
        uv_logger.propagate = True

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

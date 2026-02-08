import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(
    *,
    app_name: str = "receptor",
    log_level: str | None = None,
    log_dir: str | None = None,
    log_file: str | None = None,
) -> None:
    """
    Настраивает logging один раз на процесс:
    - Console handler -> stdout (видно в Docker)
    - File handler -> rotating log file (ограничение по размеру)
    """

    level_name = (log_level or os.getenv("LOG_LEVEL") or "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    # Куда писать файл
    default_dir = os.getenv("LOG_DIR", "/var/log/receptor")
    dir_path = Path(log_dir or default_dir)
    dir_path.mkdir(parents=True, exist_ok=True)

    file_path = Path(
        log_file or os.getenv("LOG_FILE", str(dir_path / f"{app_name}.log"))  # type: ignore
    )

    # Формат логов
    fmt = (
        "%(asctime)s | %(levelname)s | %(name)s | %(process)d:%(threadName)s | "
        "%(message)s"
    )
    datefmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)

    root = logging.getLogger()

    # Важно: чтобы не плодить хендлеры при повторном вызове
    # (например, при автоперезагрузке)
    root.handlers.clear()
    root.setLevel(level)

    # 1) Консоль — чтобы Docker показывал логи
    console = logging.StreamHandler()  # по умолчанию stderr; можно stdout, если надо
    console.setLevel(level)
    console.setFormatter(formatter)

    # 2) Файл с ротацией
    # Можно настроить через env:
    # LOG_MAX_BYTES, LOG_BACKUP_COUNT
    max_bytes = int(os.getenv("LOG_MAX_BYTES", str(10 * 1024 * 1024)))  # 10MB
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
    logging.getLogger("sqlalchemy.engine").setLevel(max(level, logging.INFO))

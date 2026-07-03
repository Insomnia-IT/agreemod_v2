import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler




def setup_logging(logger_name: str) -> None:
    
    root = logging.getLogger()

    # Защита от повторной конфигурации при повторных импортах.
    if getattr(root, "_agreemod_configured", False):
        return None

    debug_enabled = os.getenv("DEBUG", "False") == "True"
    level = logging.DEBUG if debug_enabled else logging.INFO

    
    root.setLevel(level)
    root.handlers.clear()

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(module)s] [%(levelname)s]: %(message)s",
        datefmt="%Y.%m.%d %H:%M:%S",
    )

    if os.getenv("LOG_STDOUT_ENABLED", "True") == "True":
        stdout_handler = logging.StreamHandler()
        stdout_handler.setFormatter(formatter)
        root.addHandler(stdout_handler)

    if os.getenv("LOG_FILE_ENABLED", "True") == "True":
        log_dir = Path(os.getenv("LOG_DIR", "/var/log/agreemod"))
        log_file_name = os.getenv("LOG_FILE_NAME", "agreemod.log")
        max_bytes = int(os.getenv("LOG_MAX_BYTES", "10485760"))
        backup_count = int(os.getenv("LOG_BACKUP_COUNT", "10"))

        log_dir.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            filename=log_dir / log_file_name,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)




    # Set RabbitMQ related loggers to WARNING level
    for name in ("aio_pika", "aiormq", "aio_pika.connection", "aio_pika.channel", "aio_pika.exchange", "aiormq.connection", "aiormq.channel"):
        logging.getLogger(name).setLevel(logging.WARNING)    

    root._agreemod_configured = True

    # Disable PIL debug logs
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("PIL.TiffImagePlugin").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
	return logging.getLogger(name)
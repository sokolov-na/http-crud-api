import logging
from pathlib import Path

from http_crud_api.logging.config import ENVIRONMENT, LOG_DIR, LOG_FILE
from http_crud_api.logging.formatters import ConsoleFormatter, FileFormatter


def setup_logging() -> None:
    # DEV collects all logs; PROD (or something else) starts from WARNING.
    level = logging.DEBUG if ENVIRONMENT.upper() == "DEV" else logging.WARNING

    path = Path(LOG_DIR)

    path.mkdir(exist_ok=True)

    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(path / LOG_FILE, encoding="utf-8")

    console_handler.setFormatter(ConsoleFormatter())
    file_handler.setFormatter(FileFormatter())

    logging.basicConfig(level=level, handlers=[console_handler, file_handler])

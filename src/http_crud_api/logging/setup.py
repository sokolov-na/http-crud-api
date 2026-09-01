"""Application logging configuration."""

import logging

from http_crud_api.logging.formatters import ConsoleFormatter, FileFormatter
from http_crud_api.settings import Settings


def setup_logging(settings: Settings) -> None:
    """Configure console and file logging for the application."""

    level = settings.log_level

    path = settings.log_dir

    path.mkdir(parents=True, exist_ok=True)

    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(path / "app.jsonl", encoding="utf-8")

    console_handler.setFormatter(ConsoleFormatter())
    file_handler.setFormatter(FileFormatter())

    logging.basicConfig(level=level, handlers=[console_handler, file_handler])

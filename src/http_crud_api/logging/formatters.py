import json
import logging
import sys
from typing import Final

OPTIONAL_FIELDS: Final = {
    "method",
    "endpoint",
    "status_code",
}

EXC_LEVELS: Final = {
    logging.ERROR,
    logging.CRITICAL,
}


class ConsoleFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return f"{record.levelname} | {record.name} | {record.getMessage()}"


class FileFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "event": record.getMessage(),
        }
        data.update(
            {
                attr: getattr(record, attr)
                for attr in OPTIONAL_FIELDS
                if hasattr(record, attr)
            }
        )

        # Automatically include the active exception for error-level logs.
        _, exc_value, _ = sys.exc_info()
        if record.levelno in EXC_LEVELS and exc_value is not None:
            data["exception"] = str(exc_value)
        return json.dumps(data)

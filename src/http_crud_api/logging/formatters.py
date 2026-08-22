import json
import logging
from typing import Final

OPTIONAL_FIELDS: Final = {
    "method",
    "endpoint",
    "status_code",
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

        if record.exc_info:
            exc_type, exc_value, _ = record.exc_info
            if exc_type is not None and exc_value is not None:
                data["exception_type"] = exc_type.__name__
                data["exception_value"] = str(exc_value)
        return json.dumps(data)

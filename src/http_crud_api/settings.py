"""Application settings loaded from environment variables."""

import logging
import os
from pathlib import Path
from socket import gaierror, gethostbyname

from dotenv import load_dotenv


class Settings:
    """Load and validate the application's environment settings."""

    def __init__(self) -> None:
        """Load environment variables and validate their values."""

        load_dotenv()
        self.__http_host = os.getenv("HTTP_HOST")
        self.__http_port = os.getenv("HTTP_PORT")
        self.__data_dir = os.getenv("DATA_DIR")
        self.__log_level = os.getenv("LOG_LEVEL")
        self.__log_dir = os.getenv("LOG_DIR")

    @property
    def http_host(self) -> str:
        """Return the validated host address for the HTTP server."""

        if self.__http_host is None:
            raise ValueError("HTTP_HOST is required")
        try:
            gethostbyname(self.__http_host)
        except gaierror:
            raise ValueError(
                f"Invalid HTTP_HOST: {self.__http_host}"
            ) from None

        return self.__http_host

    @property
    def http_port(self) -> int:
        """Return the validated port number for the HTTP server."""

        if self.__http_port is None:
            raise ValueError("HTTP_PORT is required")
        try:
            self.__http_port = int(self.__http_port)
        except ValueError as exc:
            raise ValueError("HTTP_PORT must be a number") from exc
        if not (1 <= self.__http_port <= 65535):
            raise ValueError("HTTP_PORT must be between 1 and 65535")

        return self.__http_port

    @property
    def data_dir(self) -> Path:
        """Return the configured directory for application data."""

        if self.__data_dir is None:
            raise ValueError("DATA_DIR is required")
        try:
            return Path(self.__data_dir)
        except ValueError as exc:
            raise ValueError("DATA_DIR must be a valid path") from exc

    @property
    def log_dir(self) -> Path:
        """Return the configured directory for application logs."""

        if not self.__log_dir:
            raise ValueError("LOG_DIR is required") from None
        try:
            return Path(self.__log_dir)
        except ValueError:
            raise ValueError("LOG_DIR must be a valid path") from None

    @property
    def log_level(self) -> str:
        """Return the configured and validated logging level."""

        if self.__log_level is None:
            raise ValueError("LOG_LEVEL is required") from None

        if self.__log_level not in logging.getLevelNamesMapping():
            raise ValueError(
                f"Invalid LOG_LEVEL: {self.__log_level}. "
                "Must be one of "
                f"{', '.join(logging.getLevelNamesMapping().keys())}"
            ) from None

        return self.__log_level

import json
import logging
from enum import Enum
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from typing import Any, Self

logger = logging.getLogger("http_crud_api.http")


class ResponseFormat(Enum):
    JSON = "application/json"
    TEXT = "text/plain"
    EMPTY = None


class Response:
    def __init__(
        self,
        status_code: HTTPStatus,
        data: Any | None = None,
        format: ResponseFormat = ResponseFormat.EMPTY,
    ) -> None:
        self.__status_code = status_code
        self.__data = data
        self.__format = format

    def __log(self, handler: BaseHTTPRequestHandler) -> None:
        if self.__status_code >= 500:
            log = logger.error
        elif self.__status_code >= 400:
            log = logger.warning
        else:
            log = logger.info

        log(
            f"Request {handler.command} {handler.path} "
            f"completed with status {self.__status_code}",
            extra={
                "method": handler.command,
                "endpoint": handler.path,
                "status_code": self.__status_code,
            },
        )

    def send(self, handler: BaseHTTPRequestHandler) -> None:
        match self.__format:
            case ResponseFormat.EMPTY:
                handler.send_response_only(self.__status_code)
                handler.end_headers()
            case ResponseFormat.JSON:
                self.__send_json(handler)
            case ResponseFormat.TEXT:
                self.__send_text(handler)

        self.__log(handler)

    def __send_json(self, handler: BaseHTTPRequestHandler) -> None:
        try:
            data = json.dumps(self.__data).encode()
        except (
            ValueError,
            TypeError,
        ):
            raise TypeError("Invalid data for JSON response") from None

        handler.send_response(self.__status_code)
        handler.send_header("Content-Type", ResponseFormat.JSON.value)
        handler.end_headers()
        handler.wfile.write(data)

    def __send_text(self, handler: BaseHTTPRequestHandler) -> None:
        if not isinstance(self.__data, str):
            raise TypeError("TEXT response requires str data")

        handler.send_response(self.__status_code)
        handler.send_header("Content-Type", ResponseFormat.TEXT.value)
        handler.end_headers()
        handler.wfile.write(self.__data.encode())

    @classmethod
    def json(cls, status_code: HTTPStatus, data: Any) -> Self:
        return cls(status_code, data, ResponseFormat.JSON)

    @classmethod
    def text(cls, status_code: HTTPStatus, data: str) -> Self:
        return cls(status_code, data, ResponseFormat.TEXT)

    @classmethod
    def empty(cls, status_code: HTTPStatus) -> Self:
        return cls(status_code)

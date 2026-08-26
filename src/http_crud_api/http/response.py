import json
import logging
from dataclasses import dataclass
from enum import Enum
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from typing import Any


class ResponseFormat(Enum):
    JSON = "application/json"
    TEXT = "text/plain"


@dataclass(frozen=True)
class Response:
    status_code: HTTPStatus
    data: Any | None = None
    format: ResponseFormat = ResponseFormat.JSON


logger = logging.getLogger("http_crud_api.http")


def send_response_new(
    handler: BaseHTTPRequestHandler, response: Response
) -> None:
    if response.status_code == HTTPStatus.NO_CONTENT:
        handler.send_response_only(response.status_code)
        handler.end_headers()
        return

    if response.data is None:
        raise ValueError

    match response.format:
        case ResponseFormat.JSON:
            handler.send_response(response.status_code)
            handler.send_header("Content-Type", response.format.value)
            handler.end_headers()
            handler.wfile.write(json.dumps(response.data).encode())
        case ResponseFormat.TEXT:
            handler.send_response(response.status_code)
            handler.send_header("Content-Type", response.format.value)
            handler.end_headers()
            handler.wfile.write(response.data.encode())

    if response.status_code >= 500:
        log = logger.error
    elif response.status_code >= 400:
        log = logger.warning
    else:
        log = logger.info

    log(
        f"Request {handler.command} {handler.path} "
        f"completed with status {response.status_code}",
        extra={
            "method": handler.command,
            "endpoint": handler.path,
            "status_code": response.status_code,
        },
    )

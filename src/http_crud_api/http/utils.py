import json
import logging
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from typing import Any

logger = logging.getLogger("http_crud_api.http")

JSONResponse = dict[str, Any] | list[dict[str, Any]]


def send_json(
    handler: BaseHTTPRequestHandler,
    data: JSONResponse,
    status_code: HTTPStatus = HTTPStatus.OK,
) -> None:
    handler.send_response(status_code)
    handler.send_header("Content-Type", "application/json")
    handler.end_headers()
    handler.wfile.write(json.dumps(data).encode())

    logger.info(
        f"Request {handler.command} {handler.path} "
        f"completed with status {status_code}",
        extra={
            "method": handler.command,
            "endpoint": handler.path,
            "status_code": status_code,
        },
    )


def send_response(
    handler: BaseHTTPRequestHandler,
    status_code: HTTPStatus,
    *,
    message: str | None = None,
) -> None:
    handler.send_response(status_code)
    handler.end_headers()
    if message is not None:
        handler.wfile.write(message.encode())

    if status_code >= 500:
        log = logger.error
    elif status_code >= 400:
        log = logger.warning
    else:
        log = logger.info

    log(
        f"Request {handler.command} {handler.path} "
        f"completed with status {status_code}",
        extra={
            "method": handler.command,
            "endpoint": handler.path,
            "status_code": status_code,
        },
    )


def get_body(handler: BaseHTTPRequestHandler) -> bytes:
    content_length = int(handler.headers.get("Content-Length", 0))
    return handler.rfile.read(content_length)


def body_to_json(body: bytes) -> Any | None:
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return


def is_user_id_path(path: str) -> bool:
    return path.startswith("/users/") and len(path.strip("/").split("/")) == 2

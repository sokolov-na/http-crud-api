import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from typing import Any

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


def send_not_found(handler: BaseHTTPRequestHandler) -> None:
    handler.send_response(HTTPStatus.NOT_FOUND)
    handler.end_headers()
    handler.wfile.write(b"NOT FOUND")


def get_body(handler: BaseHTTPRequestHandler) -> bytes:
    content_length = int(handler.headers.get("Content-Length", 0))
    return handler.rfile.read(content_length)


def body_to_json(body: bytes) -> Any | None:
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return


def is_user_id_path(handler: BaseHTTPRequestHandler) -> bool:
    return (
        handler.path.startswith("/users/")
        and len(handler.path.strip("/").split("/")) == 2
    )

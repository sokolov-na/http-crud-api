"""Utilities for processing HTTP requests."""

from http.server import BaseHTTPRequestHandler

from http_crud_api.exceptions.validation import ValidationError
from http_crud_api.validation.request import validate_id_from_path


def get_body(handler: BaseHTTPRequestHandler) -> bytes:
    """Read the request body according to its content length."""

    content_length = int(handler.headers.get("Content-Length", 0))
    return handler.rfile.read(content_length)


def is_user_id_path(path: str) -> bool:
    """Return whether a path identifies a user endpoint."""

    try:
        validate_id_from_path(path)
        return (
            path.startswith("/users/") and len(path.strip("/").split("/")) == 2
        )
    except ValidationError:
        return False

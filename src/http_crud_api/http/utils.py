import logging
from http.server import BaseHTTPRequestHandler

from http_crud_api.exceptions.validation import ValidationError
from http_crud_api.validation.request import validate_id_from_path

logger = logging.getLogger("http_crud_api.http")


def get_body(handler: BaseHTTPRequestHandler) -> bytes:
    content_length = int(handler.headers.get("Content-Length", 0))
    return handler.rfile.read(content_length)


def is_user_id_path(path: str) -> bool:
    try:
        validate_id_from_path(path)
        return (
            path.startswith("/users/") and len(path.strip("/").split("/")) == 2
        )
    except ValidationError:
        return False

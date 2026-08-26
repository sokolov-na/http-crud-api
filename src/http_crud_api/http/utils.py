import logging
from http.server import BaseHTTPRequestHandler

logger = logging.getLogger("http_crud_api.http")


def get_body(handler: BaseHTTPRequestHandler) -> bytes:
    content_length = int(handler.headers.get("Content-Length", 0))
    return handler.rfile.read(content_length)


def is_user_id_path(path: str) -> bool:
    return path.startswith("/users/") and len(path.strip("/").split("/")) == 2

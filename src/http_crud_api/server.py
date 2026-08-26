import logging
import socketserver
from functools import partial
from http.server import BaseHTTPRequestHandler
from json import JSONDecodeError
from pathlib import Path
from typing import Any, Final

from http_crud_api.http.response import send_response
from http_crud_api.http.routes import (
    create_user,
    delete_user,
    get_favicon,
    get_user,
    get_users,
    health,
    not_allowed,
    not_found,
    update_user,
)
from http_crud_api.http.utils import get_body, is_user_id_path
from http_crud_api.repositories.json_user import JsonUserRepository
from http_crud_api.service.user import UserService

PORT: Final = 8080

logger = logging.getLogger(__name__)


class RequestHandler(BaseHTTPRequestHandler):
    def __init__(
        self, *args: Any, user_service: UserService, **kwargs: Any
    ) -> None:
        self.user_service = user_service
        super().__init__(*args, **kwargs)

    def log_message(self, format: str, *args: Any) -> None:
        pass

    def do_GET(self) -> None:
        match self.path:
            case "/health":
                response = health()

            case "/users":
                response = get_users(self.user_service)

            case self.path if is_user_id_path(self.path):
                response = get_user(self.path, self.user_service)

            case "/favicon.ico":
                response = get_favicon()

            case _:
                response = not_found()

        send_response(self, response)

    def do_POST(self) -> None:
        match self.path:
            case "/health":
                response = not_allowed()

            case "/users":
                body = get_body(self)
                response = create_user(body, self.user_service)

            case _:
                response = not_found()

        send_response(self, response)

    def do_DELETE(self) -> None:
        match self.path:
            case "/health":
                response = not_allowed()
            case self.path if is_user_id_path(self.path):
                response = delete_user(self.path, self.user_service)
            case _:
                response = not_found()

        send_response(self, response)

    def do_PUT(self) -> None:
        match self.path:
            case "/health":
                response = not_allowed()
            case self.path if is_user_id_path(self.path):
                body = get_body(self)
                response = update_user(self.path, body, self.user_service)
            case _:
                response = not_found()

        send_response(self, response)


def run_server() -> None:
    try:
        repository = JsonUserRepository(Path("data/users.json"))
    except JSONDecodeError:
        logger.critical("Failed to load user data", exc_info=True)
        return

    handler = partial(RequestHandler, user_service=UserService(repository))

    logger.info("Server started")
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            logger.info("Server stopped")
        finally:
            httpd.server_close()

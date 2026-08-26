import logging
import socketserver
from functools import partial
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from json import JSONDecodeError
from pathlib import Path
from typing import Any, Final

from http_crud_api.exceptions.service import (
    UserAlreadyExistsError,
    UserNotFoundError,
)
from http_crud_api.exceptions.validation import ValidationError
from http_crud_api.http.response import send_response_new
from http_crud_api.http.routes import (
    get_favicon,
    get_user,
    get_users,
    health,
    not_found,
)
from http_crud_api.http.utils import (
    body_to_json,
    get_body,
    is_user_id_path,
    send_json,
    send_response,
)
from http_crud_api.repositories.json_user import JsonUserRepository
from http_crud_api.service.user import UserService
from http_crud_api.validation.common import validate_json_object
from http_crud_api.validation.request import validate_id_from_path

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

        send_response_new(self, response)

    def do_POST(self) -> None:
        match self.path:
            case "/health":
                send_response(self, HTTPStatus.METHOD_NOT_ALLOWED)

            case "/users":
                body = get_body(self)
                data = body_to_json(body)

                try:
                    validated_data = validate_json_object(data)
                except ValidationError as exc:
                    send_response(
                        self, HTTPStatus.BAD_REQUEST, message=str(exc)
                    )
                    return

                try:
                    user = self.user_service.create(validated_data)
                except UserAlreadyExistsError as exc:
                    send_response(self, HTTPStatus.CONFLICT, message=str(exc))
                    return
                except ValidationError as exc:
                    send_response(
                        self, HTTPStatus.BAD_REQUEST, message=str(exc)
                    )
                    return

                send_json(
                    self,
                    {"id": str(user.id), "status": "created"},
                    HTTPStatus.CREATED,
                )

            case _:
                send_response(
                    self,
                    HTTPStatus.NOT_FOUND,
                    message="NOT FOUND",
                )

    def do_DELETE(self) -> None:
        match self.path:
            case "/health":
                send_response(self, HTTPStatus.METHOD_NOT_ALLOWED)
            case self.path if is_user_id_path(self.path):
                try:
                    user_id = validate_id_from_path(self.path)
                except ValidationError as exc:
                    send_response(
                        self,
                        HTTPStatus.BAD_REQUEST,
                        message=str(exc),
                    )
                    return

                try:
                    user = self.user_service.delete(user_id)
                except UserNotFoundError as exc:
                    send_response(
                        self,
                        HTTPStatus.NOT_FOUND,
                        message=str(exc),
                    )
                    return

                send_response(
                    self,
                    HTTPStatus.OK,
                    message=f"User {user.name} was deleted",
                )
            case _:
                send_response(
                    self,
                    HTTPStatus.NOT_FOUND,
                    message="NOT FOUND",
                )

    def do_PUT(self) -> None:
        match self.path:
            case "/health":
                send_response(self, HTTPStatus.METHOD_NOT_ALLOWED)
            case self.path if is_user_id_path(self.path):
                try:
                    user_id = validate_id_from_path(self.path)
                except ValidationError as exc:
                    send_response(
                        self,
                        HTTPStatus.BAD_REQUEST,
                        message=str(exc),
                    )
                    return

                body = get_body(self)
                data = body_to_json(body)

                try:
                    validated_data = validate_json_object(data)
                except ValidationError as exc:
                    send_response(
                        self, HTTPStatus.BAD_REQUEST, message=str(exc)
                    )
                    return

                try:
                    user = self.user_service.update(
                        validated_data, user_id=user_id
                    )
                except UserAlreadyExistsError as exc:
                    send_response(self, HTTPStatus.CONFLICT, message=str(exc))
                    return
                except UserNotFoundError as exc:
                    send_response(
                        self,
                        HTTPStatus.NOT_FOUND,
                        message=str(exc),
                    )
                    return
                except ValidationError as exc:
                    send_response(
                        self, HTTPStatus.BAD_REQUEST, message=str(exc)
                    )
                    return

                send_response(
                    self,
                    HTTPStatus.OK,
                    message=f"User {user.name} was updated",
                )
            case _:
                send_response(
                    self,
                    HTTPStatus.NOT_FOUND,
                    message="NOT FOUND",
                )


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

import logging
import socketserver
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from typing import Any, Final

from http_crud_api.exceptions.service import (
    UserAlreadyExistsError,
    UserNotFoundError,
)
from http_crud_api.http.utils import (
    body_to_json,
    get_body,
    is_user_id_path,
    send_json,
    send_response,
)
from http_crud_api.repositories.memory_user import InMemoryUserRepository
from http_crud_api.service.user import UserService
from http_crud_api.storage.users import users
from http_crud_api.validation.request import validate_id_from_path
from http_crud_api.validation.user import (
    ValidationError,
    validate_user_creation,
    validate_user_update,
)

PORT: Final = 8080

logger = logging.getLogger(__name__)

repository = InMemoryUserRepository(users)
user_service = UserService(repository)


class RequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        pass

    def do_GET(self) -> None:
        match self.path:
            case "/health":
                send_json(self, {"status": "ok"})

            case "/users":
                send_json(
                    self, [user.to_dict() for user in user_service.get_all()]
                )

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
                    user = user_service.get_by_id(user_id)
                except UserNotFoundError as exc:
                    send_response(
                        self,
                        HTTPStatus.NOT_FOUND,
                        message=str(exc),
                    )
                    return

                send_json(self, user.to_dict())

            case "/favicon.ico":
                send_response(self, HTTPStatus.NO_CONTENT)

            case _:
                send_response(
                    self,
                    HTTPStatus.NOT_FOUND,
                    message="NOT FOUND",
                )

    def do_POST(self) -> None:
        match self.path:
            case "/health":
                send_response(self, HTTPStatus.METHOD_NOT_ALLOWED)

            case "/users":
                body = get_body(self)
                data = body_to_json(body)

                if data is None:
                    send_response(
                        self, HTTPStatus.BAD_REQUEST, message="Invalid JSON"
                    )
                    return

                try:
                    result = validate_user_creation(data)
                except ValidationError as exc:
                    send_response(
                        self, HTTPStatus.BAD_REQUEST, message=str(exc)
                    )
                    return

                try:
                    user = user_service.create(
                        name=result.name, email=result.email
                    )
                except UserAlreadyExistsError as exc:
                    send_response(self, HTTPStatus.CONFLICT, message=str(exc))
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
                    user = user_service.delete(user_id)
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

                if data is None:
                    send_response(
                        self, HTTPStatus.BAD_REQUEST, message="Invalid JSON"
                    )
                    return

                try:
                    result = validate_user_update(data)
                except ValidationError as exc:
                    send_response(
                        self, HTTPStatus.BAD_REQUEST, message=str(exc)
                    )
                    return

                try:
                    user = user_service.update(
                        user_id, name=result.name, email=result.email
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
    logger.info("Server started")
    with socketserver.TCPServer(("", PORT), RequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            logger.info("Server stopped")
        finally:
            httpd.server_close()

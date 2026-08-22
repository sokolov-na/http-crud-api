import socketserver
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from typing import Any, Final
from uuid import UUID

from http_crud_api.http.utils import (
    body_to_json,
    get_body,
    is_user_id_path,
    send_json,
    send_not_found,
    send_response,
)
from http_crud_api.models.user import User
from http_crud_api.storage.users import users
from http_crud_api.validation.user import (
    ValidationError,
    validate_user_creation,
    validate_user_update,
)

PORT: Final = 8080


class InvalidUserIDError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


def get_user_id(handler: BaseHTTPRequestHandler) -> UUID | None:
    user_id_str: str = handler.path.strip("/").split("/")[-1]

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        return

    return user_id


def get_user_by_id(user_id: UUID, *, storage: list[User]) -> User | None:
    return next((user for user in storage if user.id == user_id), None)


def delete_user(user: User, *, storage: list[User]) -> None:
    storage.remove(user)


def add_user(user: User, *, storage: list[User]) -> None:
    storage.append(user)


def get_user_from_request(
    handler: BaseHTTPRequestHandler,
) -> User:
    user_id = get_user_id(handler)

    if user_id is None:
        raise InvalidUserIDError("Invalid ID")

    user = get_user_by_id(user_id, storage=users)

    if user is None:
        raise UserNotFoundError("User not found")

    return user


class RequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        pass

    def do_GET(self) -> None:
        match self.path:
            case "/health":
                send_json(self, {"status": "ok"})

            case "/users":
                send_json(self, [user.to_dict() for user in users])

            case self.path if is_user_id_path(self):
                try:
                    user = get_user_from_request(self)
                except InvalidUserIDError as exc:
                    send_response(
                        self, HTTPStatus.BAD_REQUEST, message=str(exc)
                    )
                    return
                except UserNotFoundError as exc:
                    send_response(self, HTTPStatus.NOT_FOUND, message=str(exc))
                    return

                send_json(self, user.to_dict())

            case "/favicon.ico":
                self.send_response_only(HTTPStatus.NO_CONTENT)
                self.end_headers()

            case _:
                send_not_found(self)

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

                user = User(name=result.name, email=result.email)
                add_user(user, storage=users)

                send_json(
                    self,
                    {"id": str(user.id), "status": "created"},
                    HTTPStatus.CREATED,
                )

            case _:
                send_not_found(self)

    def do_DELETE(self) -> None:
        match self.path:
            case self.path if is_user_id_path(self):
                try:
                    user = get_user_from_request(self)
                except InvalidUserIDError as exc:
                    send_response(
                        self, HTTPStatus.BAD_REQUEST, message=str(exc)
                    )
                    return
                except UserNotFoundError as exc:
                    send_response(self, HTTPStatus.NOT_FOUND, message=str(exc))
                    return

                delete_user(user, storage=users)
                send_response(
                    self,
                    HTTPStatus.OK,
                    message=f"User {user.name} was deleted",
                )
            case _:
                send_not_found(self)

    def do_PUT(self) -> None:
        match self.path:
            case self.path if is_user_id_path(self):
                try:
                    user = get_user_from_request(self)
                except InvalidUserIDError as exc:
                    send_response(
                        self, HTTPStatus.BAD_REQUEST, message=str(exc)
                    )
                    return
                except UserNotFoundError as exc:
                    send_response(self, HTTPStatus.NOT_FOUND, message=str(exc))
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

                if result.name is not None:
                    user.name = result.name

                if result.email is not None:
                    user.email = result.email

                send_response(
                    self,
                    HTTPStatus.OK,
                    message=f"User {user.name} was updated",
                )
            case _:
                send_not_found(self)


def run_server() -> None:
    with socketserver.TCPServer(("", PORT), RequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.server_close()

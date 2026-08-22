import json
import socketserver
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from typing import Any, Final
from uuid import UUID

from http_crud_api.models.user import User
from http_crud_api.storage.users import users
from http_crud_api.validation.user import ValidationError, validate_user_data

PORT: Final = 8080


class RequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        pass

    def do_GET(self) -> None:
        match self.path:
            case "/health":
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                data = {"status": "ok"}
                self.wfile.write(json.dumps(data).encode())

            case "/users":
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(
                    json.dumps([user.to_dict() for user in users]).encode()
                )

            case self.path if (
                self.path.startswith("/users/")
                and len(self.path.strip("/").split("/")) == 2
            ):
                user_id_str = self.path.strip("/").split("/")[-1]

                try:
                    user_id = UUID(user_id_str)
                except ValueError:
                    self.send_response(HTTPStatus.BAD_REQUEST)
                    self.end_headers()
                    self.wfile.write(b"Invalid ID")
                    return

                user = next(
                    (user for user in users if user.id == user_id), None
                )

                if user is None:
                    self.send_response(HTTPStatus.NOT_FOUND)
                    self.end_headers()
                    self.wfile.write(b"User not found")
                    return

                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(user.to_dict()).encode())

            case "/favicon.ico":
                self.send_response_only(HTTPStatus.NO_CONTENT)
                self.end_headers()

            case _:
                self.send_response(HTTPStatus.NOT_FOUND)
                self.end_headers()
                self.wfile.write(b"NOT FOUND")

    def do_POST(self) -> None:
        match self.path:
            case "/health":
                self.send_response(HTTPStatus.METHOD_NOT_ALLOWED)
                self.end_headers()

            case "/users":
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length)

                try:
                    data = json.loads(body)
                except json.JSONDecodeError:
                    self.send_response(HTTPStatus.BAD_REQUEST)
                    self.end_headers()
                    self.wfile.write(b"Invalid JSON")
                    return

                try:
                    result = validate_user_data(data)
                except ValidationError as exc:
                    self.send_response(HTTPStatus.BAD_REQUEST)
                    self.end_headers()
                    self.wfile.write(str(exc).encode())
                    return

                user = User(name=result.name, email=result.email)
                users.append(user)

                self.send_response(HTTPStatus.CREATED)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                response = {"id": str(user.id), "status": "created"}
                self.wfile.write(json.dumps(response).encode())

            case _:
                self.send_response(HTTPStatus.NOT_FOUND)
                self.end_headers()
                self.wfile.write(b"NOT FOUND")


def run_server() -> None:
    with socketserver.TCPServer(("", PORT), RequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.server_close()

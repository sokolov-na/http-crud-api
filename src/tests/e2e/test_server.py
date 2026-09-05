import subprocess
import sys
import time
from collections.abc import Generator
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any
from uuid import UUID, uuid7

import pytest
import requests
from dotenv import load_dotenv

from http_crud_api.http.response import ResponseFormat
from http_crud_api.models.user import User
from http_crud_api.settings import Settings

load_dotenv(".env.test")
request_timeout = 0.2
settings = Settings()


@dataclass
class Server:
    base_url: str

    def request(
        self, method: str, path: str, **kwargs: Any
    ) -> requests.Response:
        """Send an HTTP request to the test server."""

        return requests.request(
            method,
            f"{self.base_url}{path}",
            timeout=request_timeout,
            **kwargs,
        )


class TestServer:
    @pytest.fixture(scope="session")
    def server(self) -> Generator[Server, Any, Any]:
        proc = subprocess.Popen(
            [sys.executable, "-m", "http_crud_api.main"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        base_url = f"http://{settings.http_host}:{settings.http_port}"
        try:
            for _ in range(5):
                if proc.poll() is not None:
                    _, errs = proc.communicate()
                    raise RuntimeError(f"Server crashed:\n{errs}")
                try:
                    resp = requests.get(
                        base_url + "/health", timeout=request_timeout
                    )
                    if resp.status_code == HTTPStatus.OK:
                        break
                except requests.RequestException, TimeoutError:
                    time.sleep(0.5)
            else:
                proc.terminate()
                _, errs = proc.communicate(timeout=2)
                raise RuntimeError(
                    "The server is not responding to the health-check:\n"
                    f"{errs.decode()}"
                )

            yield Server(base_url)
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()

            data_file = settings.data_dir / "users.json"
            log_file = settings.log_dir / "app.jsonl"

            for _ in range(5):
                try:
                    if data_file.exists():
                        data_file.unlink()
                    if log_file.exists():
                        log_file.unlink()
                    break
                except PermissionError:
                    time.sleep(0.5)
            else:
                raise RuntimeError(
                    f"Could not delete files after 5 attempts: "
                    f"data_file={data_file}, log_file={log_file}"
                )

            for directory in (data_file.parent, log_file.parent):
                if directory.exists():
                    directory.rmdir()

    def test_health_endpoint_returns_ok(self, server: Server):
        resp = server.request("GET", "/health")

        assert resp.status_code == HTTPStatus.OK
        assert resp.headers["Content-Type"] == ResponseFormat.JSON.value
        assert resp.json() == {"status": "ok"}

    @pytest.mark.parametrize(
        "method",
        [
            "POST",
            "PUT",
            "DELETE",
        ],
    )
    def test_health_rejects_unsupported_methods(
        self,
        server: Server,
        method: str,
    ):
        resp = server.request(
            method,
            "/health",
        )

        assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    @pytest.mark.parametrize(
        "method",
        [
            "POST",
            "PUT",
            "DELETE",
        ],
    )
    @pytest.mark.parametrize(
        "path",
        [
            "/",
            "/users/something",
            "/health/something",
            "/comments",
        ],
    )
    def test_unknown_paths_return_not_found(
        self,
        server: Server,
        method: str,
        path: str,
    ):
        resp = server.request(method, path)

        assert resp.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.parametrize(
        "method",
        [
            "PUT",
            "DELETE",
        ],
    )
    def test_users_collection_rejects_unsupported_methods(
        self,
        server: Server,
        method: str,
    ):
        resp = server.request(
            method,
            "/users",
        )

        assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    def test_user_crud_happy_flow(self, server: Server):
        resp = server.request("GET", "/users")

        assert resp.status_code == HTTPStatus.OK
        assert resp.headers["Content-Type"] == ResponseFormat.JSON.value
        assert resp.json() == []

        resp = server.request(
            "POST",
            "/users",
            json={"name": "John", "email": "example@google.com"},
        )

        assert resp.status_code == HTTPStatus.CREATED
        assert resp.headers["Content-Type"] == ResponseFormat.JSON.value
        response_data = resp.json()
        assert response_data["id"] is not None
        assert response_data["status"] == "created"
        user = User(
            name="John",
            email="example@google.com",
            id=UUID(response_data["id"]),
        )

        resp = server.request("GET", "/users")

        assert resp.status_code == HTTPStatus.OK
        assert resp.headers["Content-Type"] == ResponseFormat.JSON.value
        assert resp.json() == [user.to_dict()]

        resp = server.request(
            "GET",
            f"/users/{user.id}",
        )

        assert resp.status_code == HTTPStatus.OK
        assert resp.headers["Content-Type"] == ResponseFormat.JSON.value
        assert resp.json() == user.to_dict()

        resp = server.request(
            "PUT",
            f"/users/{user.id}",
            json={"name": "Jane"},
        )

        assert resp.status_code == HTTPStatus.OK
        assert resp.headers["Content-Type"] == ResponseFormat.JSON.value
        assert resp.json()["id"] == str(user.id)
        assert resp.json()["status"] == "updated"
        user.name = "Jane"

        resp = server.request(
            "GET",
            f"/users/{user.id}",
        )

        assert resp.status_code == HTTPStatus.OK
        assert resp.headers["Content-Type"] == ResponseFormat.JSON.value
        assert resp.json() == user.to_dict()

        resp = server.request(
            "PUT",
            f"/users/{user.id}",
            json={"name": "john"},
        )

        assert resp.status_code == HTTPStatus.OK
        assert resp.headers["Content-Type"] == ResponseFormat.JSON.value
        assert resp.json()["id"] == str(user.id)
        assert resp.json()["status"] == "updated"
        user.name = "John"

        resp = server.request(
            "GET",
            f"/users/{user.id}",
        )

        assert resp.status_code == HTTPStatus.OK
        assert resp.headers["Content-Type"] == ResponseFormat.JSON.value
        assert resp.json() == user.to_dict()

        resp = server.request(
            "PUT",
            f"/users/{user.id}",
            json={"name": "jANE"},
        )

        assert resp.status_code == HTTPStatus.OK
        assert resp.headers["Content-Type"] == ResponseFormat.JSON.value
        assert resp.json()["id"] == str(user.id)
        assert resp.json()["status"] == "updated"
        user.name = "Jane"

        resp = server.request(
            "GET",
            f"/users/{user.id}",
        )

        assert resp.status_code == HTTPStatus.OK
        assert resp.headers["Content-Type"] == ResponseFormat.JSON.value
        assert resp.json() == user.to_dict()

        resp = server.request(
            "PUT",
            f"/users/{user.id}",
            json={"email": "example@gmail.com"},
        )

        assert resp.status_code == HTTPStatus.OK
        assert resp.headers["Content-Type"] == ResponseFormat.JSON.value
        assert resp.json()["id"] == str(user.id)
        assert resp.json()["status"] == "updated"
        user.email = "example@gmail.com"

        resp = server.request(
            "GET",
            f"/users/{user.id}",
        )

        assert resp.status_code == HTTPStatus.OK
        assert resp.headers["Content-Type"] == ResponseFormat.JSON.value
        assert resp.json() == user.to_dict()

        resp = server.request(
            "PUT",
            f"/users/{user.id}",
            json={"name": "John", "email": "example@google.com"},
        )

        assert resp.status_code == HTTPStatus.OK
        assert resp.headers["Content-Type"] == ResponseFormat.JSON.value
        assert resp.json()["id"] == str(user.id)
        assert resp.json()["status"] == "updated"
        user.name = "John"
        user.email = "example@google.com"

        resp = server.request(
            "GET",
            f"/users/{user.id}",
        )

        assert resp.status_code == HTTPStatus.OK
        assert resp.headers["Content-Type"] == ResponseFormat.JSON.value
        assert resp.json() == user.to_dict()

        resp = server.request(
            "GET",
            "/users",
        )

        assert resp.status_code == HTTPStatus.OK
        assert resp.headers["Content-Type"] == ResponseFormat.JSON.value
        assert resp.json() == [user.to_dict()]

        resp = server.request(
            "DELETE",
            f"/users/{user.id}",
        )

        assert resp.status_code == HTTPStatus.OK
        assert resp.headers["Content-Type"] == ResponseFormat.JSON.value
        assert resp.json()["id"] == str(user.id)
        assert resp.json()["status"] == "deleted"

        resp = server.request(
            "GET",
            "/users",
        )

        assert resp.status_code == HTTPStatus.OK
        assert resp.headers["Content-Type"] == ResponseFormat.JSON.value
        assert resp.json() == []

    @pytest.mark.parametrize(
        "json_value",
        [
            None,
            {},
            {"name": "John"},
            {"email": "example@gmail.com"},
            {"name": "John", "email": "bad@bad.bad"},
            123,
            "string",
            [1, 2, 3, 4, 5],
        ],
    )
    def test_create_user_rejects_invalid_payloads(
        self,
        server: Server,
        json_value: Any,
    ):
        resp = server.request(
            "POST",
            "/users",
            json=json_value,
        )

        assert resp.status_code == HTTPStatus.BAD_REQUEST

    def test_create_user_rejects_duplicate_email(self, server: Server):
        resp = server.request(
            "POST",
            "/users",
            json={"name": "John", "email": "example@gmail.com"},
        )

        user_id = resp.json()["id"]
        assert resp.status_code == HTTPStatus.CREATED

        resp = server.request(
            "POST",
            "/users",
            json={"name": "John", "email": "example@gmail.com"},
        )

        assert resp.status_code == HTTPStatus.CONFLICT

        server.request("DELETE", f"/users/{user_id}")
        assert server.request("GET", "/users").json() == []

    def test_get_user_returns_not_found_for_missing_user(self, server: Server):
        resp = server.request(
            "GET",
            f"/users/{uuid7()}",
        )

        assert resp.status_code == HTTPStatus.NOT_FOUND

    def test_update_user_rejects_invalid_or_duplicate_email(
        self, server: Server
    ):
        resp = server.request(
            "POST",
            "/users",
            json={"name": "John", "email": "example@gmail.com"},
        )

        user1_id = resp.json()["id"]

        assert resp.status_code == HTTPStatus.CREATED

        resp = server.request(
            "POST",
            "/users",
            json={"name": "John", "email": "example@yandex.ru"},
        )

        user2_id = resp.json()["id"]

        assert resp.status_code == HTTPStatus.CREATED

        resp = server.request(
            "PUT",
            f"/users/{user2_id}",
            json={"email": "example@gmail.com"},
        )

        assert resp.status_code == HTTPStatus.CONFLICT

        resp = server.request(
            "PUT",
            f"/users/{user2_id}",
            json={"email": "bad@bad.bad"},
        )

        assert resp.status_code == HTTPStatus.BAD_REQUEST

        server.request("DELETE", f"/users/{user1_id}")
        server.request("DELETE", f"/users/{user2_id}")
        assert server.request("GET", "/users").json() == []

    def test_update_user_returns_not_found_for_missing_user(
        self, server: Server
    ):
        resp = server.request(
            "PUT",
            f"/users/{uuid7()}",
            json={"email": "example@google.com"},
        )

        assert resp.status_code == HTTPStatus.NOT_FOUND

    def test_delete_user_returns_not_found_for_missing_user(
        self, server: Server
    ):
        resp = server.request("DELETE", f"/users/{uuid7()}")

        assert resp.status_code == HTTPStatus.NOT_FOUND

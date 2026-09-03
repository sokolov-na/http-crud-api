import subprocess
import sys
import time
from collections.abc import Generator
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any
from uuid import UUID

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

        resp = requests.get(
            f"{server.base_url}/users/{user.id}",
            timeout=request_timeout,
        )

        assert resp.status_code == HTTPStatus.OK
        assert resp.headers["Content-Type"] == ResponseFormat.JSON.value
        assert resp.json() == user.to_dict()

        resp = requests.put(
            f"{server.base_url}/users/{user.id}",
            json={"name": "Jane"},
            timeout=request_timeout,
        )

        assert resp.status_code == HTTPStatus.OK
        assert resp.headers["Content-Type"] == ResponseFormat.JSON.value
        assert resp.json()["id"] == str(user.id)
        assert resp.json()["status"] == "updated"
        user.name = "Jane"

        resp = requests.get(
            f"{server.base_url}/users/{user.id}",
            timeout=request_timeout,
        )

        assert resp.status_code == HTTPStatus.OK
        assert resp.headers["Content-Type"] == ResponseFormat.JSON.value
        assert resp.json() == user.to_dict()

        resp = requests.put(
            f"{server.base_url}/users/{user.id}",
            json={"email": "example@gmail.com"},
            timeout=request_timeout,
        )

        assert resp.status_code == HTTPStatus.OK
        assert resp.headers["Content-Type"] == ResponseFormat.JSON.value
        assert resp.json()["id"] == str(user.id)
        assert resp.json()["status"] == "updated"
        user.email = "example@gmail.com"

        resp = requests.get(
            f"{server.base_url}/users/{user.id}",
            timeout=request_timeout,
        )

        assert resp.status_code == HTTPStatus.OK
        assert resp.headers["Content-Type"] == ResponseFormat.JSON.value
        assert resp.json() == user.to_dict()

        resp = requests.put(
            f"{server.base_url}/users/{user.id}",
            json={"name": "John", "email": "example@google.com"},
            timeout=request_timeout,
        )

        assert resp.status_code == HTTPStatus.OK
        assert resp.headers["Content-Type"] == ResponseFormat.JSON.value
        assert resp.json()["id"] == str(user.id)
        assert resp.json()["status"] == "updated"
        user.name = "John"
        user.email = "example@google.com"

        resp = requests.get(
            f"{server.base_url}/users/{user.id}",
            timeout=request_timeout,
        )

        assert resp.status_code == HTTPStatus.OK
        assert resp.headers["Content-Type"] == ResponseFormat.JSON.value
        assert resp.json() == user.to_dict()

        resp = requests.get(
            f"{server.base_url}/users",
            timeout=request_timeout,
        )

        assert resp.status_code == HTTPStatus.OK
        assert resp.headers["Content-Type"] == ResponseFormat.JSON.value
        assert resp.json() == [user.to_dict()]

        resp = requests.delete(
            f"{server.base_url}/users/{user.id}",
            timeout=request_timeout,
        )

        assert resp.status_code == HTTPStatus.OK
        assert resp.headers["Content-Type"] == ResponseFormat.JSON.value
        assert resp.json()["id"] == str(user.id)
        assert resp.json()["status"] == "deleted"

        resp = requests.get(
            f"{server.base_url}/users",
            timeout=request_timeout,
        )

        assert resp.status_code == HTTPStatus.OK
        assert resp.headers["Content-Type"] == ResponseFormat.JSON.value
        assert resp.json() == []

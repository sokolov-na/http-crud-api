from http.server import BaseHTTPRequestHandler
from io import BytesIO
from unittest.mock import Mock
from uuid import uuid7

import pytest

from http_crud_api.http.utils import get_body, is_user_id_path


@pytest.mark.parametrize(
    "body",
    [
        b"{'name': 'John'}",
        b"{'email': 'example@gmail.com'}",
        b"8080",
    ],
)
def test_get_body_returns_request_body(body: bytes):
    handler = Mock(spec=BaseHTTPRequestHandler)
    handler.headers = {"Content-Length": str(len(body))}
    handler.rfile = BytesIO(body)

    assert get_body(handler) == body


@pytest.mark.parametrize(
    "path, ans",
    [
        # valid user endpoints
        ("/users/{}", True),
        ("/users/{}/", True),
        # other endpoints
        ("/books/{}", False),
        ("/users/groups/", False),
        # invalid paths
        ("/", False),
        ("", False),
    ],
)
def test_is_user_id_path_returns_expected_result(path: str, ans: bool):
    formated_path = path.format(uuid7())
    assert is_user_id_path(formated_path) == ans

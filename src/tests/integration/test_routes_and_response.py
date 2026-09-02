import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from unittest.mock import MagicMock, Mock, create_autospec

import pytest

from http_crud_api.http.response import ResponseFormat
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
from http_crud_api.models.user import User
from http_crud_api.service.user import UserService


class TestHTTPRoutesAndResponses:
    @pytest.fixture
    def handler(self) -> Mock:
        _handler = Mock(spec=BaseHTTPRequestHandler)
        _handler.command = "METHOD"
        _handler.path = "/"
        _handler.send_response.return_value = None
        _handler.send_response_only.return_value = None
        _handler.send_header.return_value = None
        _handler.end_headers.return_value = None
        _handler.wfile = Mock()
        return _handler

    @pytest.fixture
    def sample_user(self) -> User:
        return User(
            name="John",
            email="example@google.com",
        )

    @pytest.fixture
    def mock_service(self) -> MagicMock:
        return create_autospec(UserService, instance=True)

    def test_health_route_sends_json_response(
        self,
        handler: Mock,
    ):
        result = health()
        result.send(handler)

        handler.send_response.assert_called_once_with(HTTPStatus.OK)
        handler.send_header.assert_called_once_with(
            "Content-Type", ResponseFormat.JSON.value
        )
        handler.wfile.write.assert_called_once_with(b'{"status": "ok"}')

    def test_get_users_route_sends_json_response(
        self,
        handler: Mock,
        mock_service: MagicMock,
        sample_user: User,
    ):
        mock_service.get_all.return_value = [sample_user]

        result = get_users(mock_service)
        result.send(handler)

        handler.send_response.assert_called_once_with(HTTPStatus.OK)
        handler.send_header.assert_called_once_with(
            "Content-Type", ResponseFormat.JSON.value
        )
        handler.wfile.write.assert_called_once_with(
            json.dumps([sample_user.to_dict()]).encode()
        )

    def test_get_user_route_sends_json_response(
        self,
        handler: Mock,
        mock_service: MagicMock,
        sample_user: User,
    ):
        path = f"/users/{sample_user.id}"
        mock_service.get_by_id.return_value = sample_user

        result = get_user(path, mock_service)
        result.send(handler)

        handler.send_response.assert_called_once_with(HTTPStatus.OK)
        handler.send_header.assert_called_once_with(
            "Content-Type", ResponseFormat.JSON.value
        )
        handler.wfile.write.assert_called_once_with(
            json.dumps(sample_user.to_dict()).encode()
        )

    def test_get_favicon_route_sends_empty_response(
        self,
        handler: Mock,
    ):
        result = get_favicon()
        result.send(handler)

        handler.send_response_only.assert_called_once_with(
            HTTPStatus.NO_CONTENT
        )
        handler.send_header.assert_not_called()
        handler.wfile.write.assert_not_called()

    def test_not_allowed_route_sends_empty_response(
        self,
        handler: Mock,
    ):
        result = not_allowed()
        result.send(handler)

        handler.send_response_only.assert_called_once_with(
            HTTPStatus.METHOD_NOT_ALLOWED
        )
        handler.send_header.assert_not_called()
        handler.wfile.write.assert_not_called()

    def test_not_found_route_sends_text_response(
        self,
        handler: Mock,
    ):
        result = not_found()
        result.send(handler)

        handler.send_response.assert_called_once_with(HTTPStatus.NOT_FOUND)
        handler.send_header.assert_called_once_with(
            "Content-Type", ResponseFormat.TEXT.value
        )
        handler.wfile.write.assert_called_once_with(b"Not Found")

    def test_create_user_route_sends_json_response(
        self,
        handler: Mock,
        mock_service: MagicMock,
        sample_user: User,
    ):
        body = b"{}"
        mock_service.create.return_value = sample_user

        result = create_user(body, mock_service)
        result.send(handler)

        handler.send_response.assert_called_once_with(HTTPStatus.CREATED)
        handler.send_header.assert_called_once_with(
            "Content-Type", ResponseFormat.JSON.value
        )
        handler.wfile.write.assert_called_once_with(
            json.dumps(
                {"id": str(sample_user.id), "status": "created"}
            ).encode()
        )

    def test_delete_user_route_sends_json_response(
        self,
        handler: Mock,
        mock_service: MagicMock,
        sample_user: User,
    ):
        path = f"/users/{sample_user.id}"
        mock_service.delete.return_value = sample_user

        result = delete_user(path, mock_service)
        result.send(handler)

        handler.send_response.assert_called_once_with(HTTPStatus.OK)
        handler.send_header.assert_called_once_with(
            "Content-Type", ResponseFormat.JSON.value
        )
        handler.wfile.write.assert_called_once_with(
            json.dumps(
                {"id": str(sample_user.id), "status": "deleted"}
            ).encode()
        )

    def test_update_user_route_sends_json_response(
        self,
        handler: Mock,
        mock_service: MagicMock,
        sample_user: User,
    ):
        path = f"/users/{sample_user.id}"
        body = b"{}"
        mock_service.update.return_value = sample_user

        result = update_user(path, body, mock_service)
        result.send(handler)

        handler.send_response.assert_called_once_with(HTTPStatus.OK)
        handler.send_header.assert_called_once_with(
            "Content-Type", ResponseFormat.JSON.value
        )
        handler.wfile.write.assert_called_once_with(
            json.dumps(
                {"id": str(sample_user.id), "status": "updated"}
            ).encode()
        )

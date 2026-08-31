from http import HTTPStatus
from unittest.mock import MagicMock, Mock, create_autospec
from uuid import uuid7

import pytest

from http_crud_api.http.response import Response
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


class TestHTTPRoutes:
    @pytest.fixture
    def mock_service(self) -> MagicMock:
        return create_autospec(UserService, instance=True)

    @pytest.fixture
    def sample_user(self) -> User:
        return User(
            id=uuid7(),
            name="John",
            email="example@google.com",
        )

    @pytest.fixture
    def mock_response_factory(self) -> Mock:
        mock = Mock(spec=Response)
        return Mock(return_value=mock)

    def test_health_returns_ok_response(
        self,
        mock_response_factory: Mock,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.setattr(Response, "json", mock_response_factory)

        result = health()

        assert result is mock_response_factory.return_value
        mock_response_factory.assert_called_once_with(
            HTTPStatus.OK,
            {"status": "ok"},
        )

    def test_get_users_returns_users_response(
        self,
        mock_response_factory: Mock,
        mock_service: MagicMock,
        sample_user: User,
        monkeypatch: pytest.MonkeyPatch,
    ):
        mock_service.get_all.return_value = [sample_user]
        monkeypatch.setattr(Response, "json", mock_response_factory)

        result = get_users(mock_service)

        assert result is mock_response_factory.return_value
        mock_response_factory.assert_called_once_with(
            HTTPStatus.OK,
            [sample_user.to_dict()],
        )

        mock_service.get_all.assert_called_once_with()

    def test_get_user_returns_user_response(
        self,
        mock_response_factory: Mock,
        mock_service: MagicMock,
        sample_user: User,
        monkeypatch: pytest.MonkeyPatch,
    ):
        path = f"/users/{sample_user.id}"
        mock_service.get_by_id.return_value = sample_user
        monkeypatch.setattr(Response, "json", mock_response_factory)

        result = get_user(path, mock_service)

        assert result is mock_response_factory.return_value
        mock_response_factory.assert_called_once_with(
            HTTPStatus.OK,
            sample_user.to_dict(),
        )

        mock_service.get_by_id.assert_called_once_with(sample_user.id)

    def test_get_favicon_returns_no_content_response(
        self,
        mock_response_factory: Mock,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.setattr(Response, "empty", mock_response_factory)

        result = get_favicon()

        assert result is mock_response_factory.return_value
        mock_response_factory.assert_called_once_with(
            HTTPStatus.NO_CONTENT,
        )

    def test_not_allowed_returns_method_not_allowed_response(
        self,
        mock_response_factory: Mock,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.setattr(Response, "empty", mock_response_factory)

        result = not_allowed()

        assert result is mock_response_factory.return_value
        mock_response_factory.assert_called_once_with(
            HTTPStatus.METHOD_NOT_ALLOWED,
        )

    def test_not_found_returns_not_found_response(
        self,
        mock_response_factory: Mock,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.setattr(Response, "text", mock_response_factory)

        result = not_found()

        assert result is mock_response_factory.return_value
        mock_response_factory.assert_called_once_with(
            HTTPStatus.NOT_FOUND,
            "Not Found",
        )

    def test_create_user_returns_created_response(
        self,
        mock_response_factory: Mock,
        mock_service: MagicMock,
        sample_user: User,
        monkeypatch: pytest.MonkeyPatch,
    ):
        body = b"{}"
        mock_service.create.return_value = sample_user
        monkeypatch.setattr(Response, "json", mock_response_factory)

        result = create_user(body, mock_service)

        assert result is mock_response_factory.return_value
        mock_response_factory.assert_called_once_with(
            HTTPStatus.CREATED,
            {"id": str(sample_user.id), "status": "created"},
        )

        mock_service.create.assert_called_once_with({})

    def test_delete_user_returns_deleted_response(
        self,
        mock_response_factory: Mock,
        mock_service: MagicMock,
        sample_user: User,
        monkeypatch: pytest.MonkeyPatch,
    ):
        path = f"/users/{sample_user.id}"
        mock_service.delete.return_value = sample_user
        monkeypatch.setattr(Response, "json", mock_response_factory)

        result = delete_user(path, mock_service)

        assert result is mock_response_factory.return_value
        mock_response_factory.assert_called_once_with(
            HTTPStatus.OK,
            {"id": str(sample_user.id), "status": "deleted"},
        )

        mock_service.delete.assert_called_once_with(sample_user.id)

    def test_update_user_returns_updated_response(
        self,
        mock_response_factory: Mock,
        mock_service: MagicMock,
        sample_user: User,
        monkeypatch: pytest.MonkeyPatch,
    ):
        path = f"/users/{sample_user.id}"
        body = b"{}"
        mock_service.update.return_value = sample_user
        monkeypatch.setattr(Response, "json", mock_response_factory)

        result = update_user(path, body, mock_service)

        assert result is mock_response_factory.return_value
        mock_response_factory.assert_called_once_with(
            HTTPStatus.OK,
            {"id": str(sample_user.id), "status": "updated"},
        )

        mock_service.update.assert_called_once_with(
            {},
            user_id=sample_user.id,
        )

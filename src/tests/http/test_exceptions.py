from http import HTTPStatus
from unittest.mock import Mock

import pytest

from http_crud_api.exceptions.service import (
    UserAlreadyExistsError,
    UserNotFoundError,
)
from http_crud_api.exceptions.validation import ValidationError
from http_crud_api.http.exceptions import handle_exception
from http_crud_api.http.response import Response


class TestHTTPExceptionHandling:
    @pytest.fixture
    def mock_response_factory(self) -> Mock:
        mock = Mock(spec=Response)
        return Mock(return_value=mock)

    def test_validation_error_returns_bad_request(
        self,
        mock_response_factory: Mock,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.setattr(Response, "text", mock_response_factory)

        result = handle_exception(ValidationError("message"))

        assert result is mock_response_factory.return_value
        mock_response_factory.assert_called_once_with(
            HTTPStatus.BAD_REQUEST,
            "message",
        )

    def test_user_already_exists_error_returns_conflict(
        self,
        mock_response_factory: Mock,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.setattr(Response, "text", mock_response_factory)

        result = handle_exception(UserAlreadyExistsError("message"))

        assert result is mock_response_factory.return_value
        mock_response_factory.assert_called_once_with(
            HTTPStatus.CONFLICT,
            "message",
        )

    def test_user_not_found_error_returns_not_found(
        self,
        mock_response_factory: Mock,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.setattr(Response, "text", mock_response_factory)

        result = handle_exception(UserNotFoundError("message"))

        assert result is mock_response_factory.return_value
        mock_response_factory.assert_called_once_with(
            HTTPStatus.NOT_FOUND,
            "message",
        )

    @pytest.mark.parametrize(
        "exc",
        [
            ValueError("message"),
            TypeError("message"),
            KeyError("message"),
            IndexError("message"),
        ],
    )
    def test_unhandled_exception_returns_internal_server_error(
        self,
        exc: Exception,
        mock_response_factory: Mock,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.setattr(Response, "empty", mock_response_factory)

        result = handle_exception(exc)

        assert result is mock_response_factory.return_value
        mock_response_factory.assert_called_once_with(
            HTTPStatus.INTERNAL_SERVER_ERROR
        )

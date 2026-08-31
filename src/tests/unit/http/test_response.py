from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from unittest.mock import Mock

import pytest

from http_crud_api.http.response import Response, ResponseFormat


class TestResponse:
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

    def test_json_response_sends_json(self, handler: Mock):
        response = Response.json(HTTPStatus.OK, {"status": "ok"})
        response.send(handler)

        handler.send_response.assert_called_once_with(HTTPStatus.OK)
        handler.send_header.assert_called_once_with(
            "Content-Type", ResponseFormat.JSON.value
        )
        handler.end_headers.assert_called_once_with()
        handler.wfile.write.assert_called_once_with(b'{"status": "ok"}')

    def test_text_response_sends_text(self, handler: Mock):
        response = Response.text(HTTPStatus.NOT_FOUND, "TEXT")
        response.send(handler)

        handler.send_response.assert_called_once_with(HTTPStatus.NOT_FOUND)
        handler.send_header.assert_called_once_with(
            "Content-Type", ResponseFormat.TEXT.value
        )
        handler.end_headers.assert_called_once_with()
        handler.wfile.write.assert_called_once_with(b"TEXT")

    def test_empty_response_sends_no_content(self, handler: Mock):
        response = Response.empty(HTTPStatus.NO_CONTENT)
        response.send(handler)

        handler.send_response_only.assert_called_once_with(
            HTTPStatus.NO_CONTENT
        )
        handler.end_headers.assert_called_once_with()
        handler.wfile.write.assert_not_called()

    def test_json_response_raises_for_invalid_data(self, handler: Mock):
        response = Response.json(HTTPStatus.OK, b"bytes")
        with pytest.raises(TypeError):
            response.send(handler)

    def test_text_response_raises_for_non_string_data(self, handler: Mock):
        response = Response(HTTPStatus.CONFLICT, 409, ResponseFormat.TEXT)
        with pytest.raises(TypeError):
            response.send(handler)

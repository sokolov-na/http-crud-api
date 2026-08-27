from http import HTTPStatus

from http_crud_api.exceptions.service import (
    UserAlreadyExistsError,
    UserNotFoundError,
)
from http_crud_api.exceptions.validation import ValidationError
from http_crud_api.http.response import Response


def handle_exception(exc: Exception) -> Response:
    if isinstance(exc, ValidationError):
        return Response.text(HTTPStatus.BAD_REQUEST, str(exc))

    if isinstance(exc, UserAlreadyExistsError):
        return Response.text(HTTPStatus.CONFLICT, str(exc))

    if isinstance(exc, UserNotFoundError):
        return Response.text(HTTPStatus.NOT_FOUND, str(exc))

    return Response.empty(HTTPStatus.INTERNAL_SERVER_ERROR)

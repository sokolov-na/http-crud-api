from http import HTTPStatus

from http_crud_api.exceptions.service import UserNotFoundError
from http_crud_api.exceptions.validation import ValidationError
from http_crud_api.http.response import Response, ResponseFormat
from http_crud_api.service.user import UserService
from http_crud_api.validation.request import validate_id_from_path


def health() -> Response:
    return Response(HTTPStatus.OK, {"status": "ok"})


def get_users(user_service: UserService) -> Response:
    return Response(
        HTTPStatus.OK,
        [user.to_dict() for user in user_service.get_all()],
    )


def get_user(path: str, user_service: UserService) -> Response:
    try:
        user_id = validate_id_from_path(path)
    except ValidationError:
        raise

    try:
        user = user_service.get_by_id(user_id)
    except UserNotFoundError:
        raise

    return Response(HTTPStatus.OK, user.to_dict())


def get_favicon() -> Response:
    return Response(HTTPStatus.NO_CONTENT)


def not_found() -> Response:
    return Response(
        HTTPStatus.NOT_FOUND, data="Not found", format=ResponseFormat.TEXT
    )

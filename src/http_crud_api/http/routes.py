from http import HTTPStatus

from http_crud_api.exceptions.service import (
    UserAlreadyExistsError,
    UserNotFoundError,
)
from http_crud_api.exceptions.validation import ValidationError
from http_crud_api.http.response import Response, ResponseFormat
from http_crud_api.service.user import UserService
from http_crud_api.validation.common import validate_json_object
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
    except ValidationError as exc:
        return Response(
            HTTPStatus.BAD_REQUEST, str(exc), format=ResponseFormat.TEXT
        )

    try:
        user = user_service.get_by_id(user_id)
    except UserNotFoundError as exc:
        return Response(
            HTTPStatus.NOT_FOUND, str(exc), format=ResponseFormat.TEXT
        )

    return Response(HTTPStatus.OK, user.to_dict())


def get_favicon() -> Response:
    return Response(HTTPStatus.NO_CONTENT)


def not_found() -> Response:
    return Response(
        HTTPStatus.NOT_FOUND, data="Not found", format=ResponseFormat.TEXT
    )


def not_allowed() -> Response:
    return Response(HTTPStatus.METHOD_NOT_ALLOWED)


def create_user(body: bytes, user_service: UserService) -> Response:
    try:
        validated_data = validate_json_object(body)
    except ValidationError as exc:
        return Response(
            HTTPStatus.BAD_REQUEST, str(exc), format=ResponseFormat.TEXT
        )

    try:
        user = user_service.create(validated_data)
    except UserAlreadyExistsError as exc:
        return Response(
            HTTPStatus.CONFLICT, str(exc), format=ResponseFormat.TEXT
        )
    except ValidationError as exc:
        return Response(
            HTTPStatus.BAD_REQUEST, str(exc), format=ResponseFormat.TEXT
        )

    return Response(
        HTTPStatus.CREATED, {"id": str(user.id), "status": "created"}
    )


def delete_user(path: str, user_service: UserService) -> Response:
    try:
        user_id = validate_id_from_path(path)
    except ValidationError as exc:
        return Response(
            HTTPStatus.BAD_REQUEST, str(exc), format=ResponseFormat.TEXT
        )

    try:
        user = user_service.delete(user_id)
    except UserNotFoundError as exc:
        return Response(
            HTTPStatus.NOT_FOUND, str(exc), format=ResponseFormat.TEXT
        )

    return Response(HTTPStatus.OK, {"id": str(user.id), "status": "deleted"})


def update_user(path: str, body: bytes, user_service: UserService) -> Response:
    try:
        user_id = validate_id_from_path(path)
    except ValidationError as exc:
        return Response(
            HTTPStatus.BAD_REQUEST, str(exc), format=ResponseFormat.TEXT
        )

    try:
        validated_data = validate_json_object(body)
    except ValidationError as exc:
        return Response(
            HTTPStatus.BAD_REQUEST, str(exc), format=ResponseFormat.TEXT
        )

    try:
        user = user_service.update(validated_data, user_id=user_id)
    except UserAlreadyExistsError as exc:
        return Response(
            HTTPStatus.CONFLICT, str(exc), format=ResponseFormat.TEXT
        )
    except UserNotFoundError as exc:
        return Response(
            HTTPStatus.NOT_FOUND, str(exc), format=ResponseFormat.TEXT
        )
    except ValidationError as exc:
        return Response(
            HTTPStatus.BAD_REQUEST, str(exc), format=ResponseFormat.TEXT
        )

    return Response(HTTPStatus.OK, {"id": str(user.id), "status": "updated"})

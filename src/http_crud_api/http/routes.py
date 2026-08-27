from http import HTTPStatus

from http_crud_api.http.response import Response
from http_crud_api.service.user import UserService
from http_crud_api.validation.common import validate_json_object
from http_crud_api.validation.request import validate_id_from_path


def health() -> Response:
    return Response.json(HTTPStatus.OK, {"status": "ok"})


def get_users(user_service: UserService) -> Response:
    return Response.json(
        HTTPStatus.OK, [user.to_dict() for user in user_service.get_all()]
    )


def get_user(path: str, user_service: UserService) -> Response:
    user_id = validate_id_from_path(path)
    user = user_service.get_by_id(user_id)
    return Response.json(HTTPStatus.OK, user.to_dict())


def get_favicon() -> Response:
    return Response.empty(HTTPStatus.NO_CONTENT)


def not_found() -> Response:
    return Response.text(HTTPStatus.NOT_FOUND, "Not Found")


def not_allowed() -> Response:
    return Response.empty(HTTPStatus.METHOD_NOT_ALLOWED)


def create_user(body: bytes, user_service: UserService) -> Response:
    validated_data = validate_json_object(body)
    user = user_service.create(validated_data)
    return Response.json(
        HTTPStatus.CREATED, {"id": str(user.id), "status": "created"}
    )


def delete_user(path: str, user_service: UserService) -> Response:
    user_id = validate_id_from_path(path)
    user = user_service.delete(user_id)
    return Response.json(
        HTTPStatus.OK, {"id": str(user.id), "status": "deleted"}
    )


def update_user(path: str, body: bytes, user_service: UserService) -> Response:
    user_id = validate_id_from_path(path)
    validated_data = validate_json_object(body)
    user = user_service.update(validated_data, user_id=user_id)
    return Response.json(
        HTTPStatus.OK, {"id": str(user.id), "status": "updated"}
    )

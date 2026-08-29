from uuid import uuid7

import pytest

from http_crud_api.exceptions.validation import ValidationError
from http_crud_api.validation.request import validate_id_from_path


@pytest.mark.parametrize(
    "path",
    [
        "users/{}",
        "/users/{}/",
        "/users/{}",
        "users/{}/",
    ],
)
def test_validate_id_from_path_returns_uuid_from_valid_path(path: str):
    user_id = uuid7()
    path_with_id = path.format(user_id)

    assert validate_id_from_path(path_with_id) == user_id


def test_validate_id_from_path_raises_on_invalid_path():
    with pytest.raises(ValidationError, match="Invalid ID"):
        path = "something"
        validate_id_from_path(path)

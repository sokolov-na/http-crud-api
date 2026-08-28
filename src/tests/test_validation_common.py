import pytest

from http_crud_api.exceptions.validation import ValidationError
from http_crud_api.validation.common import validate_json_object


def test_validate_json_object_valid_json():
    assert validate_json_object(b'{"name": "Nikita"}') == {"name": "Nikita"}


def test_validate_json_object_invalid_json():
    with pytest.raises(ValidationError, match="Invalid JSON"):
        validate_json_object(b"()")


def test_validate_json_object_non_object_json():
    with pytest.raises(ValidationError, match="Invalid JSON"):
        validate_json_object(b"[]")

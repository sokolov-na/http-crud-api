from typing import Any

import pytest

from http_crud_api.exceptions.validation import ValidationError
from http_crud_api.validation.user import (
    validate_email_address,
    validate_user_create_data,
    validate_user_update_data,
)


@pytest.mark.parametrize(
    "user_email",
    ["example@google.com ", " example@google.com", "example@google.com"],
)
def test_validate_email_address_valid(user_email: str):
    assert validate_email_address(user_email) == "example@google.com"


@pytest.mark.parametrize(
    "user_email",
    [
        "",
        "@google.com",
        "John",
    ],
)
def test_validate_email_address_invalid(user_email: str):
    with pytest.raises(ValidationError, match="Invalid email"):
        validate_email_address(user_email)


@pytest.mark.parametrize(
    "data",
    [
        {"email": "example@google.com", "name": "John"},
        {"email": "example@google.com", "name": "John", "age": 23},
    ],
)
def test_validate_user_create_data_valid(data: dict[Any, Any]):
    assert validate_user_create_data(data) == {
        "email": "example@google.com",
        "name": "John",
    }


@pytest.mark.parametrize(
    "data, expected_error",
    [
        # missing fields
        ({}, "Missing name or email"),
        ({"email": "example@google.com"}, "Missing name or email"),
        ({"name": "John"}, "Missing name or email"),
        # invalid fields
        ({"name": None, "email": None}, "Invalid name"),
        ({"name": "John", "email": None}, "Invalid email"),
    ],
)
def test_validate_user_create_data_invalid(
    data: dict[Any, Any], expected_error: str
):
    with pytest.raises(ValidationError, match=expected_error):
        validate_user_create_data(data)


@pytest.mark.parametrize(
    "data",
    [
        # base
        {"email": "example@google.com", "name": "John"},
        {"email": "example@google.com"},
        {"name": "John"},
        # extra data
        {"email": "example@google.com", "name": "John", "age": 22},
        {"email": "example@google.com", "age": 22},
        {"name": "John", "age": 22},
    ],
)
def test_validate_user_update_data_valid(data: dict[Any, Any]):
    clear_data = {k: v for k, v in data.items() if k == "email" or k == "name"}
    assert validate_user_update_data(data) == clear_data


@pytest.mark.parametrize(
    "data, expected_error",
    [
        # missing fields
        ({}, "Name or email required"),
        ({"age": 22}, "Name or email required"),
        # invalid fields
        ({"email": None}, "Invalid email"),
        ({"name": None}, "Invalid name"),
        ({"name": None, "email": None}, "Invalid name"),
        ({"name": "John", "email": None}, "Invalid email"),
    ],
)
def test_validate_user_update_data_invalid(
    data: dict[Any, Any], expected_error: str
):
    with pytest.raises(ValidationError, match=expected_error):
        validate_user_update_data(data)

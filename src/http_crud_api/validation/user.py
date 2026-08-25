from typing import Any

from email_validator import EmailNotValidError, validate_email

from http_crud_api.exceptions.validation import ValidationError
from http_crud_api.schemas.user import UserCreateData, UserUpdateData


def validate_email_address(user_email: str) -> str:
    try:
        validated_email = validate_email(user_email)
        return validated_email.normalized
    except EmailNotValidError:
        raise ValidationError("Invalid email") from None


def validate_user_create_data(data: dict[Any, Any]) -> UserCreateData:
    if "name" not in data or "email" not in data:
        raise ValidationError("Missing name or email") from None

    if not isinstance(data["name"], str):
        raise ValidationError("Invalid name") from None

    if not isinstance(data["email"], str):
        raise ValidationError("Invalid email") from None

    return UserCreateData(name=data["name"], email=data["email"])


def validate_user_update_data(data: dict[Any, Any]) -> UserUpdateData:
    has_name: bool = "name" in data
    has_email: bool = "email" in data

    if not has_name and not has_email:
        raise ValidationError("Name or email required") from None

    result = UserUpdateData()

    if has_name:
        if not isinstance(data["name"], str):
            raise ValidationError("Invalid name") from None

        result["name"] = data["name"]

    if has_email:
        if not isinstance(data["email"], str):
            raise ValidationError("Invalid email") from None

        result["email"] = data["email"]

    return result

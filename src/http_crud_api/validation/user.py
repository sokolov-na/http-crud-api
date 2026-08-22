from dataclasses import dataclass

from email_validator import EmailNotValidError, validate_email

from http_crud_api.storage.users import users


class ValidationError(Exception):
    pass


@dataclass(frozen=True, kw_only=True)
class ValidationResult:
    name: str
    email: str


def validate_user_data(data: object) -> ValidationResult:
    if not isinstance(data, dict):
        raise ValidationError("Invalid JSON")

    if "name" not in data or "email" not in data:
        raise ValidationError("Missing name or email")

    if not isinstance(data["name"], str) or not isinstance(data["email"], str):
        raise ValidationError("Invalid name or email")

    email = data["email"]
    name = data["name"]

    try:
        validated_email = validate_email(email)
        email = validated_email.normalized
    except EmailNotValidError:
        raise ValidationError("Invalid email") from None

    if any(user.email == email for user in users):
        raise ValidationError("User with this email already exists")

    return ValidationResult(email=email, name=name)

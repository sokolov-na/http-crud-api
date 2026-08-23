from dataclasses import dataclass

from email_validator import EmailNotValidError, validate_email

from http_crud_api.exceptions.validation import ValidationError


@dataclass(frozen=True, kw_only=True)
class CreationResult:
    name: str
    email: str


@dataclass(frozen=True, kw_only=True)
class UpdateResult:
    name: str | None = None
    email: str | None = None


def validate_email_address(user_email: str) -> str:
    try:
        validated_email = validate_email(user_email)
        return validated_email.normalized
    except EmailNotValidError:
        raise ValidationError("Invalid email") from None


def validate_user_creation(data: object) -> CreationResult:
    if not isinstance(data, dict):
        raise ValidationError("Invalid JSON")

    if "name" not in data or "email" not in data:
        raise ValidationError("Missing name or email")

    if not isinstance(data["name"], str) or not isinstance(data["email"], str):
        raise ValidationError("Invalid name or email")

    return CreationResult(email=data["email"], name=data["name"])


def validate_user_update(data: object) -> UpdateResult:
    if not isinstance(data, dict):
        raise ValidationError("Invalid JSON")

    has_name: bool = "name" in data
    has_email: bool = "email" in data
    if not has_name and not has_email:
        raise ValidationError("Name or email required")

    name = None
    email = None

    if has_name:
        if not isinstance(data["name"], str):
            raise ValidationError("Invalid name")
        name = data["name"]

    if has_email:
        if not isinstance(data["email"], str):
            raise ValidationError("Invalid email")
        email = data["email"]

    return UpdateResult(name=name, email=email)

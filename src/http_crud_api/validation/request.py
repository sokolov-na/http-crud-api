from uuid import UUID

from http_crud_api.exceptions.validation import ValidationError


def validate_id_from_path(path: str) -> UUID:
    user_id_str = path.strip("/").split("/")[-1]

    try:
        return UUID(user_id_str)
    except ValueError:
        raise ValidationError("Invalid ID") from None

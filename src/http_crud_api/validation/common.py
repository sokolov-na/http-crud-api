from typing import Any, cast

from http_crud_api.exceptions.validation import ValidationError


def validate_json_object(data: object) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValidationError("Invalid JSON") from None

    return cast(dict[str, Any], data)

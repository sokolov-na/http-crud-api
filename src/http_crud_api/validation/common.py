import json
from typing import Any, cast

from http_crud_api.exceptions.validation import ValidationError


def validate_json_object(data: bytes) -> dict[str, Any]:
    try:
        data = json.loads(data)
    except json.JSONDecodeError:
        raise ValidationError("Invalid JSON") from None

    if not isinstance(data, dict):
        raise ValidationError("Invalid JSON") from None

    return cast(dict[str, Any], data)

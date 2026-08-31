"""Typed input schemas for user operations."""

from typing import NotRequired, TypedDict


class UserCreateData(TypedDict):
    """Validated data required to create a user."""

    name: str
    email: str


class UserUpdateData(TypedDict):
    """Validated data accepted when updating a user."""

    name: NotRequired[str]
    email: NotRequired[str]

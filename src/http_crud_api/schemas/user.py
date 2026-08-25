from typing import NotRequired, TypedDict


class UserCreateData(TypedDict):
    name: str
    email: str


class UserUpdateData(TypedDict):
    name: NotRequired[str]
    email: NotRequired[str]

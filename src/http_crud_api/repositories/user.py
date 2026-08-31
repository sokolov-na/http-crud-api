"""User repository interface."""

from typing import Protocol
from uuid import UUID

from http_crud_api.models.user import User


class UserRepository(Protocol):
    """Define the storage operations required by the user service."""

    def get_all(self) -> list[User]: ...

    def get_by_id(self, user_id: UUID) -> User | None: ...

    def get_by_email(self, user_email: str) -> User | None: ...

    def add(self, user: User) -> None: ...

    def delete(self, user: User) -> None: ...

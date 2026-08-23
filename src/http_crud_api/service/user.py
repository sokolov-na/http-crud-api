from uuid import UUID

from http_crud_api.exceptions.service import (
    UserAlreadyExistsError,
    UserNotFoundError,
)
from http_crud_api.models.user import User
from http_crud_api.repositories.user import UserRepository
from http_crud_api.validation.user import validate_email_address


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.__repository = repository

    def __validate_email(
        self, email: str, *, exclude_user_id: UUID | None = None
    ) -> str:
        email = validate_email_address(email)

        existing_user: User | None = self.__repository.get_by_email(email)

        if existing_user is not None and existing_user.id != exclude_user_id:
            raise UserAlreadyExistsError(f"Email {email} unavailable")

        return email

    def get_all(self) -> list[User]:
        return self.__repository.get_all()

    def get_by_id(self, user_id: UUID) -> User:
        user: User | None = self.__repository.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError(f"User with ID {user_id} does not exist")

        return user

    def create(self, *, name: str, email: str) -> User:
        user = User(name=name, email=self.__validate_email(email))

        self.__repository.add(user)

        return user

    def update(
        self,
        user_id: UUID,
        *,
        name: str | None = None,
        email: str | None = None,
    ) -> User:
        user: User = self.get_by_id(user_id)

        if email is not None:
            user.email = self.__validate_email(email, exclude_user_id=user_id)

        if name is not None:
            user.name = name

        return user

    def delete(self, user_id: UUID) -> User:
        user = self.get_by_id(user_id)

        self.__repository.delete(user)

        return user

"""Business logic for user operations."""

import logging
from typing import Any
from uuid import UUID

from http_crud_api.exceptions.service import (
    UserAlreadyExistsError,
    UserNotFoundError,
)
from http_crud_api.exceptions.validation import ValidationError
from http_crud_api.models.user import User
from http_crud_api.repositories.user import UserRepository
from http_crud_api.schemas.user import UserCreateData, UserUpdateData
from http_crud_api.validation.user import (
    validate_email_address,
    validate_user_create_data,
    validate_user_update_data,
)

logger = logging.getLogger(__name__)


class UserService:
    """Validate and coordinate user operations through a repository."""

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
        """Return all users."""

        return self.__repository.get_all()

    def get_by_id(self, user_id: UUID) -> User:
        """Return a user by ID or raise if it does not exist."""

        user: User | None = self.__repository.get_by_id(user_id)

        if user is None:
            exc = UserNotFoundError(f"User with ID {user_id} does not exist")
            logger.error("User lookup failed", exc_info=exc)
            raise exc

        return user

    def create(self, data: dict[Any, Any]) -> User:
        """Validate input and create a new user."""

        try:
            validated_data: UserCreateData = validate_user_create_data(data)
        except ValidationError:
            logger.exception("User creation failed")
            raise

        try:
            email = self.__validate_email(validated_data["email"])
        except UserAlreadyExistsError, ValidationError:
            logger.exception("User creation failed")
            raise

        name = validated_data["name"]

        user = User(name=name, email=email)

        self.__repository.add(user)

        logger.info("User %s created", user.id)
        return user

    def update(self, data: dict[Any, Any], *, user_id: UUID) -> User:
        """Validate input and update an existing user."""

        user = self.get_by_id(user_id)

        try:
            validated_data: UserUpdateData = validate_user_update_data(data)
        except ValidationError:
            logger.exception("User updating failed")
            raise

        if "name" in validated_data:
            user.name = validated_data["name"]

        if "email" in validated_data:
            try:
                user.email = self.__validate_email(
                    validated_data["email"], exclude_user_id=user_id
                )
            except (
                UserAlreadyExistsError,
                ValidationError,
            ):
                logger.exception("User updating failed")
                raise

        self.__repository.update(user)

        logger.info("User %s updated", user.id)
        return user

    def delete(self, user_id: UUID) -> User:
        """Delete and return a user by ID."""

        user: User = self.get_by_id(user_id)

        self.__repository.delete(user)

        logger.info("User %s deleted", user.id)
        return user

"""JSON-backed user repository."""

import json
from copy import deepcopy
from pathlib import Path
from uuid import UUID

from http_crud_api.models.user import User


class JsonUserRepository:
    """Store users in a JSON file."""

    def __init__(self, path: Path) -> None:
        self.__path = path
        self.__prepare_storage()
        self.__users: list[User] = self.__load()

    def __prepare_storage(self) -> None:
        self.__path.parent.mkdir(parents=True, exist_ok=True)
        if not self.__path.exists():
            self.__path.write_text("[]", encoding="utf-8")

    def __load(self) -> list[User]:
        with open(self.__path, encoding="utf-8") as file:
            data = json.load(file)
            return [
                User(
                    id=UUID(item["id"]),
                    name=item["name"],
                    email=item["email"],
                )
                for item in data
            ]

    def __save(self) -> None:
        with open(self.__path, "w", encoding="utf-8") as file:
            json.dump(
                [user.to_dict() for user in self.__users],
                file,
                indent=4,
            )

    def get_all(self) -> list[User]:
        """Return all stored users."""

        return deepcopy(self.__users)

    def get_by_id(self, user_id: UUID) -> User | None:
        """Return the user with the given ID, if present."""

        return next(
            (user for user in self.get_all() if user.id == user_id), None
        )

    def get_by_email(self, user_email: str) -> User | None:
        """Return the user with the given email, if present."""

        return next(
            (user for user in self.get_all() if user.email == user_email), None
        )

    def add(self, user: User) -> None:
        """Add a user and persist the repository."""

        self.__users.append(user)
        self.__save()

    def delete(self, user: User) -> None:
        """Delete a user and persist the repository."""

        self.__users.remove(user)
        self.__save()

    def update(self, user: User) -> None:
        """Persist the updated state of an existing user."""

        stored_user = next(
            (
                target_user
                for target_user in self.__users
                if target_user.id == user.id
            ),
        )
        stored_user.email = user.email
        stored_user.name = user.name
        self.__save()

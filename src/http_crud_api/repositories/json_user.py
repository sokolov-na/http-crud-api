import json
from pathlib import Path
from uuid import UUID

from http_crud_api.models.user import User


class JsonUserRepository:
    def __init__(self, path: Path) -> None:
        self.__path = path
        self.__prepare_storage()
        self.__users: list[User] = self.__load()

    def __prepare_storage(self) -> None:
        self.__path.parent.mkdir(parents=True, exist_ok=True)
        if not self.__path.exists():
            self.__path.write_text("[]", encoding="utf-8")

    def __load(self) -> list[User]:
        with open(self.__path) as file:
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
        with open(self.__path, "w") as file:
            json.dump(
                [user.to_dict() for user in self.__users],
                file,
            )

    def get_all(self) -> list[User]:
        return self.__users.copy()

    def get_by_id(self, user_id: UUID) -> User | None:
        return next(
            (user for user in self.__users if user.id == user_id), None
        )

    def get_by_email(self, user_email: str) -> User | None:
        return next(
            (user for user in self.__users if user.email == user_email), None
        )

    def add(self, user: User) -> None:
        self.__users.append(user)
        self.__save()

    def delete(self, user: User) -> None:
        self.__users.remove(user)
        self.__save()

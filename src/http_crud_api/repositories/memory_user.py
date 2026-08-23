from uuid import UUID

from http_crud_api.models.user import User


class InMemoryUserRepository:
    def __init__(self, users: list[User]) -> None:
        self.__users = users

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

    def delete(self, user: User) -> None:
        self.__users.remove(user)

import json
from pathlib import Path
from uuid import uuid7

import pytest

from http_crud_api.exceptions.service import (
    UserAlreadyExistsError,
    UserNotFoundError,
)
from http_crud_api.models.user import User
from http_crud_api.repositories.json_user import JsonUserRepository
from http_crud_api.service.user import UserService


class TestUserServiceWithJsonRepository:
    @pytest.fixture
    def sample_user(self) -> User:
        return User(
            id=uuid7(),
            name="John",
            email="example@google.com",
        )

    @pytest.fixture
    def user_repo(
        self,
        tmp_path: Path,
        sample_user: User,
    ) -> JsonUserRepository:
        file_path = tmp_path / "users.json"
        file_path.write_text(
            json.dumps([sample_user.to_dict()]), encoding="utf-8"
        )
        return JsonUserRepository(file_path)

    @pytest.fixture
    def user_service(
        self,
        user_repo: JsonUserRepository,
    ) -> UserService:
        return UserService(user_repo)

    @pytest.fixture
    def path(
        self,
        tmp_path: Path,
    ) -> Path:
        return tmp_path / "users.json"

    def test_get_all_returns_stored_users(
        self,
        user_service: UserService,
        sample_user: User,
    ):
        result = user_service.get_all()

        assert result == [sample_user]

    def test_get_by_id_returns_stored_user(
        self,
        user_service: UserService,
        sample_user: User,
    ):
        result = user_service.get_by_id(sample_user.id)

        assert result == sample_user

    def test_get_by_id_raises_when_user_is_not_found(
        self, user_service: UserService
    ):
        with pytest.raises(UserNotFoundError):
            user_service.get_by_id(uuid7())

    def test_create_persists_new_user(
        self,
        user_service: UserService,
        path: Path,
        sample_user: User,
    ):
        data = {"name": "Jane", "email": "example@yandex.ru"}

        result = user_service.create(data)

        assert result.name == data["name"]
        assert result.email == data["email"]
        assert result.id is not None

        with open(path, encoding="utf-8") as file:
            file_content = json.load(file)
            assert file_content == [sample_user.to_dict(), result.to_dict()]

    def test_create_rejects_existing_email_without_changing_storage(
        self,
        user_service: UserService,
        path: Path,
        sample_user: User,
    ):
        data = {"name": sample_user.name, "email": sample_user.email}

        with pytest.raises(UserAlreadyExistsError):
            user_service.create(data)

        with open(path, encoding="utf-8") as file:
            file_content = json.load(file)
            assert file_content == [sample_user.to_dict()]

    def test_update_changes_only_name(
        self,
        user_service: UserService,
        path: Path,
        sample_user: User,
    ):
        data = {"name": "Jane"}

        result = user_service.update(data, user_id=sample_user.id)

        assert result.name == "Jane"

        with open(path, encoding="utf-8") as file:
            file_content = json.load(file)
            assert file_content == [result.to_dict()]

    def test_update_keeps_same_email(
        self,
        user_service: UserService,
        path: Path,
        sample_user: User,
    ):
        data = {"email": sample_user.email}
        old_email = sample_user.email

        result = user_service.update(data, user_id=sample_user.id)

        assert result.email == old_email

        with open(path, encoding="utf-8") as file:
            file_content = json.load(file)
            assert file_content == [sample_user.to_dict()]
            assert file_content == [result.to_dict()]

    def test_update_changes_only_email(
        self,
        user_service: UserService,
        path: Path,
        sample_user: User,
    ):
        data = {"email": "new@gmail.com"}

        result = user_service.update(data, user_id=sample_user.id)

        assert result.email == "new@gmail.com"

        with open(path, encoding="utf-8") as file:
            file_content = json.load(file)
            assert file_content == [result.to_dict()]

    def test_update_changes_name_and_email(
        self,
        user_service: UserService,
        path: Path,
        sample_user: User,
    ):
        data = {"name": "Jane", "email": "new@gmail.com"}

        result = user_service.update(data, user_id=sample_user.id)

        assert result.email == "new@gmail.com"
        assert result.name == "Jane"

        with open(path, encoding="utf-8") as file:
            file_content = json.load(file)
            assert file_content == [result.to_dict()]

    def test_update_rejects_existing_email_without_changing_storage(
        self,
        user_service: UserService,
        path: Path,
        sample_user: User,
    ):
        user_service.create({"name": "Jane", "email": "new@gmail.com"})
        data = {"email": "new@gmail.com"}
        old_email = sample_user.email

        with pytest.raises(UserAlreadyExistsError):
            user_service.update(data, user_id=sample_user.id)

        with open(path, encoding="utf-8") as file:
            file_content = json.load(file)
            assert file_content[0]["email"] == old_email

    def test_update_raises_when_user_not_found(
        self,
        user_service: UserService,
        path: Path,
        sample_user: User,
    ):
        with pytest.raises(UserNotFoundError):
            user_service.update(
                {"name": "Jane"},
                user_id=uuid7(),
            )

        with open(path, encoding="utf-8") as file:
            file_content = json.load(file)
            assert file_content == [sample_user.to_dict()]

    def test_delete_removes_user_from_storage(
        self,
        user_service: UserService,
        path: Path,
        sample_user: User,
    ):
        result = user_service.delete(sample_user.id)
        assert result == sample_user

        with open(path, encoding="utf-8") as file:
            file_content = json.load(file)
            assert file_content == []

    def test_delete_raises_when_user_not_found(
        self,
        user_service: UserService,
        path: Path,
        sample_user: User,
    ):
        with pytest.raises(UserNotFoundError):
            user_service.delete(uuid7())

        with open(path, encoding="utf-8") as file:
            file_content = json.load(file)
            assert file_content == [sample_user.to_dict()]

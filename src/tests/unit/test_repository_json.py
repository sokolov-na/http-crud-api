import json
from pathlib import Path
from uuid import uuid7

import pytest

from http_crud_api.models.user import User
from http_crud_api.repositories.json_user import JsonUserRepository


class TestJsonRepository:
    @pytest.fixture
    def sample_user(self) -> User:
        return User(
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
        file_path.write_text(json.dumps([sample_user.to_dict()]))
        return JsonUserRepository(file_path)

    @pytest.fixture
    def path(
        self,
        tmp_path: Path,
    ) -> Path:
        return tmp_path / "users.json"

    def test_get_all_returns_users(self, user_repo: JsonUserRepository):
        result = user_repo.get_all()
        assert len(result) == 1
        assert result[0].name == "John"

    def test_get_all_returns_empty_list_for_empty_storage(
        self,
        tmp_path: Path,
    ):
        file_path = tmp_path / "users.json"
        user_repo = JsonUserRepository(file_path)

        result = user_repo.get_all()
        assert result == []

    def test_get_by_id_returns_user(
        self,
        user_repo: JsonUserRepository,
        sample_user: User,
    ):
        result = user_repo.get_by_id(sample_user.id)
        assert result == sample_user

    def test_get_by_id_returns_none_for_unknown_id(
        self,
        user_repo: JsonUserRepository,
    ):
        result = user_repo.get_by_id(uuid7())
        assert result is None

    def test_get_by_email_returns_user(
        self,
        user_repo: JsonUserRepository,
        sample_user: User,
    ):
        result = user_repo.get_by_email(sample_user.email)
        assert result == sample_user

    def test_get_by_email_returns_none_for_unknown_email(
        self,
        user_repo: JsonUserRepository,
    ):
        result = user_repo.get_by_email("example@example.com")
        assert result is None

    def test_add_persists_user(
        self,
        path: Path,
        sample_user: User,
    ):
        user_repo = JsonUserRepository(path)

        user_repo.add(sample_user)

        with open(path) as file:
            file_content = json.load(file)
            assert file_content == [sample_user.to_dict()]

        assert user_repo.get_all() == [sample_user]

    def test_delete_removes_user(
        self,
        path: Path,
        user_repo: JsonUserRepository,
        sample_user: User,
    ):
        user_repo.delete(sample_user)

        with open(path) as file:
            file_content = json.load(file)
            assert file_content == []

        assert user_repo.get_all() == []

    def test_delete_raises_for_nonexistent_user(
        self,
        path: Path,
        user_repo: JsonUserRepository,
        sample_user: User,
    ):
        user = User(name="Jane", email="example@yandex.ru")

        with pytest.raises(ValueError):
            user_repo.delete(user)

        with open(path) as file:
            file_content = json.load(file)
            assert file_content == [sample_user.to_dict()]

        assert user_repo.get_all() == [sample_user]

    def test_get_all_returns_copy(
        self,
        user_repo: JsonUserRepository,
        sample_user: User,
    ):
        result = user_repo.get_all()

        result.clear()

        assert user_repo.get_all() == [sample_user]

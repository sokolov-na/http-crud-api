from unittest.mock import ANY, MagicMock, create_autospec
from uuid import uuid7

import pytest

from http_crud_api.exceptions.service import (
    UserAlreadyExistsError,
    UserNotFoundError,
)
from http_crud_api.models.user import User
from http_crud_api.repositories.user import UserRepository
from http_crud_api.service.user import UserService


class TestUserService:
    @pytest.fixture
    def mock_repository(self) -> MagicMock:
        return create_autospec(UserRepository, instance=True)

    @pytest.fixture
    def user_service(self, mock_repository: UserRepository) -> UserService:
        return UserService(mock_repository)

    @pytest.fixture
    def sample_user(self) -> User:
        return User(
            id=uuid7(),
            name="John",
            email="example@google.com",
        )

    @pytest.fixture(params=[None, "same_user"])
    def existing_user(
        self, request: pytest.FixtureRequest, sample_user: User
    ) -> User | None:
        if request.param == "same_user":
            return sample_user

        return None

    def test_get_all(
        self,
        user_service: UserService,
        mock_repository: MagicMock,
        sample_user: User,
    ):
        mock_repository.get_all.return_value = [sample_user]
        result = user_service.get_all()

        assert result == [sample_user]
        mock_repository.get_all.assert_called_once_with()

    def test_get_by_id_found(
        self,
        user_service: UserService,
        mock_repository: MagicMock,
        sample_user: User,
    ):
        mock_repository.get_by_id.return_value = sample_user
        result = user_service.get_by_id(sample_user.id)

        assert result == sample_user
        mock_repository.get_by_id.assert_called_once_with(sample_user.id)

    def test_get_by_id_not_found(
        self,
        user_service: UserService,
        mock_repository: MagicMock,
        sample_user: User,
    ):
        mock_repository.get_by_id.return_value = None

        with pytest.raises(UserNotFoundError):
            user_service.get_by_id(sample_user.id)

    def test_user_create_email_available(
        self,
        user_service: UserService,
        mock_repository: MagicMock,
        sample_user: User,
    ):
        data = sample_user.to_dict()
        mock_repository.add.return_value = None
        mock_repository.get_by_email.return_value = None

        result = user_service.create(data)
        assert result.name == sample_user.name
        assert result.email == sample_user.email
        assert result.id is not None
        mock_repository.add.assert_called_once_with(
            User(id=ANY, name=sample_user.name, email=sample_user.email)
        )

    def test_user_create_email_unavailable(
        self,
        user_service: UserService,
        mock_repository: MagicMock,
        sample_user: User,
    ):
        data = sample_user.to_dict()
        mock_repository.add.return_value = None
        mock_repository.get_by_email.return_value = sample_user

        with pytest.raises(UserAlreadyExistsError):
            user_service.create(data)

    def test_user_update_email_available(
        self,
        user_service: UserService,
        mock_repository: MagicMock,
        sample_user: User,
        existing_user: User | None,
    ):
        data = sample_user.to_dict()
        mock_repository.get_by_id.return_value = sample_user
        mock_repository.get_by_email.return_value = existing_user

        result = user_service.update(data, user_id=sample_user.id)
        assert result == sample_user

    def test_user_update_email_unavailable(
        self,
        user_service: UserService,
        mock_repository: MagicMock,
        sample_user: User,
    ):
        data = sample_user.to_dict()
        mock_repository.get_by_id.return_value = sample_user
        mock_repository.get_by_email.return_value = User(
            name=sample_user.name, email=sample_user.email
        )

        with pytest.raises(UserAlreadyExistsError):
            user_service.update(data, user_id=sample_user.id)

    def test_user_delete(
        self,
        user_service: UserService,
        mock_repository: MagicMock,
        sample_user: User,
    ):
        mock_repository.get_by_id.return_value = sample_user
        mock_repository.delete.return_value = None

        result = user_service.delete(sample_user.id)
        assert result == sample_user
        mock_repository.delete.assert_called_once_with(sample_user)

from unittest.mock import MagicMock, create_autospec

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
    def user_service(self, mock_repository: MagicMock) -> UserService:
        return UserService(mock_repository)

    @pytest.fixture
    def sample_user(self) -> User:
        return User(
            name="John",
            email="example@google.com",
        )

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

        mock_repository.get_by_id.assert_called_once_with(sample_user.id)

    def test_create_adds_user_when_email_is_available(
        self,
        user_service: UserService,
        mock_repository: MagicMock,
        sample_user: User,
    ):
        data = sample_user.to_dict()
        mock_repository.add.return_value = None
        mock_repository.get_by_email.return_value = None

        result = user_service.create(data)

        added_user = mock_repository.add.call_args.args[0]

        assert result.name == sample_user.name
        assert result.email == sample_user.email
        assert result.id is not None
        assert result is added_user

        assert added_user.id is not None

        mock_repository.add.assert_called_once()
        mock_repository.get_by_email.assert_called_once_with(sample_user.email)

    def test_create_rejects_existing_email(
        self,
        user_service: UserService,
        mock_repository: MagicMock,
        sample_user: User,
    ):
        data = {"name": sample_user.name, "email": sample_user.email}
        mock_repository.add.return_value = None
        mock_repository.get_by_email.return_value = sample_user

        with pytest.raises(UserAlreadyExistsError):
            user_service.create(data)

        mock_repository.get_by_email.assert_called_once_with(sample_user.email)
        mock_repository.add.assert_not_called()

    def test_update_changes_only_name(
        self,
        user_service: UserService,
        mock_repository: MagicMock,
        sample_user: User,
    ):
        data = {"name": "Jane"}
        mock_repository.get_by_id.return_value = sample_user

        result = user_service.update(data, user_id=sample_user.id)

        assert result.name == "Jane"
        assert sample_user.name == result.name

        mock_repository.get_by_id.assert_called_once_with(sample_user.id)

    def test_update_keeps_same_email(
        self,
        user_service: UserService,
        mock_repository: MagicMock,
        sample_user: User,
    ):
        data = {"email": sample_user.email}
        old_email = sample_user.email
        mock_repository.get_by_id.return_value = sample_user
        mock_repository.get_by_email.return_value = sample_user

        result = user_service.update(data, user_id=sample_user.id)

        assert result.email == old_email
        assert sample_user.email == old_email

        mock_repository.get_by_email.assert_called_once_with(sample_user.email)
        mock_repository.get_by_id.assert_called_once_with(sample_user.id)

    def test_update_changes_only_email(
        self,
        user_service: UserService,
        mock_repository: MagicMock,
        sample_user: User,
    ):
        data = {"email": "new@gmail.com"}
        mock_repository.get_by_id.return_value = sample_user
        mock_repository.get_by_email.return_value = None

        result = user_service.update(data, user_id=sample_user.id)

        assert result.email == "new@gmail.com"
        assert sample_user.email == result.email

        mock_repository.get_by_email.assert_called_once_with("new@gmail.com")
        mock_repository.get_by_id.assert_called_once_with(sample_user.id)

    def test_update_changes_name_and_email(
        self,
        user_service: UserService,
        mock_repository: MagicMock,
        sample_user: User,
    ):
        data = {"name": "Jane", "email": "new@gmail.com"}
        mock_repository.get_by_id.return_value = sample_user
        mock_repository.get_by_email.return_value = None

        result = user_service.update(data, user_id=sample_user.id)

        assert result.email == "new@gmail.com"
        assert sample_user.email == result.email

        assert result.name == "Jane"
        assert sample_user.name == result.name

        mock_repository.get_by_email.assert_called_once_with("new@gmail.com")
        mock_repository.get_by_id.assert_called_once_with(sample_user.id)

    def test_update_rejects_existing_email(
        self,
        user_service: UserService,
        mock_repository: MagicMock,
        sample_user: User,
    ):
        data = {"email": "new@gmail.com"}
        old_email = sample_user.email
        mock_repository.get_by_id.return_value = sample_user
        mock_repository.get_by_email.return_value = User(
            name=sample_user.name, email="new@gmail.com"
        )

        with pytest.raises(UserAlreadyExistsError):
            user_service.update(data, user_id=sample_user.id)

        assert sample_user.email == old_email

        mock_repository.get_by_email.assert_called_once_with("new@gmail.com")
        mock_repository.get_by_id.assert_called_once_with(sample_user.id)

    def test_update_raises_when_user_not_found(
        self,
        user_service: UserService,
        mock_repository: MagicMock,
        sample_user: User,
    ):
        mock_repository.get_by_id.return_value = None

        with pytest.raises(UserNotFoundError):
            user_service.update(
                {"name": "Jane"},
                user_id=sample_user.id,
            )

        mock_repository.get_by_id.assert_called_once_with(sample_user.id)

    def test_delete_returns_deleted_user(
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

    def test_delete_raises_when_user_not_found(
        self,
        user_service: UserService,
        mock_repository: MagicMock,
        sample_user: User,
    ):
        mock_repository.get_by_id.return_value = None

        with pytest.raises(UserNotFoundError):
            user_service.delete(sample_user.id)

        mock_repository.delete.assert_not_called()
        mock_repository.get_by_id.assert_called_once_with(sample_user.id)

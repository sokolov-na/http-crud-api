"""Service-layer exceptions."""


class UserAlreadyExistsError(Exception):
    """Raised when a user with the requested email already exists."""

    pass


class UserNotFoundError(Exception):
    """Raised when a requested user does not exist."""

    pass

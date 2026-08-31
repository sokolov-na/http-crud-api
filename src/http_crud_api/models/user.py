"""User domain model."""

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid7


@dataclass(kw_only=True)
class User:
    """Represent a user stored by the application."""

    name: str
    email: str
    id: UUID = field(default_factory=uuid7)

    def __post_init__(self) -> None:
        self.name = self.name.capitalize()

    def to_dict(self) -> dict[str, Any]:
        """Return the user as a JSON-compatible dictionary."""

        return {
            "id": str(self.id),
            "name": self.name,
            "email": self.email,
        }

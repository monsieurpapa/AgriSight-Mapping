import reflex as rx
from typing import TypedDict, Literal

Role = Literal["admin", "buyer", "cooperative"]


class Cooperative(TypedDict):
    id: str
    name: str


class Farmer(TypedDict):
    id: str
    name: str
    cooperative_id: str


class User(TypedDict):
    id: str
    name: str
    email: str
    role: Role
    partnerships: list[str]
    cooperative_id: str | None


class AuthState(rx.State):
    """Manages user authentication, roles, and permissions."""

    users: list[User] = [
        {
            "id": "user-admin",
            "name": "Admin User",
            "email": "admin@agritrace.cd",
            "role": "admin",
            "partnerships": [],
            "cooperative_id": None,
        },
        {
            "id": "user-buyer-1",
            "name": "International Coffee Traders",
            "email": "buyer@ict.com",
            "role": "buyer",
            "partnerships": ["coop-kivu", "coop-equateur"],
            "cooperative_id": None,
        },
        {
            "id": "user-coop-manager-1",
            "name": "Jean-Pierre Lumumba",
            "email": "manager@coopec-kivu.cd",
            "role": "cooperative",
            "partnerships": [],
            "cooperative_id": "coop-kivu",
        },
    ]
    current_user_id: str = "user-buyer-1"

    @rx.var
    def current_user(self) -> User | None:
        """Get the full user object for the currently logged-in user."""
        for user in self.users:
            if user["id"] == self.current_user_id:
                return user
        return None

    @rx.var
    def is_admin(self) -> bool:
        """Check if the current user is an admin."""
        user = self.current_user
        return user is not None and user["role"] == "admin"

    @rx.event
    def login_as(self, user_id: str):
        """Switch the current user for demonstration purposes."""
        self.current_user_id = user_id
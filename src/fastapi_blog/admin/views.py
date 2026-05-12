"""Custom ModelView classes for admin models."""

from typing import Any

from starlette.requests import Request
from starlette_admin.contrib.sqla import ModelView


# Lazy import to avoid initialization errors
_pwd_context = None

# Password constraints
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128
BCRYPT_MAX_BYTES = 72  # bcrypt limitation


def get_pwd_context():
    """Get or create password hashing context (lazy initialization)."""
    global _pwd_context
    if _pwd_context is None:
        from passlib.context import CryptContext  # type: ignore[import-untyped]

        _pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return _pwd_context


def validate_and_prepare_password(password: str) -> str:
    """Validate password length and prepare for bcrypt hashing.

    Args:
        password: Plain text password

    Returns:
        Password truncated to bcrypt max bytes if needed

    Raises:
        ValueError: If password is too short or too long

    """
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters long"
        )
    if len(password) > MAX_PASSWORD_LENGTH:
        raise ValueError(f"Password must not exceed {MAX_PASSWORD_LENGTH} characters")

    # Truncate to bcrypt's 72 byte limit if needed
    # This is safe - bcrypt only uses first 72 bytes anyway
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > BCRYPT_MAX_BYTES:
        password_bytes = password_bytes[:BCRYPT_MAX_BYTES]
        password = password_bytes.decode("utf-8", errors="ignore")

    return password


class UserModelView(ModelView):
    """Custom view for User model with password hashing."""

    exclude_fields_from_list = ["hashed_password"]
    exclude_fields_from_detail = ["hashed_password"]
    exclude_fields_from_edit = ["hashed_password", "created_at", "updated_at"]
    exclude_fields_from_create = ["created_at", "updated_at"]

    async def before_create(
        self, request: Request, data: dict[str, Any], obj: Any
    ) -> None:
        """Hash password before creating user."""
        if "hashed_password" in data and data["hashed_password"]:
            # Validate and prepare password
            password = validate_and_prepare_password(data["hashed_password"])
            # Hash the plain text password
            data["hashed_password"] = get_pwd_context().hash(password)
        await super().before_create(request, data, obj)

    async def before_edit(
        self, request: Request, data: dict[str, Any], obj: Any
    ) -> None:
        """Hash password before editing user if password was changed."""
        if "hashed_password" in data and data["hashed_password"]:
            # Only hash if password is being updated (non-empty)
            # If field is empty, keep existing hash
            if data["hashed_password"] != obj.hashed_password:
                # Validate and prepare password
                password = validate_and_prepare_password(data["hashed_password"])
                data["hashed_password"] = get_pwd_context().hash(password)
        await super().before_edit(request, data, obj)


class PostModelView(ModelView):
    """Custom view for Post model."""

    exclude_fields_from_edit = ["created_at", "updated_at"]
    exclude_fields_from_create = ["created_at", "updated_at"]

    # Make content field use textarea
    form_overrides = {
        "content": {"widget": "textarea", "rows": 20},
        "description": {"widget": "textarea", "rows": 3},
    }

"""Test password validation for admin views."""

import pytest

from fastapi_blog.admin.views import (
    BCRYPT_MAX_BYTES,
    MAX_PASSWORD_LENGTH,
    MIN_PASSWORD_LENGTH,
    validate_and_prepare_password,
)


def test_password_min_length():
    """Test password minimum length validation."""
    # Too short
    with pytest.raises(ValueError, match="at least 8 characters"):
        validate_and_prepare_password("short")

    # Exactly min length - should work
    password = "a" * MIN_PASSWORD_LENGTH
    assert validate_and_prepare_password(password) == password


def test_password_max_length():
    """Test password maximum length validation."""
    # Too long
    with pytest.raises(ValueError, match="must not exceed 128"):
        validate_and_prepare_password("x" * (MAX_PASSWORD_LENGTH + 1))

    # Exactly max length - should work
    password = "a" * MAX_PASSWORD_LENGTH
    result = validate_and_prepare_password(password)
    assert len(result) <= BCRYPT_MAX_BYTES  # May be truncated to bcrypt limit


def test_password_valid_range():
    """Test passwords within valid range."""
    # Short valid password
    assert validate_and_prepare_password("Password1") == "Password1"

    # Medium password
    password = "MySecurePassword123!"
    assert validate_and_prepare_password(password) == password

    # Long but valid password
    password = "a" * 50
    assert validate_and_prepare_password(password) == password


def test_password_bcrypt_truncation():
    """Test that passwords longer than 72 bytes are truncated."""
    # Create password exactly at bcrypt limit
    password_72 = "a" * BCRYPT_MAX_BYTES  # 72 bytes
    result = validate_and_prepare_password(password_72)
    assert result == password_72

    # Create password longer than bcrypt limit (but within our MAX)
    password_100 = "a" * 100
    result = validate_and_prepare_password(password_100)

    # Should be truncated to 72 bytes
    assert len(result.encode("utf-8")) <= BCRYPT_MAX_BYTES
    assert len(result) <= BCRYPT_MAX_BYTES


def test_password_unicode_handling():
    """Test password with unicode characters."""
    # Unicode password within limits
    password = "Пароль123!"  # Russian + numbers
    result = validate_and_prepare_password(password)
    assert result == password

    # Very long unicode password (each char can be multiple bytes)
    password = "й" * 50  # Cyrillic character (2 bytes in UTF-8)
    result = validate_and_prepare_password(password)
    # Should be truncated to fit in 72 bytes
    assert len(result.encode("utf-8")) <= BCRYPT_MAX_BYTES


def test_password_empty():
    """Test empty password validation."""
    with pytest.raises(ValueError, match="at least 8 characters"):
        validate_and_prepare_password("")


def test_password_constants():
    """Verify password constants are reasonable."""
    assert MIN_PASSWORD_LENGTH == 8
    assert MAX_PASSWORD_LENGTH == 128
    assert BCRYPT_MAX_BYTES == 72
    assert MIN_PASSWORD_LENGTH < BCRYPT_MAX_BYTES < MAX_PASSWORD_LENGTH

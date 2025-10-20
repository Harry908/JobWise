import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta

from app.core.security import (
    PasswordHasher,
    JWTManager,
    SecurityUtils,
    verify_password as verify_pw_fn,
    hash_password as hash_pw_fn,
)
from app.presentation.middleware import auth as auth_mw
from app.core.exceptions import AuthenticationException


def test_password_hasher_and_verify_roundtrip():
    pw = "SecurePass123"
    hashed = PasswordHasher.hash_password(pw)
    assert isinstance(hashed, str)
    assert PasswordHasher.verify_password(pw, hashed) is True
    assert verify_pw_fn(pw, hashed) is True


def test_password_verify_invalid_inputs():
    assert PasswordHasher.verify_password("", "") is False
    assert PasswordHasher.verify_password("a", "") is False


def test_security_utils_misc():
    token = SecurityUtils.generate_secure_token(16)
    assert isinstance(token, str) and len(token) > 0

    h = SecurityUtils.hash_string("abc")
    assert isinstance(h, str) and len(h) == 64

    assert SecurityUtils.constant_time_compare("a", "a") is True
    assert SecurityUtils.constant_time_compare("a", "b") is False

    assert SecurityUtils.sanitize_input(None) == ""
    assert SecurityUtils.sanitize_input("  hi  ") == "hi"
    long_str = "x" * 2000
    assert len(SecurityUtils.sanitize_input(long_str, max_length=100)) == 100


def test_jwt_manager_token_roundtrip_and_expired():
    user_id = "u-1"
    token = JWTManager.create_access_token(user_id, expires_delta=timedelta(seconds=5))
    td = JWTManager.verify_token(token)
    assert td.user_id == user_id
    assert JWTManager.is_token_expired(token) is False

    expired = JWTManager.create_access_token(user_id, expires_delta=timedelta(seconds=-1))
    with pytest.raises(AuthenticationException):
        JWTManager.verify_token(expired)
    assert JWTManager.is_token_expired(expired) is True


def test_validate_token_manual_and_get_token_from_header():
    # Patch verify_token to return object
    class FakeTD:
        def __init__(self, user_id):
            self.user_id = user_id

    with patch('app.presentation.middleware.auth.verify_token') as mock_verify:
        mock_verify.return_value = FakeTD('u1')
        assert auth_mw.validate_token_manual('tok') == 'u1'

    with patch('app.presentation.middleware.auth.verify_token') as mock_verify2:
        mock_verify2.side_effect = AuthenticationException('bad')
        assert auth_mw.validate_token_manual('tok') is None

    assert auth_mw.get_token_from_header(None) is None
    assert auth_mw.get_token_from_header('Invalid header') is None
    assert auth_mw.get_token_from_header('Bearer abc.def') == 'abc.def'
    assert auth_mw.get_token_from_header('bearer token') == 'token'


@pytest.mark.asyncio
async def test_get_current_user_repository_and_require_verified(monkeypatch):
    # Prepare a fake repo factory and user repo
    fake_user = MagicMock()
    fake_user.is_active = True
    fake_user.is_verified = True

    fake_user_repo = AsyncMock()
    fake_user_repo.get_by_id.return_value = fake_user

    class FakeFactory:
        def __init__(self, session):
            pass

        def create_user_repository(self):
            return fake_user_repo

    # Patch RepositoryFactory used in middleware
    monkeypatch.setattr('app.presentation.middleware.auth.RepositoryFactory', lambda session: FakeFactory(session))

    # Patch get_current_user_id to return a user id without HTTP flow
    async def fake_get_current_user_id():
        return "u1"

    monkeypatch.setattr('app.presentation.middleware.auth.get_current_user_id', fake_get_current_user_id)

    # Call get_current_user_repository directly
    repo = await auth_mw.get_current_user_repository()
    assert repo is not None

    # Now test require_verified_user with unverified user
    fake_user.is_verified = False
    fake_user_repo.get_by_id.return_value = fake_user

    with pytest.raises(Exception):
        # should raise HTTPException inside function
        await auth_mw.require_verified_user()

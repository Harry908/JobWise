import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.application.services.auth_service import AuthService
from app.core.exceptions import AuthenticationException, ValidationException, NotFoundError
from app.application.dtos.auth_dtos import UserRegisterRequest, UserLoginRequest, RefreshTokenRequest, PasswordChangeRequest
from app.domain.entities.user import User
from app.infrastructure.database.repositories import UserRepository


class SimpleReq:
    def __init__(self, email, password, full_name):
        self.email = email
        self.password = password
        self.full_name = full_name


@pytest.mark.asyncio
async def test_register_user_invalid_email_bypassing_dto():
    mock_repo = AsyncMock(spec=UserRepository)
    auth = AuthService(mock_repo)

    # Create a simple request object not validated by pydantic
    req = SimpleReq(email="bad-email", password="SecurePass123", full_name="A B")

    mock_repo.get_by_email.return_value = None

    with pytest.raises(ValidationException):
        await auth.register_user(req)


@pytest.mark.asyncio
async def test_register_user_weak_password_bypassing_dto():
    mock_repo = AsyncMock(spec=UserRepository)
    auth = AuthService(mock_repo)

    req = SimpleReq(email="ok@example.com", password="weak", full_name="A B")
    mock_repo.get_by_email.return_value = None

    with pytest.raises(ValidationException):
        await auth.register_user(req)


@pytest.mark.asyncio
async def test_refresh_access_token_success():
    mock_repo = AsyncMock(spec=UserRepository)
    auth = AuthService(mock_repo)

    # Setup a user model that is active
    mock_user = MagicMock()
    mock_user.is_active = True
    mock_repo.get_by_id.return_value = mock_user

    # Patch token utilities
    with patch('app.application.services.auth_service.get_user_id_from_token') as mock_get_uid, \
         patch('app.application.services.auth_service.create_access_token') as mock_at, \
         patch('app.application.services.auth_service.create_refresh_token') as mock_rt:

        mock_get_uid.return_value = 'user-1'
        mock_at.return_value = 'access.jwt'
        mock_rt.return_value = 'refresh.jwt'

        req = RefreshTokenRequest(refresh_token='t')
        res = await auth.refresh_access_token(req)

        assert res.access_token == 'access.jwt'
        assert res.refresh_token == 'refresh.jwt'
        assert res.user_id == 'user-1'


@pytest.mark.asyncio
async def test_verify_user_account_success():
    mock_repo = AsyncMock(spec=UserRepository)
    auth = AuthService(mock_repo)

    mock_user = MagicMock()
    mock_user.is_verified = False
    mock_repo.get_by_id.return_value = mock_user

    await auth.verify_user_account('user-1')
    mock_repo.update.assert_called_once_with('user-1', {'is_verified': True})


@pytest.mark.asyncio
async def test_deactivate_activate_user_success():
    mock_repo = AsyncMock(spec=UserRepository)
    auth = AuthService(mock_repo)

    mock_user = MagicMock()
    mock_user.is_active = True
    mock_repo.get_by_id.return_value = mock_user

    await auth.deactivate_user_account('user-1')
    mock_repo.update.assert_called_with('user-1', {'is_active': False})

    # Now activate
    mock_repo.get_by_id.return_value = mock_user
    await auth.activate_user_account('user-1')
    mock_repo.update.assert_called_with('user-1', {'is_active': True})


@pytest.mark.asyncio
async def test_change_password_new_password_validation_fails():
    mock_repo = AsyncMock(spec=UserRepository)
    auth = AuthService(mock_repo)

    mock_user = MagicMock()
    mock_user.password_hash = 'oldhash'
    # Ensure ID is a valid UUID string to satisfy AuthService UUID parsing
    from uuid import uuid4
    mock_user.id = str(uuid4())
    mock_repo.get_by_id.return_value = mock_user

    # Use a simple object to bypass Pydantic DTO validation which enforces length.
    class PWReq:
        def __init__(self, current_password, new_password):
            self.current_password = current_password
            self.new_password = new_password

    req = PWReq(current_password='Old', new_password='short')

    with patch('app.application.services.auth_service.verify_password') as mock_verify:
        mock_verify.return_value = True
        with pytest.raises(ValidationException):
            await auth.change_password('user-1', req)


@pytest.mark.asyncio
async def test_authenticate_user_not_verified():
    mock_repo = AsyncMock(spec=UserRepository)
    auth = AuthService(mock_repo)

    mock_user = MagicMock()
    from uuid import uuid4
    mock_user.id = str(uuid4())
    mock_user.email = 'a@b.com'
    mock_user.password_hash = 'hash'
    mock_user.first_name = 'A'
    mock_user.last_name = 'B'
    mock_user.is_active = True
    mock_user.is_verified = False
    mock_user.created_at = datetime.utcnow()
    mock_user.updated_at = datetime.utcnow()
    mock_user.last_active_at = None

    mock_repo.get_by_email.return_value = mock_user

    with patch('app.application.services.auth_service.verify_password') as mock_verify:
        mock_verify.return_value = True
        # Use UserLoginRequest for authenticate_user
        login_req = UserLoginRequest(email='a@b.com', password='SecurePass123')
        # Ensure mock_user.id is a valid UUID string
        from uuid import uuid4
        mock_user.id = str(uuid4())
        with pytest.raises(AuthenticationException):
            await auth.authenticate_user(login_req)

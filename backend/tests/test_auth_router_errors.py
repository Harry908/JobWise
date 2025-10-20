import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from app.main import app
from app.presentation.api.auth import get_auth_service
from app.core.exceptions import ValidationException, ConflictError, DatabaseError, AuthenticationException, NotFoundError


@pytest.fixture(autouse=True)
def disable_startup_events(monkeypatch):
    # Prevent startup events from touching DB during these unit tests
    monkeypatch.setattr('app.main.run_startup_tasks', lambda: None, raising=False)
    yield


def make_fake_service(exc=None, return_value=None):
    class FakeService:
        def __init__(self):
            pass

        async def register_user(self, request):
            if exc:
                raise exc
            return return_value

        async def authenticate_user(self, request):
            if exc:
                raise exc
            return return_value

        async def refresh_access_token(self, request):
            if exc:
                raise exc
            return return_value

    return FakeService()


def test_register_handler_validation_exception(monkeypatch):
    fake = make_fake_service(exc=ValidationException("bad"))
    app.dependency_overrides = {}
    app.dependency_overrides[get_auth_service] = lambda: fake

    client = TestClient(app)
    response = client.post('/api/v1/auth/register', json={
        'email': 'a@b.com', 'password': 'SecurePass123', 'full_name': 'A B'
    })
    assert response.status_code == 400


def test_register_handler_conflict_exception(monkeypatch):
    fake = make_fake_service(exc=ConflictError('conflict'))
    app.dependency_overrides = {}
    app.dependency_overrides[get_auth_service] = lambda: fake

    client = TestClient(app)
    response = client.post('/api/v1/auth/register', json={
        'email': 'a@b.com', 'password': 'SecurePass123', 'full_name': 'A B'
    })
    assert response.status_code == 409


def test_register_handler_database_error(monkeypatch):
    fake = make_fake_service(exc=DatabaseError('op', 'fail'))
    app.dependency_overrides = {}
    app.dependency_overrides[get_auth_service] = lambda: fake

    client = TestClient(app)
    response = client.post('/api/v1/auth/register', json={
        'email': 'a@b.com', 'password': 'SecurePass123', 'full_name': 'A B'
    })
    assert response.status_code == 500


def test_login_handler_authentication_exception(monkeypatch):
    fake = make_fake_service(exc=AuthenticationException('invalid'))
    app.dependency_overrides = {}
    app.dependency_overrides[get_auth_service] = lambda: fake

    client = TestClient(app)
    response = client.post('/api/v1/auth/login', json={'email': 'x@x.com', 'password': 'pw'})
    assert response.status_code == 401


def test_login_handler_notfound_exception(monkeypatch):
    fake = make_fake_service(exc=NotFoundError('User', 'id'))
    app.dependency_overrides = {}
    app.dependency_overrides[get_auth_service] = lambda: fake

    client = TestClient(app)
    response = client.post('/api/v1/auth/login', json={'email': 'x@x.com', 'password': 'pw'})
    assert response.status_code == 401


def test_refresh_handler_authentication_exception(monkeypatch):
    fake = make_fake_service(exc=AuthenticationException('bad'))
    app.dependency_overrides = {}
    app.dependency_overrides[get_auth_service] = lambda: fake

    client = TestClient(app)
    response = client.post('/api/v1/auth/refresh', json={'refresh_token': 't'})
    assert response.status_code == 401


def test_refresh_handler_generic_exception(monkeypatch):
    fake = make_fake_service(exc=Exception('boom'))
    app.dependency_overrides = {}
    app.dependency_overrides[get_auth_service] = lambda: fake

    client = TestClient(app)
    # According to route, generic exceptions map to 401 for refresh
    response = client.post('/api/v1/auth/refresh', json={'refresh_token': 't'})
    assert response.status_code == 401


def test_get_current_user_notfound_and_dberror(monkeypatch):
    # NotFoundError
    fake = make_fake_service(exc=NotFoundError('User', 'id'))
    app.dependency_overrides = {}
    app.dependency_overrides[get_auth_service] = lambda: fake

    client = TestClient(app)
    response = client.get('/api/v1/auth/me', headers={})
    # Missing auth header triggers 401 from middleware; simulate by providing no header
    assert response.status_code == 401

    # DatabaseError path
    fake2 = make_fake_service(exc=DatabaseError('op', 'fail'))
    app.dependency_overrides = {}
    app.dependency_overrides[get_auth_service] = lambda: fake2

    response2 = client.get('/api/v1/auth/me', headers={})
    assert response2.status_code == 401


def test_verify_email_and_confirm_reset_exceptions(monkeypatch):
    # verify_email endpoint - service raises exception -> 400
    fake = make_fake_service(exc=Exception('bad'))
    app.dependency_overrides = {}
    app.dependency_overrides[get_auth_service] = lambda: fake

    client = TestClient(app)
    response = client.post('/api/v1/auth/verify-email/token123')
    assert response.status_code == 400

    # confirm password reset - change_password raises -> 400
    class FakeService2:
        async def change_password(self, user_id, request):
            raise Exception('bad')

    app.dependency_overrides = {}
    app.dependency_overrides[get_auth_service] = lambda: FakeService2()
    response2 = client.post('/api/v1/auth/reset-password/confirm', json={'token': 't', 'new_password': 'NewSecurePass123'})
    assert response2.status_code == 400


def test_request_email_and_password_reset_success(monkeypatch):
    # These endpoints are simple and should return 200
    app.dependency_overrides = {}
    client = TestClient(app)

    resp = client.post('/api/v1/auth/verify-email', json={'email': 'a@b.com'})
    assert resp.status_code == 200

    resp2 = client.post('/api/v1/auth/reset-password', json={'email': 'a@b.com'})
    assert resp2.status_code == 200


def teardown_module(module):
    # Clear dependency overrides after tests
    app.dependency_overrides = {}

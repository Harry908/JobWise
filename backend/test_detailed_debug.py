"""Test with enhanced error logging to catch the exact issue."""

import asyncio
import sys
import traceback
import logging
from pathlib import Path

# Setup detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi.testclient import TestClient
from httpx import AsyncClient
from app.main import app


def test_sync_registration():
    """Test registration with sync client to see exact error."""
    print("=== SYNC CLIENT TEST ===")
    
    try:
        with TestClient(app) as client:
            response = client.post("/api/v1/auth/register", json={
                "email": "sync@test.com",
                "password": "SyncTest123",
                "full_name": "Sync Test User"
            })
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 500:
                print("❌ Still getting 500 error with sync client")
                return False
            else:
                print("✅ Registration successful with sync client!")
                return True
                
    except Exception as e:
        print(f"❌ Exception with sync client: {e}")
        traceback.print_exc()
        return False


async def test_async_registration():
    """Test registration with async client."""
    print("\n=== ASYNC CLIENT TEST ===")
    
    try:
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/v1/auth/register", json={
                "email": "async@test.com",
                "password": "AsyncTest123", 
                "full_name": "Async Test User"
            })
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 500:
                print("❌ Still getting 500 error with async client")
                return False
            else:
                print("✅ Registration successful with async client!")
                return True
                
    except Exception as e:
        print(f"❌ Exception with async client: {e}")
        traceback.print_exc()
        return False


async def test_manual_service_call():
    """Test by manually calling the service layer."""
    print("\n=== MANUAL SERVICE CALL TEST ===")
    
    try:
        from app.infrastructure.database.connection import get_db_session
        from app.infrastructure.repositories.user_repository import UserRepository
        from app.application.services.auth_service import AuthService
        from app.infrastructure.database.connection import create_engine
        from app.infrastructure.database.models import Base
        
        # Setup database
        engine = create_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Get session through dependency
        session_gen = get_db_session()
        session = await anext(session_gen)
        
        try:
            # Create service and test
            user_repo = UserRepository(session)
            auth_service = AuthService(user_repo)
            
            result = await auth_service.register_user(
                email="manual@test.com",
                password="ManualTest123",
                full_name="Manual Test User"
            )
            
            print("✅ Manual service call successful!")
            print(f"User ID: {result['user']['id']}")
            return True
            
        finally:
            await anext(session_gen, None)  # Close session properly
        
        await engine.dispose()
        
    except Exception as e:
        print(f"❌ Manual service call failed: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Testing registration with different approaches...")
    
    # Test 1: Sync client
    sync_success = test_sync_registration()
    
    # Test 2: Async client
    async_success = asyncio.run(test_async_registration())
    
    # Test 3: Manual service call
    manual_success = asyncio.run(test_manual_service_call())
    
    print(f"\n=== RESULTS ===")
    print(f"Sync client: {'✅ SUCCESS' if sync_success else '❌ FAILED'}")
    print(f"Async client: {'✅ SUCCESS' if async_success else '❌ FAILED'}")
    print(f"Manual service: {'✅ SUCCESS' if manual_success else '❌ FAILED'}")
    
    if manual_success and not sync_success:
        print("\n🔍 Issue is in FastAPI routing/middleware layer")
    elif not manual_success:
        print("\n🔍 Issue is in service/repository/database layer")
    else:
        print("\n✅ All tests passed!")
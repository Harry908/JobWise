"""Direct test to debug auth registration without test framework."""

import asyncio
import sys
import traceback
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.main import app
from app.infrastructure.database.connection import create_engine
from app.infrastructure.database.models import Base


async def test_registration_direct():
    """Test registration by directly calling the service."""
    print("=== DIRECT REGISTRATION TEST ===")
    
    try:
        # 1. Setup database
        print("1. Setting up database...")
        engine = create_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✓ Database setup complete")
        
        # 2. Test services directly
        print("\n2. Testing services directly...")
        from app.infrastructure.database.connection import get_db_session
        from app.infrastructure.repositories.user_repository import UserRepository
        from app.application.services.auth_service import AuthService
        
        # Get a database session using the dependency
        session_generator = get_db_session()
        session = await anext(session_generator)
        
        try:
            # Create repository and service
            user_repo = UserRepository(session)
            auth_service = AuthService(user_repo)
            
            # Test registration
            result = await auth_service.register_user(
                email="direct@test.com",
                password="DirectTest123",
                full_name="Direct Test User"
            )
            
            print("✓ Direct registration successful!")
            print(f"User ID: {result['user']['id']}")
            print(f"Email: {result['user']['email']}")
            print(f"Has access token: {len(result['access_token']) > 0}")
            
            return True
            
        finally:
            # Close session properly
            if hasattr(session, 'close'):
                await session.close()
            elif hasattr(session, 'aclose'):
                await session.aclose()
        
        await engine.dispose()
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\nFull traceback:")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_registration_direct())
    if success:
        print("\n✅ Direct registration works - issue is in FastAPI layer")
    else:
        print("\n❌ Issue is in the service/repository layer")
#!/usr/bin/env python3
"""
Test script to validate Groq LLM integration.
Tests both mock mode (no API key) and real mode (with API key).
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent / "app"))

# Load environment variables using dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables with dotenv")
except ImportError:
    print("⚠️  python-dotenv not available, using os.environ only")

from app.core.dependencies import get_llm_service
from app.core.config import get_settings
from app.domain.ports.llm_service import LLMMessage


async def test_llm_service():
    """Test LLM service with both mock and real Groq configurations."""
    
    print("🔄 Testing LLM Service Integration")
    print("=" * 50)
    
    # Debug configuration loading
    settings = get_settings()
    print(f"🔧 Configuration Debug:")
    print(f"   Groq API Key configured: {'✅ Yes' if settings.groq_api_key else '❌ No'}")
    if settings.groq_api_key:
        print(f"   API Key preview: {settings.groq_api_key[:10]}...")
    print(f"   Default model: {settings.llm_stage2_model}")
    
    # Test 1: Get service (should work with or without API key)
    try:
        service = get_llm_service()
        print(f"✅ LLM Service initialized: {type(service).__name__}")
    except Exception as e:
        print(f"❌ Failed to initialize LLM service: {e}")
        return False
    
    # Test 2: Basic generation test
    try:
        messages = [
            LLMMessage(role="system", content="You are a helpful assistant."),
            LLMMessage(role="user", content="Say hello in one sentence.")
        ]
        
        response = await service.generate(
            messages=messages,
            model="llama-3.3-70b-versatile",
            max_tokens=50,
            temperature=0.1
        )
        
        print(f"✅ Generation successful:")
        print(f"   Model: {response.model}")
        print(f"   Tokens: {response.tokens_used}")
        print(f"   Content: {response.content[:100]}...")
        print(f"   Finish reason: {response.finish_reason}")
        
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        return False
    
    # Test 3: Check environment configuration
    print(f"\n🔧 Environment Configuration:")
    print(f"   GROQ_API_KEY in os.environ: {'✅' if os.getenv('GROQ_API_KEY') else '❌'}")
    print(f"   GROQ_API_KEY in settings: {'✅' if settings.groq_api_key else '❌'}")
    
    env_key = os.getenv('GROQ_API_KEY')
    if env_key:
        print(f"   OS Environment key preview: {env_key[:10]}...")
    if settings.groq_api_key:
        print(f"   Settings key preview: {settings.groq_api_key[:10]}...")
    
    # Test 4: Service type validation
    from app.infrastructure.adapters.groq_llm_service import GroqLLMService
    from app.infrastructure.adapters.mock_llm_adapter import MockLLMAdapter
    
    if isinstance(service, GroqLLMService):
        print(f"   Using: ✅ Real Groq API")
        print(f"   Model: {service.default_model}")
    elif isinstance(service, MockLLMAdapter):
        print(f"   Using: ⚠️  Mock LLM (set GROQ_API_KEY for real API)")
    else:
        print(f"   Using: ❓ Unknown service type: {type(service)}")
    
    print(f"\n✅ All tests passed! Generation API is ready.")
    return True


def main():
    """Main test function."""
    print("JobWise Backend - Groq LLM Integration Test\n")
    
    try:
        success = asyncio.run(test_llm_service())
        if success:
            print(f"\n🎉 Integration test completed successfully!")
            print(f"💡 To use real Groq API, set your GROQ_API_KEY environment variable.")
        else:
            print(f"\n❌ Integration test failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
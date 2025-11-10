#!/usr/bin/env python3
"""
Direct LLM test - use the GroqAdapter directly
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.append('.')

from app.infrastructure.adapters.groq_adapter import GroqAdapter

async def test_direct_llm():
    print("🔍 Direct Groq LLM Test")
    print("=" * 50)
    
    # Test if we can import and use GroqAdapter directly
    try:
        groq = GroqAdapter()
        print(f"✅ GroqAdapter initialized")
        print(f"   Model: {groq.model}")
        
        # Simple test prompt
        test_prompt = """
Generate a professional summary for a software engineer with these qualifications:
- 5+ years experience in Python backend development
- Expert in FastAPI, SQLAlchemy, PostgreSQL
- Experience with AWS cloud services
- Led teams and mentored junior developers
- Strong problem-solving and communication skills

Write a 2-3 sentence professional summary suitable for a resume.
"""
        
        print("🚀 Testing real LLM generation...")
        result = await groq.generate(
            prompt=test_prompt,
            temperature=0.7,
            max_tokens=200
        )
        
        print("\n📄 Generated Professional Summary:")
        print("-" * 50)
        print(result)
        print("-" * 50)
        
        # Save to file
        with open("llm_test_output.txt", "w", encoding="utf-8") as f:
            f.write(f"Test Prompt:\n{test_prompt}\n\n")
            f.write(f"Generated Output:\n{result}\n")
        
        print(f"💾 Output saved to: llm_test_output.txt")
        print(f"✅ Real LLM integration working!")
        
        # Test model info
        model_info = groq.get_model_info()
        usage_stats = groq.get_usage_stats()
        
        print(f"\n🔧 Model Info:")
        for key, value in model_info.items():
            print(f"   {key}: {value}")
        
        print(f"\n📊 Usage Stats:")
        for key, value in usage_stats.items():
            print(f"   {key}: {value}")
            
    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_direct_llm())
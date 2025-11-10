#!/usr/bin/env python3
"""
Command-line interface for testing Groq LLM integration.

Usage:
    python test_groq_cli.py --help
    python test_groq_cli.py basic "What is FastAPI?"
    python test_groq_cli.py style cover_letter.txt
    python test_groq_cli.py layout resume.txt
    python test_groq_cli.py json "Analyze this text" --schema user_schema.json
"""

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, _, value = line.partition('=')
                    os.environ[key.strip()] = value.strip()
        print(f"✅ Loaded environment from {env_path}")
    else:
        print(f"⚠️ No .env file found at {env_path}")

# Load environment first
load_env_file()

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

try:
    from app.infrastructure.adapters.groq_adapter import GroqAdapter
    from app.core.exceptions import LLMServiceError, LLMTimeoutError, LLMValidationError, RateLimitError
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running this from the backend directory")
    sys.exit(1)


class GroqCLI:
    """Command-line interface for Groq testing."""
    
    def __init__(self):
        self.groq = None
        
    async def initialize(self, model: str = "llama-3.1-8b-instant"):
        """Initialize Groq adapter."""
        try:
            self.groq = GroqAdapter(model=model)
            print(f"✅ Groq adapter initialized with model: {model}")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize Groq: {e}")
            return False

    async def test_basic(self, prompt: str, temperature: float = 0.7, max_tokens: int = 500):
        """Test basic text generation."""
        try:
            print(f"\n📝 Generating response for: '{prompt[:50]}...'")
            print(f"⚙️ Temperature: {temperature}, Max tokens: {max_tokens}")
            
            start_time = time.time()
            response = await self.groq.generate(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            end_time = time.time()
            
            print(f"\n✅ Response generated in {end_time - start_time:.2f}s:")
            print("=" * 60)
            print(response)
            print("=" * 60)
            
            # Show usage stats
            stats = self.groq.get_usage_stats()
            print(f"\n📊 Usage: {stats['requests_last_minute']}/{stats['rate_limit']} requests/min")
            
        except (LLMServiceError, LLMTimeoutError, RateLimitError, LLMValidationError) as e:
            print(f"❌ LLM Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

    async def test_writing_style_extraction(self, file_path: str):
        """Test writing style extraction from cover letter."""
        try:
            # Read file
            path = Path(file_path)
            if not path.exists():
                print(f"❌ File not found: {file_path}")
                return
                
            if path.suffix.lower() not in ['.txt', '.md']:
                print(f"❌ Unsupported file type: {path.suffix}. Use .txt or .md files.")
                return
            
            print(f"\n📄 Reading cover letter from: {file_path}")
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if len(content.strip()) < 50:
                print("⚠️ File content seems too short for meaningful analysis")
                return
            
            print(f"📊 Content length: {len(content)} chars, {len(content.split())} words")
            
            # Extract writing style
            print("\n🎨 Extracting writing style preferences...")
            start_time = time.time()
            
            result = await self.groq.extract_writing_style(content)
            
            end_time = time.time()
            
            print(f"\n✅ Writing style extracted in {end_time - start_time:.2f}s:")
            print("=" * 60)
            print(json.dumps(result, indent=2))
            print("=" * 60)
            
        except (LLMServiceError, LLMTimeoutError, RateLimitError, LLMValidationError) as e:
            print(f"❌ LLM Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

    async def test_layout_extraction(self, file_path: str):
        """Test layout preference extraction from resume."""
        try:
            # Read file
            path = Path(file_path)
            if not path.exists():
                print(f"❌ File not found: {file_path}")
                return
                
            if path.suffix.lower() not in ['.txt', '.md']:
                print(f"❌ Unsupported file type: {path.suffix}. Use .txt or .md files.")
                return
            
            print(f"\n📄 Reading resume from: {file_path}")
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if len(content.strip()) < 100:
                print("⚠️ File content seems too short for meaningful analysis")
                return
            
            print(f"📊 Content length: {len(content)} chars, {len(content.split())} words")
            
            # Extract layout preferences
            print("\n🏗️ Extracting layout preferences...")
            start_time = time.time()
            
            result = await self.groq.extract_layout_preferences(content)
            
            end_time = time.time()
            
            print(f"\n✅ Layout preferences extracted in {end_time - start_time:.2f}s:")
            print("=" * 60)
            print(json.dumps(result, indent=2))
            print("=" * 60)
            
        except (LLMServiceError, LLMTimeoutError, RateLimitError, LLMValidationError) as e:
            print(f"❌ LLM Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

    async def test_structured_generation(self, prompt: str, schema_file: str = None):
        """Test structured JSON generation."""
        try:
            # Default schema
            default_schema = {
                "summary": "Brief summary of the analysis",
                "key_points": ["list", "of", "key", "points"],
                "confidence": "confidence level (low/medium/high)",
                "recommendations": ["list", "of", "recommendations"]
            }
            
            # Load custom schema if provided
            if schema_file:
                schema_path = Path(schema_file)
                if schema_path.exists():
                    with open(schema_path, 'r') as f:
                        schema = json.load(f)
                    print(f"📋 Using schema from: {schema_file}")
                else:
                    print(f"⚠️ Schema file not found: {schema_file}, using default schema")
                    schema = default_schema
            else:
                schema = default_schema
                print("📋 Using default schema")
            
            print(f"\n🔧 Schema:")
            print(json.dumps(schema, indent=2))
            
            print(f"\n🎯 Generating structured response for: '{prompt[:50]}...'")
            
            start_time = time.time()
            result = await self.groq.generate_structured(
                prompt=prompt,
                response_format=schema,
                temperature=0.1,
                max_tokens=800
            )
            end_time = time.time()
            
            print(f"\n✅ Structured response generated in {end_time - start_time:.2f}s:")
            print("=" * 60)
            print(json.dumps(result, indent=2))
            print("=" * 60)
            
        except (LLMServiceError, LLMTimeoutError, RateLimitError, LLMValidationError) as e:
            print(f"❌ LLM Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

    async def show_model_info(self):
        """Show model information and usage stats."""
        try:
            if not self.groq:
                print("❌ Groq not initialized")
                return
                
            print("\n📋 Model Information:")
            info = self.groq.get_model_info()
            for key, value in info.items():
                print(f"  {key}: {value}")
            
            print("\n📊 Usage Statistics:")
            stats = self.groq.get_usage_stats()
            for key, value in stats.items():
                print(f"  {key}: {value}")
                
        except Exception as e:
            print(f"❌ Error getting model info: {e}")

    def print_examples(self):
        """Print usage examples."""
        examples = """
🎯 Usage Examples:

1. Basic text generation:
   python test_groq_cli.py basic "Explain the benefits of FastAPI"

2. Extract writing style from cover letter:
   python test_groq_cli.py style sample_cover_letter.txt

3. Extract layout preferences from resume:
   python test_groq_cli.py layout sample_resume.txt

4. Structured JSON generation:
   python test_groq_cli.py json "Analyze the pros and cons of remote work"

5. Custom JSON schema:
   python test_groq_cli.py json "Review this product" --schema product_schema.json

6. Model information:
   python test_groq_cli.py info

7. Advanced parameters:
   python test_groq_cli.py basic "Creative writing prompt" --temp 0.9 --tokens 800

📝 File Requirements:
- Cover letters and resumes should be in .txt or .md format
- Minimum 50 characters for cover letters, 100 for resumes
- Files should contain meaningful text content

🔧 Environment:
- Set GROQ_API_KEY environment variable
- Run from the backend directory
"""
        print(examples)


async def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Test Groq LLM integration",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Basic generation
    basic_parser = subparsers.add_parser('basic', help='Basic text generation')
    basic_parser.add_argument('prompt', help='Prompt text')
    basic_parser.add_argument('--temp', type=float, default=0.7, help='Temperature (0.0-1.0)')
    basic_parser.add_argument('--tokens', type=int, default=500, help='Max tokens')
    basic_parser.add_argument('--model', default='llama-3.1-8b-instant', help='Model name')
    
    # Writing style extraction
    style_parser = subparsers.add_parser('style', help='Extract writing style from cover letter')
    style_parser.add_argument('file', help='Cover letter file (.txt or .md)')
    style_parser.add_argument('--model', default='llama-3.1-8b-instant', help='Model name')
    
    # Layout extraction
    layout_parser = subparsers.add_parser('layout', help='Extract layout preferences from resume')
    layout_parser.add_argument('file', help='Resume file (.txt or .md)')
    layout_parser.add_argument('--model', default='llama-3.1-8b-instant', help='Model name')
    
    # Structured generation
    json_parser = subparsers.add_parser('json', help='Structured JSON generation')
    json_parser.add_argument('prompt', help='Prompt text')
    json_parser.add_argument('--schema', help='JSON schema file')
    json_parser.add_argument('--model', default='llama-3.1-8b-instant', help='Model name')
    
    # Model info
    info_parser = subparsers.add_parser('info', help='Show model information')
    info_parser.add_argument('--model', default='llama-3.1-8b-instant', help='Model name')
    
    # Examples
    subparsers.add_parser('examples', help='Show usage examples')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'examples':
        cli = GroqCLI()
        cli.print_examples()
        return
    
    # Initialize CLI
    cli = GroqCLI()
    model = getattr(args, 'model', 'llama-3.1-8b-instant')
    
    if not await cli.initialize(model):
        return
    
    # Execute command
    try:
        if args.command == 'basic':
            await cli.test_basic(args.prompt, args.temp, args.tokens)
        
        elif args.command == 'style':
            await cli.test_writing_style_extraction(args.file)
        
        elif args.command == 'layout':
            await cli.test_layout_extraction(args.file)
        
        elif args.command == 'json':
            await cli.test_structured_generation(args.prompt, args.schema)
        
        elif args.command == 'info':
            await cli.show_model_info()
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("GROQ_API_KEY"):
        print("❌ GROQ_API_KEY environment variable is not set")
        print("💡 Set it with: export GROQ_API_KEY=your_api_key")
        print("💡 Or add it to your .env file")
        sys.exit(1)
    
    asyncio.run(main())
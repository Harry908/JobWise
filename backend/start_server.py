#!/usr/bin/env python3
"""
JobWise Backend Server Startup Script (Python Version)

This script provides a cross-platform way to start the FastAPI server.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def check_environment():
    """Check if we're in the right environment."""
    # Change to the script's directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    if not Path("app/main.py").exists():
        print("❌ Error: Not in backend directory. Please run this script from the backend folder.")
        sys.exit(1)

    if not Path("venv").exists():
        print("❌ Error: Virtual environment not found. Please run setup first.")
        print("Run: python -m venv venv")
        sys.exit(1)

    print("✅ Environment check passed")


def activate_venv():
    """Activate virtual environment."""
    print("🔧 Activating virtual environment...")

    if platform.system() == "Windows":
        activate_script = Path("venv/Scripts/activate.bat")
        if not activate_script.exists():
            activate_script = Path("venv/Scripts/Activate.ps1")
    else:
        activate_script = Path("venv/bin/activate")

    if not activate_script.exists():
        print(f"❌ Error: Activation script not found at {activate_script}")
        sys.exit(1)

    print(f"✅ Virtual environment ready")


def check_env_file():
    """Check for environment file."""
    if Path(".env").exists():
        print("📄 Found .env file")
    else:
        print("⚠️  Warning: .env file not found. Using default configuration.")


def start_server():
    """Start the FastAPI server."""
    print("🌐 Starting FastAPI server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📖 API Documentation at: http://localhost:8000/docs")
    print("🔄 Alternative docs at: http://localhost:8000/redoc")
    print()
    print("💡 To test the server in another terminal:")
    print("   1. Open a new terminal")
    print("   2. Navigate to the backend directory")
    print("   3. Activate venv and run tests:")
    if platform.system() == "Windows":
        print("      venv\\Scripts\\activate.bat && python -m pytest tests/ -v")
    else:
        print("      source venv/bin/activate && python -m pytest tests/ -v")
    print()

    try:
        # Start uvicorn server
        cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: Failed to start server - {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        sys.exit(0)


def main():
    """Main entry point."""
    print("🚀 JobWise Backend Server Startup")
    print("=" * 40)

    check_environment()
    activate_venv()
    check_env_file()
    print()

    start_server()


if __name__ == "__main__":
    main()
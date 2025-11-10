#!/usr/bin/env python3
"""
Comprehensive Generation API Verification Test

This test script verifies the JobWise Generation API implementation,
including database connectivity, endpoints, LLM integration, and error handling.
"""

import asyncio
import json
import sqlite3
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Add backend to path for imports
sys.path.insert(0, os.path.abspath('.'))

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

# Test configuration
TEST_BASE_URL = "http://localhost:8000"
TEST_DB_PATH = "test.db"

class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class TestResult:
    """Test result tracking."""
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.failures = []

    def record_test(self, test_name: str, passed: bool, message: str = ""):
        self.tests_run += 1
        if passed:
            self.tests_passed += 1
            print(f"  {Colors.OKGREEN}✓{Colors.ENDC} {test_name}")
            if message:
                print(f"    {Colors.OKCYAN}→{Colors.ENDC} {message}")
        else:
            self.tests_failed += 1
            self.failures.append(f"{test_name}: {message}")
            print(f"  {Colors.FAIL}✗{Colors.ENDC} {test_name}")
            print(f"    {Colors.FAIL}→{Colors.ENDC} {message}")

    def print_summary(self):
        print(f"\n{Colors.BOLD}═══ TEST SUMMARY ═══{Colors.ENDC}")
        print(f"Total Tests: {self.tests_run}")
        print(f"{Colors.OKGREEN}Passed: {self.tests_passed}{Colors.ENDC}")
        print(f"{Colors.FAIL}Failed: {self.tests_failed}{Colors.ENDC}")
        
        if self.failures:
            print(f"\n{Colors.FAIL}Failed Tests:{Colors.ENDC}")
            for failure in self.failures:
                print(f"  • {failure}")
        
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        print(f"\nSuccess Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print(f"{Colors.OKGREEN}✓ GENERATION API VERIFICATION PASSED{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}✗ GENERATION API VERIFICATION FAILED{Colors.ENDC}")

class GenerationAPIVerifier:
    """Main verification class for Generation API."""

    def __init__(self):
        self.result = TestResult()
        self.auth_token: Optional[str] = None
        self.test_user_id: Optional[int] = None
        self.test_profile_id: Optional[str] = None
        self.test_job_id: Optional[str] = None

    def print_header(self, title: str):
        """Print section header."""
        print(f"\n{Colors.HEADER}{'=' * 60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{title.center(60)}{Colors.ENDC}")
        print(f"{Colors.HEADER}{'=' * 60}{Colors.ENDC}\n")

    def verify_database_schema(self):
        """Verify database tables exist and have correct schema."""
        self.print_header("DATABASE SCHEMA VERIFICATION")
        
        # Check if database file exists
        if not os.path.exists(TEST_DB_PATH):
            self.result.record_test("Database file exists", False, f"{TEST_DB_PATH} not found")
            return

        try:
            conn = sqlite3.connect(TEST_DB_PATH)
            cursor = conn.cursor()

            # Check generations table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='generations'")
            table_exists = cursor.fetchone() is not None
            self.result.record_test("Generations table exists", table_exists)

            if table_exists:
                # Verify schema
                cursor.execute("PRAGMA table_info(generations)")
                columns = cursor.fetchall()
                column_names = [col[1] for col in columns]
                
                required_columns = [
                    'id', 'user_id', 'profile_id', 'job_id', 'document_type',
                    'status', 'current_stage', 'total_stages', 'stage_name',
                    'stage_description', 'options', 'result', 'created_at'
                ]
                
                missing_columns = [col for col in required_columns if col not in column_names]
                self.result.record_test(
                    "Required columns present",
                    len(missing_columns) == 0,
                    f"Missing: {missing_columns}" if missing_columns else f"Found {len(columns)} columns"
                )

            # Check preference tables
            preference_tables = ['user_generation_profiles', 'writing_style_configs', 'layout_configs']
            for table in preference_tables:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                exists = cursor.fetchone() is not None
                self.result.record_test(f"{table} table exists", exists)

            conn.close()

        except Exception as e:
            self.result.record_test("Database connectivity", False, str(e))

    async def verify_server_connectivity(self):
        """Verify server is running and responds."""
        self.print_header("SERVER CONNECTIVITY VERIFICATION")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Test health endpoint
                response = await client.get(f"{TEST_BASE_URL}/health")
                self.result.record_test(
                    "Server health endpoint",
                    response.status_code == 200,
                    f"Status: {response.status_code}"
                )

                # Test API documentation endpoint
                response = await client.get(f"{TEST_BASE_URL}/docs")
                self.result.record_test(
                    "API documentation endpoint",
                    response.status_code == 200,
                    f"Status: {response.status_code}"
                )

        except Exception as e:
            self.result.record_test("Server connectivity", False, str(e))

    async def setup_test_data(self):
        """Setup test user, profile, and job data."""
        self.print_header("TEST DATA SETUP")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Create test user
                register_data = {
                    "email": f"test_generation_{datetime.now().timestamp()}@example.com",
                    "password": "testpassword123",
                    "full_name": "Test User Generation"
                }
                
                response = await client.post(f"{TEST_BASE_URL}/api/v1/auth/register", json=register_data)
                if response.status_code == 201:
                    auth_data = response.json()
                    self.auth_token = auth_data["access_token"]
                    self.test_user_id = auth_data["user"]["id"]
                    self.result.record_test("Test user created", True, f"User ID: {self.test_user_id}")
                else:
                    self.result.record_test("Test user creation", False, f"Status: {response.status_code}")
                    return

                # Setup auth headers
                headers = {"Authorization": f"Bearer {self.auth_token}"}

                # Create test profile
                response = await client.get(f"{TEST_BASE_URL}/api/v1/profiles/me", headers=headers)
                if response.status_code == 200:
                    profile_data = response.json()
                    self.test_profile_id = profile_data["id"]
                    self.result.record_test("Test profile available", True, f"Profile ID: {self.test_profile_id}")
                else:
                    self.result.record_test("Test profile setup", False, f"Status: {response.status_code}")
                    return

                # Create test job
                job_data = {
                    "source": "user_created",
                    "title": "Senior Software Engineer",
                    "company": "Test Company",
                    "description": "We are seeking a Senior Software Engineer to join our team. Experience with Python, FastAPI, and AI technologies required.",
                    "location": "Remote",
                    "employment_type": "full_time",
                    "requirements": ["Python", "FastAPI", "AI/ML", "REST APIs"],
                    "salary_range": "$120,000 - $150,000"
                }
                
                response = await client.post(f"{TEST_BASE_URL}/api/v1/jobs", json=job_data, headers=headers)
                if response.status_code == 201:
                    job_response = response.json()
                    self.test_job_id = job_response["id"]
                    self.result.record_test("Test job created", True, f"Job ID: {self.test_job_id}")
                else:
                    self.result.record_test("Test job creation", False, f"Status: {response.status_code}")

        except Exception as e:
            self.result.record_test("Test data setup", False, str(e))

    async def verify_generation_endpoints(self):
        """Test all Generation API endpoints."""
        self.print_header("GENERATION ENDPOINTS VERIFICATION")
        
        if not self.auth_token or not self.test_profile_id or not self.test_job_id:
            self.result.record_test("Prerequisites for endpoint testing", False, "Missing auth token, profile, or job")
            return

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                
                # Test templates endpoint
                response = await client.get(f"{TEST_BASE_URL}/api/v1/generations/templates", headers=headers)
                self.result.record_test(
                    "GET /generations/templates",
                    response.status_code == 200,
                    f"Status: {response.status_code}"
                )

                # Test resume generation endpoint
                generation_request = {
                    "profile_id": self.test_profile_id,
                    "job_id": self.test_job_id,
                    "options": {
                        "template": "modern",
                        "length": "one_page",
                        "focus_areas": ["technical_skills", "leadership"]
                    }
                }

                response = await client.post(
                    f"{TEST_BASE_URL}/api/v1/generations/resume",
                    json=generation_request,
                    headers=headers
                )
                
                if response.status_code == 201:
                    generation_data = response.json()
                    generation_id = generation_data["id"]
                    self.result.record_test("POST /generations/resume", True, f"Generation ID: {generation_id}")
                    
                    # Test status endpoint
                    response = await client.get(
                        f"{TEST_BASE_URL}/api/v1/generations/{generation_id}",
                        headers=headers
                    )
                    self.result.record_test(
                        "GET /generations/{id} (status)",
                        response.status_code == 200,
                        f"Status: {response.status_code}"
                    )

                    # Wait a bit and check progress
                    await asyncio.sleep(2)
                    response = await client.get(
                        f"{TEST_BASE_URL}/api/v1/generations/{generation_id}",
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        status_data = response.json()
                        current_status = status_data.get("status", "unknown")
                        current_stage = status_data.get("progress", {}).get("current_stage", 0)
                        self.result.record_test(
                            "Generation progress tracking",
                            True,
                            f"Status: {current_status}, Stage: {current_stage}"
                        )
                    
                    # Test result endpoint (might not be ready yet)
                    response = await client.get(
                        f"{TEST_BASE_URL}/api/v1/generations/{generation_id}/result",
                        headers=headers
                    )
                    if response.status_code == 200:
                        self.result.record_test("GET /generations/{id}/result", True, "Result available")
                    else:
                        self.result.record_test(
                            "GET /generations/{id}/result",
                            response.status_code in [404, 400],  # Expected if not complete
                            f"Status: {response.status_code} (expected for in-progress)"
                        )

                    # Test cancel endpoint
                    response = await client.delete(
                        f"{TEST_BASE_URL}/api/v1/generations/{generation_id}",
                        headers=headers
                    )
                    self.result.record_test(
                        "DELETE /generations/{id}",
                        response.status_code == 204,
                        f"Status: {response.status_code}"
                    )

                else:
                    self.result.record_test(
                        "POST /generations/resume",
                        False,
                        f"Status: {response.status_code}, Response: {response.text[:200]}"
                    )

                # Test list generations endpoint
                response = await client.get(f"{TEST_BASE_URL}/api/v1/generations", headers=headers)
                self.result.record_test(
                    "GET /generations (list)",
                    response.status_code == 200,
                    f"Status: {response.status_code}"
                )

        except Exception as e:
            self.result.record_test("Generation endpoints testing", False, str(e))

    async def verify_error_handling(self):
        """Test error handling scenarios."""
        self.print_header("ERROR HANDLING VERIFICATION")
        
        if not self.auth_token:
            self.result.record_test("Prerequisites for error testing", False, "Missing auth token")
            return

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                
                # Test unauthorized access
                response = await client.get(f"{TEST_BASE_URL}/api/v1/generations/templates")
                self.result.record_test(
                    "Unauthorized access rejection",
                    response.status_code == 401,
                    f"Status: {response.status_code}"
                )

                # Test invalid generation ID
                response = await client.get(
                    f"{TEST_BASE_URL}/api/v1/generations/invalid-uuid-123",
                    headers=headers
                )
                self.result.record_test(
                    "Invalid generation ID handling",
                    response.status_code in [404, 400],
                    f"Status: {response.status_code}"
                )

                # Test missing profile_id in generation request
                invalid_request = {
                    "job_id": self.test_job_id if self.test_job_id else "test-job-id"
                    # Missing profile_id
                }
                response = await client.post(
                    f"{TEST_BASE_URL}/api/v1/generations/resume",
                    json=invalid_request,
                    headers=headers
                )
                self.result.record_test(
                    "Missing required fields handling",
                    response.status_code == 422,
                    f"Status: {response.status_code}"
                )

                # Test non-existent profile/job IDs
                invalid_request = {
                    "profile_id": "non-existent-profile-id",
                    "job_id": "non-existent-job-id"
                }
                response = await client.post(
                    f"{TEST_BASE_URL}/api/v1/generations/resume",
                    json=invalid_request,
                    headers=headers
                )
                self.result.record_test(
                    "Non-existent resource handling",
                    response.status_code in [404, 400],
                    f"Status: {response.status_code}"
                )

        except Exception as e:
            self.result.record_test("Error handling testing", False, str(e))

    async def verify_llm_integration(self):
        """Test LLM integration (if available)."""
        self.print_header("LLM INTEGRATION VERIFICATION")
        
        try:
            # Check if Groq API key is available
            groq_api_key = os.getenv("GROQ_API_KEY")
            if not groq_api_key:
                self.result.record_test("Groq API Key", False, "GROQ_API_KEY environment variable not set")
                return

            self.result.record_test("Groq API Key", True, "Environment variable set")

            # Test GroqAdapter initialization
            try:
                from app.infrastructure.adapters.groq_adapter import GroqAdapter
                adapter = GroqAdapter(api_key=groq_api_key)
                self.result.record_test("GroqAdapter initialization", True, f"Model: {adapter.model}")
            except Exception as e:
                self.result.record_test("GroqAdapter initialization", False, str(e))

            # Test simple generation (if adapter works)
            try:
                simple_response = await adapter.generate("Hello, world!", max_tokens=10, timeout=5.0)
                self.result.record_test("LLM generation test", True, f"Response length: {len(simple_response)}")
            except Exception as e:
                self.result.record_test("LLM generation test", False, str(e))

        except Exception as e:
            self.result.record_test("LLM integration verification", False, str(e))

    async def run_all_verifications(self):
        """Run all verification tests."""
        print(f"{Colors.BOLD}🔍 JobWise Generation API Comprehensive Verification{Colors.ENDC}")
        print(f"Starting verification at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Run all verification steps
        self.verify_database_schema()
        await self.verify_server_connectivity()
        await self.setup_test_data()
        await self.verify_generation_endpoints()
        await self.verify_error_handling()
        await self.verify_llm_integration()

        # Print final summary
        self.result.print_summary()

        return self.result.tests_passed >= int(self.result.tests_run * 0.8)  # 80% pass rate

async def main():
    """Main entry point."""
    verifier = GenerationAPIVerifier()
    success = await verifier.run_all_verifications()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
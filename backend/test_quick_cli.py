#!/usr/bin/env python3
"""
Quick CLI for JobWise Backend Testing (No Frontend Required)

This script provides a simple command-line interface to test all
backend functionality without needing the mobile frontend.
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional

import httpx

# Test configuration
BASE_URL = "http://localhost:8000"

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

class JobWiseCLI:
    """Simple CLI for JobWise backend testing."""
    
    def __init__(self):
        self.auth_token: Optional[str] = None
        self.user_id: Optional[int] = None
        self.profile_id: Optional[str] = None
        self.jobs = []
        
    def print_header(self, title: str):
        """Print section header."""
        print(f"\n{Colors.HEADER}{'=' * 60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{title.center(60)}{Colors.ENDC}")
        print(f"{Colors.HEADER}{'=' * 60}{Colors.ENDC}")
        
    def print_success(self, message: str):
        """Print success message."""
        print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")
        
    def print_error(self, message: str):
        """Print error message."""
        print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")
        
    def print_info(self, message: str):
        """Print info message."""
        print(f"{Colors.OKCYAN}→ {message}{Colors.ENDC}")

    async def check_server(self) -> bool:
        """Check if server is running."""
        self.print_header("SERVER CONNECTIVITY CHECK")
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{BASE_URL}/health")
                if response.status_code == 200:
                    self.print_success("Server is running")
                    self.print_info(f"Health check: {response.json()}")
                    return True
                else:
                    self.print_error(f"Server health check failed: {response.status_code}")
                    return False
        except Exception as e:
            self.print_error(f"Cannot connect to server: {e}")
            self.print_info("Make sure to start the server with: .\\start-server.bat")
            return False

    async def login_or_register(self) -> bool:
        """Login with existing test user or create new one."""
        self.print_header("AUTHENTICATION")
        
        # First try with existing test user
        test_credentials = [
            {"email": "sarah.chen@example.com", "password": "TestPassword123"},
            {"email": f"testuser_{datetime.now().strftime('%Y%m%d')}@example.com", "password": "TestPassword123"}
        ]
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Try login with existing test users
                for creds in test_credentials:
                    try:
                        response = await client.post(f"{BASE_URL}/api/v1/auth/login", json=creds)
                        
                        if response.status_code == 200:
                            auth_data = response.json()
                            self.auth_token = auth_data["access_token"]
                            self.user_id = auth_data["user"]["id"]
                            self.print_success(f"Logged in successfully with {creds['email']}")
                            self.print_info(f"User ID: {self.user_id}")
                            return True
                    except Exception:
                        continue
                
                # If login failed, try registration with new credentials
                register_data = {
                    "email": f"testcli_{int(datetime.now().timestamp())}@example.com",
                    "password": "TestPassword123",
                    "full_name": "Test CLI User"
                }
                
                response = await client.post(f"{BASE_URL}/api/v1/auth/register", json=register_data)
                
                if response.status_code == 201:
                    auth_data = response.json()
                    self.auth_token = auth_data["access_token"]
                    self.user_id = auth_data["user"]["id"]
                    self.print_success("New user registered successfully")
                    self.print_info(f"User ID: {self.user_id}")
                    return True
                else:
                    self.print_error(f"Authentication failed completely: {response.status_code}")
                    self.print_info(f"Response: {response.text}")
                    return False
                    
        except Exception as e:
            self.print_error(f"Authentication error: {e}")
            return False

    async def test_profile_api(self) -> bool:
        """Test profile API endpoints."""
        self.print_header("PROFILE API TESTING")
        
        if not self.auth_token:
            self.print_error("No auth token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Get current profile
                response = await client.get(f"{BASE_URL}/api/v1/profiles/me", headers=headers)
                
                if response.status_code == 200:
                    profile = response.json()
                    self.profile_id = profile["id"]
                    self.print_success("Profile retrieved successfully")
                    self.print_info(f"Profile ID: {self.profile_id}")
                    self.print_info(f"Name: {profile.get('personal_info', {}).get('full_name', 'N/A')}")
                    return True
                elif response.status_code == 404:
                    # No profile exists, create a basic one
                    self.print_info("No profile found, creating basic profile...")
                    
                    profile_data = {
                        "personal_info": {
                            "full_name": "CLI Test User",
                            "email": "cli.test@example.com",
                            "phone": "(555) 123-4567",
                            "location": "Remote, US"
                        },
                        "professional_summary": "Software Engineer with experience in Python, FastAPI, and backend development. Passionate about building scalable APIs and AI-powered applications.",
                        "experiences": [
                            {
                                "id": "exp_1",
                                "title": "Software Engineer",
                                "company": "Tech Company",
                                "location": "Remote",
                                "start_date": "2023-01-01",
                                "end_date": None,
                                "is_current": True,
                                "description": "Developing backend APIs and integrating AI services.",
                                "achievements": [
                                    "Built REST APIs with FastAPI and SQLAlchemy",
                                    "Integrated AI/LLM services for document generation",
                                    "Implemented comprehensive testing with 80%+ coverage"
                                ]
                            }
                        ],
                        "education": [
                            {
                                "id": "edu_1",
                                "institution": "University",
                                "degree": "Bachelor of Science",
                                "field_of_study": "Computer Science",
                                "start_date": "2019-09-01",
                                "end_date": "2023-06-15",
                                "gpa": 3.5,
                                "honors": []
                            }
                        ],
                        "skills": {
                            "technical": ["Python", "FastAPI", "SQLAlchemy", "REST APIs", "Docker", "Git"],
                            "soft": ["Problem Solving", "Team Collaboration", "Communication"],
                            "languages": [{"name": "English", "proficiency": "native"}],
                            "certifications": []
                        },
                        "projects": [
                            {
                                "id": "proj_1",
                                "name": "JobWise Backend",
                                "description": "AI-powered job application assistant with 5-stage resume generation pipeline.",
                                "technologies": ["Python", "FastAPI", "SQLAlchemy", "AI/ML"],
                                "url": "https://github.com/example/jobwise",
                                "start_date": "2024-01-01",
                                "end_date": "2024-12-31"
                            }
                        ],
                        "custom_fields": {}
                    }
                    
                    response = await client.post(f"{BASE_URL}/api/v1/profiles", json=profile_data, headers=headers)
                    
                    if response.status_code == 201:
                        profile = response.json()
                        self.profile_id = profile["id"]
                        self.print_success("Profile created successfully")
                        self.print_info(f"Profile ID: {self.profile_id}")
                        return True
                    else:
                        self.print_error(f"Failed to create profile: {response.status_code}")
                        self.print_info(f"Response: {response.text}")
                        return False
                else:
                    self.print_error(f"Failed to get profile: {response.status_code}")
                    self.print_info(f"Response: {response.text}")
                    return False
                    
        except Exception as e:
            self.print_error(f"Profile API error: {e}")
            return False

    async def test_jobs_api(self) -> bool:
        """Test jobs API endpoints."""
        self.print_header("JOBS API TESTING")
        
        if not self.auth_token:
            self.print_error("No auth token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Browse available jobs
                response = await client.get(f"{BASE_URL}/api/v1/jobs/browse?limit=5", headers=headers)
                
                if response.status_code == 200:
                    jobs_data = response.json()
                    browse_jobs = jobs_data.get("jobs", [])
                    self.print_success(f"Browse API: Found {len(browse_jobs)} jobs")
                else:
                    self.print_error(f"Browse jobs failed: {response.status_code}")
                
                # Create a test job
                job_data = {
                    "source": "user_created",
                    "title": "Senior Python Developer",
                    "company": "TechCorp CLI Test",
                    "description": "Looking for a Senior Python Developer with FastAPI experience. Must have strong backend development skills and experience with AI/ML integration.",
                    "location": "Remote",
                    "employment_type": "full_time",
                    "requirements": ["Python", "FastAPI", "SQLAlchemy", "REST APIs", "AsyncIO"],
                    "salary_range": "$100,000 - $130,000"
                }
                
                response = await client.post(f"{BASE_URL}/api/v1/jobs", json=job_data, headers=headers)
                
                if response.status_code == 201:
                    job = response.json()
                    job_id = job["id"]
                    self.jobs.append(job)
                    self.print_success("Test job created successfully")
                    self.print_info(f"Job ID: {job_id}")
                    self.print_info(f"Title: {job['title']}")
                    
                    # Get the job details
                    response = await client.get(f"{BASE_URL}/api/v1/jobs/{job_id}", headers=headers)
                    if response.status_code == 200:
                        self.print_success("Job retrieved successfully")
                        job_details = response.json()
                        self.print_info(f"Requirements: {', '.join(job_details.get('requirements', []))}")
                    
                    return True
                else:
                    self.print_error(f"Job creation failed: {response.status_code}")
                    self.print_info(f"Response: {response.text}")
                    return False
                    
        except Exception as e:
            self.print_error(f"Jobs API error: {e}")
            return False

    async def test_generation_api(self) -> bool:
        """Test generation API endpoints."""
        self.print_header("GENERATION API TESTING")
        
        if not self.auth_token or not self.profile_id:
            self.print_error("Missing auth token or profile")
            return False
            
        if not self.jobs:
            self.print_error("No test jobs available")
            return False
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        job_id = self.jobs[0]["id"]
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Test templates endpoint
                response = await client.get(f"{BASE_URL}/api/v1/generations/templates", headers=headers)
                if response.status_code == 200:
                    templates = response.json()
                    self.print_success("Templates retrieved successfully")
                    self.print_info(f"Available templates: {', '.join(templates.get('templates', []))}")
                else:
                    self.print_error(f"Templates failed: {response.status_code}")
                
                # Start resume generation
                generation_request = {
                    "profile_id": self.profile_id,
                    "job_id": job_id,
                    "options": {
                        "template": "modern",
                        "length": "one_page",
                        "focus_areas": ["technical_skills", "experience"]
                    }
                }
                
                self.print_info("Starting resume generation...")
                response = await client.post(
                    f"{BASE_URL}/api/v1/generations/resume",
                    json=generation_request,
                    headers=headers
                )
                
                if response.status_code == 201:
                    generation = response.json()
                    generation_id = generation["id"]
                    self.print_success("Resume generation started")
                    self.print_info(f"Generation ID: {generation_id}")
                    
                    # Check status
                    for i in range(10):  # Wait up to 10 seconds
                        await asyncio.sleep(1)
                        response = await client.get(
                            f"{BASE_URL}/api/v1/generations/{generation_id}",
                            headers=headers
                        )
                        
                        if response.status_code == 200:
                            status = response.json()
                            current_status = status.get("status", "unknown")
                            stage = status.get("progress", {}).get("current_stage", 0)
                            stage_name = status.get("progress", {}).get("stage_name", "unknown")
                            
                            self.print_info(f"Status: {current_status}, Stage: {stage}/2 ({stage_name})")
                            
                            if current_status == "completed":
                                # Try to get result
                                response = await client.get(
                                    f"{BASE_URL}/api/v1/generations/{generation_id}/result",
                                    headers=headers
                                )
                                if response.status_code == 200:
                                    result = response.json()
                                    self.print_success("Generation completed successfully!")
                                    self.print_info(f"Resume length: {len(result.get('content', ''))} characters")
                                    if result.get('content'):
                                        # Show first 200 characters
                                        preview = result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
                                        print(f"\n{Colors.OKCYAN}Preview:{Colors.ENDC}")
                                        print(preview)
                                    return True
                                break
                            elif current_status == "failed":
                                self.print_error("Generation failed")
                                error_msg = status.get("error", {}).get("message", "Unknown error")
                                self.print_info(f"Error: {error_msg}")
                                return False
                    else:
                        self.print_error("Generation timeout")
                        return False
                
                else:
                    self.print_error(f"Generation start failed: {response.status_code}")
                    self.print_info(f"Response: {response.text}")
                    return False
                    
        except Exception as e:
            self.print_error(f"Generation API error: {e}")
            return False
        
        return False  # Default return for other paths

    async def show_summary(self):
        """Show test summary."""
        self.print_header("TEST SUMMARY")
        
        if self.auth_token:
            self.print_success("Authentication: Working")
        else:
            self.print_error("Authentication: Failed")
            
        if self.profile_id:
            self.print_success("Profile API: Working")
        else:
            self.print_error("Profile API: Failed")
            
        if self.jobs:
            self.print_success(f"Jobs API: Working ({len(self.jobs)} jobs)")
        else:
            self.print_error("Jobs API: Failed")
        
        print(f"\n{Colors.BOLD}🎯 CLI Testing Complete{Colors.ENDC}")
        print(f"Server: {BASE_URL}")
        if self.user_id:
            print(f"User ID: {self.user_id}")
        if self.profile_id:
            print(f"Profile ID: {self.profile_id}")

    async def run_full_test(self):
        """Run complete test suite."""
        print(f"{Colors.BOLD}🔍 JobWise Backend CLI Test Suite{Colors.ENDC}")
        print(f"Testing server at: {BASE_URL}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Check server
        if not await self.check_server():
            return False
            
        # Authentication
        if not await self.login_or_register():
            return False
            
        # Profile API
        if not await self.test_profile_api():
            return False
            
        # Jobs API
        if not await self.test_jobs_api():
            return False
            
        # Generation API
        await self.test_generation_api()
        
        # Summary
        await self.show_summary()
        
        return True


async def main():
    """Main CLI function."""
    cli = JobWiseCLI()
    
    try:
        success = await cli.run_full_test()
        return 0 if success else 1
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}⚠️ Test interrupted by user{Colors.ENDC}")
        return 1
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ Unexpected error: {e}{Colors.ENDC}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
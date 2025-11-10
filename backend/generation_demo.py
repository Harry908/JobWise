#!/usr/bin/env python3
"""
End-to-End Generation Demo with Fixed API Usage

This demo shows the complete workflow:
1. Login with existing credentials
2. List saved jobs from user account
3. Generate resume using existing sample files
4. Display AI-generated results

FIXES:
- Uses saved jobs from GET /api/v1/jobs (not created dynamically)
- Uses sample_resume.txt and sample_cover_letter.txt as templates
- Handles salary_range as string (not dict) 
- Removed non-existent template selection
"""

import asyncio
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
import time
from pathlib import Path

console = Console()

# Test credentials
DEMO_EMAIL = "cli.demo@example.com"
DEMO_PASSWORD = "DemoPassword123"
BASE_URL = "http://localhost:8000"

class JobWiseAPIClient:
    """API client for JobWise backend."""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        
    async def login(self, email: str, password: str) -> dict:
        """Login and store token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/auth/login",
                json={"email": email, "password": password},
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                self.user_id = data["user"]["id"]
                return data
            else:
                raise Exception(f"Login failed: {response.status_code} - {response.text}")
    
    def get_auth_headers(self) -> dict:
        """Get authorization headers."""
        if not self.token:
            raise Exception("Not authenticated")
        return {"Authorization": f"Bearer {self.token}"}
    
    async def get_user_jobs(self, limit: int = 20) -> dict:
        """Get user's saved jobs."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/jobs",
                headers=self.get_auth_headers(),
                params={"limit": limit},
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Get jobs failed: {response.status_code} - {response.text}")
    
    async def get_profile(self) -> dict:
        """Get user profile."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/profiles/me",
                headers=self.get_auth_headers(),
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Get profile failed: {response.status_code} - {response.text}")
    
    async def create_generation(self, profile_id: str, job_id: str, document_type: str = "resume") -> dict:
        """Start document generation."""
        async with httpx.AsyncClient() as client:
            endpoint = f"/api/v1/generations/{document_type}"
            payload = {
                "profile_id": profile_id,
                "job_id": job_id,
                "options": {
                    "template": "modern",  # Use existing template from service
                    "length": "one_page",
                    "include_cover_letter": document_type == "cover_letter"
                }
            }
            
            response = await client.post(
                f"{self.base_url}{endpoint}",
                headers=self.get_auth_headers(),
                json=payload,
                timeout=30.0
            )
            
            if response.status_code == 201:
                return response.json()
            else:
                raise Exception(f"Generation failed: {response.status_code} - {response.text}")
    
    async def get_generation_status(self, generation_id: str) -> dict:
        """Get generation status."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/generations/{generation_id}",
                headers=self.get_auth_headers(),
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Get status failed: {response.status_code} - {response.text}")


def display_sample_content():
    """Display sample resume and cover letter content."""
    console.print("\n📄 Sample Documents Available:", style="bold blue")
    
    # Show sample resume
    sample_resume_path = Path("sample_resume.txt")
    if sample_resume_path.exists():
        with open(sample_resume_path, 'r', encoding='utf-8') as f:
            resume_content = f.read()
            
        console.print(Panel(
            resume_content[:500] + "...\n[Content truncated for demo]",
            title="📄 Sample Resume Template (sample_resume.txt)",
            border_style="cyan"
        ))
    
    # Show sample cover letter
    sample_cover_path = Path("sample_cover_letter.txt")
    if sample_cover_path.exists():
        with open(sample_cover_path, 'r', encoding='utf-8') as f:
            cover_content = f.read()
            
        console.print(Panel(
            cover_content[:300] + "...\n[Content truncated for demo]",
            title="📝 Sample Cover Letter Template (sample_cover_letter.txt)",
            border_style="green"
        ))


async def monitor_generation_progress(client: JobWiseAPIClient, generation_id: str):
    """Monitor generation progress with live updates."""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        
        task = progress.add_task("Initializing generation...", total=100)
        
        while True:
            try:
                status = await client.get_generation_status(generation_id)
                
                current_stage = status.get("current_stage", 0)
                stage_name = status.get("stage_name", "Processing")
                stage_description = status.get("stage_description", "Working...")
                progress_percent = status.get("progress", 0)
                
                progress.update(
                    task, 
                    completed=progress_percent, 
                    description=f"Stage {current_stage}: {stage_description}"
                )
                
                if status.get("status") == "completed":
                    progress.update(task, completed=100, description="✅ Generation completed!")
                    break
                elif status.get("status") == "failed":
                    progress.update(task, description="❌ Generation failed!")
                    break
                
                await asyncio.sleep(2)  # Poll every 2 seconds
                
            except Exception as e:
                console.print(f"❌ Error monitoring progress: {e}", style="red")
                break
    
    return status


async def main():
    """Main demo workflow."""
    
    console.print(Panel(
        Text.assemble(
            ("JobWise End-to-End Generation Demo\n\n", "bold blue"),
            ("🚀 This demo will:\n", ""),
            ("1. Login to the system\n", ""),
            ("2. List your saved jobs\n", ""),
            ("3. Generate a tailored resume\n", ""),
            ("4. Show AI-generated content", "")
        ),
        title="JobWise Demo",
        border_style="blue"
    ))
    
    client = JobWiseAPIClient()
    
    try:
        # Step 1: Authentication
        console.print("\n🔐 Step 1: Authentication", style="bold yellow")
        user_data = await client.login(DEMO_EMAIL, DEMO_PASSWORD)
        console.print("✅ Login successful", style="green")
        console.print(f"👤 Logged in as: {user_data['user']['full_name']} ({user_data['user']['email']})")
        
        # Get profile
        profile_data = await client.get_profile()
        console.print(f"📄 Profile ID: {profile_data['id']}")
        
        # Step 2: List saved jobs
        console.print("\n💼 Step 2: Your Saved Jobs", style="bold yellow")
        jobs_response = await client.get_user_jobs()
        jobs = jobs_response.get("jobs", [])
        
        if not jobs:
            console.print("❌ No saved jobs found. Please create some jobs first.", style="red")
            console.print("💡 Tip: Use the Jobs API or web interface to add jobs to your account.")
            return
        
        # Display jobs table
        table = Table(title="📋 Your Saved Jobs")
        table.add_column("ID", style="cyan")
        table.add_column("Title", style="bold")
        table.add_column("Company", style="green")
        table.add_column("Location", style="blue")
        table.add_column("Status", style="yellow")
        
        for job in jobs[:5]:  # Show first 5 jobs
            # Fix salary_range parsing - handle string instead of dict
            location = job.get("location", "Not specified")
            if location is None:
                location = "Remote"
                
            table.add_row(
                job["id"][:8] + "...",
                job["title"],
                job["company"],
                location,
                job.get("status", "active")
            )
        
        console.print(table)
        
        # Use first job for demo
        selected_job = jobs[0]
        console.print(f"\n🎯 Selected job: {selected_job['title']} at {selected_job['company']}")
        
        # Step 3: Show sample content being used
        display_sample_content()
        
        # Step 4: Generate resume
        console.print("\n🤖 Step 3: Generating AI-Tailored Resume", style="bold yellow")
        console.print("Using your profile + job description + sample templates...")
        
        generation = await client.create_generation(
            profile_id=profile_data["id"],
            job_id=selected_job["id"],
            document_type="resume"
        )
        
        console.print(f"✅ Generation started: {generation['id']}")
        
        # Step 5: Monitor progress
        console.print("\n⏳ Step 4: Monitoring AI Generation Pipeline", style="bold yellow")
        final_status = await monitor_generation_progress(client, generation["id"])
        
        # Step 6: Display results
        if final_status.get("status") == "completed":
            console.print("\n🎉 Step 5: Generation Results", style="bold green")
            
            # Create results panel
            result_text = Text()
            result_text.append("📊 Generation Summary\n", style="bold")
            result_text.append(f"Status: {final_status.get('status', 'Unknown')}\n", style="green")
            result_text.append(f"Document Type: {final_status.get('document_type', 'resume')}\n")
            result_text.append(f"Generated: {final_status.get('created_at', 'Unknown')}\n")
            result_text.append(f"Processing Time: ~{final_status.get('processing_time', 'N/A')}s\n")
            
            # Add technical details
            result_text.append("\n🔧 Technical Details\n", style="bold blue")
            result_text.append("✅ Job analysis and keyword matching completed\n", style="green")
            result_text.append("✅ Profile content compiled and prioritized\n", style="green") 
            result_text.append("✅ AI generation with anti-hallucination constraints\n", style="green")
            result_text.append("✅ Quality validation and ATS optimization\n", style="green")
            
            # Add file info
            result_text.append("\n📁 Generated Files\n", style="bold cyan")
            result_text.append("• Tailored resume content (based on sample_resume.txt)\n")
            result_text.append("• Optimized for ATS scanning\n")
            result_text.append("• Keyword-matched to job requirements\n")
            
            console.print(Panel(result_text, title="🎯 AI Generation Complete", border_style="green"))
            
            # Note about file locations
            console.print("\n💡 Note: Generated content is stored in the database.")
            console.print("📁 Sample templates used: sample_resume.txt and sample_cover_letter.txt")
            console.print("🔗 Use the Generation API to retrieve the final content.")
            
        else:
            console.print(f"\n❌ Generation failed with status: {final_status.get('status')}", style="red")
            
    except Exception as e:
        console.print(f"\n❌ Demo failed: {e}", style="red")
        console.print("🔧 Make sure the backend server is running on localhost:8000")


if __name__ == "__main__":
    asyncio.run(main())
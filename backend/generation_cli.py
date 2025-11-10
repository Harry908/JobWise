#!/usr/bin/env python3
"""
JobWise Generation CLI - Interactive document generation tool

Complete workflow: Login → Browse Jobs → Select Job → Generate Documents → View Results

Usage: python generation_cli.py
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import httpx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich.syntax import Syntax

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 30.0

# Rich console for beautiful output
console = Console()

class JobWiseGenerationClient:
    """JobWise API client for document generation workflow."""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.session = httpx.AsyncClient(timeout=TIMEOUT)
        self.access_token: Optional[str] = None
        self.user_info: Optional[Dict] = None
        self.profile_info: Optional[Dict] = None
    
    async def close(self):
        """Close HTTP session."""
        await self.session.aclose()
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers."""
        if not self.access_token:
            raise ValueError("Not authenticated - please login first")
        return {"Authorization": f"Bearer {self.access_token}"}
    
    async def login(self, email: str, password: str) -> bool:
        """Login and store authentication tokens."""
        try:
            response = await self.session.post(
                f"{self.base_url}/auth/login",
                json={"email": email, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                return True
            elif response.status_code == 401:
                console.print("❌ [red]Invalid credentials[/red]")
                return False
            else:
                console.print(f"❌ [red]Login failed: {response.status_code}[/red]")
                return False
                
        except Exception as e:
            console.print(f"❌ [red]Connection error: {e}[/red]")
            return False
    
    async def get_user_info(self) -> Optional[Dict]:
        """Get current user information."""
        try:
            response = await self.session.get(
                f"{self.base_url}/auth/me",
                headers=self._get_auth_headers()
            )
            
            if response.status_code == 200:
                self.user_info = response.json()
                return self.user_info
            else:
                console.print(f"❌ [red]Failed to get user info: {response.status_code}[/red]")
                return None
                
        except Exception as e:
            console.print(f"❌ [red]Error getting user info: {e}[/red]")
            return None
    
    async def get_profile(self) -> Optional[Dict]:
        """Get user profile or create if doesn't exist."""
        try:
            # Try to get existing profile
            response = await self.session.get(
                f"{self.base_url}/profiles/me",
                headers=self._get_auth_headers()
            )
            
            if response.status_code == 200:
                self.profile_info = response.json()
                return self.profile_info
            elif response.status_code == 404:
                # No profile found, create a basic one
                console.print("📝 [yellow]No profile found. Creating basic profile...[/yellow]")
                return await self.create_basic_profile()
            else:
                console.print(f"❌ [red]Failed to get profile: {response.status_code}[/red]")
                return None
                
        except Exception as e:
            console.print(f"❌ [red]Error getting profile: {e}[/red]")
            return None
    
    async def create_basic_profile(self) -> Optional[Dict]:
        """Create a basic profile for testing."""
        profile_data = {
            "personal_info": {
                "full_name": "Demo User",
                "email": self.user_info.get("email", "demo@example.com"),
                "phone": "(555) 123-4567",
                "location": "Remote, US"
            },
            "experiences": [
                {
                    "id": "exp_demo_1",
                    "title": "Software Engineer",
                    "company": "Tech Company",
                    "location": "Remote",
                    "start_date": "2022-01-01",
                    "end_date": None,
                    "is_current": True,
                    "description": "Full-stack development with modern technologies.",
                    "achievements": [
                        "Built scalable web applications with React and Node.js",
                        "Implemented AI/ML features for document generation",
                        "Led technical initiatives and mentored junior developers"
                    ]
                }
            ],
            "education": [
                {
                    "id": "edu_demo_1",
                    "institution": "University",
                    "degree": "Bachelor of Science",
                    "field_of_study": "Computer Science",
                    "start_date": "2018-09-01",
                    "end_date": "2022-06-15",
                    "gpa": 3.7
                }
            ],
            "projects": [
                {
                    "id": "proj_demo_1",
                    "name": "JobWise AI Assistant",
                    "description": "AI-powered job application assistant with intelligent document generation.",
                    "technologies": ["Python", "FastAPI", "React", "AI/ML"],
                    "url": "https://github.com/example/jobwise",
                    "start_date": "2024-01-01",
                    "end_date": "2024-12-31"
                }
            ],
            "skills": {
                "technical_skills": [
                    {"name": "Python", "category": "Programming Languages", "years_of_experience": 4},
                    {"name": "JavaScript", "category": "Programming Languages", "years_of_experience": 3},
                    {"name": "React", "category": "Frontend Frameworks", "years_of_experience": 2},
                    {"name": "FastAPI", "category": "Backend Frameworks", "years_of_experience": 2},
                    {"name": "Machine Learning", "category": "AI/ML", "years_of_experience": 1}
                ],
                "soft_skills": [],
                "certifications": [],
                "languages": [
                    {"name": "English", "proficiency": "native"},
                    {"name": "Spanish", "proficiency": "conversational"}
                ]
            }
        }
        
        try:
            response = await self.session.post(
                f"{self.base_url}/profiles",
                json=profile_data,
                headers=self._get_auth_headers()
            )
            
            if response.status_code == 201:
                self.profile_info = response.json()
                console.print("✅ [green]Basic profile created successfully[/green]")
                return self.profile_info
            else:
                console.print(f"❌ [red]Failed to create profile: {response.status_code}[/red]")
                console.print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            console.print(f"❌ [red]Error creating profile: {e}[/red]")
            return None
    
    async def browse_jobs(self, limit: int = 10) -> List[Dict]:
        """Browse available jobs."""
        try:
            response = await self.session.get(
                f"{self.base_url}/jobs/browse",
                params={"limit": limit}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("jobs", [])
            else:
                console.print(f"❌ [red]Failed to browse jobs: {response.status_code}[/red]")
                return []
                
        except Exception as e:
            console.print(f"❌ [red]Error browsing jobs: {e}[/red]")
            return []
    
    async def get_job_details(self, job_id: str) -> Optional[Dict]:
        """Get detailed job information."""
        try:
            response = await self.session.get(
                f"{self.base_url}/jobs/{job_id}",
                headers=self._get_auth_headers()
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                console.print(f"❌ [red]Failed to get job details: {response.status_code}[/red]")
                return None
                
        except Exception as e:
            console.print(f"❌ [red]Error getting job details: {e}[/red]")
            return None
    
    async def get_generation_templates(self) -> List[Dict]:
        """Get available generation templates."""
        try:
            response = await self.session.get(
                f"{self.base_url}/generations/templates",
                headers=self._get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("templates", [])
            else:
                console.print(f"❌ [red]Failed to get templates: {response.status_code}[/red]")
                return []
                
        except Exception as e:
            console.print(f"❌ [red]Error getting templates: {e}[/red]")
            return []
    
    async def start_resume_generation(
        self, 
        profile_id: str, 
        job_id: str, 
        template: str = "modern"
    ) -> Optional[str]:
        """Start resume generation and return generation ID."""
        try:
            generation_data = {
                "profile_id": profile_id,
                "job_id": job_id,
                "options": {
                    "template": template,
                    "format": "pdf",
                    "custom_sections": []
                }
            }
            
            response = await self.session.post(
                f"{self.base_url}/generations/resume",
                json=generation_data,
                headers=self._get_auth_headers()
            )
            
            if response.status_code == 201:
                data = response.json()
                return data.get("id")
            else:
                console.print(f"❌ [red]Failed to start generation: {response.status_code}[/red]")
                console.print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            console.print(f"❌ [red]Error starting generation: {e}[/red]")
            return None
    
    async def start_cover_letter_generation(
        self, 
        profile_id: str, 
        job_id: str, 
        template: str = "professional"
    ) -> Optional[str]:
        """Start cover letter generation and return generation ID."""
        try:
            generation_data = {
                "profile_id": profile_id,
                "job_id": job_id,
                "options": {
                    "template": template,
                    "tone": "professional",
                    "length": "medium"
                }
            }
            
            response = await self.session.post(
                f"{self.base_url}/generations/cover-letter",
                json=generation_data,
                headers=self._get_auth_headers()
            )
            
            if response.status_code == 201:
                data = response.json()
                return data.get("id")
            else:
                console.print(f"❌ [red]Failed to start generation: {response.status_code}[/red]")
                console.print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            console.print(f"❌ [red]Error starting generation: {e}[/red]")
            return None
    
    async def get_generation_status(self, generation_id: str) -> Optional[Dict]:
        """Get generation status and progress."""
        try:
            response = await self.session.get(
                f"{self.base_url}/generations/{generation_id}",
                headers=self._get_auth_headers()
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                console.print(f"❌ [red]Failed to get generation status: {response.status_code}[/red]")
                return None
                
        except Exception as e:
            console.print(f"❌ [red]Error getting generation status: {e}[/red]")
            return None
    
    async def get_generation_result(self, generation_id: str) -> Optional[Dict]:
        """Get completed generation result."""
        try:
            response = await self.session.get(
                f"{self.base_url}/generations/{generation_id}/result",
                headers=self._get_auth_headers()
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                console.print(f"❌ [red]Failed to get generation result: {response.status_code}[/red]")
                return None
                
        except Exception as e:
            console.print(f"❌ [red]Error getting generation result: {e}[/red]")
            return None


class JobWiseGenerationCLI:
    """Interactive CLI for JobWise document generation."""
    
    def __init__(self):
        self.client = JobWiseGenerationClient()
    
    async def run(self):
        """Main CLI loop."""
        try:
            # Welcome message
            self.show_welcome()
            
            # Authentication
            if not await self.handle_authentication():
                return
            
            # Main workflow loop
            while True:
                choice = self.show_main_menu()
                
                if choice == "1":
                    await self.workflow_generate_resume()
                elif choice == "2":
                    await self.workflow_generate_cover_letter()
                elif choice == "3":
                    await self.workflow_browse_jobs()
                elif choice == "4":
                    await self.workflow_view_profile()
                elif choice == "5":
                    await self.workflow_view_templates()
                elif choice == "q":
                    console.print("👋 [blue]Thank you for using JobWise![/blue]")
                    break
                else:
                    console.print("❌ [red]Invalid choice. Please try again.[/red]")
        
        finally:
            await self.client.close()
    
    def show_welcome(self):
        """Display welcome banner."""
        welcome_text = """
# JobWise Generation CLI

🚀 **AI-Powered Document Generation**

Generate professional resumes and cover letters tailored to specific job postings using advanced AI technology.
        """
        
        console.print(Panel(
            Markdown(welcome_text),
            title="Welcome to JobWise",
            border_style="blue"
        ))
    
    async def handle_authentication(self) -> bool:
        """Handle user authentication."""
        console.print("\n🔐 [bold blue]Authentication Required[/bold blue]")
        
        # Check for test credentials
        use_test = Confirm.ask("Use test credentials? (CLI Test User)")
        
        if use_test:
            email = "cli.demo@example.com"
            password = "DemoPassword123"
        else:
            email = Prompt.ask("Email")
            password = Prompt.ask("Password", password=True)
        
        with console.status("[bold blue]Logging in...", spinner="dots"):
            if await self.client.login(email, password):
                console.print("✅ [green]Login successful[/green]")
                
                # Get user info and profile
                await self.client.get_user_info()
                await self.client.get_profile()
                
                return True
            else:
                return False
    
    def show_main_menu(self) -> str:
        """Show main menu and return user choice."""
        console.print("\n" + "=" * 60)
        console.print("[bold blue]JobWise Generation Menu[/bold blue]")
        console.print("=" * 60)
        
        options = [
            "1. 📄 Generate Resume",
            "2. 📋 Generate Cover Letter", 
            "3. 🔍 Browse Available Jobs",
            "4. 👤 View Profile",
            "5. 🎨 View Templates",
            "q. 🚪 Quit"
        ]
        
        for option in options:
            console.print(f"  {option}")
        
        return Prompt.ask("\nChoose an option", choices=["1", "2", "3", "4", "5", "q"])
    
    async def workflow_generate_resume(self):
        """Complete resume generation workflow."""
        console.print("\n📄 [bold blue]Resume Generation Workflow[/bold blue]")
        
        # Step 1: Select job
        job = await self.select_job()
        if not job:
            return
        
        # Step 2: Select template
        template = await self.select_template("resume")
        if not template:
            template = "modern"
        
        # Step 3: Start generation
        console.print(f"\n🚀 [blue]Starting resume generation for: {job['title']}[/blue]")
        
        # Check if we have a profile before starting generation
        if not self.client.profile_info:
            console.print("❌ [red]Cannot generate resume: No profile available. Please create a profile first.[/red]")
            return
        
        generation_id = await self.client.start_resume_generation(
            profile_id=self.client.profile_info["id"],
            job_id=job["id"],
            template=template
        )
        
        if not generation_id:
            console.print("❌ [red]Failed to start generation[/red]")
            return
        
        # Step 4: Wait for completion and show results
        await self.monitor_generation_and_show_results(generation_id, "resume")
    
    async def workflow_generate_cover_letter(self):
        """Complete cover letter generation workflow."""
        console.print("\n📋 [bold blue]Cover Letter Generation Workflow[/bold blue]")
        
        # Step 1: Select job
        job = await self.select_job()
        if not job:
            return
        
        # Step 2: Select template
        template = await self.select_template("cover_letter")
        if not template:
            template = "professional"
        
        # Step 3: Start generation
        console.print(f"\n🚀 [blue]Starting cover letter generation for: {job['title']}[/blue]")
        
        # Check if we have a profile before starting generation
        if not self.client.profile_info:
            console.print("❌ [red]Cannot generate cover letter: No profile available. Please create a profile first.[/red]")
            return
        
        generation_id = await self.client.start_cover_letter_generation(
            profile_id=self.client.profile_info["id"],
            job_id=job["id"],
            template=template
        )
        
        if not generation_id:
            console.print("❌ [red]Failed to start generation[/red]")
            return
        
        # Step 4: Wait for completion and show results
        await self.monitor_generation_and_show_results(generation_id, "cover letter")
    
    async def select_job(self) -> Optional[Dict]:
        """Let user select a job from available options."""
        console.print("\n🔍 [blue]Loading available jobs...[/blue]")
        
        jobs = await self.client.browse_jobs(limit=10)
        if not jobs:
            console.print("❌ [red]No jobs available[/red]")
            return None
        
        # Display jobs table
        table = Table(title="Available Jobs")
        table.add_column("ID", style="cyan")
        table.add_column("Title", style="magenta")
        table.add_column("Company", style="green")
        table.add_column("Location", style="yellow")
        table.add_column("Type", style="blue")
        
        for job in jobs:
            table.add_row(
                str(jobs.index(job) + 1),
                job.get("title", "N/A")[:40],
                job.get("company", "N/A")[:30],
                job.get("location", "N/A")[:20],
                job.get("employment_type", "N/A")
            )
        
        console.print(table)
        
        # User selection
        try:
            choice = int(Prompt.ask("Select job by number")) - 1
            if 0 <= choice < len(jobs):
                selected_job = jobs[choice]
                
                # Show job details
                console.print(f"\n📋 [blue]Selected Job Details[/blue]")
                console.print(f"[bold]Title:[/bold] {selected_job.get('title', 'N/A')}")
                console.print(f"[bold]Company:[/bold] {selected_job.get('company', 'N/A')}")
                console.print(f"[bold]Location:[/bold] {selected_job.get('location', 'N/A')}")
                
                description = selected_job.get("description", "")
                if description:
                    console.print(f"[bold]Description:[/bold] {description[:200]}...")
                
                return selected_job
            else:
                console.print("❌ [red]Invalid selection[/red]")
                return None
                
        except ValueError:
            console.print("❌ [red]Invalid input[/red]")
            return None
    
    async def select_template(self, doc_type: str) -> Optional[str]:
        """Let user select a template."""
        console.print(f"\n🎨 [blue]Loading {doc_type} templates...[/blue]")
        
        templates = await self.client.get_generation_templates()
        if not templates:
            console.print("⚠️ [yellow]No templates available, using default[/yellow]")
            return None
        
        # Filter templates by document type if needed
        relevant_templates = [t for t in templates if doc_type.lower() in t.get("name", "").lower() or "all" in t.get("name", "").lower()]
        if not relevant_templates:
            relevant_templates = templates
        
        # Display templates
        table = Table(title=f"Available {doc_type.title()} Templates")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Description", style="green")
        table.add_column("ATS Friendly", style="yellow")
        
        for template in relevant_templates:
            table.add_row(
                str(relevant_templates.index(template) + 1),
                template.get("name", "N/A"),
                template.get("description", "N/A")[:50],
                "✅" if template.get("ats_friendly", False) else "❌"
            )
        
        console.print(table)
        
        # User selection
        try:
            choice = int(Prompt.ask("Select template by number")) - 1
            if 0 <= choice < len(relevant_templates):
                return relevant_templates[choice].get("name", "modern").lower()
            else:
                console.print("❌ [red]Invalid selection, using default[/red]")
                return None
                
        except ValueError:
            console.print("❌ [red]Invalid input, using default[/red]")
            return None
    
    async def monitor_generation_and_show_results(self, generation_id: str, doc_type: str):
        """Monitor generation progress and show final results."""
        console.print(f"\n⏳ [blue]Monitoring {doc_type} generation...[/blue]")
        console.print(f"Generation ID: {generation_id}")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Generating document...", total=None)
            
            max_attempts = 60  # 1 minute timeout
            attempt = 0
            
            while attempt < max_attempts:
                status = await self.client.get_generation_status(generation_id)
                
                if not status:
                    console.print("❌ [red]Failed to get generation status[/red]")
                    return
                
                current_status = status.get("status", "unknown")
                progress_info = status.get("progress", {})
                current_stage = progress_info.get("current_stage", 0)
                total_stages = progress_info.get("total_stages", 2)
                percentage = progress_info.get("percentage", 0)
                
                # Update progress description
                stage_name = progress_info.get("stage_name", f"Stage {current_stage}")
                progress.update(
                    task, 
                    description=f"{stage_name} ({percentage:.1f}%)"
                )
                
                if current_status == "completed":
                    progress.update(task, description="✅ Generation completed!", completed=True)
                    break
                elif current_status == "failed":
                    progress.update(task, description="❌ Generation failed!", completed=True)
                    console.print("❌ [red]Generation failed[/red]")
                    return
                
                await asyncio.sleep(2)
                attempt += 1
            else:
                console.print("⏰ [yellow]Generation timed out[/yellow]")
                return
        
        # Get and display results
        console.print(f"\n🎉 [green]Getting {doc_type} results...[/green]")
        
        result = await self.client.get_generation_result(generation_id)
        if result:
            await self.display_generation_result(result, doc_type)
        else:
            console.print("❌ [red]Failed to get generation result[/red]")
    
    async def display_generation_result(self, result: Dict, doc_type: str):
        """Display the generated document result."""
        console.print(f"\n📋 [bold green]{doc_type.title()} Generation Result[/bold green]")
        console.print("=" * 60)
        
        # Generation metadata
        console.print(f"[bold]Generation ID:[/bold] {result.get('id', 'N/A')}")
        console.print(f"[bold]Status:[/bold] {result.get('status', 'N/A')}")
        console.print(f"[bold]Created:[/bold] {result.get('created_at', 'N/A')}")
        console.print(f"[bold]Completed:[/bold] {result.get('completed_at', 'N/A')}")
        
        # Get the actual document content
        document_result = result.get("result", {})
        
        if doc_type == "resume":
            await self.display_resume_content(document_result)
        elif doc_type == "cover letter":
            await self.display_cover_letter_content(document_result)
        
        # Quality metrics if available
        quality_metrics = document_result.get("quality_metrics", {})
        if quality_metrics:
            self.display_quality_metrics(quality_metrics)
        
        # Save option
        if Confirm.ask(f"\nSave {doc_type} to file?"):
            await self.save_document_to_file(document_result, doc_type, result.get("id", "unknown"))
    
    async def display_resume_content(self, result: Dict):
        """Display resume content in a structured format."""
        resume_content = result.get("resume_content", "")
        
        if resume_content:
            console.print("\n📄 [bold blue]Generated Resume Content[/bold blue]")
            console.print("-" * 60)
            
            # Try to display as formatted text
            resume_panel = Panel(
                resume_content,
                title="Resume Content",
                border_style="green"
            )
            console.print(resume_panel)
        else:
            console.print("❌ [red]No resume content available[/red]")
    
    async def display_cover_letter_content(self, result: Dict):
        """Display cover letter content."""
        cover_letter_content = result.get("cover_letter_content", "")
        
        if cover_letter_content:
            console.print("\n📋 [bold blue]Generated Cover Letter Content[/bold blue]")
            console.print("-" * 60)
            
            # Display as formatted text
            cover_letter_panel = Panel(
                cover_letter_content,
                title="Cover Letter Content",
                border_style="green"
            )
            console.print(cover_letter_panel)
        else:
            console.print("❌ [red]No cover letter content available[/red]")
    
    def display_quality_metrics(self, metrics: Dict):
        """Display quality metrics."""
        console.print("\n📊 [bold blue]Quality Metrics[/bold blue]")
        
        metrics_table = Table(title="Generation Quality")
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Value", style="green")
        metrics_table.add_column("Status", style="yellow")
        
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                if key.endswith("_score") or key.endswith("_percentage"):
                    # Score/percentage metrics
                    status = "✅ Good" if value >= 0.8 else "⚠️ Fair" if value >= 0.6 else "❌ Poor"
                    metrics_table.add_row(key.replace("_", " ").title(), f"{value:.2f}", status)
                else:
                    metrics_table.add_row(key.replace("_", " ").title(), str(value), "")
            else:
                metrics_table.add_row(key.replace("_", " ").title(), str(value), "")
        
        console.print(metrics_table)
    
    async def save_document_to_file(self, result: Dict, doc_type: str, generation_id: str):
        """Save document content to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if doc_type == "resume":
            content = result.get("resume_content", "")
            filename = f"resume_{generation_id}_{timestamp}.txt"
        else:
            content = result.get("cover_letter_content", "")
            filename = f"cover_letter_{generation_id}_{timestamp}.txt"
        
        if content:
            try:
                output_dir = Path("generated_documents")
                output_dir.mkdir(exist_ok=True)
                
                file_path = output_dir / filename
                file_path.write_text(content, encoding="utf-8")
                
                console.print(f"✅ [green]{doc_type.title()} saved to: {file_path}[/green]")
            except Exception as e:
                console.print(f"❌ [red]Error saving file: {e}[/red]")
        else:
            console.print("❌ [red]No content to save[/red]")
    
    async def workflow_browse_jobs(self):
        """Browse and view job details."""
        console.print("\n🔍 [bold blue]Job Browser[/bold blue]")
        
        jobs = await self.client.browse_jobs(limit=20)
        if not jobs:
            console.print("❌ [red]No jobs available[/red]")
            return
        
        # Display jobs
        table = Table(title="Available Jobs")
        table.add_column("ID", style="cyan")
        table.add_column("Title", style="magenta")
        table.add_column("Company", style="green")
        table.add_column("Location", style="yellow")
        table.add_column("Salary", style="blue")
        
        for i, job in enumerate(jobs):
            salary_range = job.get("salary_range", {})
            salary_text = ""
            if salary_range:
                min_sal = salary_range.get("min")
                max_sal = salary_range.get("max")
                currency = salary_range.get("currency", "USD")
                if min_sal and max_sal:
                    salary_text = f"{min_sal}-{max_sal} {currency}"
            
            table.add_row(
                str(i + 1),
                job.get("title", "N/A")[:30],
                job.get("company", "N/A")[:25],
                job.get("location", "N/A")[:20],
                salary_text[:15]
            )
        
        console.print(table)
        
        # Option to view details
        if Confirm.ask("View details for a specific job?"):
            try:
                choice = int(Prompt.ask("Enter job number")) - 1
                if 0 <= choice < len(jobs):
                    job = jobs[choice]
                    await self.display_job_details(job)
            except ValueError:
                console.print("❌ [red]Invalid input[/red]")
    
    async def display_job_details(self, job: Dict):
        """Display detailed job information."""
        console.print(f"\n📋 [bold blue]Job Details[/bold blue]")
        
        # Basic info
        info_table = Table(title=job.get("title", "Job Details"))
        info_table.add_column("Field", style="cyan")
        info_table.add_column("Value", style="green")
        
        fields = [
            ("Company", job.get("company", "N/A")),
            ("Location", job.get("location", "N/A")),
            ("Employment Type", job.get("employment_type", "N/A")),
            ("Experience Level", job.get("experience_level", "N/A")),
            ("Department", job.get("department", "N/A")),
            ("Source", job.get("source", "N/A")),
            ("Posted Date", job.get("posted_date", "N/A"))
        ]
        
        for field, value in fields:
            info_table.add_row(field, str(value))
        
        console.print(info_table)
        
        # Salary information
        salary_range = job.get("salary_range", {})
        if salary_range:
            console.print(f"\n💰 [bold blue]Salary Information[/bold blue]")
            min_sal = salary_range.get("min")
            max_sal = salary_range.get("max")
            currency = salary_range.get("currency", "USD")
            period = salary_range.get("period", "year")
            
            if min_sal and max_sal:
                console.print(f"Range: {min_sal:,} - {max_sal:,} {currency} per {period}")
            elif min_sal:
                console.print(f"Minimum: {min_sal:,} {currency} per {period}")
        
        # Description
        description = job.get("description", "")
        if description:
            console.print(f"\n📄 [bold blue]Job Description[/bold blue]")
            desc_panel = Panel(
                description[:500] + ("..." if len(description) > 500 else ""),
                title="Description",
                border_style="blue"
            )
            console.print(desc_panel)
        
        # Requirements
        requirements = job.get("requirements", [])
        if requirements:
            console.print(f"\n✅ [bold blue]Requirements[/bold blue]")
            for i, req in enumerate(requirements[:10], 1):  # Show first 10
                console.print(f"  {i}. {req}")
    
    async def workflow_view_profile(self):
        """View current user profile."""
        if not self.client.profile_info:
            console.print("❌ [red]No profile information available[/red]")
            return
        
        profile = self.client.profile_info
        
        console.print("\n👤 [bold blue]User Profile[/bold blue]")
        console.print("=" * 60)
        
        # Personal info
        personal_info = profile.get("personal_info", {})
        if personal_info:
            console.print("\n[bold blue]Personal Information[/bold blue]")
            for key, value in personal_info.items():
                if value:
                    console.print(f"[bold]{key.replace('_', ' ').title()}:[/bold] {value}")
        
        # Experiences
        experiences = profile.get("experiences", [])
        if experiences:
            console.print(f"\n[bold blue]Work Experience ({len(experiences)} entries)[/bold blue]")
            for exp in experiences[:3]:  # Show first 3
                console.print(f"• {exp.get('title', 'N/A')} at {exp.get('company', 'N/A')}")
                if exp.get('is_current'):
                    console.print(f"  {exp.get('start_date', 'N/A')} - Present")
                else:
                    console.print(f"  {exp.get('start_date', 'N/A')} - {exp.get('end_date', 'N/A')}")
        
        # Skills
        skills = profile.get("skills", [])
        if skills:
            console.print(f"\n[bold blue]Skills ({len(skills)} total)[/bold blue]")
            skill_categories = {}
            for skill in skills:
                category = skill.get("category", "Other")
                if category not in skill_categories:
                    skill_categories[category] = []
                skill_categories[category].append(skill.get("name", "N/A"))
            
            for category, skill_list in skill_categories.items():
                console.print(f"[bold]{category}:[/bold] {', '.join(skill_list[:5])}")
                if len(skill_list) > 5:
                    console.print(f"  ... and {len(skill_list) - 5} more")
    
    async def workflow_view_templates(self):
        """View available generation templates."""
        console.print("\n🎨 [bold blue]Generation Templates[/bold blue]")
        
        templates = await self.client.get_generation_templates()
        if not templates:
            console.print("❌ [red]No templates available[/red]")
            return
        
        for template in templates:
            console.print(f"\n[bold]{template.get('name', 'N/A')}[/bold]")
            console.print(f"Description: {template.get('description', 'N/A')}")
            console.print(f"ATS Friendly: {'✅ Yes' if template.get('ats_friendly', False) else '❌ No'}")
            
            recommended_for = template.get("recommended_for", [])
            if recommended_for:
                console.print(f"Recommended for: {', '.join(recommended_for)}")
            
            console.print("-" * 40)


async def main():
    """Main entry point."""
    try:
        cli = JobWiseGenerationCLI()
        await cli.run()
    except KeyboardInterrupt:
        console.print("\n👋 [blue]Goodbye![/blue]")
    except Exception as e:
        console.print(f"\n❌ [red]Unexpected error: {e}[/red]")
        console.print("[yellow]Please check that the JobWise backend is running on http://localhost:8000[/yellow]")


if __name__ == "__main__":
    # Install required packages if missing
    required_packages = ["httpx", "rich"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Installing required packages: {' '.join(missing_packages)}")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
        print("Packages installed successfully!")
    
    asyncio.run(main())
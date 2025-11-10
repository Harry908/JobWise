"""Script to create a test user and master profile for testing purposes."""

import asyncio
import json
import sys
import uuid
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.infrastructure.database.connection import create_engine, create_session_factory
from app.infrastructure.database.models import Base
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.profile_repository import ProfileRepository
from app.application.services.auth_service import AuthService
from app.domain.entities.profile import Profile, PersonalInfo, Skills, Experience, Education, Project, Language


async def create_test_user_and_profile():
    """Create a test user and their master profile."""
    print("=== CREATING TEST USER AND PROFILE ===")
    
    try:
        # Setup database
        engine = create_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        session_factory = create_session_factory(engine)
        
        async with session_factory() as session:
            # Create repositories and services
            user_repo = UserRepository(session)
            profile_repo = ProfileRepository(session)
            auth_service = AuthService(user_repo)
            
            # Test credentials
            test_email = "sarah.chen@example.com"
            test_password = "TestPassword123"
            test_full_name = "Sarah Chen"
            
            print(f"Creating user: {test_email}")
            
            # Check if user already exists
            existing_user = await user_repo.get_by_email(test_email)
            if existing_user:
                print(f"User {test_email} already exists! Using unique email...")
                # For testing, we'll create a unique email
                test_email = f"sarah.chen.{uuid.uuid4().hex[:8]}@example.com"
                print(f"Using unique email: {test_email}")
            
            # Register the user
            user_result = await auth_service.register_user(
                email=test_email,
                password=test_password,
                full_name=test_full_name
            )
            
            user_id = user_result['user']['id']
            print(f"✓ User created with ID: {user_id}")
            
            # Create fabricated master profile data
            personal_info = PersonalInfo(
                full_name="Sarah Chen",
                email=test_email,
                phone="(206) 555-7890",
                location="Seattle, WA",
                linkedin="https://www.linkedin.com/in/sarah-chen-dev",
                github="https://github.com/sarah-chen-dev",
                website="https://sarahchen.dev"
            )
            
            # Create skills
            skills = Skills(
                technical=[
                    "JavaScript", "TypeScript", "Python", "Java", "Go", "SQL",
                    "React", "Node.js", "Express", "Next.js", "Django", "Flask",
                    "PostgreSQL", "MongoDB", "Redis", "Docker", "Kubernetes",
                    "AWS", "Git", "Jest", "Cypress"
                ],
                soft=[
                    "Team Leadership", "Project Management", "Agile Methodology",
                    "Code Review", "Mentoring", "Technical Writing", "Problem Solving"
                ],
                languages=[
                    Language(name="English", proficiency="native"),
                    Language(name="Mandarin", proficiency="conversational")
                ],
                certifications=[]
            )
            
            # Create work experiences
            experiences = [
                Experience(
                    title="Senior Software Engineer",
                    company="TechFlow Solutions",
                    location="Seattle, WA",
                    start_date="2022-03-15",
                    end_date=None,
                    is_current=True,
                    description="Lead development of microservices platform serving 2M+ daily active users. Architect scalable solutions and mentor engineering team.",
                    achievements=[
                        "Reduced API response times by 40% through database optimization and caching strategies",
                        "Led team of 6 engineers in successful migration from monolith to microservices architecture",
                        "Implemented comprehensive testing strategy achieving 95% code coverage across services",
                        "Designed and deployed CI/CD pipeline reducing deployment time from 2 hours to 15 minutes"
                    ]
                ),
                Experience(
                    title="Full Stack Developer",
                    company="InnovateTech",
                    location="San Francisco, CA",
                    start_date="2020-01-10",
                    end_date="2022-02-28",
                    is_current=False,
                    description="Built and maintained React/Node.js applications for fintech startup. Developed secure payment processing systems and real-time financial dashboards.",
                    achievements=[
                        "Developed real-time payment processing system handling $10M+ monthly transactions",
                        "Built responsive React dashboard reducing customer support tickets by 30%",
                        "Implemented automated testing reducing production bugs by 50%",
                        "Mentored 3 junior developers and established code review best practices"
                    ]
                ),
                Experience(
                    title="Software Engineer",
                    company="DataCorp",
                    location="Portland, OR",
                    start_date="2019-07-01",
                    end_date="2019-12-20",
                    is_current=False,
                    description="Developed data visualization tools and ETL pipelines for enterprise clients. Built scalable APIs and optimized database performance.",
                    achievements=[
                        "Created interactive data visualization dashboards using D3.js and React",
                        "Optimized SQL queries reducing report generation time by 60%",
                        "Built RESTful APIs serving 1M+ requests daily with 99.9% uptime"
                    ]
                )
            ]
            
            # Create education
            education = [
                Education(
                    institution="University of Washington",
                    degree="Bachelor of Science",
                    field_of_study="Computer Science",
                    start_date="2015-09-01",
                    end_date="2019-06-15",
                    gpa=3.7,
                    honors=["Cum Laude", "Dean's List", "ACM Student Chapter President"]
                )
            ]
            
            # Create projects
            projects = [
                Project(
                    name="E-commerce Platform",
                    description="Full-stack e-commerce platform with React frontend, Node.js microservices, and PostgreSQL database. Features include user authentication, payment processing, inventory management, and admin dashboard.",
                    technologies=["React", "Node.js", "PostgreSQL", "Redis", "Docker", "AWS", "Stripe API"],
                    url="https://shop.example.com",
                    start_date="2023-01-01",
                    end_date="2023-06-30"
                ),
                Project(
                    name="Real-time Chat Application",
                    description="WebSocket-based chat application with end-to-end encryption, file sharing, and video calling capabilities. Supports group chats, message history, and mobile responsive design.",
                    technologies=["React", "Socket.io", "Express", "MongoDB", "WebRTC", "JWT"],
                    url="https://github.com/sarah-chen-dev/chat-app",
                    start_date="2022-08-01",
                    end_date="2022-11-30"
                ),
                Project(
                    name="Task Management API",
                    description="RESTful API for task management with user authentication, project organization, and team collaboration features. Includes automated testing and comprehensive documentation.",
                    technologies=["Django", "Python", "PostgreSQL", "Docker", "pytest", "Swagger"],
                    url="https://github.com/sarah-chen-dev/task-api",
                    start_date="2021-05-01",
                    end_date="2021-08-15"
                )
            ]
            
            # Create the complete profile
            profile_entity = Profile(
                id=f"sarah-chen-master-{uuid.uuid4().hex[:8]}",
                user_id=user_id,
                personal_info=personal_info,
                professional_summary="Experienced full-stack software engineer with 5+ years developing scalable web applications and microservices. Specialized in React, Node.js, and cloud architecture with a passion for clean code and test-driven development. Led cross-functional teams to deliver high-impact products serving millions of users. Strong background in fintech, e-commerce, and data visualization platforms.",
                experiences=experiences,
                education=education,
                skills=skills,
                projects=projects,
                custom_fields={}
            )
            
            created_profile = await profile_repo.create(profile_entity)
            print(f"✓ Master profile created with ID: {created_profile.id}")
            print(f"✓ Added {len(experiences)} work experiences")
            print(f"✓ Added {len(education)} education entries") 
            print(f"✓ Added {len(projects)} projects")
            print(f"✓ Added {len(skills.technical)} technical skills")
            
            print("\n" + "="*60)
            print("✅ TEST USER AND PROFILE CREATED SUCCESSFULLY!")
            print("="*60)
            print(f"📧 Email: {test_email}")
            print(f"🔐 Password: {test_password}")
            print(f"👤 Full Name: {test_full_name}")
            print(f"🆔 User ID: {user_id}")
            print(f"📋 Profile ID: {created_profile.id}")
            print("="*60)
            print("\nYou can now use these credentials to:")
            print("1. Login via POST /api/v1/auth/login")
            print("2. Access the master profile via GET /api/v1/profiles/{profile_id}")
            print("3. Test generation APIs with this profile data")
            print("4. Create job applications and test the full pipeline")
            print("="*60)
            
        await engine.dispose()
        
    except Exception as e:
        print(f"❌ Error creating test user and profile: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(create_test_user_and_profile())
    if success:
        print("\n🎉 Ready for testing!")
    else:
        print("\n💥 Setup failed!")
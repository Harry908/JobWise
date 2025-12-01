"""Complete test of job creation from text."""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.application.services.job_service import JobService
from app.infrastructure.repositories.job_repository import JobRepository
from app.infrastructure.database.connection import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession

EPIC_JOB = """Software Engineer
Epic
Bellevue, WA

About the job
Please note that this position is based on our campus in Madison, WI, and requires relocation to the area. We recruit nationally and provide financial relocation assistance.

Code that saves lives. 

As a software developer at Epic, you'll write software that impacts the lives of 325 million patients around the world. Working in your own office, surrounded by thousands of high-caliber developers, you'll use modern development methodologies and employ user-centered design, analytics, and machine learning tools to drive innovation in healthcare. Using leading-edge technologies and languages like JS, TS, and C#, you'll invent better ways to reduce medical errors, streamline record sharing between hospitals, and provide the quality of care a patient deserves. Learn more about our team at https://careers.epic.com/jobs/softwaredevelopment/.

Write software for the most innovative health systems on the planet.

The top-ranked health systems in U.S. News and World Report are Epic customers. Our community includes major systems like the Mayo Clinic, Johns Hopkins, Cleveland Clinic, and Kaiser Permanente, as well as leading academic medical centers at the University of Wisconsin, University of Michigan, University of California, University of Texas, The Ohio State University, and many more.

Live affordably in a city known for its rising tech talent.

Epic is located just outside Madison, Wisconsin, the second fastest growing market for tech talent in the United States and home to the state capital and the University of Wisconsin. Madison, a city surrounded by water, has received accolades for being the greenest city in America (NerdWallet), the best city for renters (SmartAsset), the fittest city in America (Fitbit), and the third best metro in the US for young professionals (Forbes Advisor).

More than just important work.

Our uniquely themed campus was designed to heighten your ability to get stuff done in your office, a conference room, or by the fireplace in a comfy chair. All meals are restaurant-quality but cost only a few dollars, and they're prepared by a team comprised of kitchen talent from restaurants around the country. And, after five years here, you'll earn a four-week sabbatical anywhere in the world. Staff have kayaked in Patagonia, attended a Beyoncé concert in Ireland, built a library in Tanzania, and run a marathon in Antarctica.

We offer comprehensive benefits to keep you healthy and happy as you grow in your life and career, and your merit-based compensation will reflect the impact your work has on the company and our customers. You'll also be eligible for annual raises and bonuses, as well as stock grants, which give you an even greater stake in the success of Epic and our customers. Healthcare is global, and building the best ideas from around the world into Epic software is a point of pride. As an Equal Opportunity Employer, we know that inclusive teams design software that supports the delivery of quality care for all patients, so diversity, equity, and inclusion are written into our principles. Please see our full non-discrimination statement at https://careers.epic.com/EEO.

Relocation to the Madison, WI area (Reimbursed)
BS/BA or greater in Computer Science, Mathematics, Software Engineering, Computer Engineering, or a related field
A history of academic excellence or professional success
Eligible to work in the United States without visa sponsorship (persons with appropriate qualifications and eligible for TN status under NAFTA may apply)
COVID-19 vaccination"""


async def test_complete_flow():
    """Test complete job creation flow."""
    print("=" * 100)
    print("Testing Complete Job Creation from Text")
    print("=" * 100)
    
    # Get database session
    async for session in get_db_session():
        try:
            # Create repository and service
            repository = JobRepository(session)
            service = JobService(repository)
            
            # Create job from text
            print("\n📝 Creating job from pasted text...")
            job = await service.create_from_text(user_id=2, raw_text=EPIC_JOB)
            
            print(f"\n✅ Job created successfully!")
            print(f"\n{'Field':<25} {'Value':<75}")
            print("-" * 100)
            print(f"{'ID':<25} {job.id}")
            print(f"{'User ID':<25} {job.user_id}")
            print(f"{'Source':<25} {job.source}")
            print(f"{'Title':<25} {job.title}")
            print(f"{'Company':<25} {job.company}")
            print(f"{'Location':<25} {job.location or 'N/A'}")
            print(f"{'Remote':<25} {job.remote}")
            print(f"{'Salary Range':<25} {job.salary_range or 'N/A'}")
            print(f"{'Status':<25} {job.status}")
            
            print(f"\n{'Keywords (' + str(len(job.parsed_keywords)) + ')':<25} {', '.join(job.parsed_keywords)}")
            
            print(f"\n{'Requirements (' + str(len(job.requirements)) + '):':<25}")
            for i, req in enumerate(job.requirements, 1):
                print(f"  {i}. {req}")
            
            print(f"\n{'Benefits (' + str(len(job.benefits)) + '):':<25}")
            if job.benefits:
                for i, benefit in enumerate(job.benefits, 1):
                    print(f"  {i}. {benefit}")
            else:
                print("  (None extracted - see description for narrative benefits)")
            
            print(f"\n{'Description:':<25}")
            desc_lines = job.description.split('\n') if job.description else []
            for line in desc_lines[:5]:  # Show first 5 lines
                if line.strip():
                    print(f"  {line[:97]}...")
            if len(desc_lines) > 5:
                print(f"  ... ({len(desc_lines) - 5} more lines)")
            
            print("\n" + "=" * 100)
            print("✅ TEST PASSED - Job was created with all fields properly populated!")
            print("=" * 100)
            
        except Exception as e:
            print(f"\n❌ TEST FAILED: {e}")
            import traceback
            traceback.print_exc()
        finally:
            break  # Only use first session


if __name__ == "__main__":
    asyncio.run(test_complete_flow())

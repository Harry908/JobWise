"""Test ranking system with different job types to verify proper prioritization."""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0IiwiZXhwIjoxNzY0NjI2OTg0LCJ0eXBlIjoiYWNjZXNzIn0.2v8i6zqrqMw_TnFTS-idN5l9pWOv9V6DlEk06-QJ9jA"
PROFILE_ID = "53cac499-04c2-4d21-84a0-f10ed31ce4dc"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Test jobs with very different requirements
test_jobs = [
    {
        "name": "Software Engineer",
        "data": {
            "source": "test",
            "title": "Senior Software Engineer",
            "company": "Tech Solutions Inc",
            "location": "Seattle, WA",
            "description": "We're seeking a Senior Software Engineer with strong Python and FastAPI experience. You'll build scalable backend services, design RESTful APIs, work with PostgreSQL databases, and implement cloud solutions on AWS. Strong focus on microservices architecture, Docker containerization, and CI/CD pipelines.",
            "requirements": [
                "5+ years Python development experience",
                "Expert in FastAPI, Django, or Flask frameworks",
                "Strong database skills (PostgreSQL, MySQL)",
                "Experience with AWS cloud services",
                "Docker and Kubernetes knowledge",
                "RESTful API design expertise",
                "Microservices architecture experience"
            ],
            "parsed_keywords": ["python", "fastapi", "django", "postgresql", "aws", "docker", "kubernetes", "microservices", "rest-api"],
            "benefits": ["Competitive salary", "Remote work"],
            "salary_range": "120000-180000",
            "remote": True
        }
    },
    {
        "name": "QA Engineer",
        "data": {
            "source": "test",
            "title": "QA Automation Engineer",
            "company": "Quality First Corp",
            "location": "San Francisco, CA",
            "description": "Looking for a QA Automation Engineer to build and maintain automated testing frameworks. You'll write test automation scripts using Python and Selenium, perform API testing with Postman, integrate tests into CI/CD pipelines, and ensure software quality through comprehensive test coverage.",
            "requirements": [
                "3+ years QA automation experience",
                "Proficiency in Python or JavaScript for test automation",
                "Experience with Selenium, Cypress, or Playwright",
                "API testing expertise (Postman, REST Assured)",
                "CI/CD integration knowledge (Jenkins, GitLab)",
                "Understanding of testing methodologies",
                "Experience with bug tracking tools (JIRA)"
            ],
            "parsed_keywords": ["qa", "testing", "automation", "selenium", "cypress", "python", "api-testing", "ci-cd", "jenkins", "jira"],
            "benefits": ["Health insurance", "Professional development"],
            "salary_range": "85000-120000",
            "remote": False
        }
    },
    {
        "name": "Cybersecurity Engineer",
        "data": {
            "source": "test",
            "title": "Cybersecurity Engineer",
            "company": "SecureNet Systems",
            "location": "Washington, DC",
            "description": "We need a Cybersecurity Engineer to protect our systems from threats. You'll conduct penetration testing, perform vulnerability assessments, implement security controls, monitor SIEM systems, and respond to security incidents. Strong knowledge of network security, encryption, and security frameworks required.",
            "requirements": [
                "4+ years cybersecurity experience",
                "Penetration testing and vulnerability assessment skills",
                "Knowledge of security frameworks (NIST, ISO 27001)",
                "Experience with SIEM tools (Splunk, ELK)",
                "Network security expertise",
                "Scripting skills (Python, Bash)",
                "Security certifications (CISSP, CEH, OSCP) preferred"
            ],
            "parsed_keywords": ["cybersecurity", "penetration-testing", "vulnerability-assessment", "siem", "splunk", "network-security", "python", "security"],
            "benefits": ["Security clearance sponsorship", "Certification reimbursement"],
            "salary_range": "120000-170000",
            "remote": False
        }
    },
    {
        "name": "Data Scientist",
        "data": {
            "source": "test",
            "title": "Senior Data Scientist",
            "company": "AI Analytics Corp",
            "location": "Boston, MA",
            "description": "Seeking a Data Scientist to build machine learning models and extract insights from large datasets. You'll work with Python data science libraries (pandas, numpy, scikit-learn), develop predictive models, perform statistical analysis, and deploy ML solutions to production using cloud platforms.",
            "requirements": [
                "3+ years data science experience",
                "Expert in Python (pandas, numpy, scikit-learn)",
                "Machine learning and statistical modeling",
                "Experience with TensorFlow or PyTorch",
                "SQL and database knowledge",
                "Data visualization skills (Matplotlib, Seaborn)",
                "Master's degree in relevant field preferred"
            ],
            "parsed_keywords": ["data-science", "machine-learning", "python", "pandas", "numpy", "scikit-learn", "tensorflow", "sql", "statistics"],
            "benefits": ["Research opportunities", "Conference budget"],
            "salary_range": "130000-180000",
            "remote": True
        }
    }
]


def get_profile_experiences():
    """Fetch current profile experiences to show in results."""
    response = requests.get(
        f"{BASE_URL}/api/v1/profiles/{PROFILE_ID}/experiences",
        headers=headers
    )
    if response.status_code == 200:
        data = response.json()
        return data.get('experiences', [])
    return []


def create_job_and_rank(job_name, job_data):
    """Create a job and get ranking."""
    print(f"\n{'='*80}")
    print(f"Testing: {job_name}")
    print(f"{'='*80}")
    
    # Create job
    response = requests.post(
        f"{BASE_URL}/api/v1/jobs",
        headers=headers,
        json=job_data
    )
    
    if response.status_code not in [200, 201]:
        print(f"❌ Failed to create job: {response.status_code}")
        return None
    
    job = response.json()
    job_id = job["id"]
    print(f"✓ Created job: {job_data['title']} at {job_data['company']}")
    print(f"  Job ID: {job_id}")
    
    # Create ranking
    print(f"\n⏳ Ranking content for {job_name}...")
    response = requests.post(
        f"{BASE_URL}/api/v1/rankings/create",
        headers=headers,
        json={
            "profile_id": PROFILE_ID,
            "job_id": job_id
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to create ranking: {response.status_code}")
        print(response.text)
        return None
    
    ranking = response.json()
    
    # Fetch full ranking details
    response = requests.get(
        f"{BASE_URL}/api/v1/rankings/job/{job_id}",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch ranking details: {response.status_code}")
        return None
    
    ranking_details = response.json()
    
    return {
        "job_id": job_id,
        "job_name": job_name,
        "job_title": job_data["title"],
        "ranking": ranking_details,
        "keywords": job_data.get("parsed_keywords", [])
    }


def display_ranking_results(result, experiences):
    """Display ranking results in a readable format."""
    if not result:
        return
    
    print(f"\n📊 Ranking Results for {result['job_name']}")
    print(f"   Job: {result['job_title']}")
    print(f"   Keywords: {', '.join(result['keywords'][:10])}")
    
    ranked_exp_ids = result['ranking'].get('ranked_experience_ids', [])
    ranked_proj_ids = result['ranking'].get('ranked_project_ids', [])
    keyword_matches = result['ranking'].get('keyword_matches', {})
    
    print(f"\n   Keyword Matches: {json.dumps(keyword_matches, indent=6)}")
    print(f"\n   ✅ Ranked {len(ranked_exp_ids)} experiences")
    print(f"   ✅ Ranked {len(ranked_proj_ids)} projects")
    
    # Create experience lookup
    exp_lookup = {exp['id']: exp for exp in experiences}
    
    print(f"\n   Experience Ranking (Top → Bottom):")
    top_experiences = ranked_exp_ids[:10] if len(ranked_exp_ids) > 10 else ranked_exp_ids
    for i, exp_id in enumerate(top_experiences, 1):  # Show top 10
        exp = exp_lookup.get(exp_id)
        if exp:
            title = exp.get('title', 'Unknown')
            company = exp.get('company', 'Unknown')
            is_barista = 'barista' in title.lower() or 'coffee' in company.lower()
            marker = "⚠️ BARISTA (should be ranked LOW)" if is_barista else "✓"
            print(f"      {i}. {marker} {title} at {company}")
    
    return ranked_exp_ids


def analyze_rankings(all_results, experiences):
    """Analyze and compare rankings across different jobs."""
    print(f"\n\n{'='*80}")
    print("CROSS-JOB RANKING ANALYSIS")
    print(f"{'='*80}\n")
    
    exp_lookup = {exp['id']: exp for exp in experiences}
    
    # Track positions of each experience across jobs
    position_tracking = {}
    
    for result in all_results:
        if not result:
            continue
        job_name = result['job_name']
        ranked_ids = result['ranking'].get('ranked_experience_ids', [])
        
        for position, exp_id in enumerate(ranked_ids, 1):
            if exp_id not in position_tracking:
                position_tracking[exp_id] = {}
            position_tracking[exp_id][job_name] = position
    
    # Find barista experience
    barista_experiences = [
        (exp_id, exp) for exp_id, exp in exp_lookup.items()
        if 'barista' in exp.get('title', '').lower() or 
           'coffee' in exp.get('company', '').lower() or
           'starbucks' in exp.get('company', '').lower()
    ]
    
    print("🔍 Barista/Non-Tech Experience Analysis:")
    if barista_experiences:
        for exp_id, exp in barista_experiences:
            print(f"\n   Experience: {exp.get('title')} at {exp.get('company')}")
            positions = position_tracking.get(exp_id, {})
            for job_name, position in positions.items():
                total = len(all_results[0]['ranking'].get('ranked_experience_ids', [])) if all_results else 0
                percentage = (position / total * 100) if total > 0 else 0
                status = "✅ CORRECTLY LOW" if percentage > 60 else "❌ INCORRECTLY HIGH"
                print(f"      {job_name}: Rank #{position}/{total} ({percentage:.1f}%) {status}")
    else:
        print("   ⚠️ No barista experience found in profile")
    
    print(f"\n\n🎯 Position Variance Analysis (showing experiences with different rankings):")
    for exp_id, positions in position_tracking.items():
        if len(positions) < 2:
            continue
        
        position_values = list(positions.values())
        variance = max(position_values) - min(position_values)
        
        if variance >= 2:  # Only show if position changes by 2 or more
            exp = exp_lookup.get(exp_id)
            if exp:
                print(f"\n   {exp.get('title')} at {exp.get('company')}:")
                for job_name in sorted(positions.keys()):
                    position = positions[job_name]
                    print(f"      {job_name}: Rank #{position}")
    
    print(f"\n\n{'='*80}")


def main():
    """Run comprehensive ranking tests."""
    print("\n" + "="*80)
    print("JOBWISE RANKING SYSTEM TEST - Multiple Job Types")
    print("="*80)
    print("\nThis test verifies that:")
    print("  1. Different job types produce different rankings")
    print("  2. Unrelated experiences (barista) rank LOW for tech jobs")
    print("  3. Relevant experiences rank HIGH for matching job types")
    print("  4. Integer ID mapping works correctly")
    
    # Get experiences first
    print("\n⏳ Fetching profile experiences...")
    experiences = get_profile_experiences()
    print(f"✓ Found {len(experiences)} experiences in profile")
    
    # Show a few experiences
    print("\nSample experiences in profile:")
    sample_exps = experiences[:5] if len(experiences) > 5 else experiences
    for exp in sample_exps:
        print(f"  - {exp.get('title')} at {exp.get('company')}")
    
    # Test each job type
    all_results = []
    for job in test_jobs:
        result = create_job_and_rank(job["name"], job["data"])
        if result:
            display_ranking_results(result, experiences)
            all_results.append(result)
    
    # Analyze rankings
    if len(all_results) >= 2:
        analyze_rankings(all_results, experiences)
    
    print("\n\n✅ Test Complete!")
    print("\nCheck server logs for:")
    print("  - Integer IDs sent to LLM (1, 2, 3...)")
    print("  - Mapping dictionaries")
    print("  - UUID conversion")


if __name__ == "__main__":
    main()

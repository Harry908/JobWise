#!/usr/bin/env python3
"""
Job Seeding Script for JobWise Backend

This script manages the seeding and management of static job data for development and testing.
It provides functionality to:
- Generate sample job data
- Validate job data format
- Update existing job data
- Clean up invalid entries

Usage:
    python scripts/seed_jobs.py [command] [options]

Commands:
    generate    Generate sample job data
    validate    Validate existing job data
    clean       Clean invalid entries
    stats       Show statistics about job data

Options:
    --count     Number of jobs to generate (default: 20)
    --output    Output file path (default: data/static_jobs.json)
    --force     Overwrite existing files without confirmation
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import random


class JobSeeder:
    """Manages job data seeding and validation."""

    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize job seeder

        Args:
            data_dir: Directory containing job data files
        """
        if data_dir is None:
            # Default to data directory relative to script location
            script_dir = Path(__file__).parent
            backend_dir = script_dir.parent.parent
            data_dir = backend_dir / "data"

        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)

        # Default output file
        self.jobs_file = self.data_dir / "static_jobs.json"

    def generate_sample_jobs(self, count: int = 20) -> List[Dict[str, Any]]:
        """
        Generate sample job data

        Args:
            count: Number of jobs to generate

        Returns:
            List of job dictionaries
        """
        jobs = []

        # Sample data pools
        companies = [
            "TechCorp Solutions", "StartupInc", "BigTech Corp", "InnovateLabs",
            "DataDriven Inc", "CloudNative Solutions", "AISystems Ltd", "DevOps Pro",
            "MobileFirst Apps", "WebScale Technologies", "FinTech Innovations",
            "HealthTech Solutions", "EduTech Platform", "GreenTech Corp", "LogisticsPro"
        ]

        locations = [
            "Seattle, WA", "San Francisco, CA", "New York, NY", "Austin, TX",
            "Boston, MA", "Denver, CO", "Portland, OR", "Los Angeles, CA",
            "Chicago, IL", "Miami, FL", "Atlanta, GA", "Remote"
        ]

        job_titles = [
            "Senior Python Backend Developer", "Full Stack Engineer", "DevOps Engineer",
            "Data Scientist", "Machine Learning Engineer", "Frontend Developer",
            "iOS Developer", "Android Developer", "Product Manager", "QA Engineer",
            "Systems Administrator", "Database Administrator", "Security Engineer",
            "Technical Lead", "Software Architect", "React Developer", "Node.js Developer"
        ]

        industries = [
            "Technology", "Healthcare", "Finance", "Education", "E-commerce",
            "Transportation", "Entertainment", "Real Estate", "Manufacturing"
        ]

        tags_pool = [
            "python", "javascript", "react", "node.js", "aws", "docker", "kubernetes",
            "postgresql", "mongodb", "redis", "fastapi", "django", "flask", "vue.js",
            "angular", "typescript", "java", "kotlin", "swift", "golang", "rust",
            "machine learning", "data science", "devops", "agile", "scrum"
        ]

        for i in range(count):
            # Generate job data
            job_id = "02d"
            title = random.choice(job_titles)
            company = random.choice(companies)
            location = random.choice(locations)
            industry = random.choice(industries)

            # Salary ranges based on experience level
            experience_levels = ["entry", "mid", "senior"]
            exp_level = random.choice(experience_levels)

            if exp_level == "entry":
                min_salary = random.randint(50000, 70000)
                max_salary = random.randint(min_salary + 10000, min_salary + 30000)
            elif exp_level == "mid":
                min_salary = random.randint(80000, 100000)
                max_salary = random.randint(min_salary + 15000, min_salary + 40000)
            else:  # senior
                min_salary = random.randint(120000, 150000)
                max_salary = random.randint(min_salary + 20000, min_salary + 50000)

            # Job type and remote policy
            job_types = ["full-time", "part-time", "contract"]
            remote_policies = ["remote", "hybrid", "onsite"]

            # Generate description
            description = f"""We are seeking a talented {title} to join our team at {company}.

Key Responsibilities:
• Design and develop scalable software solutions
• Collaborate with cross-functional teams
• Write clean, maintainable code
• Participate in code reviews and technical discussions
• Contribute to system architecture decisions

Requirements:
• {3 + random.randint(0, 5)}+ years of relevant experience
• Strong problem-solving skills
• Experience with modern development practices
• Excellent communication skills

We offer competitive compensation, comprehensive benefits, and opportunities for professional growth."""

            # Generate requirements and benefits
            requirements = [
                f"{2 + random.randint(0, 3)}+ years of {title.split()[-1]} experience",
                "Bachelor's degree in Computer Science or related field",
                "Strong knowledge of software development principles",
                "Experience with version control systems",
                "Ability to work in a fast-paced environment"
            ]

            benefits = [
                "Competitive salary and equity package",
                "Health, dental, and vision insurance",
                "Flexible work arrangements",
                "Professional development budget",
                "401(k) with company match",
                "Unlimited PTO policy"
            ]

            # Random tags (3-6 tags per job)
            num_tags = random.randint(3, 6)
            tags = random.sample(tags_pool, num_tags)

            # Company size
            company_sizes = ["1-10", "10-50", "50-200", "200-500", "500-1000", "1000+"]
            company_size = random.choice(company_sizes)

            # Posted date (random within last 30 days)
            days_ago = random.randint(0, 30)
            posted_date = datetime.now() - timedelta(days=days_ago)

            job = {
                "id": job_id,
                "title": title,
                "company": company,
                "location": location,
                "job_type": random.choice(job_types),
                "experience_level": exp_level,
                "salary_range": {
                    "min": min_salary,
                    "max": max_salary,
                    "currency": "USD"
                },
                "description": description,
                "requirements": requirements,
                "benefits": benefits,
                "posted_date": posted_date.isoformat().replace('+00:00', 'Z'),
                "company_size": company_size,
                "industry": industry,
                "remote_work_policy": random.choice(remote_policies),
                "tags": tags
            }

            jobs.append(job)

        return jobs

    def save_jobs(self, jobs: List[Dict[str, Any]], output_file: Optional[Path] = None, force: bool = False) -> None:
        """
        Save jobs to JSON file

        Args:
            jobs: List of job dictionaries
            output_file: Output file path
            force: Overwrite without confirmation
        """
        if output_file is None:
            output_file = self.jobs_file

        if output_file.exists() and not force:
            response = input(f"File {output_file} already exists. Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("Operation cancelled.")
                return

        # Sort jobs by posted date (newest first)
        jobs_sorted = sorted(jobs, key=lambda x: x['posted_date'], reverse=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(jobs_sorted, f, indent=2, ensure_ascii=False)

        print(f"Successfully saved {len(jobs)} jobs to {output_file}")

    def load_jobs(self, input_file: Optional[Path] = None) -> List[Dict[str, Any]]:
        """
        Load jobs from JSON file

        Args:
            input_file: Input file path

        Returns:
            List of job dictionaries
        """
        if input_file is None:
            input_file = self.jobs_file

        if not input_file.exists():
            print(f"File {input_file} does not exist.")
            return []

        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                jobs = json.load(f)
            return jobs
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON file: {e}")
            return []

    def validate_jobs(self, jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate job data

        Args:
            jobs: List of job dictionaries

        Returns:
            Validation results
        """
        results = {
            "total_jobs": len(jobs),
            "valid_jobs": 0,
            "invalid_jobs": 0,
            "errors": []
        }

        required_fields = [
            "id", "title", "company", "location", "job_type",
            "experience_level", "description", "posted_date"
        ]

        for i, job in enumerate(jobs):
            is_valid = True
            job_errors = []

            # Check required fields
            for field in required_fields:
                if field not in job or not job[field]:
                    job_errors.append(f"Missing required field: {field}")
                    is_valid = False

            # Validate job_type
            if job.get("job_type") not in ["full-time", "part-time", "contract", "freelance"]:
                job_errors.append("Invalid job_type")
                is_valid = False

            # Validate experience_level
            if job.get("experience_level") not in ["entry", "mid", "senior"]:
                job_errors.append("Invalid experience_level")
                is_valid = False

            # Validate remote_work_policy
            if job.get("remote_work_policy") not in ["remote", "hybrid", "onsite"]:
                job_errors.append("Invalid remote_work_policy")
                is_valid = False

            # Validate salary_range
            salary_range = job.get("salary_range")
            if salary_range:
                if not isinstance(salary_range, dict):
                    job_errors.append("salary_range must be an object")
                    is_valid = False
                elif "min" not in salary_range or "max" not in salary_range:
                    job_errors.append("salary_range must have min and max fields")
                    is_valid = False
                elif salary_range.get("min", 0) >= salary_range.get("max", 0):
                    job_errors.append("salary_range min must be less than max")
                    is_valid = False

            if is_valid:
                results["valid_jobs"] += 1
            else:
                results["invalid_jobs"] += 1
                results["errors"].append({
                    "job_index": i,
                    "job_id": job.get("id", "unknown"),
                    "errors": job_errors
                })

        return results

    def clean_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Clean and fix job data where possible

        Args:
            jobs: List of job dictionaries

        Returns:
            Cleaned list of jobs
        """
        cleaned_jobs = []

        for job in jobs:
            # Basic cleaning
            cleaned_job = job.copy()

            # Ensure tags is a list
            if not isinstance(cleaned_job.get("tags"), list):
                cleaned_job["tags"] = []

            # Ensure requirements and benefits are lists
            if not isinstance(cleaned_job.get("requirements"), list):
                cleaned_job["requirements"] = []
            if not isinstance(cleaned_job.get("benefits"), list):
                cleaned_job["benefits"] = []

            # Fix common issues
            if cleaned_job.get("job_type") not in ["full-time", "part-time", "contract", "freelance"]:
                cleaned_job["job_type"] = "full-time"

            if cleaned_job.get("experience_level") not in ["entry", "mid", "senior"]:
                cleaned_job["experience_level"] = "mid"

            if cleaned_job.get("remote_work_policy") not in ["remote", "hybrid", "onsite"]:
                cleaned_job["remote_work_policy"] = "hybrid"

            cleaned_jobs.append(cleaned_job)

        return cleaned_jobs

    def show_stats(self, jobs: List[Dict[str, Any]]) -> None:
        """
        Display statistics about job data

        Args:
            jobs: List of job dictionaries
        """
        if not jobs:
            print("No jobs found.")
            return

        print(f"Total Jobs: {len(jobs)}")

        # Count by various categories
        job_types = {}
        experience_levels = {}
        locations = {}
        companies = {}
        industries = {}

        salaries = []

        for job in jobs:
            # Job types
            jt = job.get("job_type", "unknown")
            job_types[jt] = job_types.get(jt, 0) + 1

            # Experience levels
            el = job.get("experience_level", "unknown")
            experience_levels[el] = experience_levels.get(el, 0) + 1

            # Locations
            loc = job.get("location", "unknown")
            locations[loc] = locations.get(loc, 0) + 1

            # Companies
            comp = job.get("company", "unknown")
            companies[comp] = companies.get(comp, 0) + 1

            # Industries
            ind = job.get("industry", "unknown")
            industries[ind] = industries.get(ind, 0) + 1

            # Salary data
            salary_range = job.get("salary_range")
            if salary_range and isinstance(salary_range, dict):
                salaries.extend([
                    salary_range.get("min", 0),
                    salary_range.get("max", 0)
                ])

        print("\nJob Types:")
        for jt, count in sorted(job_types.items()):
            print(f"  {jt}: {count}")

        print("\nExperience Levels:")
        for el, count in sorted(experience_levels.items()):
            print(f"  {el}: {count}")

        print("\nTop Locations:")
        for loc, count in sorted(locations.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {loc}: {count}")

        print("\nTop Companies:")
        for comp, count in sorted(companies.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {comp}: {count}")

        print("\nIndustries:")
        for ind, count in sorted(industries.items(), key=lambda x: x[1], reverse=True):
            print(f"  {ind}: {count}")

        if salaries:
            print("\nSalary Statistics:")
            print(f"  Min: ${min(salaries):,}")
            print(f"  Max: ${max(salaries):,}")
            print(f"  Average: ${sum(salaries) // len(salaries):,}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Job data seeding and management")
    parser.add_argument("command", choices=["generate", "validate", "clean", "stats"],
                       help="Command to execute")
    parser.add_argument("--count", type=int, default=20,
                       help="Number of jobs to generate (default: 20)")
    parser.add_argument("--output", type=str,
                       help="Output file path")
    parser.add_argument("--input", type=str,
                       help="Input file path")
    parser.add_argument("--force", action="store_true",
                       help="Overwrite files without confirmation")

    args = parser.parse_args()

    # Initialize seeder
    seeder = JobSeeder()

    if args.output:
        output_file = Path(args.output)
    else:
        output_file = seeder.jobs_file

    if args.input:
        input_file = Path(args.input)
    else:
        input_file = seeder.jobs_file

    if args.command == "generate":
        print(f"Generating {args.count} sample jobs...")
        jobs = seeder.generate_sample_jobs(args.count)
        seeder.save_jobs(jobs, output_file, args.force)

    elif args.command == "validate":
        print(f"Validating jobs from {input_file}...")
        jobs = seeder.load_jobs(input_file)
        results = seeder.validate_jobs(jobs)

        print(f"Total jobs: {results['total_jobs']}")
        print(f"Valid jobs: {results['valid_jobs']}")
        print(f"Invalid jobs: {results['invalid_jobs']}")

        if results['errors']:
            print("\nValidation errors:")
            for error in results['errors'][:10]:  # Show first 10 errors
                print(f"  Job {error['job_index']} ({error['job_id']}):")
                for err in error['errors']:
                    print(f"    - {err}")

            if len(results['errors']) > 10:
                print(f"  ... and {len(results['errors']) - 10} more errors")

    elif args.command == "clean":
        print(f"Cleaning jobs from {input_file}...")
        jobs = seeder.load_jobs(input_file)
        cleaned_jobs = seeder.clean_jobs(jobs)
        seeder.save_jobs(cleaned_jobs, output_file, args.force)

    elif args.command == "stats":
        print(f"Showing statistics for {input_file}...")
        jobs = seeder.load_jobs(input_file)
        seeder.show_stats(jobs)


if __name__ == "__main__":
    main()
"""Test script to verify ranking functionality."""

import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000/api/v1"

async def test_ranking():
    """Test the ranking functionality."""
    
    # Login credentials (adjust as needed)
    login_data = {
        "email": "anakin.skywalker@tatooine.galaxy",
        "password": "SkyWalker123"
    }
    
    async with httpx.AsyncClient() as client:
        # Login
        print("🔐 Logging in...")
        response = await client.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.text}")
            return
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"✅ Logged in successfully")
        
        # Get profile
        print("\n📋 Fetching profile...")
        response = await client.get(f"{BASE_URL}/profiles/me", headers=headers)
        if response.status_code != 200:
            print(f"❌ Failed to get profile: {response.text}")
            return
        
        profile = response.json()
        print(f"✅ Profile ID: {profile['id']}")
        print(f"   Experiences: {len(profile.get('experiences', []))}")
        print(f"   Projects: {len(profile.get('projects', []))}")
        
        # Print experience IDs
        print("\n📝 Experience IDs in profile:")
        for i, exp in enumerate(profile.get('experiences', []), 1):
            print(f"   {i}. {exp['id']} - {exp['title']} at {exp['company']}")
        
        # Print project IDs
        print("\n🚀 Project IDs in profile:")
        for i, proj in enumerate(profile.get('projects', []), 1):
            print(f"   {i}. {proj['id']} - {proj['name']}")
        
        # Get jobs
        print("\n💼 Fetching jobs...")
        response = await client.get(f"{BASE_URL}/jobs?limit=5", headers=headers)
        if response.status_code != 200 or not response.json().get('jobs'):
            print(f"❌ No jobs found")
            return
        
        jobs = response.json()['jobs']
        job_id = jobs[0]['id']
        print(f"✅ Using job: {jobs[0]['title']} at {jobs[0]['company']}")
        print(f"   Job ID: {job_id}")
        
        # Create or get ranking
        print("\n🎯 Creating/Getting ranking...")
        response = await client.post(f"{BASE_URL}/rankings/create", json={"job_id": job_id}, headers=headers)
        if response.status_code != 200:
            print(f"❌ Failed to create ranking: {response.text}")
            return
        
        ranking = response.json()
        print(f"✅ Ranking created")
        print(f"   Ranking ID: {ranking['id']}")
        print(f"\n📊 Ranked Experience IDs (in order):")
        for i, exp_id in enumerate(ranking['ranked_experience_ids'], 1):
            print(f"   {i}. {exp_id}")
        
        print(f"\n📊 Ranked Project IDs (in order):")
        for i, proj_id in enumerate(ranking['ranked_project_ids'], 1):
            print(f"   {i}. {proj_id}")
        
        # Compare with profile IDs
        profile_exp_ids = [exp['id'] for exp in profile.get('experiences', [])]
        profile_proj_ids = [proj['id'] for proj in profile.get('projects', [])]
        
        print("\n🔍 ID Matching Analysis:")
        print(f"   Profile experience IDs: {len(profile_exp_ids)}")
        print(f"   Ranked experience IDs: {len(ranking['ranked_experience_ids'])}")
        matched_exps = [eid for eid in ranking['ranked_experience_ids'] if eid in profile_exp_ids]
        print(f"   ✅ Matched: {len(matched_exps)}")
        print(f"   ❌ Unmatched: {len(ranking['ranked_experience_ids']) - len(matched_exps)}")
        
        if len(matched_exps) < len(ranking['ranked_experience_ids']):
            unmatched = [eid for eid in ranking['ranked_experience_ids'] if eid not in profile_exp_ids]
            print(f"\n   ⚠️ Unmatched experience IDs: {unmatched}")
        
        print(f"\n   Profile project IDs: {len(profile_proj_ids)}")
        print(f"   Ranked project IDs: {len(ranking['ranked_project_ids'])}")
        matched_projs = [pid for pid in ranking['ranked_project_ids'] if pid in profile_proj_ids]
        print(f"   ✅ Matched: {len(matched_projs)}")
        print(f"   ❌ Unmatched: {len(ranking['ranked_project_ids']) - len(matched_projs)}")
        
        if len(matched_projs) < len(ranking['ranked_project_ids']):
            unmatched = [pid for pid in ranking['ranked_project_ids'] if pid not in profile_proj_ids]
            print(f"\n   ⚠️ Unmatched project IDs: {unmatched}")
        
        # Generate resume
        print("\n📄 Generating resume...")
        response = await client.post(
            f"{BASE_URL}/generations/resume",
            json={"job_id": job_id, "max_experiences": 5, "max_projects": 3},
            headers=headers
        )
        if response.status_code != 200:
            print(f"❌ Failed to generate resume: {response.text}")
            return
        
        resume = response.json()
        print(f"✅ Resume generated")
        print(f"\n📝 Resume preview (first 500 chars):")
        print(resume['resume_text'][:500])
        print("\n...")

if __name__ == "__main__":
    asyncio.run(test_ranking())

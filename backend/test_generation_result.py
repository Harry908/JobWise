#!/usr/bin/env python3
"""
Quick Generation Result Test - Check mock resume content
"""

import asyncio
import httpx
import json

async def test_generation_result():
    # First, use existing test user
    auth_data = {
        "email": "sarah.chen@example.com",
        "password": "TestPassword123"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Login
        response = await client.post("http://localhost:8000/api/v1/auth/login", json=auth_data)
        if response.status_code != 200:
            print(f"Login failed: {response.status_code} - {response.text}")
            return
            
        auth_token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Get profile
        response = await client.get("http://localhost:8000/api/v1/profiles/me", headers=headers)
        if response.status_code != 200:
            print(f"Profile fetch failed: {response.status_code} - {response.text}")
            return
            
        profile_id = response.json()["id"]
        
        # Get test job (from previous CLI run)
        response = await client.get("http://localhost:8000/api/v1/jobs?limit=1", headers=headers)
        if response.status_code != 200 or not response.json()["jobs"]:
            print("No test jobs found - run the CLI test first")
            return
            
        job_id = response.json()["jobs"][0]["id"]
        
        # Start generation
        generation_request = {
            "profile_id": profile_id,
            "job_id": job_id,
            "options": {"template": "modern", "length": "one_page"}
        }
        
        response = await client.post(
            "http://localhost:8000/api/v1/generations/resume",
            json=generation_request,
            headers=headers
        )
        
        if response.status_code != 201:
            print(f"Generation start failed: {response.status_code} - {response.text}")
            return
            
        generation_id = response.json()["id"]
        print(f"✓ Generation started: {generation_id}")
        
        # Wait for completion (mock should be instant)
        for i in range(5):
            await asyncio.sleep(1)
            
            response = await client.get(
                f"http://localhost:8000/api/v1/generations/{generation_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                status_data = response.json()
                print(f"Status: {status_data['status']} - Stage {status_data['progress']['current_stage']}")
                
                if status_data["status"] == "completed":
                    # Try to get result
                    print("\n🎯 Attempting to get generation result...")
                    
                    try:
                        response = await client.get(
                            f"http://localhost:8000/api/v1/generations/{generation_id}/result",
                            headers=headers
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            print("✓ SUCCESS! Generated resume content:")
                            print("=" * 60)
                            print(f"ATS Score: {result.get('ats_score', 'N/A')}")
                            print(f"Match: {result.get('match_percentage', 'N/A')}%")
                            print(f"Keywords: {result.get('keywords_matched', 0)}/{result.get('keywords_total', 0)}")
                            print("\nRecommendations:")
                            for rec in result.get('recommendations', []):
                                print(f"  • {rec}")
                            print("\nResume Content (first 300 chars):")
                            content = result.get('content', {})
                            if 'text' in content:
                                print(content['text'][:300] + "...")
                            print("=" * 60)
                            return
                        else:
                            print(f"❌ Result fetch failed: {response.status_code}")
                            print(f"Response: {response.text}")
                            return
                            
                    except Exception as e:
                        print(f"❌ Error getting result: {e}")
                        return
                        
        print("❌ Generation timeout")

if __name__ == "__main__":
    asyncio.run(test_generation_result())
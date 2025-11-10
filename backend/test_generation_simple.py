#!/usr/bin/env python3
"""
Simple generation test using existing user data
"""

import asyncio
import httpx

BASE_URL = "http://localhost:8000"

async def test_generation():
    async with httpx.AsyncClient() as client:
        print("🔍 Simple Generation Test")
        print("=" * 50)
        
        # Use existing user (from previous CLI tests)
        login_data = {
            "email": "sarah.chen@example.com",
            "password": "password123"
        }
        
        try:
            # Login
            print("🔐 Logging in...")
            login_response = await client.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
            
            if login_response.status_code != 200:
                print(f"❌ Login failed: {login_response.status_code}")
                print(f"Response: {login_response.text}")
                return
            
            login_result = login_response.json()
            token = login_result["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            print(f"✅ Login successful")
            
            # Get profile
            print("📋 Getting profile...")
            profile_response = await client.get(f"{BASE_URL}/api/v1/profiles/me", headers=headers)
            
            if profile_response.status_code != 200:
                print(f"❌ No profile found: {profile_response.status_code}")
                print(f"Response: {profile_response.text}")
                return
            
            profile = profile_response.json()
            profile_id = profile["id"]
            print(f"✅ Found profile: {profile_id}")
            
            # Get a job
            print("💼 Getting available jobs...")
            jobs_response = await client.get(f"{BASE_URL}/api/v1/jobs/browse?limit=1", headers=headers)
            
            if jobs_response.status_code != 200:
                print(f"❌ Failed to get jobs: {jobs_response.status_code}")
                return
            
            jobs = jobs_response.json()
            if not jobs["results"]:
                print("❌ No jobs available")
                return
            
            job_id = jobs["results"][0]["id"]
            print(f"✅ Using job: {job_id}")
            
            # Start generation
            print("🚀 Starting resume generation with real LLM...")
            generation_data = {
                "profile_id": profile_id,
                "job_id": job_id,
                "document_type": "resume",
                "options": {
                    "template": "modern",
                    "length": "one_page",
                    "custom_instructions": "Focus on technical skills and quantified achievements"
                }
            }
            
            generation_response = await client.post(
                f"{BASE_URL}/api/v1/generations/resume", 
                json=generation_data, 
                headers=headers
            )
            
            if generation_response.status_code != 201:
                print(f"❌ Failed to start generation: {generation_response.status_code}")
                print(f"Response: {generation_response.text}")
                return
            
            generation = generation_response.json()
            generation_id = generation["id"]
            print(f"✅ Generation started: {generation_id}")
            print(f"Status: {generation['status']}")
            
            # Monitor progress
            print("⏳ Monitoring generation progress...")
            max_attempts = 30  # 30 seconds max
            attempt = 0
            
            while attempt < max_attempts:
                await asyncio.sleep(1)
                attempt += 1
                
                status_response = await client.get(
                    f"{BASE_URL}/api/v1/generations/{generation_id}/status", 
                    headers=headers
                )
                
                if status_response.status_code != 200:
                    print(f"❌ Failed to get status: {status_response.status_code}")
                    break
                
                status = status_response.json()
                progress = status["progress"]["percentage"]
                stage = status.get("stage_name", "Unknown")
                
                print(f"📊 Progress: {progress}% - {stage}")
                
                if status["status"] == "completed":
                    print("🎉 Generation completed!")
                    
                    # Get the result
                    result_response = await client.get(
                        f"{BASE_URL}/api/v1/generations/{generation_id}/result", 
                        headers=headers
                    )
                    
                    if result_response.status_code == 200:
                        result = result_response.json()
                        content = result["result"]["content"]["text"]
                        
                        print("\n" + "="*60)
                        print("📄 GENERATED RESUME:")
                        print("="*60)
                        print(content)
                        print("="*60)
                        
                        # Also save to file
                        with open(f"resume_output_{generation_id}.txt", "w", encoding="utf-8") as f:
                            f.write(content)
                        
                        print(f"💾 Resume saved to: resume_output_{generation_id}.txt")
                        
                        # Show metrics
                        result_data = result["result"]
                        print(f"📈 ATS Score: {result_data['ats_score']:.2%}")
                        print(f"🎯 Match Percentage: {result_data['match_percentage']}%")
                        print(f"🔑 Keywords Matched: {result_data['keywords_matched']}/{result_data['keywords_total']}")
                        
                        if result_data.get('recommendations'):
                            print("💡 Recommendations:")
                            for rec in result_data['recommendations']:
                                print(f"  • {rec}")
                    
                    break
                    
                elif status["status"] == "failed":
                    print(f"❌ Generation failed: {status.get('error_message', 'Unknown error')}")
                    break
            
            if attempt >= max_attempts:
                print(f"⏰ Generation timeout after {max_attempts} seconds")
        
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_generation())
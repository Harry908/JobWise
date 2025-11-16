#!/usr/bin/env python3
"""Test script to verify the fixed error handling."""

import asyncio
import httpx
import json

async def test_generation_result_error():
    """Test the improved error handling for failed generations."""
    
    # Test with the known failed generation
    generation_id = "8da3ada3-dfcc-4858-841b-2c23307cc727"
    
    # Assuming server is running on localhost:8000
    base_url = "http://127.0.0.1:8000"
    
    async with httpx.AsyncClient() as client:
        try:
            # First, try to get the status
            print("Testing generation status endpoint...")
            status_response = await client.get(
                f"{base_url}/api/v1/generations/{generation_id}",
                headers={"Authorization": "Bearer test_user_1"}  # Mock auth for testing
            )
            print(f"Status Endpoint Response: {status_response.status_code}")
            if status_response.status_code != 404:
                status_data = status_response.json()
                print(f"Generation Status: {status_data.get('status')}")
                print(f"Error Message: {status_data.get('error_message')}")
            
            print("\nTesting generation result endpoint...")
            # Now try to get the result (this should give improved error)
            result_response = await client.get(
                f"{base_url}/api/v1/generations/{generation_id}/result",
                headers={"Authorization": "Bearer test_user_1"}  # Mock auth for testing
            )
            
            print(f"Result Endpoint Response: {result_response.status_code}")
            
            if result_response.status_code != 200:
                error_data = result_response.json()
                print(f"Error Response: {json.dumps(error_data, indent=2)}")
            
        except httpx.ConnectError:
            print("Server is not running. Start the server first with: python start_server.py")
        except Exception as e:
            print(f"Test error: {e}")

if __name__ == "__main__":
    asyncio.run(test_generation_result_error())
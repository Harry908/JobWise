#!/usr/bin/env python3
"""Debug script to check generation status."""

import asyncio
import sys
from app.infrastructure.database.connection import create_engine, create_session_factory
from app.infrastructure.repositories.generation_repository import GenerationRepository

async def check_generation_status(generation_id: str):
    """Check the status of a specific generation."""
    try:
        engine = create_engine()
        session_factory = create_session_factory(engine)
        
        async with session_factory() as db:
            repo = GenerationRepository(db)
            generation = await repo.get_by_id(generation_id)
            
            if not generation:
                print(f"Generation {generation_id} not found")
                return
            
            print(f"Generation ID: {generation.id}")
            print(f"Status: {generation.status}")
            print(f"Document Type: {generation.document_type}")
            print(f"Current Stage: {generation.current_stage}")
            print(f"Total Stages: {generation.total_stages}")
            print(f"Stage Name: {generation.stage_name}")
            print(f"Error Message: {generation.error_message}")
            print(f"Created At: {generation.created_at}")
            print(f"Started At: {generation.started_at}")
            print(f"Completed At: {generation.completed_at}")
            print(f"Has Result: {generation.result is not None}")
            
            if generation.result:
                print(f"Result Document ID: {generation.result.document_id}")
                print(f"ATS Score: {generation.result.ats_score}")
                print(f"PDF URL: {generation.result.pdf_url}")
        
        await engine.dispose()
                
    except Exception as e:
        print(f"Error checking generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generation_id = "8da3ada3-dfcc-4858-841b-2c23307cc727"
    if len(sys.argv) > 1:
        generation_id = sys.argv[1]
    
    asyncio.run(check_generation_status(generation_id))
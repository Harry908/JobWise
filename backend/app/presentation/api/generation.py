"""AI Generation API router."""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from uuid import UUID

from app.core.dependencies import get_db_session, get_current_user
from app.domain.enums.document_type import DocumentType
from app.presentation.schemas.generation import (
    EnhanceProfileRequest,
    EnhanceProfileResponse,
    CreateRankingRequest,
    RankingResponse,
    GenerateResumeRequest,
    GenerateCoverLetterRequest,
    GenerationResponse,
    GenerationHistoryResponse
)
from app.infrastructure.adapters.llm.groq_adapter import GroqAdapter
from app.infrastructure.repositories.sample_repository import SampleRepository
from app.infrastructure.repositories.writing_style_repository import WritingStyleRepository
from app.infrastructure.repositories.ranking_repository import RankingRepository
from app.infrastructure.repositories.generation_repository import GenerationRepository
from app.infrastructure.repositories.profile_repository import ProfileRepository
from app.infrastructure.repositories.job_repository import JobRepository
from app.application.services.style_extraction_service import StyleExtractionService
from app.application.services.enhancement_service import EnhancementService
from app.application.services.ranking_service import RankingService
from app.application.services.generation_service import GenerationService
from app.core.config import get_settings

router = APIRouter(prefix="/api/v1", tags=["AI Generation"])


def get_llm_adapter():
    """Get LLM adapter instance."""
    settings = get_settings()
    return GroqAdapter(api_key=settings.groq_api_key)


# Profile Enhancement Endpoint
@router.post("/profile/enhance", response_model=EnhanceProfileResponse)
async def enhance_profile(
    request: EnhanceProfileRequest,
    current_user: int = Depends(get_current_user),
    session = Depends(get_db_session)
):
    """Enhance profile using AI with writing style."""
    llm = get_llm_adapter()
    sample_repo = SampleRepository(session)
    style_repo = WritingStyleRepository(session)
    profile_repo = ProfileRepository(session)
    
    style_service = StyleExtractionService(llm, sample_repo, style_repo)
    enhancement_service = EnhancementService(llm, profile_repo, style_service)
    
    try:
        result = await enhancement_service.enhance_profile(
            profile_id=request.profile_id,
            user_id=current_user,
            custom_prompt=request.custom_prompt
        )
        
        return EnhanceProfileResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhancement failed: {str(e)}")


# Content Ranking Endpoints
@router.post("/rankings/create", response_model=RankingResponse)
async def create_ranking(
    request: CreateRankingRequest,
    current_user: int = Depends(get_current_user),
    session = Depends(get_db_session)
):
    """Create job-specific content ranking."""
    llm = get_llm_adapter()
    ranking_repo = RankingRepository(session)
    profile_repo = ProfileRepository(session)
    job_repo = JobRepository(session)
    
    ranking_service = RankingService(llm, ranking_repo, profile_repo, job_repo)
    
    try:
        ranking = await ranking_service.create_ranking(
            user_id=current_user,
            job_id=request.job_id,
            custom_prompt=request.custom_prompt
        )
        
        return RankingResponse(
            id=ranking.id,
            user_id=ranking.user_id,
            job_id=ranking.job_id,
            ranked_experience_ids=ranking.ranked_experience_ids,
            ranked_project_ids=ranking.ranked_project_ids,
            ranking_rationale=ranking.ranking_rationale,
            keyword_matches=ranking.keyword_matches,
            relevance_scores=ranking.relevance_scores,
            llm_metadata={"raw": ranking.llm_metadata} if ranking.llm_metadata else None,
            status=ranking.status.value,
            created_at=ranking.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ranking failed: {str(e)}")


@router.get("/rankings/job/{job_id}", response_model=RankingResponse)
async def get_ranking_for_job(
    job_id: UUID,
    current_user: int = Depends(get_current_user),
    session = Depends(get_db_session)
):
    """Get cached ranking for a job."""
    llm = get_llm_adapter()
    ranking_repo = RankingRepository(session)
    profile_repo = ProfileRepository(session)
    job_repo = JobRepository(session)
    
    ranking_service = RankingService(llm, ranking_repo, profile_repo, job_repo)
    
    ranking = await ranking_service.get_ranking_for_job(current_user, job_id)
    if not ranking:
        raise HTTPException(status_code=404, detail="No ranking found for this job")
    
    return RankingResponse(
        id=ranking.id,
        user_id=ranking.user_id,
        job_id=ranking.job_id,
        ranked_experience_ids=ranking.ranked_experience_ids,
        ranked_project_ids=ranking.ranked_project_ids,
        ranking_rationale=ranking.ranking_rationale,
        keyword_matches=ranking.keyword_matches,
        relevance_scores=ranking.relevance_scores,
        llm_metadata={"raw": ranking.llm_metadata} if ranking.llm_metadata else None,
        status=ranking.status.value,
        created_at=ranking.created_at
    )


# Generation Endpoints
@router.post("/generations/resume", response_model=GenerationResponse)
async def generate_resume(
    request: GenerateResumeRequest,
    current_user: int = Depends(get_current_user),
    session = Depends(get_db_session)
):
    """Generate tailored resume for a job (fast, no LLM)."""
    llm = get_llm_adapter()
    generation_repo = GenerationRepository(session)
    profile_repo = ProfileRepository(session)
    job_repo = JobRepository(session)
    ranking_repo = RankingRepository(session)
    sample_repo = SampleRepository(session)
    style_repo = WritingStyleRepository(session)
    
    ranking_service = RankingService(llm, ranking_repo, profile_repo, job_repo)
    style_service = StyleExtractionService(llm, sample_repo, style_repo)
    generation_service = GenerationService(
        llm, generation_repo, profile_repo, job_repo, ranking_service, style_service
    )
    
    try:
        generation = await generation_service.generate_resume(
            user_id=current_user,
            job_id=request.job_id,
            max_experiences=request.max_experiences,
            max_projects=request.max_projects,
            include_summary=request.include_summary,
            custom_prompt=request.custom_prompt
        )
        
        return GenerationResponse(
            generation_id=generation.id,
            job_id=generation.job_id,
            document_type=generation.document_type.value,
            status=generation.status.value,
            content_text=generation.content_text,
            ats_score=generation.ats_score,
            ats_feedback=generation.ats_feedback,
            llm_metadata={"raw": generation.llm_metadata} if generation.llm_metadata else None,
            created_at=generation.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume generation failed: {str(e)}")


@router.post("/generations/cover-letter", response_model=GenerationResponse)
async def generate_cover_letter(
    request: GenerateCoverLetterRequest,
    current_user: int = Depends(get_current_user),
    session = Depends(get_db_session)
):
    """Generate personalized cover letter (LLM-powered)."""
    llm = get_llm_adapter()
    generation_repo = GenerationRepository(session)
    profile_repo = ProfileRepository(session)
    job_repo = JobRepository(session)
    ranking_repo = RankingRepository(session)
    sample_repo = SampleRepository(session)
    style_repo = WritingStyleRepository(session)
    
    ranking_service = RankingService(llm, ranking_repo, profile_repo, job_repo)
    style_service = StyleExtractionService(llm, sample_repo, style_repo)
    generation_service = GenerationService(
        llm, generation_repo, profile_repo, job_repo, ranking_service, style_service
    )
    
    try:
        generation = await generation_service.generate_cover_letter(
            user_id=current_user,
            job_id=request.job_id,
            company_name=request.company_name,
            hiring_manager_name=request.hiring_manager_name,
            max_paragraphs=request.max_paragraphs,
            custom_prompt=request.custom_prompt
        )
        
        return GenerationResponse(
            generation_id=generation.id,
            job_id=generation.job_id,
            document_type=generation.document_type.value,
            status=generation.status.value,
            content_text=generation.content_text,
            content_structured=generation.content_structured,
            ats_score=generation.ats_score,
            ats_feedback=generation.ats_feedback,
            llm_metadata={"raw": generation.llm_metadata} if generation.llm_metadata else None,
            created_at=generation.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cover letter generation failed: {str(e)}")


@router.get("/generations/history", response_model=GenerationHistoryResponse)
async def get_generation_history(
    document_type: Optional[str] = Query(None, description="Filter by resume/cover_letter"),
    job_id: Optional[UUID] = Query(None, description="Filter by job"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: int = Depends(get_current_user),
    session = Depends(get_db_session)
):
    """Get generation history with pagination."""
    llm = get_llm_adapter()
    generation_repo = GenerationRepository(session)
    profile_repo = ProfileRepository(session)
    job_repo = JobRepository(session)
    ranking_repo = RankingRepository(session)
    sample_repo = SampleRepository(session)
    style_repo = WritingStyleRepository(session)
    
    ranking_service = RankingService(llm, ranking_repo, profile_repo, job_repo)
    style_service = StyleExtractionService(llm, sample_repo, style_repo)
    generation_service = GenerationService(
        llm, generation_repo, profile_repo, job_repo, ranking_service, style_service
    )
    
    doc_type = DocumentType(document_type) if document_type else None
    
    generations = await generation_service.get_generation_history(
        user_id=current_user,
        document_type=doc_type,
        job_id=job_id,
        limit=limit,
        offset=offset
    )
    
    response_items = [
        GenerationResponse(
            generation_id=gen.id,
            job_id=gen.job_id,
            document_type=gen.document_type.value,
            status=gen.status.value,
            content_text=gen.content_text,
            content_structured=gen.content_structured,
            ats_score=gen.ats_score,
            ats_feedback=gen.ats_feedback,
            llm_metadata={"raw": gen.llm_metadata} if gen.llm_metadata else None,
            created_at=gen.created_at
        )
        for gen in generations
    ]
    
    return GenerationHistoryResponse(
        generations=response_items,
        total=len(response_items),
        limit=limit,
        offset=offset
    )


@router.delete("/generations/{generation_id}", status_code=204)
async def delete_generation(
    generation_id: UUID,
    current_user: int = Depends(get_current_user),
    session = Depends(get_db_session)
):
    """Delete a generation."""
    generation_repo = GenerationRepository(session)
    
    # First check if the generation exists and belongs to the user
    generation = await generation_repo.get_by_id(generation_id)
    if not generation:
        raise HTTPException(status_code=404, detail="Generation not found")
    
    if generation.user_id != current_user:
        raise HTTPException(status_code=403, detail="Not authorized to delete this generation")
    
    # Delete the generation
    success = await generation_repo.delete(generation_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete generation")
    
    return None

# Testing Examples for JobWise Backend

## Domain Layer Testing (Pure Business Logic)

### Example: Profile Entity Tests
```python
# tests/domain/test_profile_entity.py
import pytest
from datetime import date
from app.domain.entities.profile import MasterProfile
from app.domain.value_objects.personal_info import PersonalInfo
from app.domain.value_objects.experience import Experience

class TestMasterProfile:
    def test_calculate_years_experience(self):
        """Test experience calculation with multiple jobs."""
        profile = MasterProfile(
            personal_info=PersonalInfo(
                full_name="John Doe",
                email="john@example.com"
            ),
            experiences=[
                Experience(
                    title="Senior Engineer",
                    company="TechCorp",
                    start_date=date(2020, 1, 1),
                    end_date=date(2023, 1, 1)
                ),
                Experience(
                    title="Junior Engineer", 
                    company="StartupInc",
                    start_date=date(2018, 1, 1),
                    end_date=date(2020, 1, 1)
                )
            ]
        )
        
        assert profile.calculate_years_experience() == 5.0
    
    def test_get_relevant_experiences_with_keywords(self):
        """Test filtering experiences by relevance."""
        profile = self._create_sample_profile()
        keywords = ["python", "fastapi", "machine learning"]
        
        relevant_experiences = profile.get_relevant_experiences(keywords)
        
        assert len(relevant_experiences) >= 1
        assert any("python" in exp.description.lower() for exp in relevant_experiences)
    
    def test_profile_validation_missing_required_fields(self):
        """Test validation fails for incomplete profiles."""
        with pytest.raises(ValidationError):
            MasterProfile(
                personal_info=None,  # Required field missing
                experiences=[]
            )
```

### Example: AI Pipeline Stage Tests
```python
# tests/domain/services/ai/test_job_analyzer.py
import pytest
from unittest.mock import Mock, AsyncMock
from app.domain.services.ai.job_analyzer import JobAnalyzer
from app.domain.entities.job import JobPosting
from app.infrastructure.ai.llm_service import LLMService

class TestJobAnalyzer:
    @pytest.fixture
    def mock_llm_service(self):
        mock = Mock(spec=LLMService)
        mock.generate_completion = AsyncMock(return_value=self._mock_job_analysis_response())
        mock.estimate_tokens = Mock(return_value=1500)
        return mock
    
    @pytest.fixture
    def job_analyzer(self, mock_llm_service):
        return JobAnalyzer(llm_service=mock_llm_service)
    
    async def test_extract_ats_keywords_success(self, job_analyzer):
        """Test successful keyword extraction from job description."""
        job = JobPosting(
            title="Senior Python Developer",
            company="TechCorp",
            description="Looking for Python developer with FastAPI and AWS experience"
        )
        
        result = await job_analyzer.execute(job)
        
        assert result.is_success()
        keywords = result.get_output("required_keywords")
        assert any(kw.keyword == "python" for kw in keywords)
        assert any(kw.keyword == "fastapi" for kw in keywords)
        assert result.tokens_used <= 1500  # Within budget
    
    async def test_token_budget_exceeded(self, job_analyzer, mock_llm_service):
        """Test handling when token estimation exceeds budget."""
        mock_llm_service.estimate_tokens.return_value = 2000  # Over budget
        
        job = JobPosting(title="Complex Job", description="Very long description...")
        
        result = await job_analyzer.execute(job)
        
        assert result.status == StageStatus.FAILED
        assert "token budget" in result.error_message.lower()
    
    def _mock_job_analysis_response(self):
        return '''
        {
            "required_keywords": [
                {"keyword": "python", "importance": "critical"},
                {"keyword": "fastapi", "importance": "high"}
            ],
            "technical_requirements": ["5+ years Python", "REST API development"],
            "seniority_level": "senior"
        }
        '''
```

## Application Layer Testing (Service Integration)

### Example: Generation Service Tests
```python
# tests/application/services/test_generation_service.py
import pytest
from unittest.mock import Mock, AsyncMock
from app.application.services.generation_service import GenerationService
from app.domain.services.ai_orchestrator import AIOrchestrator
from app.domain.repositories.profile_repository import ProfileRepository

class TestGenerationService:
    @pytest.fixture
    def mock_dependencies(self):
        return {
            'ai_orchestrator': Mock(spec=AIOrchestrator),
            'profile_repo': Mock(spec=ProfileRepository),
            'job_repo': Mock(spec=JobRepository),
            'document_repo': Mock(spec=DocumentRepository)
        }
    
    @pytest.fixture 
    def generation_service(self, mock_dependencies):
        return GenerationService(**mock_dependencies)
    
    async def test_generate_resume_success(self, generation_service, mock_dependencies):
        """Test successful resume generation workflow."""
        # Arrange
        profile_id = "profile-123"
        job_id = "job-456"
        
        mock_dependencies['profile_repo'].get_by_id = AsyncMock(return_value=self._mock_profile())
        mock_dependencies['job_repo'].get_by_id = AsyncMock(return_value=self._mock_job())
        mock_dependencies['ai_orchestrator'].execute_pipeline = AsyncMock(
            return_value=self._mock_pipeline_result()
        )
        
        # Act
        result = await generation_service.generate_resume(profile_id, job_id)
        
        # Assert
        assert result.status == "completed"
        assert result.document_id is not None
        assert result.ats_score >= 0.85
        mock_dependencies['document_repo'].save.assert_called_once()
    
    async def test_generate_resume_profile_not_found(self, generation_service, mock_dependencies):
        """Test error handling for missing profile."""
        mock_dependencies['profile_repo'].get_by_id = AsyncMock(return_value=None)
        
        with pytest.raises(NotFoundError) as exc_info:
            await generation_service.generate_resume("invalid-id", "job-123")
        
        assert "profile" in str(exc_info.value).lower()
```

## Infrastructure Layer Testing (External Dependencies)

### Example: Repository Tests
```python
# tests/infrastructure/repositories/test_profile_repository.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.repositories.profile_repository import ProfileRepositoryImpl
from app.infrastructure.database.models import ProfileModel

class TestProfileRepository:
    @pytest.fixture
    async def db_session(self):
        """Create test database session."""
        # Setup test database connection
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            yield session
    
    @pytest.fixture
    def profile_repository(self, db_session):
        return ProfileRepositoryImpl(db_session)
    
    async def test_create_profile_success(self, profile_repository):
        """Test profile creation and retrieval."""
        profile_data = {
            "personal_info": {"full_name": "John Doe", "email": "john@test.com"},
            "experiences": [],
            "skills": {"technical": ["Python"], "soft": ["Communication"]}
        }
        
        created_profile = await profile_repository.create(profile_data)
        
        assert created_profile.id is not None
        assert created_profile.personal_info.full_name == "John Doe"
        
        # Verify retrieval
        retrieved = await profile_repository.get_by_id(created_profile.id)
        assert retrieved.personal_info.email == "john@test.com"
```

### Example: External API Integration Tests
```python
# tests/infrastructure/external_services/test_openai_client.py
import pytest
from unittest.mock import patch, AsyncMock
from app.infrastructure.ai.openai_client import OpenAIClient
from app.core.exceptions import ExternalServiceError

class TestOpenAIClient:
    @pytest.fixture
    def openai_client(self):
        return OpenAIClient(api_key="test-key")
    
    @patch('openai.ChatCompletion.acreate')
    async def test_generate_completion_success(self, mock_openai, openai_client):
        """Test successful OpenAI API call."""
        mock_openai.return_value = {
            "choices": [{"message": {"content": "Generated response"}}],
            "usage": {"total_tokens": 150}
        }
        
        result = await openai_client.generate_completion(
            prompt="Test prompt",
            max_tokens=1000
        )
        
        assert result.content == "Generated response"
        assert result.tokens_used == 150
    
    @patch('openai.ChatCompletion.acreate')
    async def test_rate_limit_handling(self, mock_openai, openai_client):
        """Test rate limit error handling and retry."""
        # First call fails with rate limit
        mock_openai.side_effect = [
            Exception("Rate limit exceeded"),
            {"choices": [{"message": {"content": "Success after retry"}}]}
        ]
        
        result = await openai_client.generate_completion("Test prompt")
        
        assert result.content == "Success after retry"
        assert mock_openai.call_count == 2  # Retry happened
```

## Presentation Layer Testing (API Endpoints)

### Example: FastAPI Endpoint Tests
```python
# tests/presentation/api/test_generations.py
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import app

class TestGenerationsAPI:
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    async def async_client(self):
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client
    
    async def test_create_resume_generation_success(self, async_client):
        """Test successful resume generation request."""
        with patch('app.application.services.generation_service.GenerationService.generate_resume') as mock_generate:
            mock_generate.return_value = {
                "generation_id": "gen-123",
                "status": "pending",
                "estimated_completion": "2024-10-18T10:32:00Z"
            }
            
            response = await async_client.post(
                "/api/v1/generations/resume",
                json={
                    "profile_id": "profile-123",
                    "job_id": "job-456",
                    "options": {"template": "modern", "length": "one_page"}
                },
                headers={"Authorization": "Bearer test-token"}
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["generation_id"] == "gen-123"
            assert data["status"] == "pending"
    
    async def test_create_generation_rate_limit_exceeded(self, async_client):
        """Test rate limiting for AI generation."""
        with patch('app.presentation.middleware.rate_limit.check_rate_limit') as mock_rate_limit:
            mock_rate_limit.side_effect = RateLimitExceeded(retry_after=3600)
            
            response = await async_client.post(
                "/api/v1/generations/resume",
                json={"profile_id": "profile-123", "job_id": "job-456"}
            )
            
            assert response.status_code == 429
            assert "rate_limit_exceeded" in response.json()["error"]
    
    async def test_get_generation_status(self, async_client):
        """Test generation status endpoint."""
        with patch('app.application.services.generation_service.GenerationService.get_status') as mock_status:
            mock_status.return_value = {
                "generation_id": "gen-123",
                "status": "generating",
                "progress": {"current_stage": 2, "percentage": 40}
            }
            
            response = await async_client.get("/api/v1/generations/gen-123")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "generating"
            assert data["progress"]["percentage"] == 40
```

## End-to-End Testing

### Example: Complete Generation Workflow
```python
# tests/e2e/test_resume_generation_flow.py
import pytest
from httpx import AsyncClient
from app.main import app

class TestResumeGenerationE2E:
    async def test_complete_resume_generation_flow(self):
        """Test complete flow from profile creation to PDF download."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 1. Create profile
            profile_response = await client.post("/api/v1/profiles", json={
                "personal_info": {
                    "full_name": "John Doe",
                    "email": "john@example.com",
                    "phone": "+1-555-123-4567"
                },
                "experiences": [{
                    "title": "Software Engineer",
                    "company": "TechCorp",
                    "start_date": "2020-01-01",
                    "description": "Developed Python applications"
                }],
                "skills": {"technical": ["Python", "FastAPI"]}
            })
            assert profile_response.status_code == 201
            profile_id = profile_response.json()["id"]
            
            # 2. Save a job
            job_response = await client.post("/api/v1/saved-jobs", json={
                "job_id": "job-123",
                "notes": "Great opportunity"
            })
            assert job_response.status_code == 201
            
            # 3. Generate resume
            generation_response = await client.post("/api/v1/generations/resume", json={
                "profile_id": profile_id,
                "job_id": "job-123",
                "options": {"template": "modern"}
            })
            assert generation_response.status_code == 201
            generation_id = generation_response.json()["generation_id"]
            
            # 4. Poll for completion (in real test, use proper async handling)
            status_response = await client.get(f"/api/v1/generations/{generation_id}")
            generation_data = status_response.json()
            
            if generation_data["status"] == "completed":
                document_id = generation_data["result"]["document_id"]
                
                # 5. Download PDF
                pdf_response = await client.get(f"/api/v1/documents/{document_id}/download")
                assert pdf_response.status_code == 200
                assert pdf_response.headers["content-type"] == "application/pdf"
```

## Performance Testing

### Example: Load Testing for AI Generation
```python
# tests/performance/test_generation_performance.py
import asyncio
import time
import pytest
from concurrent.futures import ThreadPoolExecutor

class TestGenerationPerformance:
    async def test_generation_performance_targets(self):
        """Test that generation meets performance targets."""
        start_time = time.time()
        
        # Simulate generation request
        result = await self.simulate_generation()
        
        execution_time = time.time() - start_time
        
        # Performance targets from requirements
        assert execution_time < 60, f"Generation took {execution_time}s (>60s p95 target)"
        assert result.ats_score >= 0.85, f"ATS score {result.ats_score} below 0.85 target"
        assert result.tokens_used <= 8000, f"Used {result.tokens_used} tokens (>8000 budget)"
    
    async def test_concurrent_generation_load(self):
        """Test system under concurrent generation load."""
        concurrent_requests = 10
        
        async def single_generation():
            return await self.simulate_generation()
        
        # Run concurrent generations
        start_time = time.time()
        tasks = [single_generation() for _ in range(concurrent_requests)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        # Verify all succeeded
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) == concurrent_requests
        
        # Average time should still be reasonable
        avg_time = total_time / concurrent_requests
        assert avg_time < 30, f"Average generation time {avg_time}s exceeds 30s target"
```

## Testing Configuration

### Example: pytest Configuration
```python
# conftest.py
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.infrastructure.database.models import Base

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def test_db():
    """Create test database for each test."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSession(engine) as session:
        yield session
    
    await engine.dispose()

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    mock = Mock()
    mock.generate_completion = AsyncMock(return_value=MockLLMResponse(
        content="Mock AI response",
        tokens_used=100
    ))
    return mock

# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
    -v
asyncio_mode = auto
```
# JobWise Implementation Plan

## Executive Summary

This implementation plan provides a comprehensive roadmap for developing JobWise using clean architecture principles. The plan prioritizes the AI-powered resume generation feature while establishing clear pathways from prototype to production deployment.

## Implementation Strategy

### 1. Phased Development Approach

#### Phase 1: Foundation (Weeks 8-9)
**Goal**: Establish core architecture and basic functionality
**Priority**: Critical path for all subsequent development

**Sprint 1.1 (Week 8)**
- Set up clean architecture project structure
- Implement domain models and core entities
- Create repository interfaces and SQLite implementations
- Establish basic FastAPI application with dependency injection
- Implement Profile Management service (CRUD operations)

**Sprint 1.2 (Week 9)**  
- Build Flutter application structure with state management
- Implement master profile UI (create, edit, view)
- Create static job data service and basic job browsing
- Establish API client in Flutter with error handling
- Implement offline data caching mechanism

**Deliverables:**
- Functional master profile management
- Basic job browsing capability  
- Local data persistence
- Foundation for AI generation pipeline

#### Phase 2: Core AI Generation (Weeks 10-11)
**Goal**: Implement 5-stage AI generation pipeline
**Priority**: Primary business differentiator

**Sprint 2.1 (Week 10)**
- Implement AI Orchestrator service architecture
- Build Job Analyzer stage (LLM integration)
- Create Profile Compiler stage (relevance scoring)
- Establish token budget management system
- Implement generation status tracking

**Sprint 2.2 (Week 11)**
- Complete Document Generator stage (content creation)
- Build Quality Validator stage (ATS compliance)
- Implement PDF Exporter stage (template system)
- Create generation UI with progress tracking
- Add error handling and retry mechanisms

**Deliverables:**
- End-to-end resume generation pipeline
- Progress tracking UI
- PDF export capability
- Quality validation system

#### Phase 3: Enhancement & Polish (Weeks 12-13)
**Goal**: Improve user experience and system reliability
**Priority**: Production readiness

**Sprint 3.1 (Week 12)**
- Implement document management and history
- Build cover letter generation capability
- Add advanced job search and filtering
- Implement caching optimizations
- Create comprehensive error handling

**Sprint 3.2 (Week 13)**
- Optimize generation performance and quality
- Implement offline synchronization
- Add comprehensive testing suite
- Build monitoring and metrics collection
- Performance optimization and load testing

**Deliverables:**
- Complete document management system
- Cover letter generation
- Enhanced job discovery
- Robust error handling and offline support

#### Phase 4: Production Readiness (Week 14)
**Goal**: Deploy production-ready system
**Priority**: Scalability and production features

**Sprint 4.1 (Week 14)**
- Implement production database migration (PostgreSQL)
- Set up authentication system (JWT tokens)
- Deploy to production infrastructure
- Implement monitoring and alerting
- Conduct final testing and optimization

**Deliverables:**
- Production deployment
- Authentication system
- Monitoring infrastructure
- Performance benchmarks met

### 2. Architecture Implementation Order

#### 2.1 Domain Layer (Priority 1)
```
Implementation Order:
1. Core Entities (MasterProfile, Job, GeneratedDocument)
2. Value Objects (PersonalInfo, Skills, Experience)
3. Domain Services (AIOrchestrator, ValidationService)
4. Repository Interfaces (IProfileRepository, IJobRepository)
5. Domain Rules and Invariants
```

#### 2.2 Application Layer (Priority 2)
```
Implementation Order:
1. Use Case Interfaces and DTOs
2. Profile Management Use Cases
3. Job Management Use Cases  
4. Generation Use Cases
5. Document Management Use Cases
6. Command/Query Handlers
```

#### 2.3 Infrastructure Layer (Priority 3)
```
Implementation Order:
1. Database Configuration and Models
2. Repository Implementations (SQLite first)
3. External Service Adapters (LLM, PDF)
4. Caching Implementation
5. Configuration Management
6. Production Adapters (PostgreSQL, Redis)
```

#### 2.4 Presentation Layer (Priority 4)
```
Implementation Order:
1. FastAPI Controllers and Routes
2. Flutter App Structure and Navigation
3. Profile Management UI
4. Job Browsing UI
5. Generation UI with Progress Tracking
6. Document Management UI
```

## Technical Implementation Guidelines

### 1. Clean Architecture Enforcement

#### Dependency Rules
```python
# Example: Domain layer independence
class MasterProfile:
    """Domain entity with no external dependencies"""
    def __init__(self, profile_data: ProfileData):
        self._validate_profile_rules(profile_data)
        self._profile_data = profile_data
    
    def update_experience(self, experience: Experience) -> None:
        """Business rule: Experience must be valid and relevant"""
        if not self._is_valid_experience(experience):
            raise InvalidExperienceError("Experience must meet quality standards")
        self._profile_data.experiences.append(experience)
```

#### Interface Segregation
```python
# Example: Repository interface segregation
class IProfileReadRepository:
    """Read-only profile operations"""
    def get_by_id(self, profile_id: ProfileId) -> Optional[MasterProfile]:
        pass
    
class IProfileWriteRepository:
    """Write-only profile operations"""  
    def save(self, profile: MasterProfile) -> ProfileId:
        pass
    
class IProfileRepository(IProfileReadRepository, IProfileWriteRepository):
    """Combined interface for full profile management"""
    pass
```

### 2. Configuration-Based Environment Switching

#### Service Factory Pattern
```python
class ServiceFactory:
    """Factory for creating environment-specific services"""
    
    def __init__(self, config: EnvironmentConfig):
        self.config = config
    
    def create_llm_service(self) -> ILLMService:
        if self.config.environment == "prototype":
            return OpenAILLMService(
                model="gpt-3.5-turbo",
                timeout=30,
                max_retries=2
            )
        else:
            return OpenAILLMService(
                model="gpt-4",
                fallback_model="gpt-3.5-turbo", 
                timeout=60,
                max_retries=3
            )
    
    def create_database_service(self) -> IDatabase:
        if self.config.environment == "prototype":
            return SQLiteDatabase(self.config.sqlite_url)
        else:
            return PostgreSQLDatabase(self.config.postgresql_url)
```

#### Configuration Management
```python
class EnvironmentConfig:
    """Environment-specific configuration"""
    
    @classmethod
    def from_environment(cls) -> 'EnvironmentConfig':
        environment = os.getenv("ENVIRONMENT", "prototype")
        
        if environment == "prototype":
            return PrototypeConfig()
        elif environment == "production":
            return ProductionConfig()
        else:
            raise ValueError(f"Unknown environment: {environment}")

class PrototypeConfig(EnvironmentConfig):
    database_url = "sqlite:///./jobwise.db"
    llm_model = "gpt-3.5-turbo"
    job_data_source = "static"
    cache_type = "memory"
    
class ProductionConfig(EnvironmentConfig):
    database_url = os.getenv("DATABASE_URL")
    llm_model = "gpt-4"
    job_data_source = "api"
    cache_type = "redis"
```

### 3. AI Orchestrator Implementation

#### Pipeline Stage Architecture
```python
class PipelineStage:
    """Base class for AI pipeline stages"""
    
    def __init__(self, name: str, token_budget: int):
        self.name = name
        self.token_budget = token_budget
    
    async def execute(self, input_data: Any, context: PipelineContext) -> StageResult:
        """Execute stage with error handling and monitoring"""
        start_time = time.time()
        
        try:
            # Validate token budget
            if context.tokens_used + self.token_budget > context.total_budget:
                raise TokenBudgetExceededError()
            
            # Execute stage logic
            result = await self._process(input_data, context)
            
            # Update context
            execution_time = time.time() - start_time
            context.update_stage_result(self.name, result, execution_time)
            
            return result
            
        except Exception as e:
            context.record_stage_error(self.name, e)
            raise
    
    async def _process(self, input_data: Any, context: PipelineContext) -> StageResult:
        """Override in concrete stages"""
        raise NotImplementedError
```

#### Error Handling and Retry Logic
```python
class AIOrchestrator:
    """Main orchestrator for AI generation pipeline"""
    
    async def generate_resume(
        self, 
        profile: MasterProfile, 
        job: Job, 
        options: GenerationOptions
    ) -> GenerationResult:
        
        context = PipelineContext(
            generation_id=str(uuid.uuid4()),
            total_budget=8000,
            max_retries=3
        )
        
        stages = [
            JobAnalyzerStage(token_budget=1500),
            ProfileCompilerStage(token_budget=2000),
            DocumentGeneratorStage(token_budget=3000),
            QualityValidatorStage(token_budget=1500),
            PDFExporterStage(token_budget=0)
        ]
        
        try:
            input_data = {"profile": profile, "job": job, "options": options}
            
            for stage in stages:
                result = await self._execute_stage_with_retry(
                    stage, input_data, context
                )
                input_data["previous_result"] = result
            
            return GenerationResult.success(context.final_result)
            
        except Exception as e:
            return GenerationResult.failure(str(e), context.execution_log)
    
    async def _execute_stage_with_retry(
        self, 
        stage: PipelineStage, 
        input_data: Any, 
        context: PipelineContext
    ) -> StageResult:
        
        for attempt in range(context.max_retries):
            try:
                return await stage.execute(input_data, context)
            except (TimeoutError, LLMServiceError) as e:
                if attempt == context.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

### 4. Flutter State Management Implementation

#### Provider Setup (Prototype)
```dart
// providers/generation_provider.dart
class GenerationProvider extends ChangeNotifier {
  GenerationState _state = GenerationState.idle();
  
  GenerationState get state => _state;
  
  Future<void> generateResume({
    required String profileId,
    required String jobId,
    required GenerationOptions options,
  }) async {
    _state = GenerationState.loading();
    notifyListeners();
    
    try {
      final result = await _apiService.generateResume(
        profileId: profileId,
        jobId: jobId,  
        options: options,
      );
      
      // Poll for status updates
      await _pollGenerationStatus(result.generationId);
      
    } catch (error) {
      _state = GenerationState.error(error.toString());
      notifyListeners();
    }
  }
  
  Future<void> _pollGenerationStatus(String generationId) async {
    Timer.periodic(Duration(seconds: 2), (timer) async {
      final status = await _apiService.getGenerationStatus(generationId);
      
      _state = GenerationState.progress(
        stage: status.currentStage,
        progress: status.progress,
      );
      notifyListeners();
      
      if (status.isCompleted) {
        timer.cancel();
        _state = GenerationState.completed(status.result);
        notifyListeners();
      }
    });
  }
}
```

#### Riverpod Migration (Production)
```dart
// providers/generation_provider.dart
final generationProvider = StateNotifierProvider<GenerationNotifier, GenerationState>((ref) {
  return GenerationNotifier(ref.read(apiServiceProvider));
});

class GenerationNotifier extends StateNotifier<GenerationState> {
  GenerationNotifier(this._apiService) : super(GenerationState.idle());
  
  final ApiService _apiService;
  
  Future<void> generateResume({
    required String profileId,
    required String jobId,
    required GenerationOptions options,
  }) async {
    state = GenerationState.loading();
    
    try {
      final result = await _apiService.generateResume(
        profileId: profileId,
        jobId: jobId,
        options: options,
      );
      
      await _pollGenerationStatus(result.generationId);
    } catch (error, stackTrace) {
      state = GenerationState.error(error.toString());
    }
  }
}
```

### 5. Testing Strategy Implementation

#### Unit Testing (Domain Layer)
```python
# tests/domain/test_master_profile.py
def test_master_profile_creation_with_valid_data():
    # Arrange
    profile_data = ProfileData(
        personal_info=PersonalInfo(
            full_name="John Doe",
            email="john@example.com"
        ),
        experiences=[valid_experience()],
        skills=[valid_skill()]
    )
    
    # Act
    profile = MasterProfile(profile_data)
    
    # Assert
    assert profile.id is not None
    assert profile.personal_info.full_name == "John Doe"
    assert len(profile.experiences) == 1

def test_master_profile_rejects_invalid_email():
    # Arrange
    profile_data = ProfileData(
        personal_info=PersonalInfo(
            full_name="John Doe", 
            email="invalid-email"
        )
    )
    
    # Act & Assert
    with pytest.raises(InvalidEmailError):
        MasterProfile(profile_data)
```

#### Integration Testing (Application Layer)
```python
# tests/application/test_generation_use_case.py
@pytest.mark.asyncio
async def test_generate_resume_success():
    # Arrange
    profile_repo = InMemoryProfileRepository()
    job_repo = InMemoryJobRepository()
    ai_orchestrator = MockAIOrchestrator()
    
    use_case = GenerateResumeUseCase(profile_repo, job_repo, ai_orchestrator)
    
    profile = await profile_repo.save(valid_master_profile())
    job = await job_repo.save(valid_job())
    
    command = GenerateResumeCommand(
        profile_id=profile.id,
        job_id=job.id,
        options=GenerationOptions()
    )
    
    # Act
    result = await use_case.execute(command)
    
    # Assert
    assert result.is_success()
    assert result.document_id is not None
```

#### Contract Testing (Infrastructure Layer)
```python
# tests/infrastructure/test_openai_adapter.py
@pytest.mark.integration
async def test_openai_adapter_analyze_job():
    # Arrange
    adapter = OpenAILLMAdapter(api_key="test-key")
    job_description = "Software Engineer position requiring Python skills"
    
    # Act
    result = await adapter.analyze_job(job_description)
    
    # Assert
    assert isinstance(result, JobAnalysisResult)
    assert "python" in [skill.lower() for skill in result.required_skills]
    assert result.experience_level is not None
```

## Database Implementation Strategy

### 1. SQLite Schema (Prototype)

#### Migration Structure
```sql
-- migrations/001_initial_schema.sql
CREATE TABLE profiles (
    id TEXT PRIMARY KEY,
    personal_info JSON NOT NULL,
    summary TEXT,
    experiences JSON NOT NULL,
    skills JSON NOT NULL,
    education JSON NOT NULL,
    projects JSON,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE jobs (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT,
    description TEXT NOT NULL,
    requirements JSON,
    analysis JSON,
    posted_date TIMESTAMP,
    source TEXT DEFAULT 'static',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE generated_documents (
    id TEXT PRIMARY KEY,
    profile_id TEXT NOT NULL,
    job_id TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('resume', 'cover_letter')),
    content JSON NOT NULL,
    metadata JSON NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES profiles(id),
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);
```

### 2. PostgreSQL Migration (Production)

#### Schema Enhancement
```sql
-- Enhanced schema with production features
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    personal_info JSONB NOT NULL,
    summary TEXT,
    experiences JSONB NOT NULL DEFAULT '[]',
    skills JSONB NOT NULL DEFAULT '[]',
    education JSONB NOT NULL DEFAULT '[]',
    projects JSONB DEFAULT '[]',
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_profiles_user_id ON profiles(user_id);
CREATE INDEX idx_profiles_updated_at ON profiles(updated_at);
CREATE INDEX idx_jobs_title_company ON jobs USING gin(to_tsvector('english', title || ' ' || company));
```

## Deployment Implementation

### 1. Prototype Deployment

#### Docker Compose Setup
```yaml
# docker-compose.prototype.yml
version: '3.8'

services:
  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=prototype
      - DATABASE_URL=sqlite:///./data/jobwise.db
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
      - ./storage:/app/storage
    
  frontend:
    build: ./mobile_app
    ports:
      - "3000:3000"
    environment:
      - API_BASE_URL=http://api:8000
```

### 2. Production Deployment

#### Kubernetes Deployment
```yaml
# k8s/api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jobwise-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: jobwise-api
  template:
    metadata:
      labels:
        app: jobwise-api
    spec:
      containers:
      - name: api
        image: jobwise/api:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: jobwise-secrets
              key: database-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"  
            cpu: "500m"
```

## Performance Optimization Implementation

### 1. Caching Strategy

#### Multi-Level Cache Implementation
```python
class CacheManager:
    """Multi-level caching with fallback strategy"""
    
    def __init__(self, config: CacheConfig):
        self.l1_cache = MemoryCache(max_size=1000)
        self.l2_cache = RedisCache(config.redis_url) if config.redis_url else None
    
    async def get(self, key: str, type_: Type[T]) -> Optional[T]:
        # Try L1 cache first
        result = self.l1_cache.get(key, type_)
        if result is not None:
            return result
        
        # Try L2 cache if available
        if self.l2_cache:
            result = await self.l2_cache.get(key, type_)
            if result is not None:
                # Populate L1 cache
                self.l1_cache.set(key, result)
                return result
        
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        # Set in both caches
        self.l1_cache.set(key, value, ttl)
        if self.l2_cache:
            await self.l2_cache.set(key, value, ttl)
```

### 2. Database Performance

#### Query Optimization
```python
class OptimizedProfileRepository:
    """Repository with performance optimizations"""
    
    async def get_profile_with_related_data(self, profile_id: str) -> MasterProfile:
        # Use join queries to avoid N+1 problem
        query = """
        SELECT p.*, 
               json_agg(gd.*) as generated_documents
        FROM profiles p
        LEFT JOIN generated_documents gd ON p.id = gd.profile_id
        WHERE p.id = :profile_id
        GROUP BY p.id
        """
        
        result = await self.db.fetch_one(query, {"profile_id": profile_id})
        return self._map_to_domain_object(result)
    
    async def search_profiles_optimized(self, filters: ProfileFilters) -> List[MasterProfile]:
        # Use database-specific optimizations
        if isinstance(self.db, PostgreSQLDatabase):
            # Use full-text search for PostgreSQL
            return await self._search_with_fts(filters)
        else:
            # Use LIKE queries for SQLite  
            return await self._search_with_like(filters)
```

This implementation plan provides a detailed roadmap for building JobWise with clean architecture principles, prioritizing the resume generation feature while ensuring scalable, maintainable code that can evolve from prototype to production seamlessly.
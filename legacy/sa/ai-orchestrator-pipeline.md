# AI Orchestrator Pipeline Design

## Overview
The AI Orchestrator is the core intelligence component that transforms a master resume into a tailored resume for a specific job. It operates as a 5-stage pipeline with token budget management and error handling.

## Pipeline Architecture

```
Master Resume + Job Description
           ↓
    [Stage 1: Job Analyzer]
           ↓
    [Stage 2: Profile Compiler] 
           ↓
    [Stage 3: Document Generator]
           ↓
    [Stage 4: Quality Validator]
           ↓
    [Stage 5: PDF Exporter]
           ↓
      Tailored Resume PDF
```

## Token Budget Allocation

**Total Budget**: 8000 tokens per generation
- Stage 1 (Job Analyzer): 1500 tokens
- Stage 2 (Profile Compiler): 2000 tokens  
- Stage 3 (Document Generator): 3000 tokens
- Stage 4 (Quality Validator): 1500 tokens
- Stage 5 (PDF Exporter): No LLM tokens (local processing)

**Overlap Strategy**: 500 token overlap between stages for context preservation

## Stage Definitions

### Stage 1: Job Analyzer
**Purpose**: Extract and structure job requirements
**Input**: Raw job description text
**Output**: Structured job requirements JSON

```python
class JobAnalysisResult:
    required_skills: List[str]
    preferred_skills: List[str]
    experience_level: str
    industry: str
    role_type: str
    keywords: List[str]
    company_culture: str
    responsibilities: List[str]
```

**LLM Prompt Template**:
```
Analyze this job description and extract:
1. Required technical skills
2. Preferred qualifications  
3. Experience level needed
4. Key responsibilities
5. Important keywords for ATS
6. Company culture indicators

Job Description: {job_text}
```

### Stage 2: Profile Compiler
**Purpose**: Score and rank resume sections by job relevance
**Input**: Master resume + Job analysis
**Output**: Relevance-scored resume sections

```python
class ProfileCompilerResult:
    experiences: List[ExperienceSection]  # scored 0-100
    skills: List[Skill]                   # scored 0-100
    projects: List[Project]               # scored 0-100
    education: List[Education]            # scored 0-100
    recommendations: List[str]            # what to emphasize
```

**Scoring Algorithm**:
- Keyword matching: 40% weight
- Skills alignment: 30% weight
- Experience relevance: 20% weight
- Industry/role fit: 10% weight

### Stage 3: Document Generator
**Purpose**: Generate tailored resume content
**Input**: Scored profile sections + Job requirements
**Output**: Formatted resume sections

```python
class DocumentGeneratorResult:
    summary: str
    experience_bullets: List[str]
    skills_section: List[str]
    achievements: List[str]
    customized_sections: Dict[str, str]
```

**Generation Strategy**:
1. Rewrite experience bullets to highlight relevant achievements
2. Reorder skills by job relevance
3. Customize summary for target role
4. Emphasize quantifiable results
5. Include job-relevant keywords naturally

### Stage 4: Quality Validator
**Purpose**: Ensure ATS compliance and consistency
**Input**: Generated resume content
**Output**: Validation report + corrections

```python
class QualityValidatorResult:
    ats_score: float              # 0-100
    issues_found: List[str]
    corrected_content: Dict[str, str]
    recommendations: List[str]
```

**Validation Checks**:
- ATS-friendly formatting
- Keyword density optimization
- Consistency in dates/formatting
- Grammar and spelling
- Length requirements (1-2 pages)
- Section completeness

### Stage 5: PDF Exporter
**Purpose**: Generate professional PDF output
**Input**: Validated resume content
**Output**: PDF file (ATS and visual versions)

**Templates**:
- **ATS Template**: Plain text, single column, standard fonts
- **Visual Template**: Enhanced layout, colors, modern design

## Error Handling Strategy

### LLM Failures
```python
class PipelineErrorHandler:
    def handle_llm_timeout(stage: int) -> str:
        # Return cached result or simplified fallback
        
    def handle_token_limit(stage: int) -> str:
        # Compress input and retry with reduced context
        
    def handle_quality_failure() -> str:
        # Return last valid version with warning
```

### Retry Logic
- **Stage 1-4**: Maximum 2 retries with exponential backoff
- **Token overflow**: Compress context and retry once
- **Quality failure**: Single retry with stricter prompts

## Implementation Architecture

### Class Structure
```python
class AIOrchestrator:
    def __init__(self, llm_client: LLMClient):
        self.stages = [
            JobAnalyzer(llm_client),
            ProfileCompiler(llm_client),  
            DocumentGenerator(llm_client),
            QualityValidator(llm_client),
            PDFExporter()
        ]
    
    async def generate_resume(
        self, 
        master_resume: MasterResume,
        job_description: str
    ) -> GenerationResult:
        # Execute pipeline with error handling
```

### Configuration Management
```python
class PipelineConfig:
    # Prototype Configuration
    llm_model: str = "gpt-3.5-turbo"
    max_retries: int = 2
    timeout_seconds: int = 30
    cache_results: bool = True
    
    # Production Configuration  
    llm_model: str = "gpt-4"
    max_retries: int = 3
    timeout_seconds: int = 60
    cache_results: bool = True
    fallback_model: str = "gpt-3.5-turbo"
```

## Performance Optimization

### Caching Strategy
- **Job Analysis**: Cache results by job description hash
- **Profile Compilation**: Cache by master resume version
- **Generated Content**: Cache by (resume_id, job_id) pair
- **TTL**: 24 hours for analysis, 1 hour for generation

### Parallel Processing
- Stages 1 & 2 can run in parallel for different job applications
- PDF generation can be background task
- Multiple template formats can generate simultaneously

## Monitoring & Analytics

### Key Metrics
```python
class PipelineMetrics:
    generation_time_ms: int
    token_usage_by_stage: Dict[str, int]
    success_rate: float
    error_types: List[str]
    user_satisfaction: float  # from feedback
```

### Logging Requirements
- Input/output tokens per stage
- Processing time per stage
- Error rates and types
- User feedback scores
- A/B test results for prompt variations

## Quality Assurance

### Automated Testing
- Unit tests for each stage
- Integration tests for full pipeline
- Load testing with concurrent generations
- Quality regression tests

### Human Validation
- Sample output review process
- ATS compatibility testing
- User acceptance testing
- Expert review of generated content

## Deployment Options

### Prototype Deployment
- Single FastAPI service
- Local LLM API calls
- SQLite for caching
- File-based PDF storage

### Production Deployment
- Microservice per stage
- Queue-based processing (Celery/RQ)
- Redis for caching
- S3 for PDF storage
- Load balancing across instances

## Cost Management

### Token Budget Controls
```python
class TokenBudgetManager:
    daily_limit: int = 50000  # tokens per day
    per_user_limit: int = 5000  # tokens per user per day
    
    def check_budget(user_id: str, estimated_tokens: int) -> bool:
        # Validate against limits before processing
```

### Cost Optimization
- Use GPT-3.5-turbo for development
- Implement smart caching to reduce API calls
- Compress prompts without losing quality
- Batch processing for multiple applications

This AI Orchestrator design provides a robust, scalable foundation for the resume generation feature while maintaining simplicity and clear upgrade paths from prototype to production.
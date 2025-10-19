# JobWise Backend - Revised Implementation Plan (F1-F5 Complete)

## 🎯 Current Status & New Priorities

**CURRENT STATE**: ✅ **F1-F5 COMPLETED**
- ✅ **F1**: Environment & Basic Setup - FastAPI application running, middleware, health checks
- ✅ **F2**: Database Foundation - SQLAlchemy async, Alembic migrations, models, repositories  
- ✅ **F3**: Authentication System - JWT tokens, user registration/login, middleware protection
- ✅ **F4**: Profile Management - Complete master profile CRUD with experiences/education/projects
- ✅ **F5**: Job Discovery - Static job data, search/filtering, job endpoints

**NEW PRIORITIES** (User Request):
1. **Add master resume** ✅ **Already Implemented in F4**
2. **Add job description** - New entity for custom job descriptions
3. **AI process (mock/placeholders)** - Mock AI pipeline with realistic outputs
4. **Generate new resume** - AI-powered resume generation
5. **Export to PDF** - PDF generation (mock .txt if complex)

---

## 🏗️ Foundation Features (COMPLETED)

### ✅ F1: Environment & Basic Setup (COMPLETED)
**Status**: ✅ **IMPLEMENTED**

- FastAPI application running with proper middleware stack
- Environment configuration with `.env` support  
- Health check endpoints with database connectivity
- Error handling middleware and CORS configuration
- Comprehensive test infrastructure with 16/17 tests passing

### ✅ F2: Database Foundation (COMPLETED)
**Status**: ✅ **IMPLEMENTED**
- SQLAlchemy 2.0 async with proper session management and connection pooling
- Alembic migrations configured with complete schema
- All database models implemented (User, Profile, Job, Generation, etc.)
- Repository pattern with full CRUD operations and async support
- Database health checks integrated into API (13/13 tests passing)

### ✅ F3: Authentication System (COMPLETED)
**Status**: ✅ **IMPLEMENTED**
- Complete JWT token management with proper security
- User registration/login with bcrypt password hashing
- JWT middleware protection for secured endpoints
- Comprehensive authentication API endpoints
- Test coverage: 11/16 tests passing (5 failing due to configuration issues)

### ✅ F4: Profile Management (COMPLETED)
**Status**: ✅ **IMPLEMENTED**
- Complete MasterProfile entity with comprehensive value objects
- Full profile CRUD API with experience/education/project management
- ProfileService business logic with validation and error handling
- Repository interface with async database operations
- Comprehensive DTOs with Pydantic validation
- Profile analytics endpoints for user insights

**Available API Endpoints**:
```
POST   /api/v1/profiles              # Create new profile
GET    /api/v1/profiles/me           # Get current user's profile 
GET    /api/v1/profiles/{id}         # Get profile by ID
PUT    /api/v1/profiles/{id}         # Update profile
DELETE /api/v1/profiles/{id}         # Delete profile
POST   /api/v1/profiles/{id}/experiences    # Add experience
PUT    /api/v1/profiles/{id}/experiences    # Update experience
DELETE /api/v1/profiles/{id}/experiences   # Remove experience
POST   /api/v1/profiles/{id}/education     # Add education
PUT    /api/v1/profiles/{id}/education     # Update education
DELETE /api/v1/profiles/{id}/education    # Remove education
POST   /api/v1/profiles/{id}/projects      # Add project
PUT    /api/v1/profiles/{id}/projects      # Update project
DELETE /api/v1/profiles/{id}/projects     # Remove project
GET    /api/v1/profiles/{id}/analytics     # Profile analytics
```

### ✅ F5: Job Discovery (COMPLETED)
**Status**: ✅ **IMPLEMENTED**
- Complete job discovery system with static JSON data (100+ jobs)
- JobService with search, filtering, and pagination
- StaticJobRepository for data access and management
- Job seeding script for data management
- FastAPI endpoints for job search/details/filters
- Test coverage: 6/6 tests passing for job functionality

**Available API Endpoints**:
```
GET /api/v1/jobs?q=python&location=seattle&limit=20    # Search jobs with filters
GET /api/v1/jobs/{job_id}                              # Get job details
```

---

## 🚀 NEW PRIORITY FEATURES (User Requested)

### F6: Custom Job Description Management
**Duration**: 1 day | **Priority**: HIGH | **Dependencies**: F3, F5

**User Priority**: Add job description functionality for custom job postings

**Files to Create/Modify**:
```
📁 New Files:
├── app/domain/entities/job_description.py          # Custom job description entity
├── app/application/services/job_description_service.py  # Job description business logic
├── app/application/dtos/job_description_dtos.py    # Job description DTOs
├── app/infrastructure/repositories/job_description_repository.py  # Data access
├── app/presentation/api/job_descriptions.py       # Job description endpoints
├── tests/test_job_descriptions.py                 # Comprehensive tests
└── data/sample_job_descriptions.json              # Sample data

📝 Modify Files:
├── app/infrastructure/database/models.py          # Add JobDescription model
├── app/main.py                                    # Register job description routes
└── alembic/versions/004_job_descriptions.py       # Migration
```

**Deliverables**:
- [ ] JobDescription entity for custom job postings
- [ ] CRUD endpoints for job descriptions  
- [ ] Job description parsing and keyword extraction
- [ ] User-owned job descriptions with validation

**Acceptance Criteria**:
- ✅ Users can create custom job descriptions
- ✅ Parse job requirements and extract keywords
- ✅ Validate job description format and content
- ✅ Associate job descriptions with user profiles
- ✅ Search and filter personal job descriptions

**API Endpoints**:
```
POST   /api/v1/job-descriptions           # Create custom job description
GET    /api/v1/job-descriptions           # List user's job descriptions  
GET    /api/v1/job-descriptions/{id}      # Get job description details
PUT    /api/v1/job-descriptions/{id}      # Update job description
DELETE /api/v1/job-descriptions/{id}      # Delete job description
POST   /api/v1/job-descriptions/{id}/parse # Parse job description for keywords
```

---

### F7: Mock AI Generation Pipeline  
**Duration**: 2 days | **Priority**: HIGH | **Dependencies**: F4, F6

**User Priority**: AI process (mock or placeholders) - Generate new resume

**Files to Create/Modify**:
```
📁 New Files:
├── app/application/services/mock_generation_service.py  # Mock AI generation
├── app/infrastructure/ai/mock_llm_adapter.py           # Mock LLM responses
├── app/infrastructure/ai/resume_templates.py           # Resume templates  
├── app/presentation/api/generation.py                  # Generation endpoints
├── data/mock_generation_responses.json                # Mock AI responses
├── data/resume_templates/                             # Template directory
│   ├── professional_template.txt                     # Professional format
│   ├── technical_template.txt                        # Technical format
│   └── creative_template.txt                         # Creative format
├── tests/test_mock_generation.py                     # Generation tests
└── tests/integration/test_generation_pipeline.py      # Integration tests

📝 Modify Files:
├── app/domain/services/ai_orchestrator.py            # Use mock adapter
├── app/main.py                                       # Register generation routes
└── alembic/versions/005_generations.py               # Generation tables
```

**Deliverables**:
- [ ] Mock AI service with realistic response times (2-5 seconds)
- [ ] 5-stage pipeline simulation with status updates
- [ ] Resume generation with multiple templates
- [ ] Quality validation simulation with ATS scores
- [ ] Generation history and status tracking

**Acceptance Criteria**:
- ✅ Generate resumes using profile + job description
- ✅ Simulate realistic AI processing stages  
- ✅ Return formatted resume content
- ✅ Track generation progress and status
- ✅ Mock ATS compliance scoring (0.7-0.95)

**Mock Pipeline Stages**:
1. **Job Analysis** (1s) - Parse job requirements, extract keywords
2. **Profile Compilation** (1s) - Score profile sections against job
3. **Document Generation** (2s) - Generate tailored resume content
4. **Quality Validation** (1s) - ATS compliance check, scoring
5. **Export Ready** (0.5s) - Prepare for PDF export

**API Endpoints**:
```
POST /api/v1/generations/resume            # Start resume generation
GET  /api/v1/generations/{id}              # Get generation status
GET  /api/v1/generations/{id}/result       # Get generated resume
POST /api/v1/generations/{id}/regenerate   # Regenerate with changes
DELETE /api/v1/generations/{id}            # Cancel/delete generation
GET  /api/v1/generations                   # List user's generations
```

---

### F8: PDF Export System
**Duration**: 1 day | **Priority**: HIGH | **Dependencies**: F7

**User Priority**: Export to PDF (mock .txt file if PDF export is complicated)

**Files to Create/Modify**:
```
📁 New Files:
├── app/application/services/export_service.py        # Export business logic
├── app/infrastructure/export/text_exporter.py       # Text file export (.txt)
├── app/infrastructure/export/pdf_exporter.py        # Future PDF export
├── app/presentation/api/exports.py                  # Export endpoints
├── data/exports/                                    # Export storage directory
├── tests/test_exports.py                           # Export tests
└── tests/integration/test_full_generation_flow.py   # End-to-end tests

📝 Modify Files:
├── app/core/config.py                               # Add export configuration
├── app/main.py                                      # Register export routes  
└── .env                                            # Export file paths
```

**Deliverables**:
- [ ] Text file export (.txt) for generated resumes
- [ ] Mock PDF export placeholder (returns .txt initially)
- [ ] File storage and retrieval system
- [ ] Download endpoints with proper headers
- [ ] Export history and cleanup

**Acceptance Criteria**:
- ✅ Export generated resumes as formatted .txt files
- ✅ Clean, professional text formatting
- ✅ Download files with proper MIME types
- ✅ Store exports with unique filenames
- ✅ Auto-cleanup old export files (7 day retention)

**Export Formats**:
- **Text Export** (.txt): Clean, formatted plain text resume
- **PDF Placeholder**: Returns formatted .txt with "PDF Export Coming Soon" note
- **Future**: Actual PDF generation with professional templates

**API Endpoints**:
```
POST /api/v1/exports                      # Create export from generation
GET  /api/v1/exports/{id}                 # Get export details
GET  /api/v1/exports/{id}/download        # Download export file
DELETE /api/v1/exports/{id}               # Delete export
GET  /api/v1/exports                      # List user's exports
```

---

## 📋 FUTURE FEATURES (Lower Priority)

### F9: Saved Jobs Feature (Future)
**Duration**: 2 days | **Priority**: Low | **Dependencies**: F4, F5

**Files to Create/Modify**:
```
📁 New Files:
├── app/domain/entities/saved_job.py            # SavedJob entity
├── app/domain/value_objects/application_status.py # Application status enum
├── app/application/services/saved_job_service.py # SavedJob business logic
├── app/application/dtos/saved_job_dtos.py      # SavedJob DTOs
├── app/application/use_cases/saved_job_use_cases.py # SavedJob use cases
├── app/infrastructure/repositories/saved_job_repository.py # SavedJob data access
├── app/presentation/api/saved_jobs.py          # SavedJob endpoints
├── app/presentation/schemas/saved_job_schemas.py # SavedJob Pydantic schemas
├── tests/test_saved_jobs.py                    # SavedJob tests
└── tests/test_job_status.py                    # Status tracking tests

📝 Modify Files:
├── app/infrastructure/database/models.py       # Add SavedJob model
├── app/main.py                                 # Register saved job routes
└── alembic/versions/004_saved_jobs_table.py    # SavedJob migration
```

**Deliverables**:
- [ ] SavedJob entity with status tracking
- [ ] Save/unsave job endpoints
- [ ] Application status management
- [ ] Saved jobs listing with filters

**Acceptance Criteria**:
- ✅ Save jobs with notes and status
- ✅ Update application status
- ✅ List saved jobs with status filters
- ✅ Remove saved jobs
- ✅ No duplicate saves allowed

**Test Plan**:
```bash
# Test: Save job functionality
pytest tests/test_saved_jobs.py

# Test: Status tracking
pytest tests/test_job_status.py
```

**API Endpoints**:
```
POST   /api/v1/saved-jobs
GET    /api/v1/saved-jobs?status=applied
PUT    /api/v1/saved-jobs/{id}
DELETE /api/v1/saved-jobs/{id}
```

---

## 🤖 AI GENERATION FEATURES (Original Plan - Now Lower Priority)

### F10: Advanced AI Service Foundation (Future)
**Duration**: 2 days | **Priority**: Low | **Dependencies**: F4, F5

**Files to Create/Modify**:
```
📁 New Files:
├── app/domain/ports/llm_service_port.py        # LLM service interface (already exists)
├── app/infrastructure/adapters/llm/mock_adapter.py # Mock LLM implementation
├── app/infrastructure/ai/prompt_manager.py     # Prompt template manager (already exists)
├── app/infrastructure/ai/token_manager.py      # Token counting (already exists)
├── app/core/service_factory.py                # Service factory pattern
├── data/prompt_templates/                     # Prompt template directory
│   ├── job_analysis.txt                       # Job analysis prompts
│   ├── profile_compilation.txt                # Profile compilation prompts
│   ├── document_generation.txt                # Document generation prompts
│   ├── quality_validation.txt                 # Quality validation prompts
│   └── cover_letter.txt                       # Cover letter prompts
├── tests/test_mock_ai_service.py              # Mock AI service tests
└── tests/test_prompt_templates.py             # Prompt template tests

📝 Modify Files:
├── app/core/config.py                         # Add AI service config
└── .env                                       # Add mock service settings
```

**Deliverables**:
- [ ] Abstract LLM service interface
- [ ] Mock LLM implementation for testing
- [ ] Basic prompt templates
- [ ] Token usage tracking

**Acceptance Criteria**:
- ✅ Mock AI service generates realistic content
- ✅ Prompt templates configurable
- ✅ Token counting implemented
- ✅ Service can be swapped without code changes

**Test Plan**:
```bash
# Test: Mock AI service
pytest tests/test_mock_ai_service.py

# Test: Prompt templates
pytest tests/test_prompt_templates.py
```

---

### F8: Generation Pipeline Foundation
**Duration**: 3 days | **Priority**: High | **Dependencies**: F7

**Files to Create/Modify**:
```
📁 New Files:
├── app/domain/entities/generation.py           # Generation entity (already exists)
├── app/domain/services/ai_orchestrator.py      # AI pipeline orchestrator (already exists)
├── app/domain/services/pipeline_common.py      # Pipeline common utilities (already exists)
├── app/application/services/generation_service.py # Generation business logic
├── app/application/dtos/generation_dtos.py     # Generation DTOs
├── app/application/use_cases/generation_use_cases.py # Generation use cases
├── app/infrastructure/repositories/generation_repository.py # Generation data access
├── app/presentation/api/generation.py          # Generation endpoints
├── app/presentation/schemas/generation_schemas.py # Generation Pydantic schemas
├── tests/test_generation_pipeline.py           # Pipeline tests
├── tests/test_generation_status.py             # Status tracking tests
└── tests/test_generation_errors.py             # Error handling tests

📝 Modify Files:
├── app/infrastructure/database/models.py       # Add Generation model
├── app/main.py                                 # Register generation routes
└── alembic/versions/005_generation_tables.py   # Generation migration
```

**Deliverables**:
- [ ] Generation entity with status tracking
- [ ] 5-stage pipeline structure
- [ ] Pipeline progress tracking
- [ ] Error handling and retry logic

**Acceptance Criteria**:
- ✅ Generation process trackable by ID
- ✅ Status updates work (pending → completed/failed)
- ✅ Each stage can run independently
- ✅ Pipeline handles failures gracefully
- ✅ Processing time tracked

**Test Plan**:
```bash
# Test: Generation pipeline
pytest tests/test_generation_pipeline.py

# Test: Status tracking
pytest tests/test_generation_status.py

# Test: Error handling
pytest tests/test_generation_errors.py
```

**API Endpoints**:
```
POST /api/v1/generations/resume
GET  /api/v1/generations/{id}
DELETE /api/v1/generations/{id}
```

---

### F9: Job Analysis Stage (Stage 1)
**Duration**: 2 days | **Priority**: High | **Dependencies**: F8

**Files to Create/Modify**:
```
📁 New Files:
├── app/domain/services/stages/job_analyzer.py  # Job analysis service (already exists)
├── app/domain/value_objects/job_analysis_result.py # Job analysis result VO
├── app/domain/value_objects/keyword_extraction.py # Keyword extraction VO
├── app/infrastructure/ai/keyword_extractor.py  # Keyword extraction utility
├── app/infrastructure/ai/requirement_parser.py # Requirements parsing utility
├── tests/test_job_analyzer.py                  # Job analyzer tests
└── tests/test_keyword_extraction.py            # Keyword extraction tests

📝 Modify Files:
├── data/prompt_templates/job_analysis.txt      # Refine job analysis prompts
└── app/domain/services/ai_orchestrator.py      # Integrate job analyzer stage
```

**Deliverables**:
- [ ] Job analyzer service
- [ ] Keyword extraction logic
- [ ] Requirements parsing
- [ ] Job analysis result structure

**Acceptance Criteria**:
- ✅ Extract key requirements from job description
- ✅ Identify important keywords and skills
- ✅ Categorize requirements by importance
- ✅ Analysis completes in <10s
- ✅ Consistent results for same input

**Test Plan**:
```bash
# Test: Job analysis
pytest tests/test_job_analyzer.py

# Test: Keyword extraction
pytest tests/test_keyword_extraction.py
```

---

### F10: Profile Compilation Stage (Stage 2)
**Duration**: 2 days | **Priority**: High | **Dependencies**: F9

**Files to Create/Modify**:
```
📁 New Files:
├── app/domain/services/stages/profile_compiler.py # Profile compiler service (already exists)
├── app/domain/value_objects/profile_compilation_result.py # Compilation result VO
├── app/domain/value_objects/content_score.py       # Content scoring VO
├── app/domain/value_objects/relevance_ranking.py   # Relevance ranking VO
├── app/infrastructure/ai/content_scorer.py         # Content scoring algorithms
├── app/infrastructure/ai/relevance_ranker.py       # Relevance ranking utility
├── tests/test_profile_compiler.py                  # Profile compiler tests
└── tests/test_content_scoring.py                   # Content scoring tests

📝 Modify Files:
├── data/prompt_templates/profile_compilation.txt   # Refine compilation prompts
└── app/domain/services/ai_orchestrator.py          # Integrate compiler stage
```

**Deliverables**:
- [ ] Profile compiler service
- [ ] Content scoring algorithms
- [ ] Relevance ranking logic
- [ ] Profile compilation result

**Acceptance Criteria**:
- ✅ Score profile content against job requirements
- ✅ Rank experiences by relevance
- ✅ Identify skill gaps
- ✅ Compilation completes in <10s
- ✅ Scoring is consistent and logical

**Test Plan**:
```bash
# Test: Profile compilation
pytest tests/test_profile_compiler.py

# Test: Content scoring
pytest tests/test_content_scoring.py
```

---

### F11: Document Generation Stage (Stage 3)
**Duration**: 3 days | **Priority**: High | **Dependencies**: F10

**Files to Create/Modify**:
```
📁 New Files:
├── app/domain/services/stages/document_generator.py # Document generator (already exists)
├── app/domain/value_objects/document_template.py   # Document template VO
├── app/domain/value_objects/ats_optimization.py    # ATS optimization VO
├── app/infrastructure/templates/                   # Template system
│   ├── __init__.py                                 # Template package
│   ├── template_manager.py                         # Template management
│   ├── modern_template.py                          # Modern template
│   ├── classic_template.py                         # Classic template
│   ├── ats_template.py                             # ATS-optimized template
│   └── creative_template.py                        # Creative template
├── app/infrastructure/ai/content_generator.py      # Content generation utility
├── app/infrastructure/ai/ats_optimizer.py          # ATS optimization utility
├── tests/test_document_generator.py                # Document generator tests
├── tests/test_templates.py                         # Template tests
└── tests/test_ats_optimization.py                  # ATS optimization tests

📝 Modify Files:
├── data/prompt_templates/document_generation.txt   # Refine generation prompts
└── app/domain/services/ai_orchestrator.py          # Integrate generator stage
```

**Deliverables**:
- [ ] Document generator service
- [ ] Resume template system
- [ ] Content generation logic
- [ ] ATS optimization

**Acceptance Criteria**:
- ✅ Generate tailored resume content
- ✅ Apply selected template format
- ✅ Optimize for ATS scanning
- ✅ Generation completes in <20s
- ✅ Content is coherent and professional

**Test Plan**:
```bash
# Test: Document generation
pytest tests/test_document_generator.py

# Test: Template application
pytest tests/test_templates.py

# Test: ATS optimization
pytest tests/test_ats_optimization.py
```

---

### F12: Quality Validation Stage (Stage 4)
**Duration**: 2 days | **Priority**: Medium | **Dependencies**: F11

**Files to Create/Modify**:
```
📁 New Files:
├── app/domain/services/stages/quality_validator.py # Quality validator (already exists)
├── app/domain/value_objects/quality_metrics.py     # Quality metrics VO
├── app/domain/value_objects/ats_score.py           # ATS score VO
├── app/domain/value_objects/validation_result.py   # Validation result VO
├── app/infrastructure/ai/ats_scorer.py             # ATS score calculator
├── app/infrastructure/ai/fact_checker.py           # Content fact checker
├── app/infrastructure/ai/consistency_validator.py  # Content consistency checker
├── tests/test_quality_validator.py                 # Quality validator tests
└── tests/test_ats_scoring.py                       # ATS scoring tests

📝 Modify Files:
├── data/prompt_templates/quality_validation.txt    # Refine validation prompts
└── app/domain/services/ai_orchestrator.py          # Integrate validator stage
```

**Deliverables**:
- [ ] Quality validator service
- [ ] ATS score calculation
- [ ] Content fact-checking
- [ ] Quality metrics

**Acceptance Criteria**:
- ✅ Calculate accurate ATS score
- ✅ Detect potential fabrications
- ✅ Verify content consistency
- ✅ Validation completes in <10s
- ✅ Provide actionable feedback

**Test Plan**:
```bash
# Test: Quality validation
pytest tests/test_quality_validator.py

# Test: ATS scoring
pytest tests/test_ats_scoring.py
```

---

### F13: PDF Export Stage (Stage 5)
**Duration**: 3 days | **Priority**: Medium | **Dependencies**: F12

**Files to Create/Modify**:
```
📁 New Files:
├── app/domain/ports/pdf_generator_port.py          # PDF generator interface (already exists)
├── app/infrastructure/adapters/pdf/                # PDF adapter package
│   ├── __init__.py                                 # PDF package init
│   ├── weasyprint_adapter.py                       # WeasyPrint adapter
│   └── reportlab_adapter.py                        # ReportLab adapter (alternative)
├── app/infrastructure/pdf/                         # PDF utilities
│   ├── __init__.py                                 # PDF utils package
│   ├── pdf_formatter.py                            # PDF formatting utility
│   ├── pdf_optimizer.py                            # PDF size optimizer
│   └── ats_compliance_checker.py                   # ATS compliance checker
├── templates/pdf/                                  # PDF template files
│   ├── modern.html                                 # Modern PDF template
│   ├── classic.html                                # Classic PDF template
│   ├── ats_optimized.html                          # ATS-optimized template
│   └── styles/                                     # CSS styles
│       ├── modern.css                              # Modern styles
│       ├── classic.css                             # Classic styles
│       └── ats.css                                 # ATS styles
├── tests/test_pdf_generator.py                     # PDF generator tests
├── tests/test_pdf_quality.py                       # PDF quality tests
└── tests/test_pdf_templates.py                     # PDF template tests

📝 Modify Files:
├── app/domain/services/ai_orchestrator.py          # Integrate PDF export stage
├── app/core/config.py                              # Add PDF config
└── requirements.txt                                # Add PDF dependencies
```

**Deliverables**:
- [ ] PDF generator service
- [ ] Professional formatting
- [ ] Multiple template support
- [ ] PDF optimization

**Acceptance Criteria**:
- ✅ Generate professional PDF documents
- ✅ Support multiple templates
- ✅ PDF size optimized (<2MB)
- ✅ Export completes in <5s
- ✅ PDF readable by ATS systems

**Test Plan**:
```bash
# Test: PDF generation
pytest tests/test_pdf_generator.py

# Test: PDF quality
pytest tests/test_pdf_quality.py

# Test: Template support
pytest tests/test_pdf_templates.py
```

---

## 📄 Document Management Features

### F14: Document Storage & Retrieval
**Duration**: 2 days | **Priority**: Medium | **Dependencies**: F13

**Files to Create/Modify**:
```
📁 New Files:
├── app/domain/entities/document.py                 # Document entity (already exists)
├── app/domain/value_objects/document_metadata.py   # Document metadata VO
├── app/domain/ports/storage_service_port.py        # Storage service interface (already exists)
├── app/application/services/document_service.py    # Document business logic
├── app/application/dtos/document_dtos.py           # Document DTOs
├── app/application/use_cases/document_use_cases.py # Document use cases
├── app/infrastructure/repositories/document_repository.py # Document data access
├── app/infrastructure/adapters/storage/            # Storage adapters
│   ├── __init__.py                                 # Storage package
│   ├── local_storage_adapter.py                    # Local file storage
│   └── cloud_storage_adapter.py                    # Cloud storage (future)
├── app/presentation/api/documents.py               # Document endpoints
├── app/presentation/schemas/document_schemas.py    # Document Pydantic schemas
├── storage/documents/                              # Document storage directory
├── tests/test_document_storage.py                  # Document storage tests
└── tests/test_document_retrieval.py                # Document retrieval tests

📝 Modify Files:
├── app/infrastructure/database/models.py           # Add Document model
├── app/main.py                                     # Register document routes
├── app/core/config.py                              # Add storage config
├── .env                                            # Add storage paths
└── alembic/versions/006_document_tables.py         # Document migration
```

**Deliverables**:
- [ ] Document entity with metadata
- [ ] Document storage system
- [ ] Document listing and search
- [ ] Download functionality

**Acceptance Criteria**:
- ✅ Store generated documents with metadata
- ✅ List documents with filtering
- ✅ Download documents as PDF
- ✅ Document search works
- ✅ Proper file cleanup

**Test Plan**:
```bash
# Test: Document storage
pytest tests/test_document_storage.py

# Test: Document retrieval
pytest tests/test_document_retrieval.py
```

**API Endpoints**:
```
GET    /api/v1/documents
GET    /api/v1/documents/{id}
GET    /api/v1/documents/{id}/download
DELETE /api/v1/documents/{id}
```

---

### F15: Document Sharing
**Duration**: 2 days | **Priority**: Low | **Dependencies**: F14

**Files to Create/Modify**:
```
📁 New Files:
├── app/domain/entities/share_link.py               # ShareLink entity
├── app/domain/value_objects/share_settings.py     # Share settings VO
├── app/application/services/share_service.py       # Share business logic
├── app/application/dtos/share_dtos.py              # Share DTOs
├── app/application/use_cases/share_use_cases.py    # Share use cases
├── app/infrastructure/repositories/share_repository.py # Share data access
├── app/presentation/api/document_sharing.py        # Document sharing endpoints
├── app/presentation/api/public_share.py            # Public share endpoints
├── app/presentation/schemas/share_schemas.py       # Share Pydantic schemas
├── app/infrastructure/security/link_generator.py   # Secure link generation
├── app/infrastructure/analytics/share_tracker.py   # Share analytics
├── tests/test_document_sharing.py                  # Document sharing tests
└── tests/test_share_security.py                    # Share security tests

📝 Modify Files:
├── app/infrastructure/database/models.py           # Add ShareLink model
├── app/main.py                                     # Register sharing routes
├── app/core/config.py                              # Add sharing config
└── alembic/versions/007_share_tables.py            # Share migration
```

**Deliverables**:
- [ ] Temporary share link generation
- [ ] Access control for shared documents
- [ ] Download limits and expiration
- [ ] Share analytics

**Acceptance Criteria**:
- ✅ Generate secure temporary links
- ✅ Control access with passwords/limits
- ✅ Links expire automatically
- ✅ Track share analytics
- ✅ Secure link generation

**Test Plan**:
```bash
# Test: Document sharing
pytest tests/test_document_sharing.py

# Test: Share security
pytest tests/test_share_security.py
```

**API Endpoints**:
```
POST /api/v1/documents/{id}/share
GET  /shared/{share_id}
```

---

## 🔌 Integration Features

### F16: Real LLM Integration (OpenAI)
**Duration**: 3 days | **Priority**: High | **Dependencies**: F8

**Files to Create/Modify**:
```
📁 New Files:
├── app/infrastructure/adapters/llm/openai_adapter.py # OpenAI API adapter
├── app/infrastructure/adapters/llm/groq_adapter.py  # Groq adapter (already exists)
├── app/infrastructure/ai/cost_optimizer.py          # Cost optimization (already exists)
├── app/infrastructure/ai/universal_llm_service.py   # Universal LLM service (already exists)
├── app/infrastructure/core/circuit_breaker.py       # Circuit breaker (already exists)
├── app/infrastructure/core/fallback_manager.py      # Fallback manager (already exists)
├── app/infrastructure/monitoring/cost_tracker.py    # Cost tracking utility
├── app/infrastructure/monitoring/usage_metrics.py   # Usage metrics collector
├── tests/test_openai_integration.py                 # OpenAI integration tests
├── tests/test_cost_tracking.py                      # Cost tracking tests
└── tests/test_rate_limiting.py                      # Rate limiting tests

📝 Modify Files:
├── app/core/config.py                               # Add OpenAI config
├── app/core/service_factory.py                      # Register OpenAI adapter
├── .env                                             # Add OpenAI API keys
├── requirements.txt                                 # Add openai dependency
└── data/prompt_templates/*.txt                      # Optimize for OpenAI
```

**Deliverables**:
- [ ] OpenAI API integration
- [ ] Real prompt engineering
- [ ] Error handling for API failures
- [ ] Cost tracking and limits

**Acceptance Criteria**:
- ✅ Successfully call OpenAI API
- ✅ Handle API rate limits gracefully
- ✅ Track token usage and costs
- ✅ Fallback to mock on failures
- ✅ Production-quality prompts

**Test Plan**:
```bash
# Test: OpenAI integration
pytest tests/test_openai_integration.py

# Test: Cost tracking
pytest tests/test_cost_tracking.py

# Test: Rate limiting
pytest tests/test_rate_limiting.py
```

---

### F17: Caching System
**Duration**: 2 days | **Priority**: Medium | **Dependencies**: F5

**Files to Create/Modify**:
```
📁 New Files:
├── app/domain/ports/cache_service_port.py          # Cache service interface (already exists)
├── app/infrastructure/adapters/cache/             # Cache adapters
│   ├── __init__.py                                # Cache package
│   ├── redis_adapter.py                           # Redis cache adapter
│   └── memory_adapter.py                          # In-memory cache (fallback)
├── app/infrastructure/cache/                      # Cache utilities
│   ├── __init__.py                                # Cache utils package
│   ├── cache_keys.py                              # Cache key management
│   ├── cache_serializer.py                       # Cache serialization
│   └── cache_invalidator.py                      # Cache invalidation logic
├── app/application/decorators/cache_decorator.py  # Caching decorator
├── tests/test_caching.py                          # Caching functionality tests
└── tests/test_cache_performance.py                # Cache performance tests

📝 Modify Files:
├── app/core/config.py                             # Add Redis configuration
├── app/core/service_factory.py                    # Register cache service
├── app/application/services/job_service.py        # Add caching to job search
├── app/application/services/generation_service.py # Add caching to generation
├── .env                                           # Add Redis URL
└── requirements.txt                               # Add redis dependency
```

**Deliverables**:
- [ ] Redis cache integration
- [ ] Job search result caching
- [ ] Generation result caching
- [ ] Cache invalidation strategy

**Acceptance Criteria**:
- ✅ Cache job search results (TTL: 1 hour)
- ✅ Cache generation results (TTL: 24 hours)
- ✅ Automatic cache invalidation
- ✅ Cache hit ratio >80%
- ✅ Graceful degradation without cache

**Test Plan**:
```bash
# Test: Caching functionality
pytest tests/test_caching.py

# Test: Cache performance
pytest tests/test_cache_performance.py
```

---

### F18: Background Task Processing
**Duration**: 2 days | **Priority**: Medium | **Dependencies**: F8

**Files to Create/Modify**:
```
📁 New Files:
├── app/infrastructure/tasks/                       # Task processing
│   ├── __init__.py                                # Tasks package
│   ├── celery_app.py                              # Celery application setup
│   ├── task_decorator.py                          # Task decorator
│   └── task_monitor.py                            # Task monitoring
├── app/application/tasks/                         # Business task definitions
│   ├── __init__.py                                # Business tasks package
│   ├── generation_tasks.py                       # AI generation tasks
│   ├── document_tasks.py                          # Document processing tasks
│   └── cleanup_tasks.py                           # Maintenance tasks
├── app/infrastructure/monitoring/task_metrics.py  # Task metrics collector
├── scripts/start_worker.py                       # Worker startup script
├── tests/test_background_tasks.py                 # Background task tests
└── tests/test_task_reliability.py                 # Task reliability tests

📝 Modify Files:
├── app/core/config.py                             # Add Celery config
├── app/application/services/generation_service.py # Use background tasks
├── app/presentation/api/generation.py             # Async generation endpoints
├── .env                                           # Add Celery broker URL
├── requirements.txt                               # Add celery dependency
└── docker-compose.yml                            # Add Redis/Celery services
```

**Deliverables**:
- [ ] Celery task queue setup
- [ ] Background generation processing
- [ ] Task status tracking
- [ ] Queue monitoring

**Acceptance Criteria**:
- ✅ AI generation runs in background
- ✅ Task status trackable
- ✅ Failed tasks retry automatically
- ✅ Queue scalable across workers
- ✅ Task monitoring dashboard

**Test Plan**:
```bash
# Test: Background tasks
pytest tests/test_background_tasks.py

# Test: Task reliability
pytest tests/test_task_reliability.py
```

---

## 📊 Operations Features

### F19: Monitoring & Health Checks
**Duration**: 2 days | **Priority**: Medium | **Dependencies**: F2

**Files to Create/Modify**:
```
📁 New Files:
├── app/infrastructure/monitoring/                 # Monitoring package
│   ├── __init__.py                               # Monitoring package init
│   ├── health_checker.py                         # Health check service (already exists)
│   ├── metrics_collector.py                      # Metrics collection
│   ├── performance_monitor.py                    # Performance monitoring
│   └── error_tracker.py                          # Error tracking
├── app/presentation/api/health.py                # Health check endpoints
├── app/presentation/api/metrics.py               # Metrics endpoints
├── app/presentation/middleware/metrics.py        # Metrics middleware
├── app/infrastructure/monitoring/prometheus/     # Prometheus integration
│   ├── __init__.py                               # Prometheus package
│   ├── metrics_registry.py                       # Metrics registry
│   └── custom_metrics.py                         # Custom metrics
├── tests/test_health_checks.py                   # Health check tests
└── tests/test_metrics.py                         # Metrics tests

📝 Modify Files:
├── app/main.py                                   # Add monitoring middleware
├── app/core/config.py                            # Add monitoring config
├── requirements.txt                              # Add prometheus_client
└── .env                                          # Add monitoring settings
```

**Deliverables**:
- [ ] Comprehensive health check endpoints
- [ ] Application metrics collection
- [ ] Performance monitoring
- [ ] Error tracking

**Acceptance Criteria**:
- ✅ Health check covers all dependencies
- ✅ Metrics exported in Prometheus format
- ✅ Response time tracking
- ✅ Error rate monitoring
- ✅ Database connection monitoring

**Test Plan**:
```bash
# Test: Health checks
pytest tests/test_health_checks.py

# Test: Metrics collection
pytest tests/test_metrics.py
```

**API Endpoints**:
```
GET /health
GET /metrics
GET /health/detailed
```

---

### F20: API Rate Limiting
**Duration**: 1 day | **Priority**: Medium | **Dependencies**: F3

**Files to Create/Modify**:
```
📁 New Files:
├── app/presentation/middleware/rate_limiting.py   # Rate limiting middleware
├── app/infrastructure/rate_limiting/             # Rate limiting utilities
│   ├── __init__.py                               # Rate limiting package
│   ├── rate_limiter.py                           # Rate limiter implementation
│   ├── sliding_window.py                         # Sliding window algorithm
│   └── storage_backend.py                        # Rate limit storage
├── tests/test_rate_limiting.py                   # Rate limiting tests
└── tests/test_rate_limit_headers.py              # Rate limit header tests

📝 Modify Files:
├── app/main.py                                   # Add rate limiting middleware
├── app/core/config.py                            # Add rate limiting config
└── .env                                          # Add rate limiting settings
```

**Deliverables**:
- [ ] Rate limiting middleware
- [ ] Per-user rate limits
- [ ] AI generation rate limits
- [ ] Rate limit headers

**Acceptance Criteria**:
- ✅ General API: 100 req/min per user
- ✅ AI generation: 10 req/hour per user
- ✅ Rate limit headers returned
- ✅ Graceful error responses
- ✅ Different limits for different endpoints

**Test Plan**:
```bash
# Test: Rate limiting
pytest tests/test_rate_limiting.py

# Test: Rate limit headers
pytest tests/test_rate_limit_headers.py
```

---

## 🔒 Security Features

### F21: Input Validation & Sanitization
**Duration**: 2 days | **Priority**: High | **Dependencies**: F4

**Deliverables**:
- [ ] Comprehensive input validation
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] File upload security

**Acceptance Criteria**:
- ✅ All inputs validated with Pydantic
- ✅ SQL injection attempts blocked
- ✅ XSS attacks prevented
- ✅ File uploads secured
- ✅ Error messages don't leak info

**Test Plan**:
```bash
# Test: Input validation
pytest tests/test_input_validation.py

# Test: Security attacks
pytest tests/test_security_attacks.py
```

---

### F22: API Security Headers
**Duration**: 1 day | **Priority**: Medium | **Dependencies**: F1

**Deliverables**:
- [ ] Security headers middleware
- [ ] CORS configuration
- [ ] CSRF protection
- [ ] Content security policy

**Acceptance Criteria**:
- ✅ All security headers present
- ✅ CORS properly configured
- ✅ CSRF tokens validated
- ✅ CSP prevents XSS
- ✅ Security headers score >A

**Test Plan**:
```bash
# Test: Security headers
pytest tests/test_security_headers.py

# Test: CORS functionality
pytest tests/test_cors.py
```

---

## 📈 Performance Features

### F23: Database Optimization
**Duration**: 2 days | **Priority**: Medium | **Dependencies**: F2

**Deliverables**:
- [ ] Database indexing strategy
- [ ] Query optimization
- [ ] Connection pooling
- [ ] Database monitoring

**Acceptance Criteria**:
- ✅ All critical queries have indexes
- ✅ Query response time <100ms (p95)
- ✅ Connection pool prevents exhaustion
- ✅ Slow queries logged
- ✅ Database metrics collected

**Test Plan**:
```bash
# Test: Query performance
pytest tests/test_query_performance.py

# Test: Database load
pytest tests/test_database_load.py
```

---

### F24: API Performance Optimization
**Duration**: 2 days | **Priority**: Medium | **Dependencies**: F17

**Deliverables**:
- [ ] Response compression
- [ ] API response optimization
- [ ] Lazy loading strategies
- [ ] Performance profiling

**Acceptance Criteria**:
- ✅ API responses compressed (gzip)
- ✅ Response time <3s (p95)
- ✅ Large datasets paginated
- ✅ Unnecessary data excluded
- ✅ Performance bottlenecks identified

**Test Plan**:
```bash
# Test: API performance
pytest tests/test_api_performance.py

# Test: Response optimization
pytest tests/test_response_optimization.py
```

---

## 🧪 Testing & Quality

### F25: Comprehensive Test Suite
**Duration**: 3 days | **Priority**: High | **Dependencies**: All Features

**Deliverables**:
- [ ] Unit test coverage >90%
- [ ] Integration test suite
- [ ] End-to-end API tests
- [ ] Performance test suite

**Acceptance Criteria**:
- ✅ All critical paths covered
- ✅ Edge cases tested
- ✅ Error scenarios tested
- ✅ Performance benchmarks met
- ✅ Tests run in CI/CD

**Test Plan**:
```bash
# Test: Full test suite
pytest --cov=app tests/

# Test: Performance benchmarks
pytest tests/performance/
```

---

### F26: Load Testing
**Duration**: 2 days | **Priority**: Medium | **Dependencies**: F25

**Deliverables**:
- [ ] Load testing framework
- [ ] Stress testing scenarios
- [ ] Performance benchmarks
- [ ] Capacity planning

**Acceptance Criteria**:
- ✅ Handle 100 concurrent users
- ✅ AI generation: 10 req/hour sustained
- ✅ API: 1000 req/min sustained
- ✅ Response times under load
- ✅ Resource usage optimized

**Test Plan**:
```bash
# Test: Load testing
locust -f tests/load/locustfile.py

# Test: Stress testing
pytest tests/stress/
```

---

## 📋 Implementation Timeline

### Sprint 1 (Week 1): Foundation
- **F1**: Environment & Basic Setup (Day 1)
- **F2**: Database Foundation (Day 2)
- **F3**: Authentication System (Days 3-4)
- **F19**: Monitoring & Health Checks (Day 5)

### Sprint 2 (Week 2): Core Features
- **F4**: Profile Management (Days 1-3)
- **F5**: Static Job Management (Days 4-5)

### Sprint 3 (Week 3): Job Features
- **F6**: Saved Jobs Feature (Days 1-2)
- **F7**: Mock AI Service Foundation (Days 3-4)
- **F21**: Input Validation & Sanitization (Day 5)

### Sprint 4 (Week 4): AI Pipeline Foundation
- **F8**: Generation Pipeline Foundation (Days 1-3)
- **F9**: Job Analysis Stage (Days 4-5)

### Sprint 5 (Week 5): AI Pipeline Implementation
- **F10**: Profile Compilation Stage (Days 1-2)
- **F11**: Document Generation Stage (Days 3-5)

### Sprint 6 (Week 6): AI Pipeline Completion
- **F12**: Quality Validation Stage (Days 1-2)
- **F13**: PDF Export Stage (Days 3-5)

### Sprint 7 (Week 7): Document Management
- **F14**: Document Storage & Retrieval (Days 1-2)
- **F16**: Real LLM Integration (Days 3-5)

### Sprint 8 (Week 8): Performance & Integration
- **F17**: Caching System (Days 1-2)
- **F18**: Background Task Processing (Days 3-4)
- **F23**: Database Optimization (Day 5)

### Sprint 9 (Week 9): Security & Performance
- **F20**: API Rate Limiting (Day 1)
- **F22**: API Security Headers (Day 2)
- **F24**: API Performance Optimization (Days 3-4)
- **F15**: Document Sharing (Day 5)

### Sprint 10 (Week 10): Testing & Quality
- **F25**: Comprehensive Test Suite (Days 1-3)
- **F26**: Load Testing (Days 4-5)

---

## 🎯 Success Metrics

### Performance Targets
- **Resume Generation**: <30s (p50), <60s (p95)
- **Job Search**: <3s response time
- **PDF Generation**: <5s processing time
- **API Throughput**: 100 req/min per user
- **AI Generation Rate**: 10/hour per user

### Quality Targets
- **Test Coverage**: >90% unit tests, >80% integration
- **ATS Score**: >85% average
- **API Uptime**: >99.5%
- **Error Rate**: <1%
- **Security Score**: A+ rating

### Business Targets
- **User Satisfaction**: >4.0/5.0
- **Generation Success Rate**: >95%
- **Response Time SLA**: 95% under target
- **Cost per Generation**: <$0.50
- **System Scalability**: 1000+ concurrent users

---

## 🔧 Development Guidelines

### Feature Development Process
1. **Feature Planning**: Define acceptance criteria and test plan
2. **Test-First Development**: Write tests before implementation
3. **Incremental Implementation**: Small commits, frequent testing
4. **Code Review**: All code reviewed before merge
5. **Feature Testing**: Comprehensive testing before marking complete
6. **Documentation**: Update API docs and README

### Quality Standards
- **Code Coverage**: >90% for new features
- **Performance**: All endpoints <3s response time
- **Security**: No critical vulnerabilities
- **Documentation**: All public APIs documented
- **Testing**: All features have automated tests

### Deployment Strategy
- **Feature Flags**: Enable/disable features without deployment
- **Blue-Green Deployment**: Zero-downtime deployments
- **Database Migrations**: Backward-compatible migrations
- **Monitoring**: Real-time monitoring and alerting
- **Rollback Plan**: Quick rollback capability

---

## 🎯 Next Steps

1. **Choose Feature to Implement**: Start with F1 (Environment & Basic Setup)
2. **Set Up Development Environment**: Follow F1 acceptance criteria
3. **Implement Feature**: Follow test-first development
4. **Test Thoroughly**: Meet all acceptance criteria
5. **Document Progress**: Update this plan with completion status
6. **Move to Next Feature**: Continue sequentially or pick independent feature

**Ready to start? Begin with F1: Environment & Basic Setup!**

---

## 📂 Complete File Structure Summary

### Core Application Structure
```
backend/
├── .env                                    # Environment configuration
├── .env.example                            # Environment template
├── requirements.txt                        # Python dependencies
├── alembic.ini                             # Database migration config
├── docker-compose.yml                      # Development containers
│
├── app/                                    # Main application package
│   ├── __init__.py
│   ├── main.py                             # FastAPI entry point
│   │
│   ├── core/                               # Core utilities
│   │   ├── __init__.py
│   │   ├── config.py                       # Configuration management
│   │   ├── exceptions.py                   # Custom exceptions
│   │   ├── logging.py                      # Logging configuration
│   │   ├── security.py                     # JWT & password utilities
│   │   └── service_factory.py              # Service factory pattern
│   │
│   ├── domain/                             # Domain layer (business logic)
│   │   ├── entities/                       # Business entities
│   │   │   ├── user.py                     # User entity
│   │   │   ├── profile.py                  # Profile entity
│   │   │   ├── job.py                      # Job entity
│   │   │   ├── saved_job.py                # SavedJob entity
│   │   │   ├── generation.py               # Generation entity
│   │   │   ├── document.py                 # Document entity
│   │   │   └── share_link.py               # ShareLink entity
│   │   │
│   │   ├── value_objects/                  # Value objects
│   │   │   ├── personal_info.py            # Personal information
│   │   │   ├── experience.py               # Work experience
│   │   │   ├── education.py                # Education information
│   │   │   ├── skills.py                   # Skills and certifications
│   │   │   ├── project.py                  # Project information
│   │   │   ├── salary_range.py             # Salary range
│   │   │   ├── application_status.py       # Application status enum
│   │   │   ├── job_analysis_result.py      # Job analysis results
│   │   │   ├── profile_compilation_result.py # Profile compilation results
│   │   │   ├── document_template.py        # Document templates
│   │   │   ├── ats_optimization.py         # ATS optimization
│   │   │   ├── quality_metrics.py          # Quality metrics
│   │   │   ├── ats_score.py                # ATS scoring
│   │   │   ├── validation_result.py        # Validation results
│   │   │   ├── document_metadata.py        # Document metadata
│   │   │   ├── share_settings.py           # Share settings
│   │   │   ├── keyword_extraction.py       # Keyword extraction
│   │   │   ├── content_score.py            # Content scoring
│   │   │   └── relevance_ranking.py        # Relevance ranking
│   │   │
│   │   ├── ports/                          # Interface abstractions
│   │   │   ├── llm_service_port.py         # LLM service interface
│   │   │   ├── pdf_generator_port.py       # PDF generator interface
│   │   │   ├── cache_service_port.py       # Cache service interface
│   │   │   ├── storage_service_port.py     # Storage service interface
│   │   │   ├── job_search_service_port.py  # Job search interface
│   │   │   └── monitoring_service_port.py  # Monitoring interface
│   │   │
│   │   └── services/                       # Domain services
│   │       ├── ai_orchestrator.py          # AI pipeline orchestrator
│   │       ├── pipeline_common.py          # Pipeline utilities
│   │       └── stages/                     # AI pipeline stages
│   │           ├── job_analyzer.py         # Job analysis stage
│   │           ├── profile_compiler.py     # Profile compilation stage
│   │           ├── document_generator.py   # Document generation stage
│   │           └── quality_validator.py    # Quality validation stage
│   │
│   ├── application/                        # Application layer (use cases)
│   │   ├── services/                       # Application services
│   │   │   ├── auth_service.py             # Authentication service
│   │   │   ├── profile_service.py          # Profile service
│   │   │   ├── job_service.py              # Job service
│   │   │   ├── saved_job_service.py        # Saved job service
│   │   │   ├── generation_service.py       # Generation service
│   │   │   ├── document_service.py         # Document service
│   │   │   └── share_service.py            # Share service
│   │   │
│   │   ├── use_cases/                      # Business use cases
│   │   │   ├── profile_use_cases.py        # Profile use cases
│   │   │   ├── job_use_cases.py            # Job use cases
│   │   │   ├── saved_job_use_cases.py      # Saved job use cases
│   │   │   ├── generation_use_cases.py     # Generation use cases
│   │   │   ├── document_use_cases.py       # Document use cases
│   │   │   └── share_use_cases.py          # Share use cases
│   │   │
│   │   ├── dtos/                           # Data transfer objects
│   │   │   ├── auth_dtos.py                # Authentication DTOs
│   │   │   ├── profile_dtos.py             # Profile DTOs
│   │   │   ├── job_dtos.py                 # Job DTOs
│   │   │   ├── saved_job_dtos.py           # Saved job DTOs
│   │   │   ├── generation_dtos.py          # Generation DTOs
│   │   │   ├── document_dtos.py            # Document DTOs
│   │   │   └── share_dtos.py               # Share DTOs
│   │   │
│   │   ├── decorators/                     # Application decorators
│   │   │   └── cache_decorator.py          # Caching decorator
│   │   │
│   │   └── tasks/                          # Background tasks
│   │       ├── generation_tasks.py         # AI generation tasks
│   │       ├── document_tasks.py           # Document processing tasks
│   │       └── cleanup_tasks.py            # Maintenance tasks
│   │
│   ├── infrastructure/                     # Infrastructure layer
│   │   ├── database/                       # Database infrastructure
│   │   │   ├── __init__.py
│   │   │   ├── connection.py               # Database connections
│   │   │   ├── models.py                   # SQLAlchemy models
│   │   │   └── repositories.py             # Base repository
│   │   │
│   │   ├── repositories/                   # Data repositories
│   │   │   ├── user_repository.py          # User data access
│   │   │   ├── profile_repository.py       # Profile data access
│   │   │   ├── job_repository.py           # Job data access
│   │   │   ├── saved_job_repository.py     # Saved job data access
│   │   │   ├── generation_repository.py    # Generation data access
│   │   │   ├── document_repository.py      # Document data access
│   │   │   └── share_repository.py         # Share data access
│   │   │
│   │   ├── adapters/                       # External service adapters
│   │   │   ├── llm/                        # LLM provider adapters
│   │   │   │   ├── mock_adapter.py         # Mock LLM for testing
│   │   │   │   ├── openai_adapter.py       # OpenAI API adapter
│   │   │   │   └── groq_adapter.py         # Groq API adapter
│   │   │   │
│   │   │   ├── cache/                      # Cache adapters
│   │   │   │   ├── redis_adapter.py        # Redis cache
│   │   │   │   └── memory_adapter.py       # In-memory cache
│   │   │   │
│   │   │   ├── storage/                    # Storage adapters
│   │   │   │   ├── local_storage_adapter.py # Local file storage
│   │   │   │   └── cloud_storage_adapter.py # Cloud storage
│   │   │   │
│   │   │   └── pdf/                        # PDF generation adapters
│   │   │       ├── weasyprint_adapter.py   # WeasyPrint adapter
│   │   │       └── reportlab_adapter.py    # ReportLab adapter
│   │   │
│   │   ├── ai/                             # AI infrastructure
│   │   │   ├── prompt_manager.py           # Prompt template management
│   │   │   ├── token_manager.py            # Token usage tracking
│   │   │   ├── cost_optimizer.py           # Cost optimization
│   │   │   ├── universal_llm_service.py    # Universal LLM service
│   │   │   ├── keyword_extractor.py        # Keyword extraction
│   │   │   ├── requirement_parser.py       # Requirements parsing
│   │   │   ├── content_scorer.py           # Content scoring
│   │   │   ├── relevance_ranker.py         # Relevance ranking
│   │   │   ├── content_generator.py        # Content generation
│   │   │   ├── ats_optimizer.py            # ATS optimization
│   │   │   ├── ats_scorer.py               # ATS scoring
│   │   │   ├── fact_checker.py             # Fact checking
│   │   │   └── consistency_validator.py    # Consistency validation
│   │   │
│   │   ├── templates/                      # Template system
│   │   │   ├── template_manager.py         # Template management
│   │   │   ├── modern_template.py          # Modern template
│   │   │   ├── classic_template.py         # Classic template
│   │   │   ├── ats_template.py             # ATS template
│   │   │   └── creative_template.py        # Creative template
│   │   │
│   │   ├── pdf/                            # PDF utilities
│   │   │   ├── pdf_formatter.py            # PDF formatting
│   │   │   ├── pdf_optimizer.py            # PDF optimization
│   │   │   └── ats_compliance_checker.py   # ATS compliance
│   │   │
│   │   ├── cache/                          # Cache utilities
│   │   │   ├── cache_keys.py               # Cache key management
│   │   │   ├── cache_serializer.py         # Cache serialization
│   │   │   └── cache_invalidator.py        # Cache invalidation
│   │   │
│   │   ├── security/                       # Security utilities
│   │   │   └── link_generator.py           # Secure link generation
│   │   │
│   │   ├── analytics/                      # Analytics utilities
│   │   │   └── share_tracker.py            # Share analytics
│   │   │
│   │   ├── rate_limiting/                  # Rate limiting
│   │   │   ├── rate_limiter.py             # Rate limiter
│   │   │   ├── sliding_window.py           # Sliding window
│   │   │   └── storage_backend.py          # Rate limit storage
│   │   │
│   │   ├── monitoring/                     # Monitoring infrastructure
│   │   │   ├── health_checker.py           # Health checking
│   │   │   ├── metrics_collector.py        # Metrics collection
│   │   │   ├── performance_monitor.py      # Performance monitoring
│   │   │   ├── error_tracker.py            # Error tracking
│   │   │   ├── cost_tracker.py             # Cost tracking
│   │   │   ├── usage_metrics.py            # Usage metrics
│   │   │   ├── task_metrics.py             # Task metrics
│   │   │   └── prometheus/                 # Prometheus integration
│   │   │       ├── metrics_registry.py     # Metrics registry
│   │   │       └── custom_metrics.py       # Custom metrics
│   │   │
│   │   ├── tasks/                          # Task infrastructure
│   │   │   ├── celery_app.py               # Celery setup
│   │   │   ├── task_decorator.py           # Task decorator
│   │   │   └── task_monitor.py             # Task monitoring
│   │   │
│   │   └── core/                           # Core infrastructure
│   │       ├── circuit_breaker.py          # Circuit breaker
│   │       ├── fallback_manager.py         # Fallback management
│   │       ├── health_checker.py           # Health checking
│   │       └── service_factory.py          # Service factory
│   │
│   └── presentation/                       # Presentation layer (HTTP)
│       ├── api/                            # API endpoints
│       │   ├── __init__.py
│       │   ├── auth.py                     # Authentication endpoints
│       │   ├── profiles.py                 # Profile endpoints
│       │   ├── jobs.py                     # Job endpoints
│       │   ├── saved_jobs.py               # Saved job endpoints
│       │   ├── generation.py               # Generation endpoints
│       │   ├── documents.py                # Document endpoints
│       │   ├── document_sharing.py         # Document sharing endpoints
│       │   ├── public_share.py             # Public share endpoints
│       │   ├── health.py                   # Health endpoints
│       │   └── metrics.py                  # Metrics endpoints
│       │
│       ├── schemas/                        # Pydantic schemas
│       │   ├── profile_schemas.py          # Profile validation schemas
│       │   ├── job_schemas.py              # Job validation schemas
│       │   ├── saved_job_schemas.py        # Saved job schemas
│       │   ├── generation_schemas.py       # Generation schemas
│       │   ├── document_schemas.py         # Document schemas
│       │   └── share_schemas.py            # Share schemas
│       │
│       └── middleware/                     # HTTP middleware
│           ├── auth.py                     # JWT authentication middleware
│           ├── rate_limiting.py            # Rate limiting middleware
│           └── metrics.py                  # Metrics collection middleware
│
├── alembic/                                # Database migrations
│   ├── versions/                           # Migration files
│   │   ├── 001_initial_schema.py           # Initial database schema
│   │   ├── 002_profile_tables.py           # Profile tables
│   │   ├── 003_job_tables.py               # Job tables
│   │   ├── 004_saved_jobs_table.py         # Saved jobs table
│   │   ├── 005_generation_tables.py        # Generation tables
│   │   ├── 006_document_tables.py          # Document tables
│   │   └── 007_share_tables.py             # Share link tables
│   └── env.py                              # Alembic environment
│
├── data/                                   # Static data and templates
│   ├── static_jobs.json                    # Static job data (100+ jobs)
│   └── prompt_templates/                   # AI prompt templates
│       ├── job_analysis.txt                # Job analysis prompts
│       ├── profile_compilation.txt         # Profile compilation prompts
│       ├── document_generation.txt         # Document generation prompts
│       ├── quality_validation.txt          # Quality validation prompts
│       └── cover_letter.txt                # Cover letter prompts
│
├── templates/                              # PDF templates
│   └── pdf/                                # PDF template files
│       ├── modern.html                     # Modern PDF template
│       ├── classic.html                    # Classic PDF template
│       ├── ats_optimized.html              # ATS-optimized template
│       └── styles/                         # CSS styles
│           ├── modern.css                  # Modern styles
│           ├── classic.css                 # Classic styles
│           └── ats.css                     # ATS styles
│
├── storage/                                # Local file storage
│   └── documents/                          # Generated document storage
│
├── scripts/                                # Utility scripts
│   ├── seed_jobs.py                        # Job data seeding
│   └── start_worker.py                     # Celery worker startup
│
└── tests/                                  # Test suite
    ├── conftest.py                         # Test configuration
    ├── test_environment.py                 # Environment tests
    ├── test_database_connection.py         # Database connection tests
    ├── test_models.py                      # Model tests
    ├── test_auth.py                        # Authentication tests
    ├── test_auth_protection.py             # Auth protection tests
    ├── test_profile_crud.py                # Profile CRUD tests
    ├── test_profile_validation.py          # Profile validation tests
    ├── test_profile_history.py             # Profile history tests
    ├── test_job_search.py                  # Job search tests
    ├── test_job_filters.py                 # Job filtering tests
    ├── test_job_performance.py             # Job search performance tests
    ├── test_saved_jobs.py                  # Saved jobs tests
    ├── test_job_status.py                  # Job status tests
    ├── test_mock_ai_service.py             # Mock AI service tests
    ├── test_prompt_templates.py            # Prompt template tests
    ├── test_generation_pipeline.py         # Generation pipeline tests
    ├── test_generation_status.py           # Generation status tests
    ├── test_generation_errors.py           # Generation error tests
    ├── test_job_analyzer.py                # Job analyzer tests
    ├── test_keyword_extraction.py          # Keyword extraction tests
    ├── test_profile_compiler.py            # Profile compiler tests
    ├── test_content_scoring.py             # Content scoring tests
    ├── test_document_generator.py          # Document generator tests
    ├── test_templates.py                   # Template tests
    ├── test_ats_optimization.py            # ATS optimization tests
    ├── test_quality_validator.py           # Quality validator tests
    ├── test_ats_scoring.py                 # ATS scoring tests
    ├── test_pdf_generator.py               # PDF generator tests
    ├── test_pdf_quality.py                 # PDF quality tests
    ├── test_pdf_templates.py               # PDF template tests
    ├── test_document_storage.py            # Document storage tests
    ├── test_document_retrieval.py          # Document retrieval tests
    ├── test_document_sharing.py            # Document sharing tests
    ├── test_share_security.py              # Share security tests
    ├── test_openai_integration.py          # OpenAI integration tests
    ├── test_cost_tracking.py               # Cost tracking tests
    ├── test_caching.py                     # Caching tests
    ├── test_cache_performance.py           # Cache performance tests
    ├── test_background_tasks.py            # Background task tests
    ├── test_task_reliability.py            # Task reliability tests
    ├── test_health_checks.py               # Health check tests
    ├── test_metrics.py                     # Metrics tests
    ├── test_rate_limiting.py               # Rate limiting tests
    ├── test_rate_limit_headers.py          # Rate limit header tests
    ├── test_input_validation.py            # Input validation tests
    ├── test_security_attacks.py            # Security attack tests
    ├── test_security_headers.py            # Security header tests
    ├── test_cors.py                        # CORS tests
    ├── test_query_performance.py           # Query performance tests
    ├── test_database_load.py               # Database load tests
    ├── test_api_performance.py             # API performance tests
    ├── test_response_optimization.py       # Response optimization tests
    ├── performance/                        # Performance test suite
    ├── load/                               # Load testing
    │   └── locustfile.py                   # Locust load testing
    └── stress/                             # Stress testing
```

### Key Dependencies by Feature
```
F1  → Basic FastAPI app, environment setup
F2  → SQLAlchemy, Alembic, database models
F3  → JWT authentication, password hashing
F4  → Profile management (depends on F3)
F5  → Job management (depends on F3)
F6  → Saved jobs (depends on F4, F5)
F7  → Mock AI service foundation
F8  → Generation pipeline (depends on F7)
F9  → Job analyzer (depends on F8)
F10 → Profile compiler (depends on F9)
F11 → Document generator (depends on F10)
F12 → Quality validator (depends on F11)
F13 → PDF export (depends on F12)
F14 → Document storage (depends on F13)
F15 → Document sharing (depends on F14)
F16 → OpenAI integration (depends on F8)
F17 → Caching system (depends on F5)
F18 → Background tasks (depends on F8)
F19 → Monitoring (depends on F2)
F20 → Rate limiting (depends on F3)
F21 → Input validation (depends on F4)
F22 → Security headers (depends on F1)
F23 → Database optimization (depends on F2)
F24 → API optimization (depends on F17)
F25 → Comprehensive testing (depends on all)
F26 → Load testing (depends on F25)
```

This structure ensures each feature is:
- ✅ **Self-contained** with clear file boundaries
- ✅ **Testable** with dedicated test files
- ✅ **Independent** with minimal dependencies
- ✅ **Deliverable** with measurable outcomes
- ✅ **Scalable** following clean architecture principles

---

# 🎯 REVISED IMPLEMENTATION TIMELINE & PRIORITIES

## ✅ FOUNDATION COMPLETE (F1-F5) 
**Status**: All foundation features implemented and tested

### What's Already Built:
1. **Master Resume** ✅ Complete in F4 - Full profile CRUD API available
2. **Job Discovery** ✅ Complete in F5 - Static job data with search
3. **Authentication** ✅ Complete in F3 - JWT tokens and user management
4. **Database Layer** ✅ Complete in F2 - SQLAlchemy async with migrations
5. **API Foundation** ✅ Complete in F1 - FastAPI with middleware

## 🚀 NEW PRIORITY IMPLEMENTATION ORDER

### IMMEDIATE (Next 1-2 Weeks):
**F6 → F7 → F8** (User Priority Features)

1. **F6: Custom Job Description** (1 day)
   - User-owned job descriptions for targeted resume generation
   
2. **F7: Mock AI Generation Pipeline** (2 days) 
   - 5-stage mock AI processing with realistic outputs
   - Resume generation using profile + job description
   
3. **F8: Export System** (1 day)
   - Text file export (.txt) as requested
   - Download endpoints and file management

### SUCCESS CRITERIA:
- ✅ Users create custom job descriptions
- ✅ AI pipeline generates tailored resumes (mock)
- ✅ Export resumes as formatted .txt files
- ✅ Complete end-to-end workflow functional

**Total Implementation Time**: ~4 days for MVP functionality
**Foundation Quality**: Excellent (F1-F5 provide solid base)
**Current Progress**: 62% complete, strong foundation established
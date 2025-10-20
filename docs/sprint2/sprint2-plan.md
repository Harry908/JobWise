# Sprint 2 Detailed Plan - Generation & Document Export APIs

**Project:** JobWise - AI-Powered Job Application Assistant  
**Sprint Duration:** Week 11 (October 21-27, 2025)  
**Sprint Goal:** Implement AI-powered resume generation pipeline and document export functionality  
**Time Budget:** 40 hours  
**Deliverable Date:** Monday, October 28, 2025

---

## 🎯 Sprint 2 Objectives

### Primary Goals
1. **Generation API (API-3)**: Implement complete AI-powered resume generation with 5-stage mock pipeline
2. **Document Export API (API-4)**: Build professional PDF export functionality with multiple templates
3. **Integration Testing**: Validate end-to-end flow from Profile → Job → Generation → Export
4. **Quality Assurance**: Achieve 65%+ test coverage with comprehensive test suite

### Success Criteria
- ✅ Generation API fully functional with all endpoints operational
- ✅ 5-stage mock pipeline completing in <6 seconds total
- ✅ Document Export API producing ATS-compatible PDFs
- ✅ 20+ new tests passing with 65%+ overall coverage
- ✅ End-to-end generation flow validated from profile to PDF
- ✅ Generation history and status tracking working correctly

---

## 📋 Sprint 2 Task Breakdown (40 Hours)

### Phase 1: Generation API Foundation (12 hours)

#### Task 1.1: Generation Domain Models (2 hours)
**Files to Create:**
- `backend/app/domain/generation.py` - Domain models and value objects
- `backend/app/domain/resume_template.py` - Resume template definitions

**Deliverables:**
```python
# Domain Models
- GenerationModel (id, user_id, profile_id, job_id, status, stage, progress)
- GenerationStage (ANALYZING, COMPILING, GENERATING, VALIDATING, EXPORTING)
- GenerationStatus (PENDING, IN_PROGRESS, COMPLETED, FAILED, CANCELLED)
- ResumeContent (sections, formatting, metadata)
- ATSScore (overall_score, keyword_match, format_compliance, recommendations)
- GenerationMetadata (start_time, end_time, duration, template_id)
```

**Value Objects:**
- ResumeSection (title, content, order, visible)
- Keyword (term, frequency, matched_from_job)
- ValidationResult (passed, issues, suggestions)

#### Task 1.2: Generation Repository (2 hours)
**Files to Create:**
- `backend/app/infrastructure/repositories/generation_repository.py`

**Deliverables:**
```python
class GenerationRepository:
    async def create_generation(generation: GenerationModel) -> GenerationModel
    async def get_generation_by_id(id: str) -> Optional[GenerationModel]
    async def get_user_generations(user_id: str, filters) -> List[GenerationModel]
    async def update_generation_status(id: str, status, stage, progress) -> bool
    async def update_generation_result(id: str, content: ResumeContent) -> bool
    async def delete_generation(id: str) -> bool
    async def get_generation_history(user_id: str, limit: int) -> List[GenerationModel]
```

#### Task 1.3: Mock AI Pipeline Services (4 hours)
**Files to Create:**
- `backend/app/application/services/generation_pipeline.py`
- `backend/app/application/services/job_analyzer.py`
- `backend/app/application/services/profile_compiler.py`
- `backend/app/application/services/content_generator.py`
- `backend/app/application/services/quality_validator.py`

**Deliverables:**
```python
# Stage 1: Job Analyzer (1s processing time)
class JobAnalyzerService:
    async def analyze_job(job: JobModel) -> JobAnalysis
    # Extract: required_skills, experience_level, key_responsibilities
    # Keywords: technical_keywords, soft_skills, domain_keywords
    # Priorities: must_have_skills, nice_to_have_skills

# Stage 2: Profile Compiler (1s processing time)
class ProfileCompilerService:
    async def compile_profile(profile: ProfileModel, job_analysis: JobAnalysis) -> ProfileCompilation
    # Score relevance of each experience, education, project
    # Select top-matching experiences (80% match threshold)
    # Prioritize keywords found in job description
    # Calculate match_score (0.0-1.0)

# Stage 3: Content Generator (2s processing time)
class ContentGeneratorService:
    async def generate_resume(profile_compilation: ProfileCompilation, template_id: str) -> ResumeContent
    # Generate tailored bullet points for each experience
    # Optimize keyword density (5-7% target)
    # Format according to template (Professional, Modern, Creative)
    # Generate summary/objective section

# Stage 4: Quality Validator (1s processing time)
class QualityValidatorService:
    async def validate_resume(content: ResumeContent, job_analysis: JobAnalysis) -> ValidationResult
    # ATS compliance check (format, structure, keywords)
    # Calculate ATS score (0.70-0.95 realistic range)
    # Check keyword match percentage
    # Identify missing key requirements
    # Suggest improvements

# Stage 5: Export Preparation (0.5s processing time)
class ExportPreparationService:
    async def prepare_export(content: ResumeContent) -> ExportReadyContent
    # Clean formatting for PDF conversion
    # Validate required sections present
    # Generate document metadata
    # Prepare multiple format options (PDF, DOCX, TXT)
```

**Pipeline Orchestrator:**
```python
class GenerationPipelineService:
    async def start_generation(profile_id: str, job_id: str, user_id: str) -> GenerationModel
    async def execute_pipeline(generation_id: str) -> ResumeContent
    async def update_progress(generation_id: str, stage: str, progress: float)
    async def handle_pipeline_error(generation_id: str, error: Exception)
```

#### Task 1.4: Generation API Endpoints (4 hours)
**Files to Create:**
- `backend/app/presentation/api/v1/generation.py`

**Deliverables:**
```python
# Core Generation Operations
POST   /api/v1/generations/resume          # Start new generation
GET    /api/v1/generations/{id}            # Get generation status & progress
GET    /api/v1/generations/{id}/result     # Get generated resume content
POST   /api/v1/generations/{id}/regenerate # Regenerate with changes
DELETE /api/v1/generations/{id}            # Cancel/delete generation

# Generation Management
GET    /api/v1/generations                 # List user generations (with filters)
POST   /api/v1/generations/{id}/feedback   # Provide improvement feedback
GET    /api/v1/generations/templates       # List available templates

# Generation Analytics
GET    /api/v1/generations/{id}/analytics  # Quality metrics & ATS score
POST   /api/v1/generations/{id}/validate   # Re-run validation

# Request/Response Models
- CreateGenerationRequest (profile_id, job_id, template_id, options)
- GenerationResponse (id, status, stage, progress, estimated_time)
- GenerationResultResponse (content, metadata, ats_score, recommendations)
- GenerationListResponse (generations, total, page, filters_applied)
```

**Features:**
- Real-time progress tracking via WebSocket or polling
- Async background task execution
- Proper error handling and cancellation support
- Generation history with pagination
- Template selection (3 professional templates)

---

### Phase 2: Document Export API (10 hours)

#### Task 2.1: Document Domain Models (2 hours)
**Files to Create:**
- `backend/app/domain/document.py`
- `backend/app/domain/export_format.py`

**Deliverables:**
```python
# Domain Models
- DocumentModel (id, user_id, generation_id, title, content, format, metadata)
- DocumentStatus (DRAFT, READY, EXPORTED, ARCHIVED)
- ExportFormat (PDF, DOCX, TXT, HTML)
- ExportOptions (template, font_size, margins, color_scheme)
- DocumentMetadata (created_at, updated_at, version, file_size)
```

#### Task 2.2: PDF Export Service (4 hours)
**Files to Create:**
- `backend/app/application/services/pdf_export_service.py`
- `backend/app/application/services/document_formatter.py`

**Deliverables:**
```python
class PDFExportService:
    async def export_to_pdf(content: ResumeContent, options: ExportOptions) -> bytes
    async def generate_pdf_from_template(content: ResumeContent, template_id: str) -> bytes
    async def validate_pdf_ats_compliance(pdf_bytes: bytes) -> ATSComplianceReport
    
# Professional Resume Templates (3 templates)
class ResumeTemplates:
    PROFESSIONAL = "professional"  # Traditional ATS-friendly
    MODERN = "modern"              # Clean, contemporary design  
    CREATIVE = "creative"          # Visual, design-focused

# PDF Generation Features:
- ReportLab or WeasyPrint for PDF generation
- Multiple font options (professional fonts)
- Configurable margins and spacing
- ATS-compatible formatting (no tables, images, headers/footers)
- Proper text extraction for ATS parsing
- Metadata embedding (author, title, keywords)
```

#### Task 2.3: Document Repository (2 hours)
**Files to Create:**
- `backend/app/infrastructure/repositories/document_repository.py`

**Deliverables:**
```python
class DocumentRepository:
    async def create_document(document: DocumentModel) -> DocumentModel
    async def get_document_by_id(id: str) -> Optional[DocumentModel]
    async def get_user_documents(user_id: str, filters) -> List[DocumentModel]
    async def update_document(id: str, updates) -> bool
    async def delete_document(id: str) -> bool
    async def store_export_file(document_id: str, file_bytes: bytes, format: str) -> str
    async def retrieve_export_file(document_id: str, format: str) -> bytes
```

#### Task 2.4: Document API Endpoints (2 hours)
**Files to Create:**
- `backend/app/presentation/api/v1/documents.py`

**Deliverables:**
```python
# Document Management
GET    /api/v1/documents                   # List user documents
GET    /api/v1/documents/{id}              # Get document details
DELETE /api/v1/documents/{id}              # Delete document
PUT    /api/v1/documents/{id}              # Update document metadata

# Export Operations
POST   /api/v1/documents/{id}/export       # Export document to format
GET    /api/v1/documents/{id}/download     # Download exported file
GET    /api/v1/documents/export-formats    # List available formats
POST   /api/v1/documents/preview           # Generate preview (no save)

# Request/Response Models
- ExportRequest (format, template, options)
- ExportResponse (document_id, download_url, expires_at)
- DocumentResponse (id, title, status, formats_available, metadata)
- DocumentListResponse (documents, total, pagination)
```

---

### Phase 3: Integration & Testing (12 hours)

#### Task 3.1: Generation API Tests (4 hours)
**Files to Create:**
- `backend/tests/test_generation_api.py`
- `backend/tests/test_generation_pipeline.py`

**Test Coverage:**
```python
# Generation API Tests (15+ tests)
test_create_generation_success()
test_create_generation_invalid_profile()
test_create_generation_invalid_job()
test_get_generation_status()
test_get_generation_result_before_complete()
test_get_generation_result_after_complete()
test_list_user_generations_with_filters()
test_regenerate_with_feedback()
test_cancel_in_progress_generation()
test_delete_generation()
test_generation_progress_tracking()
test_generation_templates_list()
test_generation_analytics()
test_concurrent_generations()
test_generation_error_handling()

# Pipeline Tests (10+ tests)
test_job_analysis_stage()
test_profile_compilation_stage()
test_content_generation_stage()
test_quality_validation_stage()
test_export_preparation_stage()
test_full_pipeline_execution()
test_pipeline_error_recovery()
test_pipeline_cancellation()
test_ats_score_calculation()
test_keyword_matching()
```

#### Task 3.2: Document Export Tests (4 hours)
**Files to Create:**
- `backend/tests/test_document_api.py`
- `backend/tests/test_pdf_export.py`

**Test Coverage:**
```python
# Document API Tests (10+ tests)
test_list_user_documents()
test_get_document_details()
test_update_document_metadata()
test_delete_document()
test_export_to_pdf()
test_export_to_docx()
test_download_exported_file()
test_preview_generation()
test_list_export_formats()
test_document_ownership_validation()

# PDF Export Tests (8+ tests)
test_pdf_generation_professional_template()
test_pdf_generation_modern_template()
test_pdf_generation_creative_template()
test_pdf_ats_compliance_validation()
test_pdf_text_extraction()
test_pdf_metadata_embedding()
test_invalid_export_options()
test_large_content_handling()
```

#### Task 3.3: End-to-End Integration Tests (4 hours)
**Files to Create:**
- `backend/tests/integration/test_generation_flow.py`
- `backend/tests/integration/test_export_flow.py`

**Test Scenarios:**
```python
# Complete Generation Flow (5+ tests)
test_profile_to_generation_to_export_flow()
test_multiple_job_generations_for_same_profile()
test_generation_with_different_templates()
test_regeneration_with_feedback_loop()
test_concurrent_user_generations()

# Error Recovery & Edge Cases (5+ tests)
test_generation_with_incomplete_profile()
test_generation_with_minimal_job_description()
test_export_failure_recovery()
test_database_connection_failure_handling()
test_service_timeout_handling()

# Performance Tests (3+ tests)
test_generation_completion_under_6_seconds()
test_pdf_export_completion_under_2_seconds()
test_concurrent_generation_performance()
```

---

### Phase 4: Documentation & Refinement (6 hours)

#### Task 4.1: API Documentation (2 hours)
**Files to Update:**
- `.context/api/openapi-spec.yaml` - Add Generation & Document endpoints
- `backend/README.md` - Update with new API documentation

**Deliverables:**
- Complete OpenAPI 3.0 specifications for all new endpoints
- Request/response examples with realistic data
- Error response documentation
- Authentication requirements
- Rate limiting specifications

#### Task 4.2: Implementation Documentation (2 hours)
**Files to Create/Update:**
- `docs/sprint2/generation-pipeline-architecture.md`
- `docs/sprint2/pdf-export-implementation.md`
- `backend/FEATURE_IMPLEMENTATION_PLAN_CLEAN.md` - Update status

**Deliverables:**
- Generation pipeline architecture diagrams
- Mock AI pipeline stage specifications
- PDF export template documentation
- ATS compliance validation guidelines
- Performance benchmarks and optimization notes

#### Task 4.3: Testing & Bug Fixes (2 hours)
**Activities:**
- Run full test suite and fix failing tests
- Manual testing of all new endpoints
- Performance profiling and optimization
- Code review and refactoring
- Test coverage analysis (target: 65%+)

---

## 🗓️ Sprint 2 Daily Schedule (40 Hours)

### Day 1 (Monday, Oct 21): Generation Foundation (8 hours)
**Morning (4h):**
- Task 1.1: Generation domain models (2h)
- Task 1.2: Generation repository (2h)

**Afternoon (4h):**
- Task 1.3: Mock AI pipeline services - Job Analyzer & Profile Compiler (4h)

**Deliverable:** Domain models and repository ready, first 2 pipeline stages implemented

---

### Day 2 (Tuesday, Oct 22): Pipeline Completion (8 hours)
**Morning (4h):**
- Task 1.3: Mock AI pipeline services - Content Generator & Quality Validator (4h)

**Afternoon (4h):**
- Task 1.3: Export Preparation & Pipeline Orchestrator (2h)
- Task 1.4: Generation API endpoints - Core operations (2h)

**Deliverable:** Complete 5-stage pipeline, basic generation endpoints working

---

### Day 3 (Wednesday, Oct 23): Generation API & Document Foundation (8 hours)
**Morning (4h):**
- Task 1.4: Generation API endpoints - Management & analytics (2h)
- Task 2.1: Document domain models (2h)

**Afternoon (4h):**
- Task 2.2: PDF export service - Template setup & basic generation (4h)

**Deliverable:** Complete Generation API, document models ready, PDF generation started

---

### Day 4 (Thursday, Oct 24): Document Export API (8 hours)
**Morning (4h):**
- Task 2.2: PDF export service - Multi-template support & ATS validation (2h)
- Task 2.3: Document repository (2h)

**Afternoon (4h):**
- Task 2.4: Document API endpoints - All operations (2h)
- Task 3.1: Start generation API tests (2h)

**Deliverable:** Complete Document Export API, tests started

---

### Day 5 (Friday, Oct 25): Testing & Integration (8 hours)
**Morning (4h):**
- Task 3.1: Generation API tests completion (2h)
- Task 3.2: Document export tests (2h)

**Afternoon (4h):**
- Task 3.2: Document export tests completion (2h)
- Task 3.3: End-to-end integration tests (2h)

**Deliverable:** Comprehensive test suite (25+ new tests), integration validated

---

### Weekend (Oct 26-27): Documentation & Polish (Optional buffer)
**Activities:**
- Task 4.1: API documentation (2h)
- Task 4.2: Implementation documentation (2h)
- Task 4.3: Testing & bug fixes (2h)
- Buffer time for unexpected issues

**Deliverable:** Complete documentation, all tests passing, Sprint 2 ready for review

---

## 📊 Sprint 2 Success Metrics

### Quantitative Metrics
- **Test Coverage**: Increase from 55% to 65%+ (target: 67 total tests passing)
- **API Endpoints**: Add 20+ new endpoints across Generation & Document APIs
- **Pipeline Performance**: <6 seconds for complete generation (5 stages)
- **PDF Export**: <2 seconds per document export
- **Code Quality**: Zero critical bugs, all linting passing

### Qualitative Metrics
- **ATS Compliance**: Generated PDFs pass basic ATS validation
- **Template Quality**: 3 professional resume templates fully functional
- **Error Handling**: Comprehensive error recovery at each pipeline stage
- **User Experience**: Clear progress tracking and status updates
- **Documentation**: Complete API specs and implementation guides

---

## 🎯 Key Technical Decisions

### Generation Pipeline Architecture
**Decision**: Mock pipeline with realistic timing vs. real LLM integration  
**Rationale**: 
- Mock pipeline allows rapid development without API costs
- Realistic timing (total 5.5s) simulates actual LLM response times
- Easy to swap with real LLM services in future sprints
- Predictable behavior simplifies testing and debugging

### PDF Export Library
**Decision**: ReportLab (Python) for server-side PDF generation  
**Rationale**:
- Pure Python, no external dependencies
- Excellent ATS compatibility (text-based, no images)
- Fine-grained control over formatting
- Well-documented and actively maintained
- Alternative: WeasyPrint (HTML/CSS to PDF) for more complex layouts

### Document Storage
**Decision**: Store generated content in database, export on-demand  
**Rationale**:
- Reduces storage costs (PDFs generated when needed)
- Allows template changes without regenerating content
- Easier content versioning and tracking
- Export options can change without content regeneration

### Generation Status Tracking
**Decision**: Database-based polling vs. WebSocket real-time updates  
**Rationale**:
- Polling simpler to implement in Sprint 2
- WebSocket can be added in future sprint for real-time updates
- Database approach works well for 5.5s generation time
- Scalable with proper caching and optimization

---

## 🚨 Risk Assessment & Mitigation

### High Priority Risks

**Risk 1: PDF Generation Complexity**  
*Impact*: Medium | *Probability*: Medium  
*Mitigation*:
- Use proven library (ReportLab) with extensive examples
- Start with simple template, add complexity incrementally
- Allocate buffer time (2h) for PDF troubleshooting
- Have fallback to plain text export if PDF blocks

**Risk 2: Pipeline Timing Accuracy**  
*Impact*: Low | *Probability*: Medium  
*Mitigation*:
- Use `asyncio.sleep()` for mock timing
- Monitor actual processing time in tests
- Add performance benchmarks to catch timing drift
- Document expected vs. actual timings

**Risk 3: Test Coverage Target**  
*Impact*: Medium | *Probability*: Low  
*Mitigation*:
- Write tests alongside implementation (TDD approach)
- Allocate dedicated testing time (12 hours)
- Focus on critical paths first, edge cases second
- Use coverage reports to identify gaps

**Risk 4: Integration Complexity**  
*Impact*: High | *Probability*: Low  
*Mitigation*:
- Test each API independently before integration
- Allocate 4 hours specifically for integration tests
- Use existing Profile & Job APIs as solid foundation
- Comprehensive error handling at each boundary

---

## 🔄 AI Agent Coordination Strategy

### Backend Developer Agent (Primary)
**Tool**: GitHub Copilot + Claude 3.5 Sonnet  
**Responsibilities**:
- Implement Generation & Document APIs
- Build mock AI pipeline services
- Create PDF export functionality
- Write comprehensive tests

**Coordination Points**:
- Daily progress updates in `log/backend-developer-log.md`
- Technical decisions documented in ADRs
- Code reviews with Solutions Architect Agent

### Solutions Architect Agent (Supporting)
**Tool**: ChatGPT-4  
**Responsibilities**:
- Review pipeline architecture design
- Validate API contract specifications
- Provide optimization recommendations
- Review integration testing strategy

**Coordination Points**:
- Architecture review at Phase 1 completion
- API contract validation before implementation
- Integration testing strategy review

### QA Engineer Agent (Supporting)
**Tool**: GitHub Copilot + ChatGPT  
**Responsibilities**:
- Design comprehensive test strategy
- Review test coverage reports
- Validate error handling approaches
- Performance testing recommendations

**Coordination Points**:
- Test strategy review at sprint start
- Daily test coverage monitoring
- Bug triage and prioritization
- Final quality validation

---

## 📦 Sprint 2 Deliverables Checklist

### Code Deliverables
- [ ] Generation domain models and value objects
- [ ] Generation repository with full CRUD operations
- [ ] 5-stage mock AI pipeline services
- [ ] Generation API with 11 endpoints
- [ ] Document domain models
- [ ] PDF export service with 3 templates
- [ ] Document repository
- [ ] Document API with 8 endpoints

### Testing Deliverables
- [ ] Generation API tests (15+ tests)
- [ ] Generation pipeline tests (10+ tests)
- [ ] Document API tests (10+ tests)
- [ ] PDF export tests (8+ tests)
- [ ] Integration tests (10+ tests)
- [ ] Performance benchmarks
- [ ] Test coverage report (65%+ target)

### Documentation Deliverables
- [ ] Updated OpenAPI specification
- [ ] Generation pipeline architecture document
- [ ] PDF export implementation guide
- [ ] API usage examples and tutorials
- [ ] Updated FEATURE_IMPLEMENTATION_PLAN_CLEAN.md
- [ ] Sprint 2 retrospective notes

### Quality Gates
- [ ] All 53+ new tests passing
- [ ] Overall test coverage ≥65%
- [ ] Zero critical or high-priority bugs
- [ ] API documentation complete
- [ ] Performance targets met (<6s generation, <2s export)
- [ ] Code review approved by Solutions Architect Agent

---

## 🎓 Learning Objectives

### Technical Skills
- **Async Pipeline Orchestration**: Build multi-stage async processing pipeline
- **PDF Generation**: Master server-side PDF creation with ATS compliance
- **Domain-Driven Design**: Apply DDD principles to complex generation logic
- **Test Strategy**: Comprehensive testing including unit, integration, performance
- **API Design**: RESTful API best practices for long-running operations

### AI Coordination Skills
- **Multi-Agent Collaboration**: Coordinate Backend, Architect, and QA agents
- **Context Management**: Efficient handoffs between implementation and testing phases
- **Documentation-First**: Use documentation to align agents before coding
- **Iterative Refinement**: Incorporate agent feedback into implementation

---

## 📝 Sprint 2 Definition of Done

A feature is considered "Done" when:
1. ✅ Code implemented following clean architecture principles
2. ✅ Unit tests written and passing (>80% coverage for new code)
3. ✅ Integration tests validating end-to-end flow
4. ✅ API documentation updated in OpenAPI spec
5. ✅ Manual testing completed with no critical bugs
6. ✅ Code reviewed and approved
7. ✅ Performance benchmarks met
8. ✅ Logging and error handling implemented
9. ✅ Implementation notes documented
10. ✅ Sprint log updated with learnings

---

## 🚀 Post-Sprint 2 Roadmap

### Sprint 3 Priorities (Week 12)
- Flutter mobile app foundation setup
- Profile management UI screens
- Job browsing interface
- API client integration layer
- Local storage and caching

### Sprint 4 Priorities (Week 13)
- Generation request UI and progress tracking
- Document viewing and editing interface
- PDF preview and download functionality
- Job search and filtering UI
- State management implementation

### Sprint 5 Priorities (Week 14)
- End-to-end mobile integration testing
- Performance optimization
- Offline mode support
- Error handling and user feedback
- UI/UX polish

---

**Sprint 2 Start Date**: Monday, October 21, 2025  
**Sprint 2 End Date**: Friday, October 25, 2025  
**Review & Documentation**: Weekend, October 26-27, 2025  
**Sprint 2 Demo**: Monday, October 28, 2025

**Prepared by**: Backend Developer Agent + Solutions Architect Agent  
**Last Updated**: October 20, 2025

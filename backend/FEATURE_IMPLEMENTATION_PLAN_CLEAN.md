# JobWise Backend - API-Service Focused Implementation Plan

## Current Status & API Service Priorities

**FOUNDATION COMPLETE**: F1-F3 + Database Foundation
- [DONE] **F1**: Environment & Basic Setup - FastAPI application running, middleware, health checks
- [DONE] **F2**: Database Foundation - SQLAlchemy async, unified job model, repositories  
- [DONE] **F3**: Authentication System - JWT tokens, user registration/login, middleware protection

**PRIORITY API SERVICES** (User Request - Focus Areas):
1. **Profile API** - Master resume management ([DONE] F4 Complete)
2. **Job Description API** - Custom job descriptions with unified job model
3. **Generation API** - AI-powered resume generation with mock pipeline
4. **Document API** - Document management and export (Later Phase)
5. **Job Search API** - Job discovery and search (Later Phase)

---

## Foundation Layer (COMPLETED)

### [DONE] F1: Environment & Basic Setup
**Status**: COMPLETE | **Test Coverage**: 16/17 passing

**Implementation**:
- FastAPI application with middleware stack (CORS, auth, error handling)
- Environment configuration with `.env` support and validation  
- Health check endpoints with database connectivity monitoring
- Comprehensive logging and error handling infrastructure

### [DONE] F2: Database Foundation  
**Status**: COMPLETE | **Test Coverage**: 13/13 passing

**Implementation**:
- SQLAlchemy 2.0 async with connection pooling and session management
- **Unified Job Model**: Single JobModel supporting all input methods (API, static, user-created)
- Repository pattern with full CRUD operations and async support
- Database health checks and performance monitoring

### [DONE] F3: Authentication System
**Status**: COMPLETE | **Test Coverage**: 13/13 passing (100%)

**Implementation**:
- JWT token management with proper security (bcrypt password hashing)
- User registration/login with comprehensive validation
- JWT middleware protection for all secured endpoints
- Token refresh and user context management

---

## Priority API Services Implementation

### API-1: Profile API (COMPLETE)
**Status**: [DONE] IMPLEMENTED | **Priority**: HIGH | **Dependencies**: F1-F3

**Core Features**:
- Master profile CRUD with comprehensive value objects (Personal Info, Experience, Education, Skills, Projects)
- Profile business logic with validation and ownership verification
- Profile analytics endpoints providing insights and completeness scores
- Async repository pattern with full database integration

**API Contract** (`/api/v1/profiles`):
```yaml
# Core Profile Operations
POST   /api/v1/profiles                    # Create new master profile
GET    /api/v1/profiles/me                 # Get current user's profile 
GET    /api/v1/profiles/{id}               # Get profile by ID
PUT    /api/v1/profiles/{id}               # Update profile
DELETE /api/v1/profiles/{id}               # Delete profile

# Profile Components Management
POST   /api/v1/profiles/{id}/experiences   # Add work experience
PUT    /api/v1/profiles/{id}/experiences/{exp_id}  # Update experience
DELETE /api/v1/profiles/{id}/experiences/{exp_id}  # Remove experience
POST   /api/v1/profiles/{id}/education     # Add education entry
PUT    /api/v1/profiles/{id}/education/{edu_id}    # Update education
DELETE /api/v1/profiles/{id}/education/{edu_id}    # Remove education
POST   /api/v1/profiles/{id}/projects      # Add project
PUT    /api/v1/profiles/{id}/projects/{proj_id}    # Update project
DELETE /api/v1/profiles/{id}/projects/{proj_id}    # Remove project

# Profile Analytics & Insights
GET    /api/v1/profiles/{id}/analytics     # Profile completeness and analytics
GET    /api/v1/profiles/{id}/summary       # Profile summary for generation
```

### API-2: Job Description API (HIGH PRIORITY)
**Status**: [TODO] IN PROGRESS | **Priority**: HIGH | **Dependencies**: F3, Unified Job Model
**Duration**: 1-2 days | **Implementation Target**: Next Sprint

**Core Features**:
- Unified job model supporting all input methods (API, static, user-created)
- Custom job description CRUD with user ownership validation
- Keyword extraction and job analysis for generation pipeline
- Job status management (draft, active, archived) for user-created jobs

**API Contract** (`/api/v1/jobs`):
```yaml
# Unified Job Management (All Sources)
GET    /api/v1/jobs                        # Search all jobs (static + user-created)
GET    /api/v1/jobs/{id}                   # Get job details (any source)
POST   /api/v1/jobs                        # Create user custom job description
PUT    /api/v1/jobs/{id}                   # Update user job (ownership required)
DELETE /api/v1/jobs/{id}                   # Delete user job (ownership required)

# User Job Management
GET    /api/v1/jobs/my-jobs                # List user's custom job descriptions
PUT    /api/v1/jobs/{id}/status            # Change job status (draft/active/archived)
POST   /api/v1/jobs/{id}/analyze           # Extract keywords and analyze job

# Job Templates & Conversion
GET    /api/v1/jobs/template               # Get JSON template for copy-paste conversion
POST   /api/v1/jobs/convert-text           # Convert raw job text to structured JSON
```

**Key Implementation Points**:
- Extend existing unified JobModel with user ownership (`user_id` field)
- Source field distinguishes: `api`, `static`, `user_created`, `scraped`, `imported`
- User-created jobs support status management and full CRUD operations
- JSON template approach for copy-paste job description conversion
- Keyword extraction pipeline for all job types

### API-3: Generation API (HIGH PRIORITY)  
**Status**: [READY] STRUCTURE READY | **Priority**: HIGH | **Dependencies**: API-1, API-2
**Duration**: 2-3 days | **Implementation Target**: Next Sprint

**Core Features**:
- 5-stage mock AI pipeline with realistic timing and responses
- Resume generation using Profile + Job combination
- Generation status tracking and progress updates  
- Mock ATS scoring and quality validation
- Generation history and user management

**API Contract** (`/api/v1/generations`):
```yaml
# Generation Operations
POST   /api/v1/generations/resume          # Start resume generation
GET    /api/v1/generations/{id}            # Get generation status and progress
GET    /api/v1/generations/{id}/result     # Get generated resume content
POST   /api/v1/generations/{id}/regenerate # Regenerate with feedback/changes
DELETE /api/v1/generations/{id}            # Cancel/delete generation

# Generation Management
GET    /api/v1/generations                 # List user's generations with filters
POST   /api/v1/generations/{id}/feedback   # Provide feedback for improvement
GET    /api/v1/generations/templates       # Get available resume templates

# Generation Analytics
GET    /api/v1/generations/{id}/analytics  # Generation quality metrics and ATS score
POST   /api/v1/generations/{id}/validate   # Re-run quality validation
```

**Mock Pipeline Stages**:
1. **Job Analysis** (1s): Parse requirements, extract keywords, identify key skills
2. **Profile Compilation** (1s): Score profile sections against job requirements  
3. **Content Generation** (2s): Generate tailored resume using professional templates
4. **Quality Validation** (1s): ATS compliance check, keyword density, formatting
5. **Export Preparation** (0.5s): Prepare content for document export

---

## Future API Services (Later Implementation)

### API-4: Document API (FUTURE)
**Status**: [READY] STRUCTURE READY | **Priority**: MEDIUM | **Dependencies**: API-3
**Implementation Target**: Phase 2

**API Contract** (`/api/v1/documents`):
```yaml
# Document Management
GET    /api/v1/documents                   # List user documents
GET    /api/v1/documents/{id}              # Get document details
DELETE /api/v1/documents/{id}              # Delete document
PUT    /api/v1/documents/{id}              # Update document metadata

# Export Operations  
POST   /api/v1/documents/{id}/export       # Export document (PDF/TXT)
GET    /api/v1/documents/{id}/download     # Download exported file
GET    /api/v1/documents/export-formats    # Get available export formats
```

### API-5: Job Search API (FUTURE)
**Status**: [BASIC] BASIC IMPLEMENTED | **Priority**: LOW | **Dependencies**: None
**Implementation Target**: Phase 3 (Enhancement)

**Current Implementation**: Static job search working (6/6 tests passing)
**Future Enhancements**: External API integration, advanced filtering, job recommendations

**API Contract** (`/api/v1/job-search`):
```yaml
# Enhanced Job Search (Future)
GET    /api/v1/job-search                  # Advanced job search with ML recommendations
POST   /api/v1/job-search/save             # Save job search criteria
GET    /api/v1/job-search/recommendations  # Personalized job recommendations
POST   /api/v1/job-search/alerts           # Set up job alerts
```

---

## Implementation Roadmap

### **Sprint 1** (Current Focus - API Services Core)
**Duration**: 3-4 days | **Priority**: HIGH

#### Day 1-2: API-2 Job Description API
- [ ] Implement unified job CRUD endpoints with user ownership
- [ ] Add job status management (draft/active/archived)  
- [ ] Create JSON template system for copy-paste conversion
- [ ] Implement keyword extraction pipeline
- [ ] Write comprehensive API tests (target: 8/8 passing)

#### Day 2-3: API-3 Generation API Foundation
- [ ] Implement 5-stage mock AI pipeline with realistic timing
- [ ] Create generation status tracking and progress updates
- [ ] Build professional resume templates (3 formats)
- [ ] Implement mock ATS scoring system (0.7-0.95 range)
- [ ] Add generation history and user management

#### Day 3-4: API Integration & Testing
- [ ] Integrate Profile API -> Job Description API -> Generation API flow
- [ ] End-to-end testing of complete resume generation pipeline
- [ ] Performance optimization and caching implementation
- [ ] API documentation updates and OpenAPI spec completion

### **Sprint 2** (Future Enhancement)  
**Duration**: 2-3 days | **Priority**: MEDIUM

#### Phase 2A: API-4 Document API
- [ ] Document management and versioning system
- [ ] Text export system (.txt format) with professional formatting
- [ ] File storage and download endpoints  
- [ ] Document sharing and access control

#### Phase 2B: API-5 Job Search API Enhancement
- [ ] External job API integration (Indeed, LinkedIn)
- [ ] Advanced search filters and job recommendations
- [ ] Job application tracking and status management
- [ ] Job alert and notification system

---

## Technical Architecture Focus

### API Service Boundaries
```
+-------------+    +-----------------+    +-----------------+
| Profile API |<-->|Job Description  |<-->| Generation API  |
|   (Ready)   |    |API (High Priority)|   | (High Priority) |
+-------------+    +-----------------+    +-----------------+
                                                    |
                                                    v
                   +-------------+    +-----------------+
                   |Document API |<-->|Job Search API   |
                   |  (Future)   |    |   (Future)      |
                   +-------------+    +-----------------+
```

### Database Schema Focus
- **Unified Job Model**: Single entity supporting all job input methods
- **Generation Tracking**: Complete generation lifecycle management
- **User Ownership**: Clear ownership boundaries for user-created content
- **API Consistency**: Table names aligned with API endpoints

### Quality Targets
- **Test Coverage**: >90% for all API endpoints
- **Response Time**: <500ms for CRUD operations, <5s for generation
- **Error Handling**: Comprehensive error responses with proper HTTP status codes
- **Documentation**: Complete OpenAPI 3.0 specification with examples

---

## Implementation Checklist

### [DONE] COMPLETED (Foundation Ready)
- [x] F1: FastAPI Environment & Basic Setup (16/17 tests passing)
- [x] F2: Database Foundation with Unified Job Model (13/13 tests passing)  
- [x] F3: Authentication System with JWT (13/13 tests passing)
- [x] API-1: Profile API Complete (Full CRUD with analytics)

### [NEXT] HIGH PRIORITY (Next Implementation)

#### API-2: Job Description API
- [ ] **JobService Enhancement**: Extend to support user-created jobs with unified model
- [ ] **Job CRUD Endpoints**: POST/GET/PUT/DELETE for user job descriptions
- [ ] **Job Templates**: JSON template system for copy-paste conversion
- [ ] **Keyword Extraction**: Job analysis and keyword parsing pipeline
- [ ] **Status Management**: Draft/active/archived status for user jobs
- [ ] **Ownership Validation**: Ensure users can only modify their own jobs
- [ ] **API Testing**: Comprehensive test suite (target: 8/8 passing)

#### API-3: Generation API  
- [ ] **Mock AI Pipeline**: 5-stage generation with realistic timing (5s total)
- [ ] **Generation Tracking**: Status updates and progress monitoring
- [ ] **Resume Templates**: Professional templates (3 formats minimum)
- [ ] **ATS Scoring**: Mock quality validation (0.7-0.95 score range)  
- [ ] **Generation History**: User generation management and history
- [ ] **Profile Integration**: Use Profile API data for generation
- [ ] **Job Integration**: Use Job Description API data for tailoring
- [ ] **API Testing**: End-to-end generation flow testing

### [LATER] FUTURE PHASES (Lower Priority)

#### API-4: Document API
- [ ] Document storage and metadata management
- [ ] Text export system (.txt format)
- [ ] File download and sharing capabilities
- [ ] Document versioning system

#### API-5: Job Search API Enhancement
- [ ] External API integration (Indeed, LinkedIn)
- [ ] Advanced search and filtering
- [ ] Job recommendations engine
- [ ] Application tracking system

---

## API Dependencies & Integration Flow

### Core Data Flow
```
User -> Profile API -> Job Description API -> Generation API -> Document API
  |         |              |                     |              |
Auth    Master Resume   Custom Jobs      AI Generation    Export/Share
```

### API Integration Requirements
1. **Profile API** provides user profile data for AI generation
2. **Job Description API** provides job requirements for tailored resume generation  
3. **Generation API** combines profile + job data to create tailored resumes
4. **Document API** (future) manages generated documents and exports
5. **Job Search API** (future) provides external job discovery

### Service Communication
- All APIs use consistent error handling and response formats
- JWT authentication required for all user-specific operations
- Async database operations with proper transaction management
- Comprehensive logging and monitoring for all API interactions

---

## Success Metrics

### API Performance Targets
- **Profile API**: <200ms response time for CRUD operations
- **Job Description API**: <300ms response time, supports 100+ user jobs
- **Generation API**: <5s total generation time, 95% success rate
- **Document API**: <1s for exports, <500ms for metadata operations

### Quality Metrics  
- **Test Coverage**: >90% for all API endpoints
- **Error Handling**: <1% unexpected errors, proper HTTP status codes
- **Documentation**: Complete OpenAPI 3.0 spec with examples
- **User Experience**: Clear error messages, consistent response formats

### Business Metrics
- **Generation Success**: 95% of generations complete successfully  
- **User Adoption**: Profile completion rate >80%
- **Performance**: API availability >99.5%
- **Scalability**: Support 100+ concurrent users
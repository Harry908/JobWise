# User Preference System - Implementation Status

**Last Updated**: November 11, 2025  
**Component**: User Writing Style & Layout Preferences
**Sprint**: Sprint 4 (Planned)

---

## Executive Summary

The **User Preference System** allows JobWise to generate resumes and cover letters that match the user's **writing style** and **structural preferences** by analyzing uploaded sample documents.

**Current Status**: 
- ✅ Database schema complete (all 6 tables exist)
- ✅ Domain entities implemented
- ✅ Repository layer partially implemented
- ✅ Service layer (preference extraction) implemented
- ❌ API endpoints **NOT IMPLEMENTED**
- ❌ Mobile UI **NOT IMPLEMENTED**

---

## Architecture Verified

### Database Tables (All Exist ✅)

```sql
-- Verified in jobwise.db (November 11, 2025)

✅ example_resumes               -- Uploaded sample resumes/cover letters
✅ writing_style_configs         -- Extracted writing style preferences  
✅ layout_configs                -- Extracted layout/structure preferences
✅ user_generation_profiles      -- Combined user generation profile
✅ consistency_scores            -- Quality validation tracking
✅ job_type_overrides            -- Job-specific preference adjustments
```

### Domain Entities (Implemented ✅)

**Location**: `backend/app/domain/entities/preferences/`

```
✅ ExampleResume              - example_resume.py
✅ WritingStyleConfig         - writing_style_config.py  
✅ LayoutConfig               - layout_config.py
✅ UserGenerationProfile      - user_generation_profile.py
✅ ConsistencyScore           - consistency_score.py
✅ JobTypeOverride            - job_type_override.py
```

### Repository Layer (Partial ⚠️)

**Location**: `backend/app/infrastructure/repositories/`

```
✅ ExampleResumeRepository    - example_resume_repository.py (COMPLETE)
❌ WritingStyleConfigRepository - MISSING (needs creation)
❌ LayoutConfigRepository       - MISSING (needs creation)
❌ UserGenerationProfileRepository - MISSING (needs creation)
```

### Service Layer (Implemented ✅)

**Location**: `backend/app/application/services/`

```
✅ PreferenceExtractionService - preference_extraction_service.py (COMPLETE)
   - extract_writing_style_from_cover_letter()
   - extract_layout_from_example_resume()
   - create_user_generation_profile()
```

### API Layer (NOT IMPLEMENTED ❌)

**Location**: `backend/app/presentation/api/` - **MISSING FILE**

```
❌ preferences.py - NEEDS CREATION
   Required endpoints:
   - POST   /preferences/upload-sample-resume
   - POST   /preferences/upload-cover-letter  
   - GET    /preferences/generation-profile
   - PUT    /preferences/generation-profile
   - GET    /preferences/example-resumes
   - DELETE /preferences/example-resumes/{id}
   - POST   /preferences/example-resumes/{id}/set-primary
   - POST   /preferences/extract-preferences (manual trigger)
```

---

## Implementation Gaps

### Critical Missing Components

#### 1. File Upload Infrastructure

**Status**: ❌ Not Implemented

**Required**:
- File upload endpoint with multipart/form-data support
- File validation (PDF, DOCX, TXT formats)
- Temporary file storage
- File size limits (max 5MB)
- Virus scanning (optional but recommended)

**Implementation**:
```python
# backend/app/application/services/file_upload/file_upload_service.py
class FileUploadService:
    async def upload_file(self, file: UploadFile, user_id: int) -> str:
        """Upload file and return storage path"""
        pass
```

#### 2. Text Extraction Service

**Status**: ⚠️ Referenced but Implementation Unclear

**Required**:
- PDF text extraction (PyPDF2 or pdfplumber)
- DOCX text extraction (python-docx)
- Plain text handling
- Error handling for corrupted files

**Implementation**:
```python
# backend/app/application/services/file_upload/text_extraction_service.py  
class TextExtractionService:
    async def extract_text(self, file_path: str) -> Dict[str, Any]:
        """Extract text from PDF/DOCX/TXT file"""
        pass
```

#### 3. Missing Repositories

**Status**: ❌ Not Implemented

**Required Files**:
```python
# backend/app/infrastructure/repositories/writing_style_config_repository.py
class WritingStyleConfigRepository:
    async def create(self, config: WritingStyleConfig) -> WritingStyleConfig
    async def get_by_user_id(self, user_id: int) -> Optional[WritingStyleConfig]
    async def update(self, config: WritingStyleConfig) -> WritingStyleConfig
    async def delete(self, config_id: str, user_id: int) -> bool

# backend/app/infrastructure/repositories/layout_config_repository.py  
class LayoutConfigRepository:
    async def create(self, config: LayoutConfig) -> LayoutConfig
    async def get_by_user_id(self, user_id: int) -> Optional[LayoutConfig]
    async def update(self, config: LayoutConfig) -> LayoutConfig
    async def delete(self, config_id: str, user_id: int) -> bool

# backend/app/infrastructure/repositories/user_generation_profile_repository.py
class UserGenerationProfileRepository:
    async def create(self, profile: UserGenerationProfile) -> UserGenerationProfile
    async def get_by_user_id(self, user_id: int) -> Optional[UserGenerationProfile]
    async def update(self, profile: UserGenerationProfile) -> UserGenerationProfile
    async def delete(self, user_id: int) -> bool
```

#### 4. API Endpoints

**Status**: ❌ Not Implemented

**Required File**: `backend/app/presentation/api/preferences.py`

**Endpoints to Implement**:

```python
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/preferences", tags=["preferences"])

@router.post("/upload-sample-resume", status_code=201)
async def upload_sample_resume(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """
    Upload sample resume for layout preference extraction.
    
    1. Validate file (PDF/DOCX, <5MB)
    2. Store file in storage
    3. Extract text
    4. Analyze layout with LLM
    5. Create LayoutConfig
    6. Create ExampleResume record
    7. Return extraction results
    """
    pass

@router.post("/upload-cover-letter", status_code=201)
async def upload_cover_letter(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """
    Upload sample cover letter for writing style extraction.
    
    1. Validate file (PDF/DOCX, <5MB)
    2. Store file in storage
    3. Extract text
    4. Analyze writing style with LLM
    5. Create WritingStyleConfig
    6. Create ExampleResume record (type: cover_letter)
    7. Return extraction results
    """
    pass

@router.get("/generation-profile")
async def get_generation_profile(
    current_user = Depends(get_current_user)
):
    """
    Get user's complete generation profile.
    
    Returns:
    - WritingStyleConfig (from cover letter)
    - LayoutConfig (from sample resume)
    - List of ExampleResume records
    - UserGenerationProfile metadata
    """
    pass

@router.put("/generation-profile")
async def update_generation_profile(
    updates: Dict[str, Any],
    current_user = Depends(get_current_user)
):
    """
    Update generation preferences manually.
    
    Allows user to adjust:
    - Tone/formality sliders
    - Section order
    - Bullet point style
    - Keyword density
    - ATS optimization level
    """
    pass

@router.get("/example-resumes")
async def list_example_resumes(
    current_user = Depends(get_current_user)
):
    """List user's uploaded example resumes and cover letters."""
    pass

@router.delete("/example-resumes/{id}")
async def delete_example_resume(
    id: str,
    current_user = Depends(get_current_user)
):
    """Delete an uploaded example resume."""
    pass

@router.post("/example-resumes/{id}/set-primary")
async def set_primary_example(
    id: str,
    current_user = Depends(get_current_user)
):
    """Mark an example resume as primary reference."""
    pass
```

#### 5. LLM Prompts

**Status**: ⚠️ Referenced but Files Missing

**Required Files**:
```python
# backend/app/domain/prompts/writing_style_prompts.py
class WritingStylePrompts:
    def create_style_analysis_prompt(
        self, 
        cover_letter_text: str, 
        context: Dict[str, Any]
    ) -> str:
        """Create prompt for LLM to analyze writing style"""
        pass

# backend/app/domain/prompts/structural_analysis_prompts.py
class StructuralAnalysisPrompts:
    def create_layout_analysis_prompt(
        self, 
        resume_text: str, 
        context: Dict[str, Any]
    ) -> str:
        """Create prompt for LLM to analyze resume structure"""
        pass
```

---

## Sprint 4 Implementation Checklist

### Phase 1: Infrastructure Setup

- [ ] Create `FileUploadService` with multipart/form-data handling
- [ ] Implement `TextExtractionService` (PDF, DOCX, TXT extraction)
- [ ] Create file storage directory structure
- [ ] Add file validation utilities (size, type, content)

### Phase 2: Repository Layer

- [ ] Create `WritingStyleConfigRepository`
- [ ] Create `LayoutConfigRepository`  
- [ ] Create `UserGenerationProfileRepository`
- [ ] Write unit tests for all repositories

### Phase 3: LLM Prompt Engineering

- [ ] Create `WritingStylePrompts` class with extraction prompts
- [ ] Create `StructuralAnalysisPrompts` class with layout prompts
- [ ] Test prompts with Groq LLM
- [ ] Optimize for JSON-mode output

### Phase 4: API Endpoints

- [ ] Create `backend/app/presentation/api/preferences.py`
- [ ] Implement `/upload-sample-resume` endpoint
- [ ] Implement `/upload-cover-letter` endpoint
- [ ] Implement `/generation-profile` GET/PUT endpoints
- [ ] Implement example resume management endpoints
- [ ] Add authentication middleware
- [ ] Write integration tests

### Phase 5: Service Integration

- [ ] Connect `PreferenceExtractionService` to API endpoints
- [ ] Implement background task for LLM analysis (async)
- [ ] Add progress tracking for extraction process
- [ ] Implement error handling and retry logic

### Phase 6: Testing

- [ ] Unit tests for preference extraction service
- [ ] Integration tests for file upload flow
- [ ] End-to-end tests for full preference setup
- [ ] Load testing for LLM calls (rate limits)

---

## Dependencies Required

### Python Packages (requirements.txt)

```txt
# File handling
python-multipart==0.0.6  # For file uploads
python-docx==1.1.0       # DOCX text extraction
PyPDF2==3.0.1            # PDF text extraction (or pdfplumber)
# Alternative: pdfplumber==0.10.3

# Already installed:
groq==0.33.0            # LLM API
pydantic==2.x           # Data validation
```

---

## API Request/Response Examples

### Upload Sample Resume

**Request**:
```bash
POST /api/v1/preferences/upload-sample-resume
Content-Type: multipart/form-data
Authorization: Bearer <jwt_token>

file: <sample_resume.pdf>
```

**Response (201)**:
```json
{
  "example_resume_id": "uuid-1234",
  "extraction_status": "completed",
  "layout_config": {
    "section_order": ["Summary", "Experience", "Skills", "Education"],
    "bullet_style": "achievement-focused",
    "header_style": "left-aligned",
    "date_format": "MM/YYYY"
  },
  "confidence_score": 0.87,
  "message": "Layout preferences extracted successfully"
}
```

### Upload Cover Letter

**Request**:
```bash
POST /api/v1/preferences/upload-cover-letter
Content-Type: multipart/form-data
Authorization: Bearer <jwt_token>

file: <cover_letter.pdf>
```

**Response (201)**:
```json
{
  "writing_style_config_id": "uuid-5678",
  "extraction_status": "completed",
  "writing_style": {
    "tone": "semi-formal",
    "formality_level": 6,
    "vocabulary_level": "professional",
    "sentence_structure": "varied",
    "action_verbs": ["developed", "led", "implemented"]
  },
  "confidence_score": 0.92,
  "message": "Writing style preferences extracted successfully"
}
```

### Get Generation Profile

**Request**:
```bash
GET /api/v1/preferences/generation-profile
Authorization: Bearer <jwt_token>
```

**Response (200)**:
```json
{
  "user_id": 1,
  "writing_style_config": {
    "id": "uuid-5678",
    "tone": "semi-formal",
    "formality_level": 6,
    "vocabulary_level": "professional"
  },
  "layout_config": {
    "id": "uuid-9012",
    "section_order": ["Summary", "Experience", "Skills", "Education"],
    "bullet_style": "achievement-focused"
  },
  "example_resumes": [
    {
      "id": "uuid-1234",
      "file_name": "john_doe_resume_2024.pdf",
      "is_primary": true,
      "created_at": "2025-11-10T10:30:00Z"
    }
  ],
  "setup_stage": "completed",
  "is_active": true
}
```

---

## Mobile UI Requirements (Sprint 5)

### Screens to Implement

1. **Preference Setup Screen** (`lib/screens/preferences/preference_setup_screen.dart`)
   - Welcome message explaining preference extraction
   - Upload sample resume button
   - Upload cover letter button
   - Progress indicators

2. **File Upload Screen** (`lib/screens/preferences/file_upload_screen.dart`)
   - File picker integration
   - Upload progress indicator
   - Extraction status display
   - Review extracted preferences

3. **Generation Profile Screen** (`lib/screens/preferences/generation_profile_screen.dart`)
   - Display current writing style settings
   - Display current layout settings
   - Manual adjustment controls (sliders, toggles)
   - Save/reset buttons

4. **Example Resume Management** (`lib/screens/preferences/example_resumes_screen.dart`)
   - List of uploaded examples
   - Set primary button
   - Delete button
   - Upload new button

---

## Performance Considerations

### LLM Analysis Time

- **Writing Style Extraction**: ~3-5 seconds (Llama 3.1 8B)
- **Layout Analysis**: ~3-5 seconds (Llama 3.1 8B)
- **Total Setup Time**: ~10 seconds for both uploads

### Optimization Strategies

1. **Async Processing**: Run LLM analysis in background, return immediately
2. **Polling**: Mobile polls for extraction status every 2 seconds
3. **Caching**: Cache extracted preferences, only re-extract on new upload
4. **Batch Analysis**: If user uploads multiple examples, analyze in parallel

---

## Security Considerations

1. **File Validation**: 
   - Max file size: 5MB
   - Allowed types: PDF, DOCX, TXT
   - Virus scanning (optional but recommended)

2. **Storage Security**:
   - Store files outside web root
   - Use UUID-based filenames (prevent path traversal)
   - Set proper file permissions (read-only)

3. **User Isolation**:
   - Only owner can access their uploaded files
   - Delete files when user deletes account
   - Expire temporary files after 30 days

---

## Estimated Implementation Effort

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| Phase 1: Infrastructure | File upload, text extraction | 2 days |
| Phase 2: Repositories | 3 repo classes + tests | 1 day |
| Phase 3: LLM Prompts | Writing style + layout prompts | 1 day |
| Phase 4: API Endpoints | 7 endpoints + tests | 2 days |
| Phase 5: Service Integration | Connect all layers | 1 day |
| Phase 6: Testing | Unit + integration tests | 1 day |
| **Total Backend** | | **8 days** |
| Mobile UI (Sprint 5) | 4 screens + state management | **4 days** |
| **Grand Total** | | **12 days** |

---

## Next Steps

1. **Immediate**:
   - Create missing repository classes
   - Implement file upload infrastructure
   - Create LLM prompt templates

2. **Sprint 4**:
   - Complete API endpoint implementation
   - Test with real user uploads
   - Validate LLM extraction quality

3. **Sprint 5**:
   - Build mobile UI for preference setup
   - Integrate with backend API
   - End-to-end testing

---

**Status**: 📋 **Ready for Sprint 4 Implementation**  
**Reviewed By**: Backend Developer  
**Last Updated**: November 11, 2025

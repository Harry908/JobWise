# TXT File Integration Test Specification

**Version**: 1.0  
**Date**: November 16, 2025  
**Scope**: Frontend-Backend TXT file upload integration  
**Priority**: High (Sprint 4 prototype focus)

## Test Overview

This specification validates the complete TXT file upload workflow from mobile frontend to backend processing, with emphasis on text extraction, preference analysis, and data mapping.

## Integration Points

### 1. File Upload Flow (Frontend → Backend)
```
Mobile App → File Picker → Select TXT file → 
PreferenceApiClient.uploadSampleResume() → 
HTTP POST /api/v1/preferences/upload-sample-resume → 
Backend FileUploadService → TextExtractionService → 
PreferenceExtractionService → Database Storage → 
Response with extraction results
```

### 2. Data Retrieval Flow (Frontend ← Backend)
```
Mobile App → PreferenceApiClient.getExampleResumes() → 
HTTP GET /api/v1/preferences/example-resumes → 
Backend ExampleResumeRepository → 
Response with {total, examples: [...]} → 
Mobile maps to List<ExampleResume>
```

## Test Cases

### TC1: Basic TXT File Upload
**Objective**: Verify successful TXT file upload and text extraction
**Priority**: P0 (Blocker)

**Pre-conditions**:
- Backend server running on http://10.0.2.2:8000
- User authenticated with valid JWT token
- TXT file available with sample resume content

**Test Steps**:
1. Open mobile app preferences screen
2. Tap "Upload Sample Resume"
3. Select TXT file from file picker
4. Verify file appears in upload preview
5. Tap "Upload" button
6. Monitor upload progress (0-100%)
7. Wait for LLM extraction (3-5s)
8. Verify success message displayed

**Expected Results**:
- File uploads successfully (HTTP 201)
- Text extraction completes without errors
- Layout preferences extracted and stored
- ExampleResume entity created with correct fields
- Success message: "Resume uploaded successfully!"

**API Validation**:
```json
POST /api/v1/preferences/upload-sample-resume
Content-Type: multipart/form-data

Response (201):
{
  "success": true,
  "message": "Sample resume uploaded and analyzed successfully",
  "example_resume_id": "uuid-string",
  "layout_config_id": "uuid-string",
  "extraction_metadata": {...},
  "is_primary": false
}
```

### TC2: TXT File Content Validation
**Objective**: Verify different TXT content types are handled correctly
**Priority**: P0 (Blocker)

**Test Data**:
- **Valid resume.txt**: Well-formatted resume with sections
- **Minimal.txt**: Basic resume with minimal content (>50 chars)
- **Complex.txt**: Resume with special characters, unicode
- **Empty.txt**: Empty file (should fail gracefully)

**Test Matrix**:
| File | Expected Result | Error Handling |
|------|----------------|----------------|
| valid_resume.txt | Success, complete extraction | N/A |
| minimal_resume.txt | Success, basic extraction | "Limited content detected" warning |
| unicode_resume.txt | Success, clean text | Unicode characters normalized |
| empty.txt | Validation error | "File content too short" error |

### TC3: Response Format Mapping
**Objective**: Verify backend response maps correctly to mobile models
**Priority**: P0 (Blocker)

**Backend Response Format**:
```json
{
  "total": 1,
  "examples": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "userId": 456,
      "filePath": "/uploads/example_resumes/user_456/resume.txt",
      "originalFilename": "resume.txt",
      "layoutConfigId": "789e1234-e89b-12d3-a456-426614174001",
      "isPrimary": false,
      "fileHash": "sha256hash",
      "uploadedAt": "2025-11-16T10:30:00Z",
      "fileSize": 2048,
      "fileType": "txt"
    }
  ]
}
```

**Mobile Model Mapping Verification**:
```dart
// Verify ExampleResume.fromJson() correctly maps all fields
final resume = ExampleResume.fromJson(json['examples'][0]);

assert(resume.id == "123e4567-e89b-12d3-a456-426614174000");
assert(resume.userId == 456);
assert(resume.originalFilename == "resume.txt");
assert(resume.fileType == "txt");
assert(resume.fileSize == 2048);
assert(!resume.isPrimary);
```

### TC4: Error Scenarios
**Objective**: Validate error handling for various failure conditions
**Priority**: P1 (Important)

**Error Test Cases**:

| Scenario | Expected HTTP Status | Expected Mobile Behavior |
|----------|---------------------|---------------------------|
| File too large (>5MB) | 413 Payload Too Large | Show "File size limit exceeded" |
| Unsupported file type | 415 Unsupported Media Type | Show "Please upload PDF, DOCX, or TXT" |
| Network timeout | 408 Request Timeout | Show retry button |
| Server error | 500 Internal Server Error | Show generic error with retry |
| Invalid JWT | 401 Unauthorized | Redirect to login |
| Rate limit exceeded | 429 Too Many Requests | Show rate limit dialog |

**Error Response Format**:
```json
{
  "error": {
    "code": "file_too_large",
    "message": "File size exceeds 5MB limit",
    "details": {
      "max_size": 5242880,
      "actual_size": 6291456
    }
  }
}
```

### TC5: Text Extraction Quality
**Objective**: Verify TXT text extraction maintains content integrity
**Priority**: P1 (Important)

**Test Content Types**:
1. **Plain ASCII**: Standard English resume content
2. **Unicode Characters**: Resume with accented names, international text
3. **Mixed Encoding**: Files with different character encodings
4. **Special Formatting**: Tabs, multiple spaces, line breaks

**Validation Points**:
- Text content preserved accurately
- Special characters normalized properly
- Line breaks maintained for structure
- No content truncation or corruption
- Extraction statistics reported correctly

**Expected TextExtractionService Output**:
```json
{
  "extracted_text": "John Doe\nSoftware Engineer...",
  "statistics": {
    "character_count": 2048,
    "word_count": 350,
    "line_count": 45,
    "estimated_reading_time_minutes": 2,
    "sections_detected": ["contact", "summary", "experience", "skills"],
    "extraction_quality": "good"
  }
}
```

### TC6: End-to-End Integration
**Objective**: Validate complete workflow from upload to display
**Priority**: P0 (Blocker)

**Complete User Flow**:
1. **Setup**: User authenticated, no existing preferences
2. **Upload**: User uploads sample_resume.txt via mobile app
3. **Processing**: Backend extracts text and analyzes layout
4. **Storage**: Data stored in database with proper relationships
5. **Retrieval**: Mobile app fetches updated example resumes list
6. **Display**: Resume appears in management screen with correct metadata

**Integration Checkpoints**:
- [ ] File upload completes successfully
- [ ] Text extraction produces valid output
- [ ] LLM analysis generates layout preferences
- [ ] Database entities created with correct relationships
- [ ] API response includes all required fields
- [ ] Mobile app displays updated list
- [ ] User can view extracted preferences

## Performance Criteria

### Upload Performance
- **File Upload**: <5s for typical TXT files (<1MB)
- **Text Extraction**: <1s for TXT files (fastest format)
- **LLM Analysis**: 3-5s (as documented)
- **Total Workflow**: <10s end-to-end

### Memory Usage
- **Mobile App**: <10MB increase during upload
- **Backend**: <50MB per concurrent upload
- **Database**: Efficient storage without content duplication

## Security Validation

### File Validation
- File size limits enforced (5MB max)
- File type validation (only TXT, PDF, DOCX allowed)
- Content scanning for malicious patterns
- User ownership verification

### API Security
- JWT authentication required for all endpoints
- User isolation (can only access own files)
- Rate limiting enforced (10 uploads/hour)
- CORS headers properly configured

## Integration Environment

### Backend Configuration
```bash
# Required environment variables
GROQ_API_KEY=your_api_key
DATABASE_URL=sqlite:///jobwise.db
UPLOAD_MAX_FILE_SIZE=5242880
ALLOWED_ORIGINS=["http://10.0.2.2:*"]
```

### Mobile Configuration
```dart
// API base URL for Android emulator
const String API_BASE_URL = "http://10.0.2.2:8000/api/v1";

// File picker configuration
allowedExtensions: ['pdf', 'docx', 'txt']
type: FileType.custom
```

## Test Data

### Sample TXT Files
Create test files in `backend/data/test_samples/`:

**1. valid_resume.txt** (348 words, well-formatted):
```
John Doe
Software Engineer
Phone: (555) 123-4567
Email: john.doe@email.com

SUMMARY
Experienced software engineer with 5+ years in full-stack development...

EXPERIENCE
Senior Software Engineer - TechCorp (2022-Present)
• Developed scalable web applications using React and Node.js
• Led team of 4 developers on critical projects
• Improved system performance by 40%

Software Engineer - StartupXYZ (2020-2022)
• Built REST APIs using Python and FastAPI
• Implemented CI/CD pipelines with Docker
• Collaborated with cross-functional teams

EDUCATION
Bachelor of Science in Computer Science
University of Technology (2016-2020)

SKILLS
• Programming: Python, JavaScript, TypeScript, Java
• Frameworks: React, Node.js, FastAPI, Django
• Databases: PostgreSQL, MongoDB, Redis
• Tools: Docker, Git, AWS, Jenkins
```

**2. minimal_resume.txt** (75 words, basic format):
```
Jane Smith
Data Scientist
jane.smith@email.com

EXPERIENCE
Data Scientist at DataCorp (2021-Present)
Analyzed large datasets using Python and SQL

EDUCATION  
MS Data Science, State University

SKILLS
Python, SQL, Machine Learning, Pandas, Scikit-learn
```

**3. unicode_resume.txt** (includes international characters):
```
José García-López
Ingénieur Logiciel / Software Engineer
José.García@email.com

EXPÉRIENCE / EXPERIENCE
Développeur Senior - Société Française (2022-Présent)
• Développement d'applications web avec React et Node.js
• Amélioration des performances système de 40%

ÉDUCATION / EDUCATION
Maîtrise en Informatique - Université de Paris
```

## Acceptance Criteria

**Must Have (P0)**:
- [x] TXT files upload successfully via mobile app
- [x] Text extraction completes without errors
- [x] API responses map correctly to mobile models
- [x] Error scenarios handled gracefully
- [x] File size and type validation enforced

**Should Have (P1)**:
- [ ] Unicode content handled properly
- [ ] Upload progress feedback accurate
- [ ] Performance meets stated criteria
- [ ] Comprehensive error messages provided

**Nice to Have (P2)**:
- [ ] Upload cancellation support
- [ ] Batch file upload capability
- [ ] Advanced text preprocessing
- [ ] Content quality scoring

## Test Execution Notes

### Setup Requirements
1. Backend server running with all dependencies installed
2. Mobile app built and running on emulator/device
3. Test TXT files prepared and accessible
4. Database initialized with user account
5. Valid JWT token for authentication

### Execution Order
1. Run TC1 (Basic Upload) first to validate core functionality
2. Execute TC3 (Response Mapping) to verify data flow
3. Run TC2 (Content Validation) with different file types
4. Test TC4 (Error Scenarios) to validate edge cases
5. Perform TC6 (End-to-End) as final integration validation

### Success Criteria
- All P0 test cases pass without manual intervention
- Error handling provides clear, actionable user feedback
- Performance meets documented targets
- No data corruption or security vulnerabilities detected
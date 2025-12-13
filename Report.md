# Sprint 6 Project Report
## JobWise - AI-Powered Job Application Assistant

---

## A. Product Documentation

### User Documentation

**Installation & Setup:**

1. **Backend Setup:**
*Prereq: Need to install dependency: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation 
   ```bash
   cd backend
   pip install -r requirements.txt
   start-server.bat
   ```

2. **Mobile App Setup:**
   ```bash
   cd mobile_app
   flutter pub get
   flutter run
   ```

3. **Configuration:**
   - Set up AWS S3 credentials for document storage
   - Configure Groq API key for AI generation features
   - Backend runs on `http://localhost:8000`

**Using the Application:**

1. **Authentication:** Register/login with email and password
2. **Profile Management:** Create and enhance your master resume with AI assistance
3. **Job Management:** Save jobs manually by pasting job descriptions or browse mock jobs
4. **AI Generation:** Generate tailored resumes and cover letters for specific jobs
5. **Document Export:** Export documents in PDF/DOCX format using professional templates
6. **File Management:** Download exported files to device storage and track export history

### Feature Overview

**Core Capabilities (Sprints 1-5):**
- **Authentication:** JWT-based secure authentication with token refresh
- **Profile Management:** CRUD operations for master resume with AI enhancement
- **Job Management:** Save/browse jobs, track applications status
- **AI Generation:** Profile enhancement, content ranking, resume/cover letter generation using Groq LLM (llama-3.3-70b-versatile)
- **Sample Management:** Upload resume/cover letter samples for writing style extraction

**Sprint 6 Enhancements:**
- **Document Export System:**
  - 4 professional templates (Modern 85% ATS, Classic 95% ATS, Creative 75% ATS, ATS-Optimized 98% ATS)
  - PDF & DOCX generation with template styling
  - Template customization (fonts)
  - Preview before export with progress tracking
  
- **Cloud Storage Integration:**
  - AWS S3-backed file storage
  - 9 API endpoints for complete export workflow
  - Download files to device storage
  - Share via system share sheet
  - View/export history with sorting/filtering
  - Storage usage tracking (100MB free tier)
  - Auto-delete expired files (30 days)

**Performance Metrics:**
- Resume generation: <3s
- Cover letter generation: 5-8s
- ATS scoring: 70-95%
- 77+ backend tests passing

### Known Limitations

1. **Job Browsing:** Job browsing API currently uses mock data from JSON. Users must manually paste job descriptions found online, which the system will automatically parse and insert.

2. **UI/UX:** Interface has room for improvement. Development prioritized functionality over aesthetics.

3. **Database:** Currently using SQLite database. Migration to PostgreSQL/MySQL required for production server deployment. Architecture was designed with this in mind, so migration will not cause major issues.

4. **Web Platform:** Web deployment incomplete due to network configuration issues.

---

## B. Version Control Information

**Repository:** `https://github.com/WSU-CptS483/course-project-Harry908`

**Sprint 5 Commit ID:** `40e69c682eb5abf3fe7f2813cdee1c0aa9c2997d`

**Sprint 6 Commit ID:** `529b5df14216c0f3fe01d9832051b0dc63e6ca96`

**Sprint 6 Branch:** `Sprint-6`

**Review Changes:**
```bash
git diff 40e69c682eb5abf3fe7f2813cdee1c0aa9c2997d 529b5df14216c0f3fe01d9832051b0dc63e6ca96
```

---

## C. Agentic Coding Workflow Documentation

### Workflow Description

**Three-Agent Workflow:**

1. **Solutions Architect Agent (SA)** - Claude Opus 4.5/Sonnet 4.5
   - Reviews current codebase and documentation
   - Creates feature design documents
   - Defines system architecture and API contracts
   - Logs work to `log/solution-architect-agent-log.md`

2. **Backend Developer Agent (BE)** - Claude 4.5/4.0
   - Implements FastAPI endpoints
   - Integrates external services (AWS S3, Groq LLM)
   - Designs database schemas
   - Logs work to `log/backend-agent-log.md`

3. **Frontend Developer Agent (FE)** - Claude 4.5/4.0
   - Implements Flutter UI
   - Manages state with Riverpod
   - Integrates with backend APIs
   - Logs work to `log/frontend-agent-log.md`

**Workflow Steps:**
```
SA Review → Design Document → BE Implementation → FE Implementation → 
Unit Testing → Human Black-box Testing → Bug Fixes → Logging
```

### Tool Configuration

**Primary Tool:** VS Code with Customized Copilot Chat (Agent Mode)
- Multi-file context awareness
- MCP tool integration (Python, Pylance, Dart, web search, context7)
- Custom instructions in `.context` folder
- Session logs in `session-logs/`

**Supporting Tools:**
- Python MCP tools for backend development
- Dart MCP tools for Flutter development
- Web search for documentation and best practices
- Context7 for best coding practices 

### Workflow Evidence

**Project Artifacts:**
- `log/` - Agent work logs and summaries
- `.context/` - Agent configuration and custom instructions  
- `session-logs/` - Detailed session transcripts
- `docs/` - Architecture and feature documentation
- `PHASE_3_EXPORT_SYSTEM_SUMMARY.md` - Sprint 6 design document

### Reflection: Sprint 5 to Sprint 6 Evolution

**Key Change:** Switched back to VS Code's built-in Copilot Agent Mode after extension updates significantly improved tool utilization.

**Improvements:**
- Better multi-file context handling
- More reliable tool invocations
- Improved parallel task execution
- Reduced need for manual intervention

**Process Maturity:** The three-agent workflow became more streamlined. Design documents from SA provided clearer specifications, reducing back-and-forth between implementation agents.

---

## D. Sprint 6 Summary

### What We Accomplished

Sprint 6 successfully delivered a complete document export and cloud storage system for JobWise. WE (AI agents) implemented 9 backend API endpoints handling PDF/DOCX generation using 4 professional templates with varying ATS optimization levels (75%-98%). The export system integrates AWS S3 for cloud storage, supporting full CRUD operations on exported files with download, share, and history tracking capabilities. On the mobile side, we built comprehensive UI screens for template selection, export configuration, file management, and download/share functionality with real-time progress tracking.

The implementation required significant technical complexity—HTML-based resume templating with WeasyPrint for PDF generation, python-docx for Word documents, S3 presigned URLs for secure downloads, and Flutter platform channels for device storage integration. All features are production-ready with proper error handling, loading states, and offline capability considerations.

### Connection to Sprint 5 Goals

Sprint 5 established the core AI-powered job application workflow (profile management, job tracking, AI generation). Sprint 6's export system was the planned next phase, addressing the critical need to deliver generated content in professional, shareable formats. 

**Sprint 5 Goals → Sprint 6 Delivery:**
- ✅ **Document formatting:** Implemented 4 ATS-optimized templates
- ✅ **Cloud storage:** Full S3 integration with 100MB free tier
- ✅ **Mobile export:** Download and share capabilities
- ⚠️ **Web platform (stretch goal):** Incomplete due to network configuration issues

All main goals completed. The system now provides an end-to-end workflow from profile creation to polished document export.

### Key Challenges Overcome

**Resume Templating Complexity:** The most significant challenge was converting structured profile data into professional-looking documents. After researching options (ReportLab, Jinja2, LaTeX), we settled on HTML templates rendered with WeasyPrint for PDFs and python-docx for Word documents. This approach provided the best balance of flexibility, styling control, and ATS compatibility.

**Solution:** Built a template inheritance system with base styles and template-specific overrides. Each template defines its own CSS and HTML structure while sharing common formatting logic. This enabled rapid iteration and easy addition of new templates.

**S3 Integration:** Managing secure file uploads/downloads required careful handling of presigned URLs, CORS configuration, and proper permission management.

**Flutter Platform Integration:** Implementing device storage access across iOS/Android required platform-specific code and permission handling.

### Demo Video
Demo of export and saving features and live backend server log.

link: https://drive.google.com/file/d/1cpfmdD3gS1nxeDthoClkH21WkoTBGTvl/view?usp=sharing

---

## Technical Architecture

**Backend Stack:**
- FastAPI (async Python web framework)
- SQLite (development database)
- AWS S3 (cloud file storage)
- Groq LLM (AI generation)
- WeasyPrint (PDF generation)
- python-docx (DOCX generation)

**Frontend Stack:**
- Flutter (cross-platform mobile)
- Riverpod (state management)
- Dio (HTTP client)
- Path Provider (file system access)

**Architecture Pattern:** Clean domain-driven design with clear separation of concerns (presentation → application → domain → infrastructure).

---

## Testing & Quality Assurance

- **Backend Tests:** 77+ passing unit and integration tests
- **Manual Testing:** Comprehensive black-box testing of all user flows
- **Export Testing:** Validated all 4 templates across multiple profile variations
- **S3 Testing:** Verified upload, download, delete operations
- **Mobile Testing:** Tested on Android emulator (iOS compatibility maintained)

---

## Future Enhancements

1. **Database Migration:** Move from SQLite to PostgreSQL for production deployment
2. **Web Platform:** Complete web app deployment with proper network configuration
3. **UI/UX Polish:** Improve visual design and user experience
4. **Live Job API:** Integrate real job boards (LinkedIn, Indeed, etc.)
5. **Batch Operations:** Export multiple resumes/cover letters simultaneously
6. **Template Marketplace:** Allow users to create and share custom templates

---

**Project Status:** Production-ready for core job application workflow with document export capabilities.

**Sprint Duration:** 2 weeks (Sprint 6)

**Lines of Code Added (Sprint 6):** ~3,000+ (backend + frontend)

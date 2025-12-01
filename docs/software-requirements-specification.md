# Software Requirements Specification (SRS)
## JobWise - AI-Powered Job Application Assistant

**Document Version:** 1.2  
**Date:** November 2025  
**Prepared by:** Solutions Architect Team  
**Project:** JobWise AI Resume Generation System  
**LLM Provider:** Groq (llama-3.3-70b-versatile, llama-3.1-8b-instant)  

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Overall Description](#2-overall-description)
3. [System Features](#3-system-features)
4. [External Interface Requirements](#4-external-interface-requirements)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [System Models](#6-system-models)
7. [Appendices](#7-appendices)

---

## 1. Introduction

### 1.1 Purpose
This Software Requirements Specification (SRS) describes the functional and non-functional requirements for JobWise, an AI-powered job application assistant that generates tailored resumes and cover letters from master resume profiles.

### 1.2 Scope
JobWise is a mobile-first application consisting of:
- **Flutter mobile application** for user interaction
- **FastAPI backend service** for business logic
- **AI Orchestrator pipeline** for resume generation
- **Data persistence layer** for profile and document storage

The system prioritizes resume generation from master resumes using a 5-stage AI pipeline while providing job discovery and document management capabilities.

### 1.3 Definitions, Acronyms, and Abbreviations

| Term | Definition |
|------|------------|
| AI | Artificial Intelligence |
| API | Application Programming Interface |
| ATS | Applicant Tracking System |
| CRUD | Create, Read, Update, Delete |
| LLM | Large Language Model |
| MVP | Minimum Viable Product |
| PDF | Portable Document Format |
| REST | Representational State Transfer |
| SLA | Service Level Agreement |
| SRS | Software Requirements Specification |
| UI/UX | User Interface/User Experience |

### 1.4 References
- Business Analyst Requirements Analysis Summary
- JobWise Project Proposal
- Architecture Decision Records (ADRs)
- System Architecture Overview

### 1.5 Overview
This SRS is organized into seven main sections covering system introduction, overall description, detailed features, interface requirements, non-functional requirements, system models, and appendices.

---

## 2. Overall Description

### 2.1 Product Perspective
JobWise is a standalone mobile application with cloud-based backend services. The system integrates with external AI services (Groq LLM) and job listing APIs while maintaining offline-first capabilities.

#### 2.1.1 System Context
```
[User] ↔ [Flutter App] ↔ [FastAPI Backend] ↔ [AI Pipeline] ↔ [External APIs]
                                    ↓
                              [Data Storage]
```

### 2.2 Product Functions
The major functions of JobWise include:

1. **Master Resume Management**
   - Create, edit, and maintain comprehensive resume profiles
   - Store personal information, experiences, skills, education, and projects
   - Version control and history tracking

2. **Job Discovery and Management**
   - Browse and search job listings
   - Save jobs of interest with status tracking
   - Static job data (prototype) with API integration (production)

3. **AI-Powered Resume Generation**
   - 5-stage pipeline for tailored resume creation
   - Job analysis and profile matching
   - ATS-optimized and visual template options
   - Quality validation and compliance checking
   - Tailored cover letter generation
   - Generation progress tracking and status updates

4. **Document Management**
   - PDF generation and export
   - Document versioning and history
   - Offline access and synchronization
   - Search and filtering across generated documents

### 2.3 User Classes and Characteristics

#### 2.3.1 Primary Users - Job Seekers
- **Characteristics**: Individuals actively seeking employment
- **Technical Expertise**: Basic to intermediate mobile app usage
- **Frequency of Use**: Daily during active job search periods
- **Key Needs**: Quick, professional resume customization for multiple applications

#### 2.3.2 Secondary Users - Career Counselors
- **Characteristics**: Professionals assisting job seekers
- **Technical Expertise**: Intermediate to advanced
- **Frequency of Use**: Weekly for client consultations
- **Key Needs**: Tools to help multiple clients optimize their resumes

### 2.4 Constraints

#### 2.4.1 Technical Constraints
- **Platform**: Flutter framework for cross-platform compatibility
- **Backend**: Python FastAPI for REST API services
- **Database**: SQLite (prototype) → PostgreSQL (production)
- **AI Provider**: Groq LLM (llama-3.3-70b-versatile, llama-3.1-8b-instant) with rate limiting

#### 2.4.2 Business Constraints
- **Budget**: Limited token usage for AI processing (~$100/month development)
- **Timeline**: 6-week development sprint (Weeks 8-14)
- **Team Size**: Multi-agent development pattern with 5 specialized agents

#### 2.4.3 Regulatory Constraints
- **Data Privacy**: Compliance with user data protection requirements
- **Content Policy**: Adherence to AI provider content policies
- **Employment Law**: Accurate representation of qualifications

### 2.5 Assumptions and Dependencies

#### 2.5.1 Assumptions
- Users have basic smartphone/tablet proficiency
- Internet connectivity available for AI generation
- Users understand resume best practices
- Job descriptions are in English language

#### 2.5.2 Dependencies
- **Groq API**: LLM inference availability and rate limits
- **Flutter Framework**: Continued support and compatibility
- **Job APIs**: Future integration with Indeed/LinkedIn
- **PDF Libraries**: Reliable PDF generation capabilities

---

## 3. System Features

### 3.1 Master Resume Management

#### 3.1.1 Description
Core functionality for creating and maintaining comprehensive resume profiles that serve as the foundation for tailored resume generation.

#### 3.1.2 Priority
**High** - Essential for core functionality

#### 3.1.3 Functional Requirements

**FR-3.1.1**: Profile Creation
- The system SHALL allow users to create a new master resume profile
- The system SHALL capture personal information (name, email, phone, location)
- The system SHALL support multiple work experiences with dates, descriptions, and achievements
- The system SHALL categorize skills by type (technical, soft, language, certification)
- The system SHALL store education history with degrees, institutions, and dates
- The system SHALL support optional project entries with descriptions and technologies

**FR-3.1.2**: Profile Management
- The system SHALL allow users to edit existing profile information
- The system SHALL provide profile validation with required field checking
- The system SHALL support profile deletion with confirmation
- The system SHALL maintain profile version history
- The system SHALL auto-save profile changes locally

**FR-3.1.3**: Data Persistence
- The system SHALL store profiles locally for offline access
- The system SHALL synchronize profiles with backend when online
- The system SHALL handle sync conflicts with last-write-wins strategy
- The system SHALL backup profiles to prevent data loss

### 3.2 Job Discovery and Management

#### 3.2.1 Description
Functionality for browsing, searching, and managing job opportunities that users want to apply for.

#### 3.2.2 Priority
**Medium** - Important for user workflow

#### 3.2.3 Functional Requirements

**FR-3.2.1**: Job Browsing
- The system SHALL display a list of available job postings
- The system SHALL support job search by title, company, and location
- The system SHALL show job details including description, requirements, and posting date
- The system SHALL provide job filtering by experience level and job type

**FR-3.2.2**: Job Management
- The system SHALL allow users to save jobs for later reference
- The system SHALL support job status tracking (interested, applied, interviewing, closed)
- The system SHALL provide a saved jobs dashboard
- The system SHALL allow users to add notes to saved jobs

**FR-3.2.3**: Data Sources
- The system SHALL use static JSON job data for prototype
- The system SHALL integrate with job APIs for production deployment
- The system SHALL cache job listings for offline browsing
- The system SHALL refresh job data periodically

**FR-3.2.5**: Offline Saves & Sync Queue
- The system SHALL allow saving jobs and updating statuses while offline and SHALL queue these changes for synchronization.
- Upon reconnection, queued operations SHALL sync within 5 seconds when the backend is available.

### 3.3 AI-Powered Resume Generation

#### 3.3.1 Description
The core AI functionality that analyzes job requirements and generates tailored resumes from master profiles using a 5-stage pipeline.

#### 3.3.2 Priority
**Critical** - Primary system differentiator

#### 3.3.3 Functional Requirements

**FR-3.3.1**: Generation Pipeline
- The system SHALL implement a 5-stage AI processing pipeline
- Stage 1 SHALL analyze job descriptions and extract requirements
- Stage 2 SHALL score profile sections by relevance to job requirements
- Stage 3 SHALL generate tailored resume content based on scoring
- Stage 4 SHALL validate generated content for ATS compliance and quality
- Stage 5 SHALL export content to PDF format with template options

**FR-3.3.2**: Job Analysis
- The system SHALL extract required and preferred skills from job descriptions
- The system SHALL identify experience level requirements
- The system SHALL extract key responsibilities and company culture indicators
- The system SHALL generate ATS-optimized keyword lists

**FR-3.3.3**: Profile Compilation
- The system SHALL score experience entries by job relevance (0-100 scale)
- The system SHALL rank skills by importance to target job
- The system SHALL recommend content emphasis areas
- The system SHALL calculate overall profile-job match percentage

**FR-3.3.4**: Content Generation
- The system SHALL rewrite experience bullets to highlight relevant achievements
- The system SHALL customize professional summary for target role
- The system SHALL optimize skills section ordering
- The system SHALL incorporate job-relevant keywords naturally

**FR-3.3.5**: Quality Validation
- The system SHALL check ATS compatibility of generated content
- The system SHALL validate grammar and spelling
- The system SHALL ensure date and formatting consistency
- The system SHALL verify section completeness and length requirements

**FR-3.3.6**: Template Options
- The system SHALL provide ATS-optimized template (plain text, single column)
- The system SHALL provide visual-enhanced template (modern design)
- The system SHALL support one-page and two-page length options
- The system SHALL maintain consistent formatting across templates

**FR-3.3.7**: Cover Letter Generation
- The system SHALL generate a tailored cover letter tied to a specific job using analyzed job requirements and the master profile.
- The cover letter SHALL include an introduction, 2–3 body paragraphs, and a closing with a professional tone.

**FR-3.3.8**: Generation Progress & Status
- The system SHALL expose generation progress at the stage level (analysis, scoring, drafting, validation, export).
- The system SHALL update and surface statuses including: pending, generating, generated, needs review, failed.

**FR-3.3.9**: Factuality Validation & Controlled Regeneration
- The system SHALL validate that generated content is traceable to the master profile and SHALL not fabricate information.
- On validation failure, the system SHALL perform at most one stricter regeneration; if still failing, mark the document "Needs Review" with guidance.

**FR-3.3.10**: ATS Keyword Coverage Threshold
- The system SHALL ensure that at least 90% of required ATS keywords from the job analysis appear naturally in the generated resume content without keyword stuffing.

### 3.4 Document Management

#### 3.4.1 Description
Functionality for managing generated resumes, cover letters, and document versions.

#### 3.4.2 Priority
**Medium** - Important for user organization

#### 3.4.3 Functional Requirements

**FR-3.4.1**: Document Storage
- The system SHALL store generated documents with metadata
- The system SHALL maintain generation history with timestamps
- The system SHALL link documents to source profiles and target jobs
- The system SHALL provide document search and filtering capabilities

**FR-3.4.2**: PDF Management
- The system SHALL generate high-quality PDF documents
- The system SHALL support PDF viewing within the application
- The system SHALL enable PDF sharing via email and other apps
- The system SHALL provide PDF download for local storage

**FR-3.4.3**: Version Control
- The system SHALL maintain document version history
- The system SHALL allow comparison between document versions
- The system SHALL support reverting to previous versions
- The system SHALL track generation parameters for reproducibility

---

## 4. External Interface Requirements

### 4.1 User Interfaces

#### 4.1.1 Mobile Application Interface
- **Platform**: Flutter cross-platform framework
- **Design**: Material Design 3.0 principles
- **Navigation**: Bottom navigation with 4 main sections (Profile, Jobs, Generate, Documents)
- **Responsive**: Adaptive layouts for phones and tablets
- **Accessibility**: Basic accessibility compliance (excluding advanced standards per requirements)

#### 4.1.2 Screen Requirements

**Profile Management Screens**
- Profile list/dashboard screen
- Profile creation/editing form (multi-step)
- Profile detail view with sections

**Job Management Screens**
- Job listing/search screen with filters
- Job detail view with save/apply options
- Saved jobs dashboard with status tracking

**Generation Screens**
- Generation setup screen (profile + job selection)
- Generation progress tracking screen
- Generated document preview screen
 - Status dashboard indicating stage-level progress and outcome (generated/needs review/failed)

### 4.2 Hardware Interfaces

#### 4.2.1 Mobile Device Requirements
- **Minimum OS**: iOS 12.0+ / Android 7.0+ (API level 24)
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 100MB for application, 500MB for document cache
- **Network**: Wi-Fi or cellular data connection for AI generation

### 4.3 Software Interfaces

#### 4.3.1 Backend API Interface
- **Protocol**: HTTP/HTTPS REST API
- **Format**: JSON request/response bodies
- **Authentication**: API key (prototype) / JWT tokens (production)
- **Base URL**: Configurable endpoint for different environments

#### 4.3.2 AI Service Interface
- **Provider**: Groq API
- **Models**: llama-3.1-8b-instant (fast/ranking), llama-3.3-70b-versatile (quality/generation)
- **Authentication**: API key management
- **Rate Limiting**: Request throttling per user and per endpoint

#### 4.3.3 Database Interface
- **Prototype**: SQLite embedded database
- **Production**: PostgreSQL with connection pooling
- **ORM**: SQLAlchemy for Python backend
- **Migrations**: Alembic for schema versioning

### 4.4 Communication Interfaces

#### 4.4.1 Network Protocols
- **HTTP/HTTPS**: RESTful API communication
- **TLS 1.2+**: Encrypted data transmission
- **JSON**: Data serialization format
- **WebSocket**: Future real-time updates (not in MVP)

---

## 5. Non-Functional Requirements

### 5.1 Performance Requirements

#### 5.1.1 Response Time Requirements
- **API Response Time**: < 2 seconds for CRUD operations
- **Resume Generation Time**: < 30 seconds median (< 60 seconds maximum)
- **Job Search Response**: < 3 seconds for search queries
- **Application Launch**: < 2 seconds cold start time
- **PDF Generation**: < 5 seconds for document creation

#### 5.1.2 Throughput Requirements
- **Concurrent Users**: Support 100 concurrent users (prototype) / 1000+ (production)
- **Generation Queue**: Handle 10 concurrent resume generations
- **API Rate Limiting**: 1000 requests/hour per user
- **Token Usage**: 50,000 tokens/day system limit

#### 5.1.3 Capacity Requirements
- **Database Storage**: 10GB (prototype) / 1TB (production)
- **File Storage**: 1GB (prototype) / 100GB (production)
- **User Profiles**: 1000 users (prototype) / 100,000 users (production)
- **Document Archive**: 90-day retention for generated documents

### 5.2 Reliability Requirements

#### 5.2.1 Availability
- **System Uptime**: 99.0% (prototype) / 99.9% (production)
- **Planned Maintenance**: < 4 hours/month during off-peak hours
- **Disaster Recovery**: 24-hour RTO (Recovery Time Objective)
- **Backup Frequency**: Daily automated backups

#### 5.2.2 Error Handling
- **Graceful Degradation**: Offline mode for core profile management
- **Retry Logic**: Exponential backoff for failed API calls (max 3 attempts)
- **Fallback Mechanisms**: Cached data when external services unavailable
- **Error Recovery**: Automatic retry for transient failures
 - **Offline Queue**: Operations performed offline (job saves, edits) SHALL be queued and synchronized automatically upon reconnection.

#### 5.2.3 Data Integrity
- **Transaction Management**: ACID compliance for critical operations
- **Data Validation**: Server-side validation for all inputs
- **Consistency Checks**: Regular data integrity verification
- **Audit Trail**: Logging of all significant system operations
 - **Data Retention & Deletion**: Upon user-initiated deletion of a generated document, the document SHALL become immediately inaccessible in the app and the backend SHALL flag the document for deletion from archival storage within 24 hours.

### 5.3 Security Requirements

#### 5.3.1 Authentication and Authorization
- **User Authentication**: API key (prototype) / OAuth 2.0 + JWT (production)
- **Session Management**: Secure token handling with expiration
- **Access Control**: Role-based permissions (future enhancement)
- **Password Policy**: Strong password requirements (production)

#### 5.3.2 Data Protection
- **Data Encryption**: TLS 1.2+ for data in transit
- **Storage Encryption**: Encrypted local storage for sensitive data
- **API Security**: Input sanitization and SQL injection prevention
- **Privacy Compliance**: User data anonymization capabilities
 - **Privacy-Aware Logging**: System logs SHALL not store PII; events SHALL use anonymized identifiers and timestamps.

#### 5.3.3 Content Security
- **Input Validation**: Sanitization of all user inputs
- **LLM Safety**: Content filtering for generated text
- **File Upload Security**: Validation and scanning of uploaded files
- **XSS Prevention**: Output encoding for web interfaces

### 5.4 Usability Requirements

#### 5.4.1 User Experience
- **Learning Curve**: New users productive within 15 minutes
- **Navigation**: Intuitive interface with clear information architecture
- **Help System**: Contextual help and tooltips for complex features
- **Error Messages**: Clear, actionable error descriptions

#### 5.4.2 Accessibility
- **Basic Compliance**: Large touch targets, readable fonts
- **Color Contrast**: Sufficient contrast ratios for readability
- **Text Scaling**: Support for system font size preferences
- **Simple Navigation**: Clear visual hierarchy and navigation patterns
 - **Measurable Thresholds**: Text and key UI elements SHALL remain functional and readable at up to 200% system text scaling without loss of content or functionality; contrast ratios SHALL meet platform-appropriate accessibility guidance.

### 5.5 Scalability Requirements

#### 5.5.1 Horizontal Scaling
- **API Scaling**: Load balancer support for multiple backend instances
- **Database Scaling**: Read replica support for query distribution
- **Cache Scaling**: Distributed caching with Redis cluster
- **File Storage**: CDN integration for document delivery

#### 5.5.2 Vertical Scaling
- **Resource Utilization**: Efficient memory and CPU usage
- **Connection Pooling**: Database connection management
- **Async Processing**: Non-blocking I/O for concurrent operations
- **Queue Management**: Background job processing for generation tasks

---

## 6. System Models

### 6.1 Use Case Model

#### 6.1.1 Primary Use Cases

**UC1: Create Master Resume**
- **Actor**: Job Seeker
- **Precondition**: User has installed the application
- **Main Flow**: User creates profile with personal info, experiences, skills, education
- **Postcondition**: Master resume stored and available for generation

**UC2: Generate Tailored Resume**
- **Actor**: Job Seeker
- **Precondition**: Master resume exists, target job selected
- **Main Flow**: System processes job requirements, matches profile, generates tailored resume
- **Postcondition**: PDF resume generated and stored

**UC3: Search and Save Jobs**
- **Actor**: Job Seeker
- **Precondition**: Application connected to job data source
- **Main Flow**: User searches jobs, views details, saves interesting positions
- **Postcondition**: Jobs saved to user's dashboard with status tracking

**UC4: Generate Tailored Cover Letter**
- **Actor**: Job Seeker
- **Precondition**: Master resume exists, target job selected
- **Main Flow**: System analyzes job + profile and generates a tailored cover letter (intro, 2–3 body paragraphs, closing)
- **Postcondition**: Cover letter generated and stored; status updated

**UC5: Review and Edit Documents**
- **Actor**: Job Seeker
- **Precondition**: Generated resume or cover letter exists
- **Main Flow**: User edits sections, saves versions, compares versions, and may revert
- **Postcondition**: New version created with metadata and history

**UC6: Export as ATS-Compatible PDF**
- **Actor**: Job Seeker
- **Precondition**: Validated document exists
- **Main Flow**: User selects template (ATS/visual) and exports PDF for viewing/sharing
- **Postcondition**: PDF available via viewer and sharing mechanisms

**UC7: View Application Pipeline & Status**
- **Actor**: Job Seeker
- **Precondition**: One or more generations in progress or completed
- **Main Flow**: User views stage-level progress and status (pending, generating, generated, needs review, failed)
- **Postcondition**: User understands progress and next steps

**UC8: Offline Save and Sync**
- **Actor**: Job Seeker
- **Precondition**: Device offline, cached jobs available
- **Main Flow**: User saves jobs and adds notes; operations queued; on reconnection, changes sync automatically
- **Postcondition**: Saved jobs and notes reflected in backend within expected time

### 6.2 Data Model

#### 6.2.1 Core Entities
- **MasterProfile**: User's complete resume information
- **Job**: Job posting with requirements and details
- **GenerationRequest**: Request to generate tailored resume
- **GeneratedDocument**: Result of generation process with metadata
- **PersonalInfo**: Contact information and basic details
- **Experience**: Work history entries with achievements
- **Skill**: Categorized abilities and competencies
- **Education**: Academic background and certifications

#### 6.2.2 Entity Relationships
```
MasterProfile 1--* Experience
MasterProfile 1--* Skill  
MasterProfile 1--* Education
MasterProfile 1--* GenerationRequest
Job 1--* GenerationRequest
GenerationRequest 1--1 GeneratedDocument
```

### 6.3 Process Model

#### 6.3.1 Resume Generation Process
1. **Input Validation**: Verify profile completeness and job details
2. **Job Analysis**: Extract requirements using AI analysis
3. **Profile Matching**: Score profile sections by relevance
4. **Content Generation**: Create tailored resume content
5. **Quality Validation**: Check ATS compliance and consistency
6. **PDF Export**: Generate final document with selected template
7. **Storage**: Save document with metadata for future access

### 6.4 Deployment Model

#### 6.4.1 Development Environment
- **Client**: Flutter development on local machine
- **Server**: FastAPI running locally with SQLite
- **AI**: Groq API calls with development rate limits
- **Storage**: Local file system for documents

#### 6.4.2 Production Environment
- **Client**: Mobile app stores (iOS App Store, Google Play)
- **Server**: Cloud deployment (AWS/GCP) with load balancing
- **Database**: Managed PostgreSQL with read replicas
- **Storage**: Cloud storage (S3/Cloud Storage) with CDN
- **Cache**: Redis cluster for performance optimization

---

## 7. Appendices

### Appendix A: Glossary

**ATS (Applicant Tracking System)**: Software used by employers to filter and rank job applications automatically.

**Master Resume**: A comprehensive resume profile containing all of a user's experiences, skills, and qualifications.

**Pipeline**: The 5-stage AI processing system that transforms a master resume into a tailored resume.

**Token**: Unit of measurement for AI model usage, roughly equivalent to 4 characters of text.

### Appendix B: Assumptions

1. Users have basic smartphone proficiency and understand resume concepts
2. Internet connectivity is available for AI generation and job searching
3. Groq API availability and rate limits remain stable during development
4. Job description text is primarily in English language
5. Users understand the difference between ATS-optimized and visual resume formats

### Appendix C: Dependencies

**Critical Dependencies:**
- Groq API for LLM-powered generation capabilities
- Flutter framework for cross-platform mobile development
- FastAPI framework for backend services

**Important Dependencies:**
- SQLite/PostgreSQL for data persistence
- PDF generation libraries for document export
- HTTP client libraries for API communication

**Future Dependencies:**
- Indeed/LinkedIn APIs for job data (production)
- Cloud storage services for scalable file storage
- Push notification services for real-time updates

### Appendix D: Risks and Mitigation

**High Risk: AI Service Availability**
- Risk: Groq API downtime or rate limiting
- Mitigation: Caching, model fallback (8b to 70b or vice versa), graceful degradation

**Medium Risk: Performance Requirements**
- Risk: Generation time exceeds 30-second target
- Mitigation: Optimization, caching, asynchronous processing

**Low Risk: Cross-Platform Compatibility**
- Risk: Flutter platform-specific issues
- Mitigation: Comprehensive testing, platform-specific implementations

---

**Document Control:**
- Version: 1.2
- Last Updated: January 2025
- Changes: Updated LLM provider from OpenAI to Groq
- Approved by: Solutions Architect Team
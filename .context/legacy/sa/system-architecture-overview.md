# JobWise System Architecture Overview

## Core Design Principles
- **Simple & Focused**: 4-component architecture prioritizing resume generation
- **Prototype-to-Production**: Clear upgrade paths for each technology choice
- **AI-First**: Orchestrated 5-stage generation pipeline as primary feature
- **Offline-Capable**: Local storage with sync capabilities

## High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Flutter App   │◄──►│  FastAPI Backend│
│  (Mobile/Web)   │    │   (REST API)    │
└─────────────────┘    └─────────────────┘
         │                       │
         │              ┌─────────────────┐
         │              │ AI Orchestrator │
         │              │   (5 Stages)    │
         │              └─────────────────┘
         │                       │
┌─────────────────┐    ┌─────────────────┐
│  Local Storage  │    │   Data Layer    │
│ (SQLite/Cache)  │    │ (SQLite/PgSQL)  │
└─────────────────┘    └─────────────────┘
```

## Component Responsibilities

### 1. Flutter Mobile App
**Role**: User interface and offline-first experience
- Master resume management (CRUD)
- Job browsing and search
- Resume generation requests
- PDF viewing and sharing
- Offline data caching

### 2. FastAPI Backend
**Role**: Business logic and API gateway
- REST API endpoints
- Request validation
- Business rule enforcement
- AI orchestrator coordination
- Data persistence

### 3. AI Orchestrator
**Role**: 5-stage resume generation pipeline
- Job analysis and requirement extraction
- Profile-to-job relevance scoring
- Tailored document generation
- ATS compliance validation
- PDF export formatting

### 4. Data Layer
**Role**: Persistent storage and caching
- User profiles and master resumes
- Job listings and metadata
- Generated documents and versions
- Generation history and analytics

## Technology Stack Options

### Frontend (Flutter)
| Component | Prototype | Production | Rationale |
|-----------|-----------|------------|-----------|
| State Management | Provider | Riverpod | Provider for simplicity, Riverpod for scale |
| Local Storage | SharedPreferences | SQLite/Hive | Simple key-value vs structured data |
| HTTP Client | dio | dio + retry | Same client, add retry logic |

### Backend (FastAPI)
| Component | Prototype | Production | Rationale |
|-----------|-----------|------------|-----------|
| Database | SQLite | PostgreSQL | File-based vs client-server |
| Job Data | Static JSON | API Integration | Mock data vs live feeds |
| LLM Provider | GPT-3.5-turbo | GPT-4/Claude | Cost vs quality |
| Cache | In-memory | Redis | Simple vs distributed |

### Infrastructure
| Component | Prototype | Production | Rationale |
|-----------|-----------|------------|-----------|
| Deployment | Local/Docker | Cloud (AWS/GCP) | Development vs scalable hosting |
| Monitoring | Print statements | Structured logging | Basic vs production observability |
| Security | Basic API keys | OAuth + JWT | Simple vs enterprise auth |

## Data Flow: Resume Generation

```
1. User selects job + master resume
2. Flutter app → FastAPI /generate endpoint
3. FastAPI → AI Orchestrator pipeline
4. Stage 1: Analyze job requirements
5. Stage 2: Score resume sections by relevance
6. Stage 3: Generate tailored content
7. Stage 4: Validate ATS compliance
8. Stage 5: Export PDF
9. Return generated document to app
10. Cache locally for offline access
```

## Core API Endpoints

```
POST /api/profiles                    # Create master resume
GET  /api/profiles/{id}              # Get master resume
PUT  /api/profiles/{id}              # Update master resume

GET  /api/jobs                       # List/search jobs
GET  /api/jobs/{id}                  # Get job details

POST /api/generate/resume            # Generate tailored resume
POST /api/generate/cover-letter      # Generate cover letter
GET  /api/documents/{id}             # Retrieve generated document
```

## Security Model

### Prototype
- Simple API key authentication
- No user accounts required
- Local data storage only

### Production
- OAuth 2.0 + JWT tokens
- User account management
- Encrypted data storage
- Rate limiting per user

## Performance Targets

| Metric | Prototype | Production |
|--------|-----------|------------|
| API Response | <5s | <2s |
| Resume Generation | <60s | <30s |
| Job Search | <10s | <3s |
| App Launch | <5s | <2s |

## Scalability Considerations

### Prototype Limitations
- Single SQLite file
- No horizontal scaling
- Limited concurrent users
- In-memory caching only

### Production Scaling
- PostgreSQL with read replicas
- Horizontal API scaling
- Redis cluster for caching
- CDN for PDF delivery
- Load balancers

## Development Phases

### Phase 1: Core MVP (Weeks 8-10)
- Master resume CRUD
- Static job data
- Basic AI generation
- Local PDF export

### Phase 2: Enhancement (Weeks 11-12)
- Job search and filters
- Generation history
- Improved UI/UX

### Phase 3: Production Ready (Weeks 13-14)
- Live job APIs
- User authentication
- Cloud deployment
- Performance optimization

## Next Steps for Implementation

1. **Backend Developer**: Implement FastAPI structure and AI orchestrator
2. **Mobile Developer**: Create Flutter app with master resume management
3. **Both**: Define and validate API contracts
4. **QA Engineer**: Create test scenarios for generation pipeline

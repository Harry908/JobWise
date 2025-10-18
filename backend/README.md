# JobWise Backend

AI-powered job application assistant backend built with FastAPI and Clean Architecture.

## Architecture

This backend follows Clean Architecture principles with clear separation of concerns:

- **Domain Layer**: Core business entities and rules
- **Application Layer**: Use cases and business workflows  
- **Infrastructure Layer**: External services and data persistence
- **Presentation Layer**: HTTP controllers and API interfaces

## Quick Start

1. **Setup Environment**
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

2. **Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Database Setup**
   ```bash
   alembic upgrade head
   ```

4. **Run Development Server**
   ```bash
   uvicorn app.main:app --reload
   ```

## Key Features

### 🚀 AI Resume Generation (Priority)
- 5-stage AI pipeline for tailored resume creation
- Job analysis and keyword extraction
- Profile scoring and content optimization
- ATS compliance validation
- Professional PDF generation

### 📋 Master Resume Management
- Comprehensive profile creation and editing
- Version control and history tracking
- Skills categorization and validation
- Import/export capabilities

### 🔍 Job Discovery
- Job search with advanced filtering
- Save and track application status
- Integration with job listing APIs
- Offline browsing with sync

### 📄 Document Management
- Generated document storage
- PDF download and sharing
- Version history and metadata
- Search and filtering

## Project Structure

```
backend/
├── app/
│   ├── domain/              # Domain Layer - Business Entities
│   ├── application/         # Application Layer - Use Cases
│   ├── infrastructure/      # Infrastructure Layer - External Services
│   ├── presentation/        # Presentation Layer - HTTP Controllers
│   ├── core/               # Shared Core Components
│   └── main.py             # Application Entry Point
├── tests/                  # Test Suite
├── alembic/               # Database Migrations
├── scripts/               # Utility Scripts
├── requirements.txt       # Python Dependencies
├── .env.example          # Environment Configuration Template
└── README.md             # This File
```

## API Documentation

- **Development**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

## Development

### Code Quality
- **Linting**: `flake8 app/`
- **Formatting**: `black app/`
- **Type Checking**: `mypy app/`
- **Testing**: `pytest`

### Environment Variables

Required configuration in `.env`:

```bash
# Database
DATABASE_URL=sqlite:///./jobwise.db
DATABASE_URL_PROD=postgresql://user:pass@localhost/jobwise

# AI Services
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=8000

# Redis Cache
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External APIs
INDEED_PUBLISHER_ID=your_indeed_publisher_id
LINKEDIN_API_KEY=your_linkedin_api_key

# Storage
PDF_STORAGE_PATH=./storage/pdfs
DOCUMENT_STORAGE_PATH=./storage/documents
```

## Performance Targets

- **Resume Generation**: <30s (p50), <60s (p95)
- **Job Search**: <3s response time
- **PDF Generation**: <5s processing time
- **API Throughput**: 100 requests/minute per user

## Monitoring

- **Health Check**: `GET /health`
- **Metrics**: `GET /metrics` (Prometheus format)
- **Logs**: Structured JSON logging with correlation IDs

## Deployment

### Docker
```bash
docker build -t jobwise-backend .
docker run -p 8000:8000 jobwise-backend
```

### Production
- Use PostgreSQL database
- Configure Redis for caching
- Set up reverse proxy (nginx)
- Enable SSL/TLS
- Configure monitoring and alerting

## Contributing

1. Follow Clean Architecture principles
2. Maintain test coverage >80%
3. Update documentation for new features
4. Use conventional commits
5. Run pre-commit hooks

## License

MIT License - see LICENSE file for details.
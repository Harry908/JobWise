# JobWise Implementation Guide

## Technical Handoff Checklist

### For Backend Developer Agent
- [ ] API contracts with examples provided ✅
- [ ] Data models with validation rules defined ✅
- [ ] Performance targets specified ✅
- [ ] Error handling strategies documented ✅
- [ ] Dependencies and integration points listed ✅
- [ ] ADR references included ✅
- [ ] Security requirements defined ✅
- [ ] Testing requirements specified ✅

### For Mobile Developer Agent
- [ ] API endpoints documented with examples ✅
- [ ] State management strategy defined ✅
- [ ] UI/UX requirements specified ✅
- [ ] Offline behavior requirements documented ✅
- [ ] Data caching strategies provided ✅
- [ ] Error handling patterns defined ✅
- [ ] Performance targets specified ✅
- [ ] Testing approach outlined ✅

## Implementation Priorities

### Phase 1: Foundation (Weeks 8-9)
**Backend Developer:**
1. Set up FastAPI project structure
2. Implement data models and database
3. Create profile CRUD endpoints
4. Implement basic job listing endpoints
5. Set up environment configuration

**Mobile Developer:**
1. Create Flutter project structure
2. Implement master resume management UI
3. Set up Provider state management
4. Create profile forms and validation
5. Implement local storage

### Phase 2: AI Integration (Week 10)
**Backend Developer:**
1. Implement AI Orchestrator pipeline
2. Create resume generation endpoints
3. Add job analysis functionality
4. Implement PDF export
5. Add error handling and logging

**Mobile Developer:**
1. Create job browsing interface
2. Implement resume generation flow
3. Add PDF viewing capabilities
4. Create generation status tracking
5. Implement offline caching

### Phase 3: Enhancement (Weeks 11-12)
**Both Developers:**
1. Performance optimization
2. Comprehensive testing
3. UI/UX improvements
4. Error handling refinement
5. Documentation completion

## Backend Implementation Guide

### Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app
│   ├── config.py              # Environment config
│   ├── database.py            # Database setup
│   ├── models/
│   │   ├── __init__.py
│   │   ├── profile.py         # User profile models
│   │   ├── job.py             # Job models
│   │   └── generation.py      # Generation models
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── profile.py         # Pydantic schemas
│   │   ├── job.py
│   │   └── generation.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── profiles.py        # Profile endpoints
│   │   ├── jobs.py            # Job endpoints
│   │   └── generate.py        # Generation endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_orchestrator.py # AI pipeline
│   │   ├── job_analyzer.py    # Stage 1
│   │   ├── profile_compiler.py # Stage 2
│   │   ├── document_generator.py # Stage 3
│   │   ├── quality_validator.py # Stage 4
│   │   └── pdf_exporter.py    # Stage 5
│   └── data/
│       └── mock_jobs.json     # Static job data
├── requirements.txt
├── alembic/                   # Database migrations
└── tests/
```

### Key Implementation Steps

#### 1. Environment Setup
```python
# config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./jobwise.db"
    openai_api_key: str
    environment: str = "development"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

#### 2. Database Models
```python
# models/profile.py
from sqlalchemy import Column, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from .base import Base

class Profile(Base):
    __tablename__ = "profiles"
    
    id = Column(String, primary_key=True)
    personal_info = Column(JSON, nullable=False)
    summary = Column(Text, nullable=False)
    experiences = Column(JSON, nullable=False)
    skills = Column(JSON, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
```

#### 3. API Endpoints
```python
# api/profiles.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.profile import ProfileCreate, ProfileResponse
from ..models.profile import Profile

router = APIRouter(prefix="/profiles", tags=["profiles"])

@router.post("/", response_model=ProfileResponse)
async def create_profile(
    profile: ProfileCreate,
    db: Session = Depends(get_db)
):
    # Implementation here
    pass
```

#### 4. AI Orchestrator
```python
# services/ai_orchestrator.py
from typing import Dict, Any
import openai
from ..config import settings

class AIOrchestrator:
    def __init__(self):
        openai.api_key = settings.openai_api_key
        self.stages = [
            JobAnalyzer(),
            ProfileCompiler(),
            DocumentGenerator(),
            QualityValidator(),
            PDFExporter()
        ]
    
    async def generate_resume(
        self, 
        profile: Dict[str, Any],
        job: Dict[str, Any]
    ) -> Dict[str, Any]:
        context = {"profile": profile, "job": job}
        
        for stage in self.stages:
            try:
                context = await stage.process(context)
            except Exception as e:
                # Error handling
                raise
        
        return context["result"]
```

## Mobile Implementation Guide

### Project Structure
```
mobile_app/
├── lib/
│   ├── main.dart
│   ├── app.dart                # App configuration
│   ├── models/
│   │   ├── profile.dart        # Data models
│   │   ├── job.dart
│   │   └── generation.dart
│   ├── providers/
│   │   ├── profile_provider.dart # State management
│   │   ├── job_provider.dart
│   │   └── generation_provider.dart
│   ├── services/
│   │   ├── api_service.dart    # HTTP client
│   │   ├── storage_service.dart # Local storage
│   │   └── pdf_service.dart    # PDF handling
│   ├── screens/
│   │   ├── profile/
│   │   │   ├── profile_list_screen.dart
│   │   │   ├── profile_form_screen.dart
│   │   │   └── profile_detail_screen.dart
│   │   ├── jobs/
│   │   │   ├── job_list_screen.dart
│   │   │   └── job_detail_screen.dart
│   │   └── generation/
│   │       ├── generation_screen.dart
│   │       └── generation_status_screen.dart
│   ├── widgets/
│   │   ├── profile_form.dart
│   │   ├── job_card.dart
│   │   └── generation_progress.dart
│   └── utils/
│       ├── constants.dart
│       ├── validators.dart
│       └── formatters.dart
├── assets/
├── test/
└── pubspec.yaml
```

### Key Implementation Steps

#### 1. Dependencies Setup
```yaml
# pubspec.yaml
dependencies:
  flutter:
    sdk: flutter
  provider: ^6.0.5
  dio: ^5.3.2
  shared_preferences: ^2.2.2
  path_provider: ^2.1.1
  pdf_render: ^1.4.9
  json_annotation: ^4.8.1

dev_dependencies:
  flutter_test:
    sdk: flutter
  json_serializable: ^6.7.1
  build_runner: ^2.4.7
```

#### 2. Data Models
```dart
// models/profile.dart
import 'package:json_annotation/json_annotation.dart';

part 'profile.g.dart';

@JsonSerializable()
class MasterProfile {
  final String id;
  final PersonalInfo personalInfo;
  final String summary;
  final List<Experience> experiences;
  final List<Skill> skills;
  final DateTime createdAt;
  final DateTime updatedAt;

  MasterProfile({
    required this.id,
    required this.personalInfo,
    required this.summary,
    required this.experiences,
    required this.skills,
    required this.createdAt,
    required this.updatedAt,
  });

  factory MasterProfile.fromJson(Map<String, dynamic> json) =>
      _$MasterProfileFromJson(json);

  Map<String, dynamic> toJson() => _$MasterProfileToJson(this);
}
```

#### 3. State Management
```dart
// providers/profile_provider.dart
import 'package:flutter/foundation.dart';
import '../models/profile.dart';
import '../services/api_service.dart';

class ProfileProvider extends ChangeNotifier {
  final ApiService _apiService;
  MasterProfile? _currentProfile;
  bool _isLoading = false;
  String? _error;

  ProfileProvider(this._apiService);

  MasterProfile? get currentProfile => _currentProfile;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> loadProfile(String profileId) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _currentProfile = await _apiService.getProfile(profileId);
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> createProfile(MasterProfile profile) async {
    _isLoading = true;
    notifyListeners();

    try {
      _currentProfile = await _apiService.createProfile(profile);
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
```

#### 4. API Service
```dart
// services/api_service.dart
import 'package:dio/dio.dart';
import '../models/profile.dart';
import '../models/job.dart';
import '../models/generation.dart';

class ApiService {
  final Dio _dio;
  
  ApiService({String? baseUrl}) : _dio = Dio(BaseOptions(
    baseUrl: baseUrl ?? 'http://localhost:8000/api/v1',
    connectTimeout: const Duration(seconds: 5),
    receiveTimeout: const Duration(seconds: 10),
  ));

  Future<MasterProfile> getProfile(String profileId) async {
    final response = await _dio.get('/profiles/$profileId');
    return MasterProfile.fromJson(response.data);
  }

  Future<MasterProfile> createProfile(MasterProfile profile) async {
    final response = await _dio.post('/profiles', data: profile.toJson());
    return MasterProfile.fromJson(response.data);
  }

  Future<List<Job>> searchJobs({
    String? query,
    String? location,
    int limit = 20,
    int offset = 0,
  }) async {
    final response = await _dio.get('/jobs', queryParameters: {
      if (query != null) 'search': query,
      if (location != null) 'location': location,
      'limit': limit,
      'offset': offset,
    });
    
    return (response.data['jobs'] as List)
        .map((json) => Job.fromJson(json))
        .toList();
  }

  Future<GenerationResult> generateResume({
    required String profileId,
    required String jobId,
    GenerationOptions? options,
  }) async {
    final response = await _dio.post('/generate/resume', data: {
      'profile_id': profileId,
      'job_id': jobId,
      'options': options?.toJson() ?? {},
    });
    
    return GenerationResult.fromJson(response.data);
  }
}
```

## Testing Strategy

### Backend Testing
```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_profile():
    profile_data = {
        "personal_info": {"full_name": "Test User"},
        "summary": "Test summary",
        "experiences": [],
        "skills": []
    }
    
    response = client.post("/api/v1/profiles", json=profile_data)
    assert response.status_code == 201
    assert "id" in response.json()

def test_generate_resume():
    # Test resume generation endpoint
    pass
```

### Mobile Testing
```dart
// test/providers/profile_provider_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import '../lib/providers/profile_provider.dart';
import '../lib/services/api_service.dart';

class MockApiService extends Mock implements ApiService {}

void main() {
  group('ProfileProvider', () {
    late ProfileProvider provider;
    late MockApiService mockApiService;

    setUp(() {
      mockApiService = MockApiService();
      provider = ProfileProvider(mockApiService);
    });

    test('should load profile successfully', () async {
      // Arrange
      final profile = MasterProfile(/* test data */);
      when(mockApiService.getProfile('test-id'))
          .thenAnswer((_) async => profile);

      // Act
      await provider.loadProfile('test-id');

      // Assert
      expect(provider.currentProfile, equals(profile));
      expect(provider.isLoading, isFalse);
      expect(provider.error, isNull);
    });
  });
}
```

## Deployment Strategy

### Development Environment
```bash
# Backend
cd backend
python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd mobile_app
flutter pub get
flutter run
```

### Production Environment
```bash
# Backend (Docker)
docker build -t jobwise-backend .
docker run -p 8000:8000 jobwise-backend

# Frontend (Build)
flutter build apk --release
flutter build web --release
```

## Performance Targets

| Component | Development | Production |
|-----------|-------------|------------|
| API Response Time | <5s | <2s |
| Resume Generation | <60s | <30s |
| App Launch Time | <5s | <2s |
| Job Search | <10s | <3s |
| Database Queries | <1s | <500ms |

## Monitoring and Logging

### Backend Monitoring
```python
# Add to main.py
import logging
from fastapi import Request
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.2f}s"
    )
    
    return response
```

### Mobile Analytics
```dart
// Add to app initialization
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize analytics
  await Analytics.initialize();
  
  runApp(JobWiseApp());
}
```

## Next Steps

1. **Backend Developer**: Start with FastAPI setup and profile endpoints
2. **Mobile Developer**: Initialize Flutter project and master resume UI
3. **Both**: Validate API contracts with sample data
4. **Integration**: Test end-to-end resume generation flow
5. **QA Engineer**: Create comprehensive test scenarios

This implementation guide provides concrete steps for both development teams to begin building JobWise while maintaining architectural consistency and quality standards.
# ADR-001: Database Selection for JobWise

## Status
Accepted

## Context
JobWise requires a database solution that can support both rapid prototyping and production scalability. The application stores user profiles, job listings, generation requests, and generated documents with varying complexity and query patterns.

## Decision Drivers
- **Development Velocity**: Fast prototyping and testing capability
- **Production Scalability**: Support for concurrent users and complex queries
- **Data Complexity**: JSON documents, full-text search, relationships
- **Cost Considerations**: Hosting and operational costs
- **Team Expertise**: Available skills and learning curve

## Considered Options

### Option 1: SQLite Only
**Pros:**
- Zero configuration setup
- Perfect for single-user prototyping
- File-based, no server required
- Excellent for development and testing

**Cons:**
- No concurrent write support
- Limited scalability
- No full-text search capabilities
- Single-point-of-failure

### Option 2: PostgreSQL Only
**Pros:**
- Production-ready scalability
- Excellent JSON support (JSONB)
- Full-text search built-in
- ACID compliance
- Rich indexing options

**Cons:**
- Complex setup for development
- Requires server infrastructure
- Overkill for early prototyping
- Higher operational complexity

### Option 3: Dual Strategy (Chosen)
**Pros:**
- SQLite for rapid prototyping and development
- PostgreSQL for production deployment
- Clear migration path
- Cost-effective development
- Production-ready scalability

**Cons:**
- Dual maintenance overhead
- Schema compatibility considerations
- Migration complexity

## Decision Outcome
**Chosen Option:** Dual Strategy (SQLite → PostgreSQL)

**Rationale:** This approach optimizes for both development velocity and production requirements. SQLite enables rapid prototyping without infrastructure overhead, while PostgreSQL provides production scalability and advanced features.

## Implementation Guidance

### Development Environment
```python
# database.py
DATABASE_CONFIG = {
    "development": {
        "url": "sqlite:///./jobwise_dev.db",
        "echo": True
    },
    "production": {
        "url": "postgresql://user:pass@host:5432/jobwise",
        "pool_size": 20,
        "max_overflow": 0
    }
}
```

### Migration Strategy
1. Use SQLAlchemy ORM for database abstraction
2. Maintain schema compatibility between SQLite and PostgreSQL
3. Provide migration scripts for data transfer
4. Implement feature flags for database-specific optimizations

## Consequences

### Positive
- Rapid development cycles with SQLite
- Production scalability with PostgreSQL
- Cost-effective development environment
- Clear upgrade path for growing applications

### Negative
- Additional complexity in maintaining two database systems
- Potential schema drift between environments
- Migration effort required for production deployment

### Neutral
- Team needs to understand both database systems
- Testing required in both environments

## Validation
Success metrics:
- Development setup time < 5 minutes
- Production deployment supports > 1000 concurrent users
- Migration completes without data loss
- Query performance meets SLA requirements

---

# ADR-002: LLM Provider Strategy

## Status
Accepted

## Context
Resume generation requires high-quality language model capabilities for analyzing jobs, compiling profiles, and generating tailored content. Cost, quality, and reliability are key factors.

## Decision Drivers
- **Cost Management**: Token usage and pricing models
- **Quality Requirements**: Output quality for professional documents
- **Reliability**: Service availability and response times
- **Development Velocity**: Easy integration and testing

## Considered Options

### Option 1: OpenAI GPT-3.5-turbo (Development)
**Pros:**
- Cost-effective for development ($0.002/1K tokens)
- Fast response times
- Reliable API
- Good documentation

**Cons:**
- Lower quality than GPT-4
- May require more prompt engineering
- Limited context window (4K tokens)

### Option 2: OpenAI GPT-4 (Production)
**Pros:**
- Superior output quality
- Better instruction following
- Larger context window (8K/32K tokens)
- Industry standard

**Cons:**
- Higher cost ($0.03/1K tokens)
- Slower response times
- May be overkill for simple tasks

### Option 3: Dual Strategy with Fallback (Chosen)
**Pros:**
- Cost optimization through tiered usage
- Quality optimization for production
- Fallback reliability
- Environment-appropriate choices

**Cons:**
- Complex configuration management
- Different prompt optimization needed
- Monitoring multiple providers

## Decision Outcome
**Chosen Option:** Dual Strategy
- **Development**: GPT-3.5-turbo for cost efficiency
- **Production**: GPT-4 for quality, with GPT-3.5-turbo fallback
- **Rate Limiting**: Automatic fallback on quota exhaustion

## Implementation Guidance

```python
class LLMProvider:
    def __init__(self, environment: str):
        self.config = {
            "development": {
                "primary": "gpt-3.5-turbo",
                "fallback": None,
                "max_tokens": 4000
            },
            "production": {
                "primary": "gpt-4",
                "fallback": "gpt-3.5-turbo", 
                "max_tokens": 8000
            }
        }[environment]
```

## Consequences

### Positive
- Optimized cost/quality ratio
- Reliable fallback mechanism
- Environment-appropriate resource usage

### Negative
- Complex provider management
- Prompt optimization for multiple models
- Monitoring overhead

---

# ADR-003: Flutter State Management Selection

## Status
Accepted

## Context
Flutter app requires state management for user profiles, job listings, generation status, and offline caching. Solution must balance simplicity for rapid development with scalability for production.

## Decision Drivers
- **Learning Curve**: Team familiarity and onboarding time
- **Development Speed**: Time to implement features
- **Scalability**: Support for complex state interactions
- **Testing**: Ease of unit and widget testing
- **Community Support**: Documentation and ecosystem

## Considered Options

### Option 1: Provider (Development)
**Pros:**
- Simple mental model
- Fast to implement
- Good for small to medium apps
- Official Flutter team support
- Excellent documentation

**Cons:**
- Can become complex with growth
- Manual dependency injection
- Limited code generation benefits

### Option 2: Riverpod (Production)
**Pros:**
- Compile-time safety
- Better testing capabilities
- Automatic dependency injection
- Code generation support
- Scales well with complexity

**Cons:**
- Steeper learning curve
- More boilerplate initially
- Newer ecosystem

### Option 3: Phased Adoption (Chosen)
**Pros:**
- Start simple with Provider
- Migrate to Riverpod for production
- Learn incrementally
- Validate patterns before committing

**Cons:**
- Migration effort required
- Temporary technical debt
- Dual approach complexity

## Decision Outcome
**Chosen Option:** Phased adoption (Provider → Riverpod)

**Implementation Plan:**
1. **Sprint 1-2**: Implement core features with Provider
2. **Sprint 3**: Evaluate Riverpod migration needs
3. **Sprint 4-5**: Migrate to Riverpod for production

## Implementation Guidance

### Provider Implementation
```dart
// providers/profile_provider.dart
class ProfileProvider extends ChangeNotifier {
  MasterProfile? _profile;
  
  MasterProfile? get profile => _profile;
  
  Future<void> loadProfile() async {
    // Implementation
    notifyListeners();
  }
}
```

### Riverpod Migration Path
```dart
// providers/profile_provider.dart (Riverpod)
final profileProvider = StateNotifierProvider<ProfileNotifier, AsyncValue<MasterProfile?>>((ref) {
  return ProfileNotifier();
});
```

## Consequences

### Positive
- Rapid initial development with Provider
- Production-ready architecture with Riverpod
- Learning opportunity for team
- Validated patterns before scaling

### Negative
- Migration effort required
- Temporary dual knowledge requirement
- Code refactoring overhead

---

# ADR-004: Job Data Source Strategy

## Status
Accepted

## Context
JobWise needs job listings for resume tailoring. Requirements differ significantly between development (static testing data) and production (live job feeds).

## Decision Drivers
- **Development Efficiency**: Fast, reliable test data
- **Data Quality**: Diverse, realistic job descriptions
- **Production Requirements**: Live, up-to-date job listings
- **Cost Considerations**: API usage and rate limiting
- **Legal Compliance**: Terms of service and data usage rights

## Considered Options

### Option 1: Static JSON Only
**Pros:**
- Complete control over test data
- No API rate limits
- Offline development
- Predictable for testing

**Cons:**
- Not production-viable
- Manual data maintenance
- Limited diversity
- No real-time updates

### Option 2: Live APIs Only
**Pros:**
- Real-time data
- Production-ready from start
- Authentic job descriptions
- No manual maintenance

**Cons:**
- Complex development setup
- API rate limiting issues
- Dependent on external services
- Cost during development

### Option 3: Hybrid Approach (Chosen)
**Pros:**
- Static data for development
- Live APIs for production
- Cost-effective development
- Production authenticity
- Gradual integration complexity

**Cons:**
- Dual data management
- Integration testing complexity
- Schema compatibility requirements

## Decision Outcome
**Chosen Option:** Hybrid Approach

### Development Phase
- 100+ curated job descriptions in JSON format
- Diverse roles, industries, and experience levels
- Predictable data for automated testing

### Production Phase
- Indeed API integration (primary)
- LinkedIn API integration (secondary)
- Fallback to cached static data

## Implementation Guidance

```python
class JobDataService:
    def __init__(self, environment: str):
        self.sources = {
            "development": [StaticJobSource()],
            "production": [
                IndeedAPISource(),
                LinkedInAPISource(),
                StaticJobSource()  # Fallback
            ]
        }[environment]
    
    async def search_jobs(self, query: str) -> List[Job]:
        for source in self.sources:
            try:
                return await source.search(query)
            except Exception as e:
                logger.warning(f"Source {source} failed: {e}")
        return []
```

## Consequences

### Positive
- Cost-effective development with reliable test data
- Production-ready with live job feeds
- Fallback mechanisms for reliability
- Gradual complexity introduction

### Negative
- Dual data source maintenance
- Schema compatibility requirements
- Integration testing complexity
- API key management overhead

## Validation
Success metrics:
- Development environment setup < 2 minutes
- Job search results < 3 seconds in production
- 99% uptime with fallback mechanisms
- Legal compliance with all data sources
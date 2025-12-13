# Structured Content Specification

**Purpose**: Complete specification for generation service to build structured JSON content from master profile.

**Target**: `generations.content_structured` column (JSON field)

**Status**: 📋 Implementation Required

---

## Master Profile Fields Mapping

### ✅ Currently Included (Plain Text)

- ✅ Personal Info: `full_name`, `email`, `phone`, `location`
- ✅ Professional Summary (enhanced or original)
- ✅ Technical Skills (first 20)
- ✅ Experiences (ranked, with enhanced descriptions)
- ✅ Projects (ranked, with enhanced descriptions)
- ✅ Education (first 2, with degree, institution, GPA)

### ❌ Currently MISSING (Need to Add)

#### Header Section
- ❌ `personal_info.linkedin` - LinkedIn profile URL
- ❌ `personal_info.github` - GitHub profile URL
- ❌ `personal_info.website` - Personal website URL

#### Skills Section
- ❌ `skills.soft` - Soft skills list (Leadership, Communication, etc.)
- ❌ `skills.languages` - Language proficiencies
  - `name` (string)
  - `proficiency` (native|fluent|conversational|basic)
- ❌ `skills.certifications` - Professional certifications
  - `name` (string)
  - `issuer` (string)
  - `date_obtained` (ISO date)
  - `expiry_date` (ISO date, optional)
  - `credential_id` (string, optional)

#### Experience Section
- ❌ `is_current` - Boolean flag for current position
- ❌ Better handling of all experiences (not just top 5)

#### Projects Section
- ❌ `start_date` - Project start date (optional)
- ❌ `end_date` - Project end date (optional)

#### Education Section
- ❌ `honors` - Academic honors list (Dean's List, Summa Cum Laude, etc.)
- ❌ All education entries (not just first 2)
- ❌ `end_date` handling (currently assumes always present)

---

## Complete Structured Content Schema

```json
{
  "header": {
    "name": "string",              // ✅ profile.personal_info.full_name
    "title": "string",             // 🔄 Derived from latest experience or custom
    "email": "string",             // ✅ profile.personal_info.email
    "phone": "string",             // ✅ profile.personal_info.phone
    "location": "string",          // ✅ profile.personal_info.location
    "linkedin": "string",          // ❌ profile.personal_info.linkedin (MISSING)
    "github": "string",            // ❌ profile.personal_info.github (MISSING)
    "website": "string"            // ❌ profile.personal_info.website (MISSING)
  },
  "sections": [
    {
      "type": "professional_summary",
      "content": "string"          // ✅ profile.enhanced_professional_summary || profile.professional_summary
    },
    {
      "type": "skills",
      "categories": [
        {
          "name": "Technical Skills",
          "items": ["string"]      // ✅ profile.skills.technical (currently limited to 20)
        },
        {
          "name": "Soft Skills",
          "items": ["string"]      // ❌ profile.skills.soft (MISSING)
        },
        {
          "name": "Languages",
          "items": [
            {
              "name": "string",
              "proficiency": "string"  // ❌ profile.skills.languages (MISSING)
            }
          ]
        },
        {
          "name": "Certifications",
          "items": [
            {
              "name": "string",
              "issuer": "string",
              "date_obtained": "string",
              "expiry_date": "string",
              "credential_id": "string"  // ❌ profile.skills.certifications (MISSING)
            }
          ]
        }
      ]
    },
    {
      "type": "experience",
      "entries": [
        {
          "id": "string",          // ✅ exp.id
          "title": "string",       // ✅ exp.title
          "company": "string",     // ✅ exp.company
          "location": "string",    // ✅ exp.location
          "start_date": "string",  // ✅ exp.start_date
          "end_date": "string",    // ✅ exp.end_date || "Present"
          "is_current": boolean,   // ❌ exp.is_current (MISSING)
          "description": "string", // ✅ exp.enhanced_description || exp.description
          "bullets": ["string"],   // 🔄 Could extract from description
          "achievements": ["string"]  // ✅ exp.achievements
        }
      ]
    },
    {
      "type": "projects",
      "entries": [
        {
          "id": "string",          // ✅ proj.id
          "name": "string",        // ✅ proj.name
          "description": "string", // ✅ proj.enhanced_description || proj.description
          "technologies": ["string"],  // ✅ proj.technologies
          "url": "string",         // ✅ proj.url
          "start_date": "string",  // ❌ proj.start_date (MISSING)
          "end_date": "string"     // ❌ proj.end_date (MISSING)
        }
      ]
    },
    {
      "type": "education",
      "entries": [
        {
          "id": "string",          // ✅ edu.id
          "degree": "string",      // ✅ edu.degree
          "field_of_study": "string",  // ✅ edu.field_of_study
          "institution": "string", // ✅ edu.institution
          "start_date": "string",  // ✅ edu.start_date
          "end_date": "string",    // ✅ edu.end_date (needs null handling)
          "gpa": float,            // ✅ edu.gpa
          "honors": ["string"]     // ❌ edu.honors (MISSING)
        }
      ]
    }
  ],
  "metadata": {
    "total_years_experience": int,     // 🔄 Calculate from experiences
    "top_skills": ["string"],          // 🔄 Extract from profile.skills.technical
    "industries": ["string"],          // 🔄 Extract from experiences
    "total_projects": int,             // 🔄 len(profile.projects)
    "total_certifications": int        // 🔄 len(profile.skills.certifications)
  }
}
```

---

## Implementation Checklist

### Phase 1: Extend Current Generation Service

**File**: `backend/app/application/services/generation_service.py`

**Method**: `generate_resume()` around lines 120-220

#### Step 1: Build Complete Header
```python
header = {
    "name": profile.personal_info.full_name,
    "title": ranked_exps[0].title if ranked_exps else "Professional",  # Derive from latest exp
    "email": profile.personal_info.email,
    "phone": profile.personal_info.phone,
    "location": profile.personal_info.location,
    "linkedin": profile.personal_info.linkedin,     # ❌ ADD THIS
    "github": profile.personal_info.github,         # ❌ ADD THIS
    "website": profile.personal_info.website        # ❌ ADD THIS
}
```

#### Step 2: Build Complete Skills Section
```python
skills_section = {
    "type": "skills",
    "categories": []
}

# Technical skills (✅ already included in plain text)
if profile.skills.technical:
    skills_section["categories"].append({
        "name": "Technical Skills",
        "items": profile.skills.technical  # Remove [:20] limit
    })

# Soft skills (❌ ADD THIS)
if profile.skills.soft:
    skills_section["categories"].append({
        "name": "Soft Skills",
        "items": profile.skills.soft
    })

# Languages (❌ ADD THIS)
if profile.skills.languages:
    skills_section["categories"].append({
        "name": "Languages",
        "items": [
            {
                "name": lang.name,
                "proficiency": lang.proficiency
            }
            for lang in profile.skills.languages
        ]
    })

# Certifications (❌ ADD THIS)
if profile.skills.certifications:
    skills_section["categories"].append({
        "name": "Certifications",
        "items": [
            {
                "name": cert.name,
                "issuer": cert.issuer,
                "date_obtained": cert.date_obtained,
                "expiry_date": cert.expiry_date,
                "credential_id": cert.credential_id
            }
            for cert in profile.skills.certifications
        ]
    })
```

#### Step 3: Build Experience Section with is_current
```python
experience_section = {
    "type": "experience",
    "entries": [
        {
            "id": str(exp.id),
            "title": exp.title,
            "company": exp.company,
            "location": exp.location,
            "start_date": exp.start_date,
            "end_date": exp.end_date or "Present",
            "is_current": exp.is_current,  # ❌ ADD THIS
            "description": exp.enhanced_description or exp.description,
            "bullets": [],  # Could parse from description
            "achievements": exp.achievements
        }
        for exp in ranked_exps
    ]
}
```

#### Step 4: Build Projects Section with Dates
```python
projects_section = {
    "type": "projects",
    "entries": [
        {
            "id": str(proj.id),
            "name": proj.name,
            "description": proj.enhanced_description or proj.description,
            "technologies": proj.technologies,
            "url": proj.url,
            "start_date": proj.start_date,  # ❌ ADD THIS
            "end_date": proj.end_date       # ❌ ADD THIS
        }
        for proj in ranked_projs
    ]
}
```

#### Step 5: Build Education Section with Honors
```python
education_section = {
    "type": "education",
    "entries": [
        {
            "id": str(edu.id),
            "degree": edu.degree,
            "field_of_study": edu.field_of_study,
            "institution": edu.institution,
            "start_date": edu.start_date,
            "end_date": edu.end_date,  # Already handles None
            "gpa": edu.gpa,
            "honors": edu.honors  # ❌ ADD THIS
        }
        for edu in profile.education  # Remove [:2] limit
    ]
}
```

#### Step 6: Build Metadata
```python
from datetime import datetime

def calculate_years_experience(experiences):
    """Calculate total years of experience."""
    if not experiences:
        return 0
    
    total_days = 0
    for exp in experiences:
        start = datetime.fromisoformat(exp.start_date)
        end = datetime.fromisoformat(exp.end_date) if exp.end_date else datetime.now()
        total_days += (end - start).days
    
    return round(total_days / 365.25, 1)

metadata = {
    "total_years_experience": calculate_years_experience(ranked_exps),
    "top_skills": profile.skills.technical[:10],
    "industries": list(set(exp.company for exp in ranked_exps[:5])),  # Unique companies
    "total_projects": len(profile.projects),
    "total_certifications": len(profile.skills.certifications)
}
```

#### Step 7: Assemble Complete Structure
```python
content_structured = {
    "header": header,
    "sections": [
        {"type": "professional_summary", "content": summary},
        skills_section,
        experience_section,
        projects_section,
        education_section
    ],
    "metadata": metadata
}

# Store both plain text AND structured content
generation = Generation(
    id=uuid4(),
    user_id=user_id,
    job_id=job_id,
    ranking_id=ranking.id,
    document_type=DocumentType.RESUME,
    content_text=resume_text,              # ✅ Plain text
    content_structured=json.dumps(content_structured),  # ❌ ADD THIS
    status=GenerationStatus.COMPLETED,
    ats_score=ats_result["score"],
    ats_feedback=ats_result.get("analysis", ""),
    llm_metadata=str(ats_result.get("llm_metadata", {}))
)
```

---

## Testing Checklist

After implementation, verify:

- [ ] Header includes all 8 fields (name, title, email, phone, location, linkedin, github, website)
- [ ] Skills section has 4 categories (technical, soft, languages, certifications)
- [ ] Technical skills are NOT limited to 20 items
- [ ] Languages include name and proficiency
- [ ] Certifications include all 5 fields
- [ ] Experiences include `is_current` boolean
- [ ] Projects include `start_date` and `end_date` (nullable)
- [ ] Education includes `honors` array
- [ ] All education entries included (not just first 2)
- [ ] Metadata calculates total years correctly
- [ ] Metadata includes `total_projects` and `total_certifications`
- [ ] Both `content_text` and `content_structured` are populated
- [ ] JSON structure validates against schema

---

## Notes

1. **Backward Compatibility**: Keep `content_text` for existing features (search, display, history)
2. **Data Source**: Use enhanced versions when available (`enhanced_description`, `enhanced_professional_summary`)
3. **Nullability**: Handle optional fields gracefully (use `None` or empty arrays)
4. **Date Formatting**: ISO format dates (YYYY-MM-DD) from database
5. **ID Consistency**: Use string UUIDs for all IDs in JSON

---

**Last Updated**: December 2025
**Status**: Ready for Implementation
**Target Sprint**: Sprint 6

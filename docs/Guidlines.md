# AI Tailored Resume and Cover Letter Generation Flow

## Core Principle
Generation is grounded in the user's **stored preferences profile** and master resume content. The system extracts reusable characteristics once, then applies them efficiently to each job application. Content must come from the user's master resume/profile and target job posting—never fabricate experiences or skills.

---

## Phase 1: Initial Profile Setup (One-Time)

### Step 1.1: Collect Initial Inputs
**Required**:
- **Master Resume**: Source-of-truth for all experiences, projects, skills, education

**Recommended for Quality**:
- **User Cover Letter**: Sample to auto-extract writing style and voice preferences
- **Example Resume(s)**: Well-structured exemplars to auto-extract layout/formatting preferences

**Optional**:
- **Manual Preferences**: User can override auto-generated settings

### Step 1.2: Auto-Generate Writing Style Profile
**Source**: LLM analysis of user-provided cover letter  
**Process**:
1. User uploads cover letter (any format: PDF, Docx, text)
2. LLM analyzes and extracts writing characteristics
3. System auto-generates preference profile
4. User reviews and can adjust settings

**Auto-Generated Characteristics** (user-adjustable after generation):

```json
{
  "writing_style": {
    "vocabulary_level": "professional|academic|conversational|technical",
    "vocabulary_complexity": 1-10,
    "tone": "formal|semi-formal|enthusiastic|authoritative",
    "sentence_structure": "simple|compound|complex|varied",
    "active_voice_preference": 0.0-1.0,
    "first_person_usage": "never|minimal|moderate|frequent"
  },
  "voice_characteristics": {
    "action_verb_style": ["spearheaded", "orchestrated", "pioneered"],
    "transition_phrases": ["Additionally", "Furthermore", "Moreover"],
    "closing_patterns": "call-to-action|gratitude|enthusiasm"
  }
}
```

**User Controls**:
- Adjust tone formality slider (1-10)
- Toggle technical jargon usage
- Preview generated sample paragraphs with different settings
- Upload new cover letter to regenerate profile
- **Reset to defaults** if unsatisfied with extraction

**LLM Prompt for Extraction**:
```
Analyze the following cover letter and extract writing style characteristics:
[User's cover letter text]

Extract and return:
1. Vocabulary level (professional/academic/conversational/technical)
2. Vocabulary complexity score (1-10)
3. Tone (formal/semi-formal/enthusiastic/authoritative)
4. Sentence structure patterns
5. Active vs passive voice ratio
6. First-person usage frequency
7. Top 10 action verbs used
8. Common transition phrases
9. Closing pattern style
```

### Step 1.3: Auto-Generate Structural Preferences
**Source**: LLM analysis of example resume(s)  
**Process**:
1. User uploads 1-3 example resumes (PDF, Docx, or text)
2. LLM analyzes structure, formatting, and section organization
3. System auto-generates layout preferences
4. User reviews and can adjust via visual editor

**Auto-Generated Characteristics** (user-adjustable after generation):

```json
{
  "layout_preferences": {
    "section_order": ["summary", "experience", "education", "skills", "projects"],
    "bullet_point_style": "standard|achievement|CAR|STAR",
    "bullet_points_per_role": 3-6,
    "date_format": "MM/YYYY|Month YYYY|YYYY",
    "location_display": "city_state|city_country|remote_ok"
  },
  "section_formatting": {
    "summary_length": "2-3 sentences|short paragraph|bullet points",
    "project_description_length": "1-2 sentences|full paragraph",
    "skill_grouping": "by_category|by_proficiency|flat_list",
    "certification_display": "inline|separate_section|omit"
  }
}
```

**User Controls**:
- Drag-and-drop section reordering
- Choose bullet point format with live preview
- Set target resume length (1 page / 2 pages)
- Configure ATS optimization level (minimal / balanced / aggressive)
- **Upload additional examples** to refine extraction
- **Reset to defaults** if unsatisfied

**LLM Prompt for Extraction**:
```
Analyze the following example resume and extract structural characteristics:
[Example resume text]

Extract and return:
1. Section order (exact sequence)
2. Bullet point style (standard/CAR/STAR/achievement-focused)
3. Average bullet points per experience (min-max range)
4. Date format pattern
5. Location display style
6. Summary/objective length and format
7. Project description style
8. Skill categorization approach
9. Overall layout structure (single-column/two-column)
10. White space and density assessment
```

**Quality Validation**: 
- If multiple example resumes uploaded, LLM identifies common patterns vs variations
- Warns user about conflicting styles and asks for preference
- Scores consistency across examples (0.0-1.0)

### Step 1.4: Auto-Extract & Store Content Strengths
**Source**: Master resume analysis  
**Stored Characteristics** (auto-generated, user-refinable):

```json
{
  "skill_taxonomy": {
    "technical_skills": {
      "web_development": ["React", "Node.js", "FastAPI"],
      "mobile_development": ["Flutter", "Dart"],
      "ai_ml": ["PyTorch", "Scikit-learn"],
      "proficiency_scores": {"React": 0.95, "Flutter": 0.80}
    },
    "domain_expertise": ["fintech", "healthcare", "e-commerce"],
    "soft_skills": ["leadership", "cross-functional collaboration"]
  },
  "achievement_patterns": {
    "quantification_style": "percentages|absolute_numbers|scale_descriptors",
    "impact_categories": ["performance", "cost_savings", "user_growth"],
    "common_metrics": ["latency reduction", "conversion rate", "test coverage"]
  },
  "experience_ranking": {
    "relevance_weights": {
      "tech_stack_match": 0.40,
      "role_seniority": 0.25,
      "recency": 0.20,
      "impact_scale": 0.15
    }
  }
}
```

**User Controls**:
- Mark skills as "expert" / "proficient" / "familiar"
- Highlight key achievements for emphasis
- Set skill category priorities for different job types
- Define custom achievement templates

### Step 1.5: Store Generation Parameters
**Source**: User configuration  
**Stored Settings** (fully user-configurable):

```json
{
  "quality_targets": {
    "ats_optimization": "minimal|balanced|aggressive",
    "keyword_density": 0.02-0.08,
    "readability_score": "8th_grade|college|professional",
    "length_targets": {
      "resume_pages": 1-2,
      "cover_letter_words": 250-400,
      "summary_words": 50-100
    }
  },
  "content_policies": {
    "keyword_stuffing_tolerance": "strict|moderate|permissive",
    "paraphrase_aggressiveness": 0.0-1.0,
    "tone_normalization": "preserve_original|normalize_casual|elevate_formal",
    "missing_skill_handling": "omit|emphasize_adjacent|note_willingness"
  },
  "industry_presets": {
    "target_industries": ["tech", "finance", "healthcare"],
    "compliance_requirements": ["FAANG_format", "federal_resume"]
  }
}
```

**User Controls**:
- Choose industry-specific templates
- Set keyword matching aggressiveness
- Configure fallback behavior for skill gaps
- Enable/disable ATS-specific optimizations

---

## Phase 2: Job-Specific Generation (Per Application)

### Step 2.1: Analyze Job Posting
**Input**: Target job description  
**Analysis** (real-time, not stored):
- Extract required skills, tech stack, seniority level
- Identify top 10-15 keywords for emphasis
- Parse years of experience, citizenship, sponsorship requirements
- Classify job type (entry/mid/senior, IC/lead/management)

### Step 2.2: Content Matching & Ranking
**Process**:
1. Score master resume experiences/projects against job requirements
2. Apply stored `experience_ranking.relevance_weights`
3. Reorder sections based on stored `layout_preferences.section_order`
4. Filter skills using stored `skill_taxonomy` + job keywords

**Output**: Prioritized content selection for this specific job

### Step 2.3: Generate Tailored Documents
**Process**:
1. Apply stored `writing_style` profile to all content
2. Use stored `layout_preferences` for structure
3. Incorporate job keywords naturally (respecting `keyword_density` setting)
4. Format using stored `section_formatting` rules
5. **Validate against example resumes for quality consistency**

**Quality Validation Against Examples**:
```
LLM Validation Prompt:
Compare the generated resume with the user's example resumes:
[Generated resume]
[Example resume(s)]

Validate:
1. Structural consistency (section order, bullet format)
2. Tone and formality alignment
3. Content density and white space similarity
4. Professional polish level
5. ATS-friendliness compared to examples

Return:
- Consistency score (0.0-1.0)
- List of deviations with severity (minor/moderate/major)
- Recommendations for alignment
```

**Outputs**:
- Tailored resume (PDF/Docx + structured JSON)
- Tailored cover letter (styled per user profile + JSON)
- **Generation Report**:
  - Keyword coverage (matched: 12/15 required keywords)
  - Missing skills with suggestions
  - ATS score estimate
  - **Quality consistency score vs. example resumes**
  - Recommendations for improvement

### Step 2.4: User Review & Iterative Refinement
**User Actions**:
1. **Review generated documents** in preview mode
2. **Provide feedback** via multiple methods:
   - Quick adjustments: "too formal" / "missing emphasis on X" / "great!"
   - **Direct editing**: Mark up generated resume with changes
   - **Preference updates**: Adjust tone slider, keyword density, etc.

**System Response Options**:

**Option A: Quick Regeneration**
- User clicks "Too formal" → system regenerates with tone -2
- User clicks "Emphasize ML experience" → system boosts ML project ranking
- Regeneration time: ~3-5 seconds (preference tweak only)

**Option B: Learn from Edits**
- User manually edits generated resume (changes wording, reorders bullets)
- System analyzes edits: "User prefers 'developed' over 'created', moved ML project higher"
- Offers to update preferences: "Apply these changes to future generations?"
- If accepted, updates `writing_style.action_verb_style` and `experience_ranking.relevance_weights`

**Option C: Comparative Refinement**
- User uploads their manually edited version
- System performs diff analysis against generated version
- Extracts preference adjustments automatically
- **Validates against example resumes**: "Your edits align better with example resume style"
- Updates profile settings with extracted preferences

**Learning & Feedback Loop** (optional but recommended):
```
LLM Analysis of User Edits:
Original generated text: [text]
User's edited version: [text]
Example resumes for reference: [examples]

Analyze changes:
1. Vocabulary substitutions (identify patterns)
2. Structural reorganizations
3. Content additions/removals
4. Tone shifts
5. Formatting adjustments

Extract preference updates:
- Writing style adjustments
- Content ranking changes
- Structural preferences
- Quality expectations

Validate if edits improve alignment with example resumes.
Return: Suggested preference profile updates
```

**Job-Specific Overrides** (stored separately):
- "For data science roles, emphasize ML projects 2x"
- "For startup roles, use more enthusiastic tone (+2 formality)"
- "For finance roles, omit Project X"
- These apply automatically to matching future jobs

---

## Phase 3: Continuous Improvement & Quality Assurance

### Option A: Incremental Profile Updates
**Triggers**:
- User uploads new master resume → re-extract content strengths
- **User uploads new example resume → LLM re-analyzes + validates consistency**
- **User uploads new cover letter → LLM re-generates writing style profile**

**Process**:
1. Re-run LLM extraction for updated input
2. **Compare with existing preferences** (show diff)
3. **Validate quality**: Check if new preferences improve or degrade consistency
4. User approves/rejects changes
5. Merge approved updates into profile

**Quality Validation for Updates**:
```
LLM Validation Prompt:
Current preferences: [existing profile]
New extraction from updated input: [new preferences]
Historical example resumes: [examples]

Compare and assess:
1. Are new preferences consistent with examples?
2. Will changes improve or degrade generation quality?
3. Are there conflicts between old and new preferences?
4. Recommendation: accept, reject, or merge selectively?

Return: Detailed comparison with quality impact assessment
```

### Option B: Manual Tuning & A/B Testing
**User Interface Features**:

1. **"Style Lab"**: Test writing style settings on sample content
   - Adjust tone slider → see instant preview on master resume content
   - Compare side-by-side with example resumes
   - **LLM validates alignment**: "Current settings match example resume style at 87%"

2. **"Layout Designer"**: Visual editor for section order and formatting
   - Drag-and-drop section reordering
   - Choose bullet point formats with live preview
   - **Consistency check**: Highlights deviations from example resumes

3. **"Skill Manager"**: Tag skills, set proficiency, define categories
   - Auto-categorized from master resume
   - User refines and adds proficiency levels
   - Industry-specific skill groupings

4. **"Generation Presets"**: Save configurations for different job types
   - "Tech Startup" preset: enthusiastic tone, innovation emphasis
   - "Enterprise" preset: formal tone, stability/scale emphasis
   - "Research" preset: academic vocabulary, publication focus
   - Each preset validated against relevant example resumes

5. **"A/B Comparison"**: Generate multiple versions for testing
   - System generates 2-3 variations with slight preference differences
   - User picks winner or hybrid approach
   - **LLM analyzes choice**: "You prefer more concise bullet points (-15% length)"
   - Auto-updates preferences based on selections

### Option C: AI-Assisted Quality Monitoring

**Continuous Quality Checks**:
```
After each generation, LLM validates:

Quality Checklist:
1. Structural consistency with example resumes (target: 90%+)
2. Writing style alignment with user cover letter (target: 85%+)
3. ATS compliance score (target: based on user setting)
4. Keyword coverage vs job requirements (target: 80%+)
5. Professional polish level matching examples

If any metric falls below target:
- Flag for user review
- Suggest preference adjustments
- Offer to regenerate with corrections
```

**Trend Analysis & Insights**:
- Track generation quality scores over time
- "Your applications for senior roles perform better with formal tone (+3)"
- "Resumes with 4-5 bullets per role get higher consistency scores than 6-7"
- "ML project emphasis increased success for data science applications"
- Suggest preference optimizations based on patterns

**Example Resume Drift Detection**:
- Monitor if generated resumes drift from example quality over time
- **Weekly/monthly quality audit**: Batch-validate recent generations against examples
- Alert user: "Recent generations show 12% decrease in style consistency"
- Recommend preference recalibration or example refresh

### Option D: Feedback from Real-World Results

**Application Outcome Tracking** (optional premium feature):
- User marks applications: "Got interview" / "Rejected" / "No response"
- System correlates with generation settings used
- Identifies high-performing preference combinations
- **A/B testing at scale**: "Resume version A (formal tone) gets 23% more responses than version B"

**Collaborative Learning** (privacy-preserving):
- Anonymized aggregation of successful preference patterns
- "Users in software engineering with 5-7 years experience see best results with..."
- Offer to apply proven patterns to user's profile (opt-in)

---

## Revision & Regeneration Workflows

### Workflow 1: Quick Adjustment Regeneration
**Scenario**: User wants minor changes to generated resume

1. User selects quick adjustment option:
   - "Make more formal" (+2 tone)
   - "Emphasize leadership experience"
   - "Reduce to 1 page"
   
2. System regenerates with adjustments (~3-5 seconds)

3. **Quality validation**: Ensure adjustments maintain consistency with examples

4. User accepts or requests further tweaks

### Workflow 2: Edit-Based Learning
**Scenario**: User manually edits generated resume

1. User downloads generated resume, makes edits locally

2. User uploads edited version to system

3. **LLM performs diff analysis**:
```
Compare generated vs user-edited versions:

Identify changes:
- Word substitutions: ["created" → "developed", "managed" → "led"]
- Content reordering: [Moved ML project from position 3 to 1]
- Structural changes: [Reduced bullets per role from 5 to 4]
- Tone shifts: [More action-oriented verbs]

Extract preference learnings:
- Preferred action verbs for this user/role type
- Content prioritization patterns
- Optimal bullet count
- Formality adjustments

Validate against example resumes:
- Do user edits align better with examples? [Yes/No]
- Quality improvement score: [+12%]

Recommend preference updates
```

4. System presents findings: "You prefer 'developed' over 'created' and prioritize ML projects for data roles"

5. User approves preference updates → applied to future generations

6. **Store as job-type-specific override** if applicable

### Workflow 3: Multi-Version Refinement
**Scenario**: User wants to compare multiple approaches

1. User requests generation with variation: "Generate 3 versions: formal, balanced, enthusiastic"

2. System generates 3 versions using preference variations

3. **Each version validated against example resumes** with consistency scores

4. User reviews side-by-side comparison

5. User selects favorite or requests hybrid: "Use version A's tone with version B's structure"

6. System learns from selection and refines preference profile

7. **Quality check**: Ensure hybrid maintains example consistency

### Workflow 4: Preference Reset & Recalibration
**Scenario**: User uploads significantly better example resume

1. User uploads new gold-standard example resume

2. **LLM analyzes quality difference**:
   - Compare new example vs current examples
   - Assess if new example represents quality upgrade
   - Identify key differences in style/structure

3. System offers options:
   - **"Recalibrate"**: Re-extract all preferences from new example
   - **"Merge"**: Blend new example patterns with existing preferences
   - **"Replace"**: Use new example, archive old ones

4. If recalibrate selected:
   - Re-run all extraction LLM prompts
   - Generate new preference profile
   - **Preview impact**: Show sample generation with new vs old preferences
   - User approves transition

5. **Validate all stored job-specific overrides** still make sense with new baseline

---

## Stored Preferences Schema (Database Design)

```python
# User Generation Profile
class UserGenerationProfile(BaseModel):
    user_id: str
    
    # Style Profile (LLM-extracted from cover letter, user-refinable)
    writing_style: WritingStyleConfig
    voice_characteristics: VoiceCharacteristics
    writing_style_source: str  # "auto_generated" | "user_customized"
    writing_style_last_extracted: datetime  # When LLM last analyzed
    
    # Structural Preferences (LLM-extracted from examples, user-refinable)
    layout_preferences: LayoutConfig
    section_formatting: SectionFormattingConfig
    layout_source: str  # "auto_generated" | "user_customized"
    layout_last_extracted: datetime
    
    # Content Strengths (auto-generated from master resume)
    skill_taxonomy: SkillTaxonomy
    achievement_patterns: AchievementPatterns
    experience_ranking: RankingWeights
    
    # Generation Parameters (user-configured)
    quality_targets: QualityConfig
    content_policies: ContentPolicyConfig
    industry_presets: List[str]
    
    # Reference Documents (stored for validation)
    example_resumes: List[ExampleResumeReference]  # Original examples
    user_cover_letter: Optional[CoverLetterReference]
    
    # Quality Tracking
    quality_metrics: QualityMetrics
    consistency_score_history: List[ConsistencyScore]  # Track over time
    
    # Job-Specific Overrides (learned from user feedback)
    job_type_overrides: Dict[str, PreferenceOverride]  # e.g., {"data_science": {...}}
    
    # Metadata
    created_at: datetime
    last_updated: datetime
    version: int  # Track schema changes
    preference_generation: int  # Increment on each recalibration

class ExampleResumeReference(BaseModel):
    """Reference to uploaded example resume"""
    id: str
    filename: str
    upload_date: datetime
    content_hash: str  # Detect if file changed
    extracted_preferences: Dict  # What was learned from this example
    quality_score: float  # LLM-assessed quality (0.0-1.0)
    is_active: bool  # Can be archived without deleting

class ConsistencyScore(BaseModel):
    """Track quality consistency over time"""
    timestamp: datetime
    job_id: Optional[str]
    generation_id: str
    structural_consistency: float  # vs example resumes
    style_consistency: float  # vs cover letter
    ats_score: float
    overall_quality: float
    deviations: List[str]  # What didn't match

class PreferenceOverride(BaseModel):
    """Job-type-specific preference adjustments"""
    job_category: str  # "data_science", "frontend", "management"
    tone_adjustment: int  # +/- formality
    emphasized_skills: List[str]
    emphasized_projects: List[str]
    suppressed_content: List[str]
    keyword_density_override: Optional[float]
    created_from: str  # "user_feedback" | "a_b_test" | "manual"
    success_rate: Optional[float]  # If tracking outcomes
```

---

## LLM Validation & Quality Prompts

### Prompt 1: Writing Style Extraction
```
TASK: Extract writing style characteristics from user's cover letter

INPUT:
[User's cover letter text]

ANALYSIS REQUIRED:
1. Vocabulary Analysis:
   - Level: professional/academic/conversational/technical
   - Complexity: Rate 1-10 based on word choice sophistication
   - Industry-specific jargon usage frequency
   
2. Tone & Voice:
   - Formality: formal/semi-formal/informal/enthusiastic/authoritative
   - Confidence level: assertive/balanced/humble
   - Passion indicators: emotional words, exclamation usage
   
3. Sentence Structure:
   - Average sentence length
   - Complexity: simple/compound/complex/varied
   - Paragraph structure patterns
   
4. Voice Preferences:
   - Active vs passive voice ratio
   - First-person usage: never/minimal/moderate/frequent
   - Second-person addressing
   
5. Stylistic Elements:
   - Top 10 action verbs used
   - Common transition phrases
   - Opening sentence pattern
   - Closing pattern: call-to-action/gratitude/enthusiasm
   
6. Grammar & Punctuation:
   - Comma usage style
   - Dash/semicolon frequency
   - Sentence variety

OUTPUT FORMAT: JSON matching WritingStyleConfig + VoiceCharacteristics schema

VALIDATION: Flag any inconsistencies or unusual patterns that may need user clarification
```

### Prompt 2: Structural Preference Extraction
```
TASK: Extract structural and formatting preferences from example resume

INPUT:
[Example resume text with formatting preserved]

ANALYSIS REQUIRED:
1. Section Organization:
   - Exact section order (top to bottom)
   - Section titles used
   - Subsection groupings
   
2. Content Formatting:
   - Bullet point style: standard/CAR/STAR/achievement
   - Bullet points per experience: min-max range
   - Experience description pattern: title+company+dates, or variations
   - Date format: MM/YYYY, Month YYYY, YYYY, or range style
   
3. Layout & Density:
   - Column structure: single/two-column/hybrid
   - White space distribution: sparse/balanced/dense
   - Section spacing patterns
   - Font size variations (if detectable)
   
4. Content Length Patterns:
   - Professional summary: word count, sentence count, style
   - Experience descriptions: character/word count per role
   - Project descriptions: length and detail level
   - Education section detail level
   
5. Skill Presentation:
   - Categorized by type or flat list
   - Proficiency indicators present?
   - Certification display: inline/separate/omitted
   
6. Special Elements:
   - Contact info placement and format
   - LinkedIn/portfolio/GitHub inclusion
   - Awards/publications section
   - Language proficiency display

OUTPUT FORMAT: JSON matching LayoutConfig + SectionFormattingConfig schema

QUALITY ASSESSMENT: Rate resume quality 0.0-1.0 based on professional polish, ATS-friendliness, clarity
```

### Prompt 3: Generation Quality Validation
```
TASK: Validate generated resume quality against user's example resumes

INPUTS:
Generated Resume: [new resume text]
Example Resume 1: [example 1 text]
Example Resume 2: [example 2 text]
User Preferences: [stored preference profile JSON]

VALIDATION CHECKS:
1. Structural Consistency (weight: 30%):
   - Section order matches preferred pattern?
   - Bullet format consistent with examples?
   - Content density similar to examples?
   - Scoring: 0.0-1.0
   
2. Style Consistency (weight: 25%):
   - Tone and formality match user cover letter style?
   - Vocabulary level appropriate?
   - Action verb usage consistent?
   - Scoring: 0.0-1.0
   
3. Professional Polish (weight: 20%):
   - Grammar and punctuation correct?
   - Parallel structure in bullets?
   - Consistent tense usage?
   - No awkward phrasing?
   - Scoring: 0.0-1.0
   
4. ATS Compliance (weight: 15%):
   - Keyword integration natural?
   - Standard section headers?
   - No complex formatting?
   - Scoring: 0.0-1.0
   
5. Content Quality (weight: 10%):
   - Achievements quantified where possible?
   - Relevant experience prioritized?
   - No fabricated information?
   - Scoring: 0.0-1.0

DEVIATION ANALYSIS:
List all deviations from example resumes with severity:
- MINOR: Small formatting differences, negligible impact
- MODERATE: Noticeable style/structure differences, may affect consistency
- MAJOR: Significant departures that hurt quality or user intent

OUTPUT FORMAT:
{
  "overall_quality_score": 0.0-1.0,
  "structural_consistency": 0.0-1.0,
  "style_consistency": 0.0-1.0,
  "professional_polish": 0.0-1.0,
  "ats_compliance": 0.0-1.0,
  "content_quality": 0.0-1.0,
  "deviations": [
    {"type": "MINOR|MODERATE|MAJOR", "description": "...", "suggestion": "..."}
  ],
  "recommendations": ["...", "..."],
  "passes_threshold": true|false  // Based on user's quality_targets
}
```

### Prompt 4: User Edit Analysis for Learning
```
TASK: Analyze user's manual edits to learn preference refinements

INPUTS:
Generated Resume (original): [original text]
User Edited Resume: [edited text]
Current Preferences: [preference profile JSON]
Example Resumes: [reference examples]

ANALYSIS REQUIRED:
1. Content Changes:
   - Word substitutions: Map original → user's choice
   - Phrase replacements
   - Sentence restructuring
   - Content additions/deletions
   
2. Structural Changes:
   - Section reordering
   - Bullet point additions/removals
   - Experience reordering
   - Formatting adjustments
   
3. Tone & Style Shifts:
   - Formality changes: more/less formal?
   - Vocabulary adjustments: simpler/more technical?
   - Voice changes: active/passive ratio shifts
   
4. Pattern Extraction:
   - Identify consistent patterns across multiple edits
   - "User always changes 'managed' → 'led'"
   - "User prefers 4 bullets per role, not 5"
   - "User emphasizes ML projects higher"
   
5. Alignment Assessment:
   - Do user edits move closer to example resume style?
   - Quality improvement score: original vs edited
   - Does edited version maintain ATS compliance?

OUTPUT FORMAT:
{
  "word_substitution_patterns": {"original": "preferred", ...},
  "structural_preference_updates": {...},
  "tone_adjustment": -2 to +2,  // More/less formal
  "content_prioritization_changes": [...],
  "quality_impact": {
    "consistency_with_examples": "+12%",
    "ats_score_change": "-3%",
    "overall_improvement": "+8%"
  },
  "recommended_preference_updates": {
    "writing_style": {...},
    "layout_preferences": {...},
    "experience_ranking": {...}
  },
  "confidence": 0.0-1.0,  // How confident in these learnings
  "apply_globally": true|false,  // Or just for this job type?
  "job_specific_override_suggestion": {...}  // If patterns job-specific
}
```

---

## Benefits of Preference-Based Architecture

### For Users:
1. **Minimal initial setup**: Upload cover letter + example resumes → LLM auto-generates preferences (10-15 min)
2. **Fast subsequent generations**: 2-3 min per application vs 10-15 min manual tailoring
3. **Consistency with quality validation**: Same professional voice, validated against your own examples
4. **Control with intelligence**: Transparent settings with AI-assisted optimization
5. **Learning system**: Improves from your edits without re-uploading documents
6. **Flexible refinement**: Quick tweaks or deep customization as needed

### For System:
1. **Reduced LLM costs**: One-time analysis vs per-generation analysis (70-80% cost reduction)
2. **Faster generation**: Pre-computed preferences, only analyze job posting (5-8s vs 20-30s)
3. **Better quality**: Refined preferences + validation > one-off document analysis
4. **Personalization depth**: Store user-specific patterns, job-type overrides, learned optimizations
5. **Quality monitoring**: Continuous validation against example baselines
6. **Feedback incorporation**: Direct edit analysis improves future generations

### For Performance:
- **Initial setup**: ~15-30 seconds LLM extraction (one-time)
- **Per-job generation**: ~5-8 seconds (vs 20-30s analyzing everything each time)
- **Regeneration with tweaks**: ~3-5 seconds (preference adjustment only)
- **Quality validation**: ~2-3 seconds (parallel with generation)
- **Edit analysis**: ~5-7 seconds (when user provides feedback)

### For Quality Assurance:
- **Automatic consistency checks** against example resumes every generation
- **Quality score tracking** over time to detect drift
- **User edit learning** to align with unspoken preferences
- **A/B testing** to find optimal preference combinations
- **Outcome correlation** (optional) to measure real-world effectiveness

---

## Migration Path from Current Flow

### Phase 1 (Immediate): Database Schema
- Add preference storage tables
- Add example resume reference storage
- Add quality metrics tracking
- Add job-specific override storage

### Phase 2 (Sprint 4): LLM Extraction Logic
- Implement writing style extraction from cover letter
- Implement structural extraction from example resumes
- Implement content strength auto-categorization
- Build preference profile generation pipeline

### Phase 3 (Sprint 5): Generation with Validation
- Integrate preferences into generation pipeline
- Implement quality validation against examples
- Build generation report with consistency scoring
- Add quick adjustment regeneration

### Phase 4 (Sprint 6): User Feedback & Learning
- Build user edit upload and diff analysis
- Implement preference update suggestions from edits
- Add A/B testing for preference optimization
- Create job-specific override management

### Phase 5 (Sprint 7): Advanced Features
- Style Lab for preference experimentation
- Layout Designer visual editor
- Trend analysis and insights dashboard
- Collaborative learning (anonymized aggregation)

---

## Example User Journey

### First-Time User Setup (15 minutes)
1. **Upload master resume** → System extracts all experiences, projects, skills
2. **Upload cover letter** → LLM analyzes, generates writing style profile
3. **Upload 1-2 example resumes** → LLM analyzes, generates layout preferences
4. **Review auto-generated preferences** → Adjust tone slider, approve settings
5. **Test generation** → Generate sample resume from master content
6. **Validate quality** → Compare with example, see consistency score (92%)
7. **Profile ready** → Can now generate tailored resumes in 2-3 minutes

### Applying to First Job (3 minutes)
1. **Select/paste job posting** → System analyzes requirements
2. **Click "Generate"** → 5-8 seconds processing
3. **Review generated resume** → Consistency score: 89%, keyword coverage: 13/15
4. **See quality report** → 2 minor deviations from example style, suggestions provided
5. **Download PDF/Docx** → Ready to submit

### Refining After Manual Edit (5 minutes)
1. **User edits resume locally** → Changes some wording, reorders bullets
2. **Upload edited version** → System analyzes changes
3. **Review learning suggestions** → "You prefer 'developed' over 'created', want ML project first"
4. **Approve updates** → Preferences updated for future generations
5. **Validated improvement** → Edited version 94% consistent with examples (+5%)

### Applying to 10th Job (2 minutes)
1. **Paste job posting** → System recognizes "data science" role type
2. **Auto-applies learned overrides** → Emphasizes ML projects, uses preferred vocabulary
3. **Generate** → 3 seconds (faster due to learned patterns)
4. **Quality validation** → 96% consistency (preferences refined over time)
5. **One-click download** → Confidence in quality, minimal review needed

---

## Success Metrics

### Quality Metrics
- **Consistency score**: Target 90%+ alignment with example resumes
- **ATS compliance**: Target 85%+ based on industry standards
- **Keyword coverage**: Target 80%+ of required keywords naturally integrated
- **User satisfaction**: Track acceptance rate of generated resumes (target: 85%+)

### Efficiency Metrics
- **Time savings**: 80%+ reduction in time per application (15 min → 3 min)
- **Regeneration rate**: <20% of generations require regeneration
- **Learning effectiveness**: Preference quality improves over 5+ generations
- **Edit incorporation**: 90%+ of user edit patterns successfully learned

### System Performance
- **Generation speed**: <10 seconds for 95% of requests
- **LLM cost per generation**: <$0.15 (vs $0.60 without preferences)
- **Quality validation overhead**: <3 seconds additional time
- **Database query performance**: <100ms for preference retrieval
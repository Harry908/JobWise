sequenceDiagram
    participant U as User
    participant UI as Frontend UI
    participant IO as Integration Orchestrator
    participant BP as Backend Processor
    participant JS as Job Search
    participant PC as Profile Compiler
    participant JA as Job Analyzer
    participant DG as Document Generator
    participant QV as Quality Validator
    participant PE as PDF Exporter
    participant LLM as LLM Service
    participant DB as Database
    
    U->>UI: Search for jobs
    UI->>IO: Job search request
    IO->>JS: Query job listings
    JS-->>IO: Job results
    IO-->>UI: Display job cards
    UI-->>U: Show swipeable job cards
    
    U->>UI: Save job for tailoring
    UI->>IO: Generate documents request
    IO->>BP: Process generation request
    
    BP->>DB: Fetch user profile
    DB-->>BP: Profile data
    BP->>PC: Compile profile context
    PC-->>BP: Structured profile
    
    BP->>JA: Analyze job description
    JA-->>BP: Job requirements matrix
    
    BP->>DG: Generate tailored documents
    DG->>LLM: Resume generation prompt
    LLM-->>DG: Resume draft
    DG->>LLM: Cover letter prompt
    LLM-->>DG: Cover letter draft
    DG->>LLM: Optimization prompt
    LLM-->>DG: Optimized versions
    
    DG->>QV: Validate documents
    QV-->>DG: Quality scores
    
    DG->>PE: Convert to PDF
    PE-->>DG: PDF documents
    
    DG-->>BP: Final documents
    BP->>DB: Store generated documents
    BP-->>IO: Generation complete
    IO-->>UI: Documents ready signal
    UI->>U: Display editable documents
    
    U->>UI: Review and edit
    UI->>U: Download PDF
    U->>UI: Apply to job
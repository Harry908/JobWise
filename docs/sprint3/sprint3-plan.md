# Sprint 3 Detailed Plan - Mobile UI for Generation & Job Browsing

**Project:** JobWise - AI-Powered Job Application Assistant  
**Sprint Duration:** Week 12 (October 28 - November 3, 2025)  
**Sprint Goal:** Implement mobile UI for job browsing, generation flow, and document preview  
**Time Budget:** 40 hours  
**Deliverable Date:** Monday, November 4, 2025

---

## 🎯 Sprint 3 Objectives

### Primary Goals
1. **Job Browsing UI**: Swipeable job cards with search and filtering
2. **Generation Flow UI**: Profile + Job selection → Generation request → Progress tracking
3. **Document Preview UI**: View generated resumes with template switching
4. **API Integration**: Connect mobile app to Generation & Document APIs
5. **State Management**: Implement Riverpod providers for new features

### Success Criteria
- ✅ Job browsing with swipeable cards and search functionality
- ✅ Generation request flow with real-time progress tracking
- ✅ Document preview with template switching (3 templates)
- ✅ API integration with error handling and offline support
- ✅ 15+ widget tests covering core UI components
- ✅ Smooth animations and transitions throughout
- ✅ Complete user flow: Browse Jobs → Save → Generate → Preview → Download

---

## 📋 Sprint 3 Task Breakdown (40 Hours)

### Phase 1: API Client Integration (8 hours)

#### Task 1.1: Generation API Client (3 hours)
**Files to Create:**
- `mobile_app/lib/services/api/generation_api_client.dart`

**Deliverables:**
```dart
class GenerationApiClient {
  // Core Generation Operations
  Future<Generation> createGeneration({
    required String profileId,
    required String jobId,
    String? templateId,
    Map<String, dynamic>? options,
  });
  
  Future<Generation> getGenerationById(String id);
  Future<GenerationResult> getGenerationResult(String id);
  Future<Generation> regenerateWithFeedback(String id, String feedback);
  Future<void> cancelGeneration(String id);
  
  // Generation Management
  Future<PaginatedResponse<Generation>> listGenerations({
    GenerationStatus? status,
    int page = 1,
    int limit = 20,
  });
  
  Future<void> provideFeedback(String id, String feedback);
  Future<List<ResumeTemplate>> getAvailableTemplates();
  
  // Analytics
  Future<GenerationAnalytics> getGenerationAnalytics(String id);
}

// Models
class Generation {
  final String id;
  final String userId;
  final String profileId;
  final String jobId;
  final GenerationStatus status;
  final GenerationStage stage;
  final double progress; // 0.0 to 1.0
  final DateTime? startedAt;
  final DateTime? completedAt;
  final String? templateId;
  
  const Generation({...});
}

enum GenerationStatus { pending, inProgress, completed, failed, cancelled }
enum GenerationStage { analyzing, compiling, generating, validating, exporting }

class GenerationResult {
  final String generationId;
  final ResumeContent content;
  final ATSScore atsScore;
  final List<String> recommendations;
  final Map<String, dynamic> metadata;
  
  const GenerationResult({...});
}

class ResumeContent {
  final Map<String, dynamic> sections; // Flexible section structure
  final String? summary;
  final List<Experience> experiences;
  final List<Education> education;
  final Skills skills;
  final List<Project> projects;
  
  const ResumeContent({...});
}

class ATSScore {
  final double overallScore; // 0.0 to 1.0
  final double keywordMatch;
  final double formatCompliance;
  final List<String> matchedKeywords;
  final List<String> missingKeywords;
  
  const ATSScore({...});
}
```

#### Task 1.2: Document API Client (2 hours)
**Files to Create:**
- `mobile_app/lib/services/api/document_api_client.dart`

**Deliverables:**
```dart
class DocumentApiClient {
  // Document Management
  Future<PaginatedResponse<Document>> listDocuments({
    DocumentStatus? status,
    int page = 1,
    int limit = 20,
  });
  
  Future<Document> getDocumentById(String id);
  Future<void> deleteDocument(String id);
  Future<Document> updateDocumentMetadata(String id, Map<String, dynamic> metadata);
  
  // Export Operations
  Future<ExportResponse> exportDocument({
    required String documentId,
    required ExportFormat format,
    String? templateId,
    ExportOptions? options,
  });
  
  Future<Uint8List> downloadDocument(String documentId, ExportFormat format);
  Future<Uint8List> previewDocument(String generationId, String templateId);
  Future<List<ExportFormat>> getAvailableFormats();
}

// Models
class Document {
  final String id;
  final String userId;
  final String generationId;
  final String title;
  final DocumentStatus status;
  final List<ExportFormat> formatsAvailable;
  final Map<String, dynamic> metadata;
  final DateTime createdAt;
  final DateTime updatedAt;
  
  const Document({...});
}

enum DocumentStatus { draft, ready, exported, archived }
enum ExportFormat { pdf, docx, txt, html }

class ExportResponse {
  final String documentId;
  final String downloadUrl;
  final DateTime expiresAt;
  
  const ExportResponse({...});
}

class ExportOptions {
  final String? templateId;
  final double fontSize;
  final EdgeInsets margins;
  final String? colorScheme;
  
  const ExportOptions({...});
}
```

#### Task 1.3: Job API Client Enhancement (2 hours)
**Files to Update:**
- `mobile_app/lib/services/api/job_api_client.dart`

**Deliverables:**
```dart
class JobApiClient {
  // Existing CRUD methods
  Future<Job> createJob(Job job);
  Future<Job> getJobById(String id);
  Future<Job> updateJob(String id, Job job);
  Future<void> deleteJob(String id);
  
  // NEW: Search and Filtering
  Future<PaginatedResponse<Job>> searchJobs({
    String? query,
    List<String>? keywords,
    String? location,
    JobStatus? status,
    JobSource? source,
    int page = 1,
    int limit = 20,
    String? sortBy,
    SortOrder? sortOrder,
  });
  
  // NEW: Job Status Management
  Future<Job> updateJobStatus(String id, JobStatus status);
  Future<List<Job>> getJobsByStatus(JobStatus status);
  
  // NEW: Job Statistics
  Future<JobStatistics> getJobStatistics();
}

enum JobStatus { draft, active, saved, applied, archived }
enum JobSource { api, static, userCreated, scraped, imported }
enum SortOrder { asc, desc }

class JobStatistics {
  final int totalJobs;
  final int savedJobs;
  final int appliedJobs;
  final Map<String, int> jobsByStatus;
  
  const JobStatistics({...});
}
```

#### Task 1.4: State Management - Providers (1 hour)
**Files to Create:**
- `mobile_app/lib/providers/generation_provider.dart`
- `mobile_app/lib/providers/document_provider.dart`
- `mobile_app/lib/providers/job_provider.dart`

**Deliverables:**
```dart
// Generation State Management
class GenerationNotifier extends StateNotifier<GenerationState> {
  final GenerationApiClient _apiClient;
  
  Future<void> startGeneration(String profileId, String jobId, String? templateId);
  Future<void> pollGenerationProgress(String generationId);
  Future<void> loadGenerationResult(String generationId);
  Future<void> regenerateWithFeedback(String generationId, String feedback);
  Future<void> cancelGeneration(String generationId);
  Future<void> loadGenerationHistory();
}

class GenerationState {
  final Generation? currentGeneration;
  final GenerationResult? currentResult;
  final List<Generation> history;
  final bool isLoading;
  final String? error;
  
  const GenerationState({...});
}

// Document State Management
class DocumentNotifier extends StateNotifier<DocumentState> {
  final DocumentApiClient _apiClient;
  
  Future<void> loadDocuments();
  Future<void> exportDocument(String documentId, ExportFormat format, String? templateId);
  Future<void> downloadDocument(String documentId, ExportFormat format);
  Future<void> previewDocument(String generationId, String templateId);
  Future<void> deleteDocument(String documentId);
}

// Job State Management (Enhanced)
class JobNotifier extends StateNotifier<JobState> {
  final JobApiClient _apiClient;
  
  Future<void> searchJobs(String? query, Map<String, dynamic>? filters);
  Future<void> loadJobsByStatus(JobStatus status);
  Future<void> saveJob(String jobId);
  Future<void> markJobAsApplied(String jobId);
  Future<void> loadJobStatistics();
}
```

---

### Phase 2: Job Browsing UI (10 hours)

#### Task 2.1: Job Card Widget (3 hours)
**Files to Create:**
- `mobile_app/lib/widgets/job_card.dart`
- `mobile_app/lib/widgets/swipeable_job_cards.dart`

**Deliverables:**
```dart
// Swipeable Job Card with Tinder-style interactions
class SwipeableJobCard extends StatefulWidget {
  final Job job;
  final VoidCallback onSwipeRight; // Save/Like
  final VoidCallback onSwipeLeft;  // Skip/Pass
  final VoidCallback onTap;        // View details
  
  const SwipeableJobCard({...});
}

// Job Card Display
class JobCard extends StatelessWidget {
  final Job job;
  final bool compact; // Compact vs. detailed view
  
  // Displays:
  // - Job title (headline)
  // - Company name and logo
  // - Location (remote/hybrid/onsite)
  // - Salary range (if available)
  // - Posted date (e.g., "2 days ago")
  // - Key requirements (3-5 tags)
  // - Job type badge (full-time, contract, etc.)
  // - Match score (if available)
  
  const JobCard({...});
}

// Job Details Bottom Sheet
class JobDetailsSheet extends StatelessWidget {
  final Job job;
  final VoidCallback onSave;
  final VoidCallback onGenerate;
  
  // Displays:
  // - Full job description
  // - Requirements (bulleted list)
  // - Responsibilities
  // - Benefits
  // - Application instructions
  // - Company information
  // - Actions: Save, Generate Resume, Share, Report
  
  const JobDetailsSheet({...});
}
```

**UI Features:**
- Swipe right to save job (animated checkmark)
- Swipe left to skip job (animated X)
- Tap to view full details in bottom sheet
- Smooth card animations with spring physics
- Loading shimmer for async card loading
- Empty state with CTA for search

#### Task 2.2: Job Search Screen (3 hours)
**Files to Create:**
- `mobile_app/lib/screens/job_search_screen.dart`
- `mobile_app/lib/widgets/job_search_bar.dart`
- `mobile_app/lib/widgets/job_filters_sheet.dart`

**Deliverables:**
```dart
class JobSearchScreen extends ConsumerStatefulWidget {
  const JobSearchScreen({Key? key}) : super(key: key);
}

class _JobSearchScreenState extends ConsumerState<JobSearchScreen> {
  // Features:
  // - Search bar with autocomplete
  // - Filter button (opens bottom sheet)
  // - Swipeable job cards deck
  // - "No more jobs" empty state
  // - Pull to refresh
  // - Tab bar: Browse | Saved | Applied
  
  Widget build(BuildContext context) {
    // Layout:
    // AppBar with search bar and filter icon
    // TabBar (Browse, Saved, Applied)
    // Body: SwipeableJobCards or ListView of saved/applied jobs
    // FAB: Add custom job (opens create job form)
  }
}

// Job Filters Bottom Sheet
class JobFiltersSheet extends StatefulWidget {
  final JobFilters currentFilters;
  final Function(JobFilters) onApplyFilters;
  
  // Filters:
  // - Keywords (multi-select chips)
  // - Location (text input with suggestions)
  // - Job Type (full-time, part-time, contract, internship)
  // - Experience Level (entry, mid, senior)
  // - Remote/Hybrid/Onsite
  // - Salary Range (slider)
  // - Date Posted (last 24h, week, month, all)
  
  const JobFiltersSheet({...});
}
```

#### Task 2.3: Saved Jobs Dashboard (2 hours)
**Files to Create:**
- `mobile_app/lib/screens/saved_jobs_screen.dart`
- `mobile_app/lib/widgets/saved_job_card.dart`

**Deliverables:**
```dart
class SavedJobsScreen extends ConsumerWidget {
  // Features:
  // - List of saved jobs with status badges
  // - Group by status (Saved, Generating, Generated, Applied)
  // - Swipe to delete or mark as applied
  // - Tap to view details or generate resume
  // - Sort options (date saved, match score, company)
  // - Empty state with CTA to browse jobs
  
  const SavedJobsScreen({Key? key}) : super(key: key);
}

class SavedJobCard extends StatelessWidget {
  final Job job;
  final Generation? generation; // If generation in progress or completed
  final VoidCallback onGenerateResume;
  final VoidCallback onViewDetails;
  final VoidCallback onDelete;
  
  // Displays:
  // - Job title and company
  // - Status badge (Saved, Generating, Generated, Applied)
  // - Generation progress (if in progress)
  // - Action buttons: Generate Resume, View Details, Delete
  // - Match score indicator
  
  const SavedJobCard({...});
}
```

#### Task 2.4: Job Statistics Widget (2 hours)
**Files to Create:**
- `mobile_app/lib/widgets/job_statistics_card.dart`
- `mobile_app/lib/screens/job_statistics_screen.dart`

**Deliverables:**
```dart
class JobStatisticsCard extends ConsumerWidget {
  // Compact statistics card for dashboard
  // - Total saved jobs
  // - Resumes generated
  // - Applications submitted
  // - Tap to view detailed statistics
  
  const JobStatisticsCard({Key? key}) : super(key: key);
}

class JobStatisticsScreen extends ConsumerWidget {
  // Detailed statistics and analytics
  // - Jobs by status (pie chart)
  // - Application timeline (line chart)
  // - Top companies applied to
  // - Average match scores
  // - Generation success rate
  // - Time spent per application
  
  const JobStatisticsScreen({Key? key}) : super(key: key);
}
```

---

### Phase 3: Generation Flow UI (10 hours)

#### Task 3.1: Generation Request Screen (3 hours)
**Files to Create:**
- `mobile_app/lib/screens/generation_request_screen.dart`
- `mobile_app/lib/widgets/template_selector.dart`

**Deliverables:**
```dart
class GenerationRequestScreen extends ConsumerStatefulWidget {
  final String jobId;
  final String? profileId; // Optional, defaults to active profile
  
  const GenerationRequestScreen({required this.jobId, this.profileId, Key? key});
}

class _GenerationRequestScreenState extends ConsumerState<GenerationRequestScreen> {
  // Step 1: Profile Selection (if multiple profiles)
  // Step 2: Template Selection (Professional, Modern, Creative)
  // Step 3: Customization Options (optional)
  //   - Summary focus (achievements vs. skills vs. experience)
  //   - Keywords emphasis
  //   - Length preference (1-page vs. 2-page)
  // Step 4: Review & Confirm
  //   - Show profile summary
  //   - Show job summary
  //   - Show selected template
  //   - Estimated generation time
  // CTA: "Generate Resume" button
  
  Widget build(BuildContext context) {
    // Use Stepper or PageView for multi-step flow
    // Show progress indicator at top
    // Back button to cancel or go to previous step
    // "Skip to defaults" for quick generation
  }
}

// Template Selector with Preview
class TemplateSelectorWidget extends StatefulWidget {
  final String? selectedTemplateId;
  final Function(String) onTemplateSelected;
  
  // Display 3 template cards with previews:
  // - Professional: Traditional ATS-friendly layout
  // - Modern: Clean contemporary design
  // - Creative: Visual design-focused layout
  
  // Each card shows:
  // - Template name
  // - Preview thumbnail
  // - Description
  // - "Best for" tags (e.g., "Technical Roles", "Creative Industries")
  // - Selection checkmark
  
  const TemplateSelectorWidget({...});
}
```

#### Task 3.2: Generation Progress Screen (3 hours)
**Files to Create:**
- `mobile_app/lib/screens/generation_progress_screen.dart`
- `mobile_app/lib/widgets/generation_progress_indicator.dart`

**Deliverables:**
```dart
class GenerationProgressScreen extends ConsumerStatefulWidget {
  final String generationId;
  
  const GenerationProgressScreen({required this.generationId, Key? key});
}

class _GenerationProgressScreenState extends ConsumerState<GenerationProgressScreen> {
  // Features:
  // - Real-time progress tracking with polling
  // - Stage-by-stage progress display
  // - Animated progress indicators
  // - Estimated time remaining
  // - Cancel button (with confirmation)
  // - Auto-navigate to result screen when complete
  
  @override
  void initState() {
    super.initState();
    // Start polling generation status every 1 second
    _startProgressPolling();
  }
  
  void _startProgressPolling() async {
    while (mounted) {
      await ref.read(generationProvider.notifier).pollGenerationProgress(widget.generationId);
      final state = ref.read(generationProvider);
      
      if (state.currentGeneration?.status == GenerationStatus.completed) {
        // Navigate to result screen
        context.go('/generation/${widget.generationId}/result');
        break;
      } else if (state.currentGeneration?.status == GenerationStatus.failed) {
        // Show error dialog
        _showErrorDialog(state.error ?? 'Generation failed');
        break;
      }
      
      await Future.delayed(const Duration(seconds: 1));
    }
  }
  
  Widget build(BuildContext context) {
    // Display:
    // - Circular progress indicator (0-100%)
    // - Current stage text (e.g., "Analyzing job requirements...")
    // - Stage list with checkmarks for completed stages
    // - Animated illustrations for each stage
    // - Cancel button at bottom
  }
}

// Multi-Stage Progress Indicator
class GenerationProgressIndicator extends StatelessWidget {
  final GenerationStage currentStage;
  final double progress; // 0.0 to 1.0
  
  // Displays:
  // 1. Analyzing (0-20%) - Magnifying glass icon
  // 2. Compiling (20-40%) - Document icon
  // 3. Generating (40-80%) - Sparkles icon
  // 4. Validating (80-95%) - Checkmark icon
  // 5. Exporting (95-100%) - Download icon
  
  // Each stage shows:
  // - Stage name
  // - Icon (animated when active)
  // - Checkmark when complete
  // - Progress bar connecting stages
  
  const GenerationProgressIndicator({...});
}
```

#### Task 3.3: Generation Result Screen (4 hours)
**Files to Create:**
- `mobile_app/lib/screens/generation_result_screen.dart`
- `mobile_app/lib/widgets/resume_preview_widget.dart`
- `mobile_app/lib/widgets/ats_score_card.dart`

**Deliverables:**
```dart
class GenerationResultScreen extends ConsumerStatefulWidget {
  final String generationId;
  
  const GenerationResultScreen({required this.generationId, Key? key});
}

class _GenerationResultScreenState extends ConsumerState<GenerationResultScreen> {
  // Features:
  // - Resume content preview (scrollable)
  // - ATS score card with breakdown
  // - Template switcher (regenerate with different template)
  // - Action buttons: Download PDF, Edit, Share, Regenerate
  // - Recommendations list from validator
  // - Matched vs. missing keywords
  
  Widget build(BuildContext context) {
    // Layout:
    // AppBar with title "Resume Generated" and share icon
    // Body:
    //   - ATS Score Card (collapsible)
    //   - Resume Preview (scrollable)
    //   - Recommendations Section (collapsible)
    // Bottom Sheet:
    //   - Template selector (switch template)
    //   - Download options (PDF, DOCX, TXT)
    //   - Edit button (opens resume editor)
    //   - Regenerate button (with feedback input)
  }
}

// Resume Preview Widget
class ResumePreviewWidget extends StatelessWidget {
  final ResumeContent content;
  final String templateId;
  
  // Renders resume sections in preview format:
  // - Summary/Objective
  // - Experience (with tailored bullet points)
  // - Education
  // - Skills (categorized: technical, soft, languages)
  // - Projects
  // - Certifications
  
  // Styled according to selected template
  // Tap sections to edit (future feature)
  
  const ResumePreviewWidget({...});
}

// ATS Score Breakdown Card
class ATSScoreCard extends StatelessWidget {
  final ATSScore score;
  
  // Displays:
  // - Overall ATS score (large number with progress ring)
  // - Score interpretation (Excellent, Good, Fair, Poor)
  // - Breakdown:
  //   - Keyword Match: X%
  //   - Format Compliance: X%
  // - Matched Keywords (chips)
  // - Missing Keywords (chips with warning icon)
  // - "Learn More" link to ATS tips
  
  const ATSScoreCard({...});
}

// Recommendations List
class RecommendationsWidget extends StatelessWidget {
  final List<String> recommendations;
  
  // Displays actionable recommendations:
  // - Add more quantifiable achievements
  // - Include missing keywords: [X, Y, Z]
  // - Expand technical skills section
  // - Optimize bullet point formatting
  
  // Each recommendation has:
  // - Icon (lightbulb)
  // - Text
  // - "Apply" button (for auto-fixes)
  
  const RecommendationsWidget({...});
}
```

---

### Phase 4: Document Management UI (8 hours)

#### Task 4.1: Document Library Screen (3 hours)
**Files to Create:**
- `mobile_app/lib/screens/document_library_screen.dart`
- `mobile_app/lib/widgets/document_card.dart`

**Deliverables:**
```dart
class DocumentLibraryScreen extends ConsumerWidget {
  // Features:
  // - Grid or list view toggle
  // - Filter by status (Draft, Ready, Exported, Archived)
  // - Sort options (date, name, job company)
  // - Search documents
  // - Multi-select for batch operations
  // - Empty state with CTA to generate first resume
  
  const DocumentLibraryScreen({Key? key}) : super(key: key);
}

class DocumentCard extends StatelessWidget {
  final Document document;
  final VoidCallback onTap;
  final VoidCallback onDownload;
  final VoidCallback onDelete;
  final VoidCallback onShare;
  
  // Displays:
  // - Document title (job title + company)
  // - Thumbnail preview (if available)
  // - Status badge
  // - Date created
  // - Available formats (PDF, DOCX icons)
  // - ATS score badge
  // - Actions: Download, Share, Delete
  
  const DocumentCard({...});
}
```

#### Task 4.2: Document Viewer Screen (3 hours)
**Files to Create:**
- `mobile_app/lib/screens/document_viewer_screen.dart`
- `mobile_app/lib/widgets/pdf_viewer_widget.dart`

**Deliverables:**
```dart
class DocumentViewerScreen extends ConsumerStatefulWidget {
  final String documentId;
  
  const DocumentViewerScreen({required this.documentId, Key? key});
}

class _DocumentViewerScreenState extends ConsumerState<DocumentViewerScreen> {
  // Features:
  // - PDF viewer with zoom and scroll
  // - Page navigation (if multi-page)
  // - Template switcher (regenerate with different template)
  // - Action buttons: Download, Share, Edit, Print
  // - Metadata display (generation date, template, ATS score)
  
  Widget build(BuildContext context) {
    // Layout:
    // AppBar with document title and actions
    // Body: PDF viewer (using pdf_render or syncfusion_flutter_pdfviewer)
    // Bottom bar:
    //   - Page indicator (Page 1 of 2)
    //   - Zoom controls
    //   - Download button
    //   - Share button
  }
}

// PDF Viewer Widget (using pdf_render package)
class PDFViewerWidget extends StatefulWidget {
  final Uint8List pdfBytes;
  
  // Features:
  // - Pinch to zoom
  // - Pan and scroll
  // - Page thumbnails
  // - Loading indicator
  // - Error handling
  
  const PDFViewerWidget({required this.pdfBytes, Key? key});
}
```

#### Task 4.3: Document Download & Share (2 hours)
**Files to Create:**
- `mobile_app/lib/services/document_download_service.dart`
- `mobile_app/lib/widgets/download_options_sheet.dart`

**Deliverables:**
```dart
class DocumentDownloadService {
  // Download document to device storage
  Future<String> downloadDocument({
    required String documentId,
    required ExportFormat format,
    String? customFilename,
  });
  
  // Share document via system share sheet
  Future<void> shareDocument({
    required String documentId,
    required ExportFormat format,
  });
  
  // Open document in external app
  Future<void> openInExternalApp(String filePath);
  
  // Get download history
  Future<List<DownloadedDocument>> getDownloadHistory();
}

// Download Options Bottom Sheet
class DownloadOptionsSheet extends StatelessWidget {
  final String documentId;
  
  // Options:
  // - Select format (PDF, DOCX, TXT)
  // - Select template (if re-exporting)
  // - Custom filename input
  // - Save location (Downloads folder)
  // - Action buttons: Download, Share, Cancel
  
  const DownloadOptionsSheet({required this.documentId, Key? key});
}

// Share Sheet with native integration
class ShareDocumentSheet extends StatelessWidget {
  final String documentId;
  final ExportFormat format;
  
  // Share via:
  // - Email
  // - Messaging apps
  // - Cloud storage (Drive, Dropbox, etc.)
  // - Copy link (if document hosted)
  
  const ShareDocumentSheet({...});
}
```

---

### Phase 5: Testing & Polish (4 hours)

#### Task 5.1: Widget Tests (2 hours)
**Files to Create:**
- `mobile_app/test/widgets/job_card_test.dart`
- `mobile_app/test/widgets/generation_progress_test.dart`
- `mobile_app/test/widgets/document_card_test.dart`

**Test Coverage:**
```dart
// Job Card Tests
testWidgets('JobCard displays job information correctly', ...);
testWidgets('SwipeableJobCard handles swipe gestures', ...);
testWidgets('JobDetailsSheet shows full job information', ...);

// Generation Tests
testWidgets('GenerationProgressIndicator shows correct stage', ...);
testWidgets('GenerationProgressScreen polls status', ...);
testWidgets('ATSScoreCard displays score breakdown', ...);
testWidgets('ResumePreviewWidget renders all sections', ...);

// Document Tests
testWidgets('DocumentCard displays document info', ...);
testWidgets('PDFViewerWidget loads and displays PDF', ...);
testWidgets('DownloadOptionsSheet shows format options', ...);

// Target: 15+ widget tests covering critical UI components
```

#### Task 5.2: Integration Tests (1 hour)
**Files to Create:**
- `mobile_app/integration_test/generation_flow_test.dart`
- `mobile_app/integration_test/job_browsing_test.dart`

**Test Scenarios:**
```dart
// Complete generation flow
testWidgets('User can browse jobs, save, generate resume, and download', ...);

// Job search and filtering
testWidgets('User can search jobs with filters and save', ...);

// Document management
testWidgets('User can view, download, and share documents', ...);

// Error handling
testWidgets('App handles API errors gracefully', ...);
```

#### Task 5.3: UI/UX Polish & Performance (1 hour)
**Activities:**
- Add loading skeletons for async operations
- Implement smooth page transitions
- Optimize image loading and caching
- Add haptic feedback for swipe gestures
- Ensure proper keyboard handling in forms
- Test on multiple screen sizes (phone, tablet)
- Dark mode support (if time permits)
- Accessibility improvements (semantic labels, contrast)

---

## 🗓️ Sprint 3 Daily Schedule (40 Hours)

### Day 1 (Monday, Oct 28): API Integration (8 hours)
**Morning (4h):**
- Task 1.1: Generation API Client (3h)
- Task 1.2: Document API Client (1h)

**Afternoon (4h):**
- Task 1.2: Document API Client completion (1h)
- Task 1.3: Job API Client Enhancement (2h)
- Task 1.4: State Management Providers (1h)

**Deliverable:** All API clients and Riverpod providers ready for UI integration

---

### Day 2 (Tuesday, Oct 29): Job Browsing UI (8 hours)
**Morning (4h):**
- Task 2.1: Job Card Widget (3h)
- Task 2.2: Job Search Screen (1h)

**Afternoon (4h):**
- Task 2.2: Job Search Screen completion (2h)
- Task 2.3: Saved Jobs Dashboard (2h)

**Deliverable:** Job browsing with swipeable cards, search, filters, and saved jobs list

---

### Day 3 (Wednesday, Oct 30): Generation Flow UI (8 hours)
**Morning (4h):**
- Task 3.1: Generation Request Screen (3h)
- Task 3.2: Generation Progress Screen (1h)

**Afternoon (4h):**
- Task 3.2: Generation Progress Screen completion (2h)
- Task 3.3: Generation Result Screen (2h)

**Deliverable:** Complete generation request flow with progress tracking and result display

---

### Day 4 (Thursday, Oct 31): Generation Result & Document Management (8 hours)
**Morning (4h):**
- Task 3.3: Generation Result Screen completion (2h)
- Task 2.4: Job Statistics Widget (2h)

**Afternoon (4h):**
- Task 4.1: Document Library Screen (3h)
- Task 4.2: Document Viewer Screen (1h)

**Deliverable:** Generation result screen complete, document library, and viewer started

---

### Day 5 (Friday, Nov 1): Document Management & Testing (8 hours)
**Morning (4h):**
- Task 4.2: Document Viewer Screen completion (2h)
- Task 4.3: Document Download & Share (2h)

**Afternoon (4h):**
- Task 5.1: Widget Tests (2h)
- Task 5.2: Integration Tests (1h)
- Task 5.3: UI/UX Polish & Performance (1h)

**Deliverable:** Complete document management, comprehensive tests, polished UI

---

### Weekend (Nov 2-3): Buffer & Final Polish (Optional)
**Activities:**
- Bug fixes from testing
- UI/UX refinements
- Performance optimization
- Sprint 3 documentation
- Prepare demo for Sprint 4 kickoff

---

## 📊 Sprint 3 Success Metrics

### Quantitative Metrics
- **Test Coverage**: 15+ widget tests for new UI components
- **API Integration**: 3 new API clients (Generation, Document, enhanced Job)
- **UI Screens**: 8+ new screens implemented
- **Performance**: <100ms screen transitions, <500ms API calls
- **Code Quality**: Zero critical bugs, all linting passing

### Qualitative Metrics
- **User Experience**: Smooth animations, intuitive navigation
- **Visual Design**: Consistent with Material Design 3 guidelines
- **Error Handling**: User-friendly error messages and recovery
- **Accessibility**: Semantic labels, contrast compliance
- **Responsiveness**: Works on multiple screen sizes

---

## 🎯 Key Technical Decisions

### Swipeable Cards Implementation
**Decision**: Use `flutter_card_swiper` package for job cards  
**Rationale**:
- Production-ready swipe gestures with customizable animations
- Support for swipe left/right/up callbacks
- Smooth physics and spring animations
- Reduced development time vs. custom implementation

### Progress Polling Strategy
**Decision**: Poll generation status every 1 second during generation  
**Rationale**:
- Simple implementation without WebSocket complexity
- Acceptable UX for 5-6 second generation time
- Easy to implement with Riverpod state management
- Can upgrade to WebSocket in future sprint if needed

### PDF Viewing Library
**Decision**: Use `syncfusion_flutter_pdfviewer` package  
**Rationale**:
- Excellent performance with large PDFs
- Built-in zoom, scroll, and navigation
- Page thumbnails support
- Text selection and search capabilities
- Community edition available for free

### Document Storage Strategy
**Decision**: Download PDFs to app documents directory, provide share options  
**Rationale**:
- Keeps generated documents accessible offline
- System share sheet integrates with all user apps
- Avoids complex cloud storage setup in Sprint 3
- Simple file management with path_provider

---

## 🚨 Risk Assessment & Mitigation

### High Priority Risks

**Risk 1: PDF Rendering Performance**  
*Impact*: High | *Probability*: Medium  
*Mitigation*:
- Use optimized PDF viewer package (Syncfusion)
- Test with multi-page documents early
- Implement loading indicators
- Cache rendered pages for quick navigation
- Have fallback to text-only view if rendering fails

**Risk 2: Swipeable Cards UX Complexity**  
*Impact*: Medium | *Probability*: Low  
*Mitigation*:
- Use proven package (flutter_card_swiper)
- Test gesture recognition on multiple devices
- Provide alternative tap-based navigation
- Add tutorial overlay on first use

**Risk 3: Generation Progress Polling Overhead**  
*Impact*: Low | *Probability*: Medium  
*Mitigation*:
- Limit polling to 1-second intervals
- Cancel polling when screen not visible
- Implement exponential backoff if errors occur
- Cache generation status to reduce API calls

**Risk 4: State Management Complexity**  
*Impact*: Medium | *Probability*: Low  
*Mitigation*:
- Follow established Riverpod patterns from Sprint 1
- Keep providers focused and single-purpose
- Comprehensive error handling in all providers
- Use context7 for Riverpod best practices reference

---

## 🔄 AI Agent Coordination Strategy

### Mobile Developer Agent (Primary)
**Tool**: GitHub Copilot + Claude 3.5 Sonnet  
**Responsibilities**:
- Implement all mobile UI screens and widgets
- Integrate with Generation & Document APIs
- Create Riverpod state management providers
- Write widget and integration tests

**Coordination Points**:
- Daily progress updates in `log/mobile-developer-log.md`
- UI/UX decisions documented with screenshots
- Technical challenges logged for Solutions Architect review
- Test results tracked for QA validation

### Solutions Architect Agent (Supporting)
**Tool**: ChatGPT-4  
**Responsibilities**:
- Review mobile architecture design
- Validate state management approach
- Provide UX optimization recommendations
- Review API integration patterns

**Coordination Points**:
- Architecture review at Phase 1 completion (API clients)
- UI/UX review at Phase 2 completion (Job browsing)
- Integration pattern validation before testing phase

### Backend Developer Agent (Coordination)
**Tool**: GitHub Copilot  
**Responsibilities**:
- Provide API documentation and examples
- Support API integration debugging
- Clarify API behaviors and error responses

**Coordination Points**:
- API documentation in OpenAPI spec
- Example requests/responses in Postman collection
- Quick response to mobile integration questions

### QA Engineer Agent (Supporting)
**Tool**: GitHub Copilot + ChatGPT  
**Responsibilities**:
- Design widget test strategy
- Review test coverage reports
- Validate error handling flows
- Performance testing recommendations

**Coordination Points**:
- Test strategy review at sprint start
- Daily test coverage monitoring
- Bug triage and prioritization
- Final quality validation before sprint close

---

## 📦 Sprint 3 Deliverables Checklist

### Code Deliverables
- [ ] Generation API Client with models
- [ ] Document API Client with models
- [ ] Enhanced Job API Client with search/filters
- [ ] Riverpod providers (Generation, Document, Job)
- [ ] Job browsing UI with swipeable cards
- [ ] Job search screen with filters
- [ ] Saved jobs dashboard
- [ ] Generation request screen with template selector
- [ ] Generation progress screen with real-time updates
- [ ] Generation result screen with ATS score
- [ ] Document library screen
- [ ] Document viewer with PDF rendering
- [ ] Document download and share functionality
- [ ] Job statistics widget

### Testing Deliverables
- [ ] 15+ widget tests covering critical components
- [ ] 5+ integration tests for user flows
- [ ] Manual testing checklist completed
- [ ] Performance benchmarks documented
- [ ] Accessibility audit passed

### Documentation Deliverables
- [ ] Mobile feature documentation updates
- [ ] API integration guide
- [ ] Widget catalog with screenshots
- [ ] User flow diagrams
- [ ] Sprint 3 retrospective notes

### Quality Gates
- [ ] All widget tests passing
- [ ] Integration tests passing
- [ ] Zero critical or high-priority bugs
- [ ] UI/UX reviewed and approved
- [ ] Performance targets met
- [ ] Accessibility requirements met
- [ ] Code review approved

---

## 🎓 Learning Objectives

### Technical Skills
- **Complex UI Patterns**: Implement swipeable cards, progress tracking, PDF viewing
- **State Management**: Advanced Riverpod patterns with polling and real-time updates
- **API Integration**: Connect mobile app to multiple backend services
- **Performance Optimization**: Optimize list rendering, image caching, API calls
- **Testing**: Comprehensive widget and integration testing

### Mobile Development Skills
- **Material Design 3**: Apply modern design patterns and components
- **Gesture Recognition**: Implement intuitive swipe and tap interactions
- **File Management**: Handle document downloads and sharing
- **Offline Support**: Cache data for offline viewing
- **Animations**: Create smooth transitions and loading states

---

## 📝 Sprint 3 Definition of Done

A feature is considered "Done" when:
1. ✅ UI implemented following Material Design 3 guidelines
2. ✅ API integration working with proper error handling
3. ✅ Widget tests written and passing (>80% coverage for new widgets)
4. ✅ Integration tests validating user flows
5. ✅ Manual testing completed on Android emulator
6. ✅ UI/UX reviewed with screenshots in documentation
7. ✅ Performance benchmarks met (transitions <100ms, API <500ms)
8. ✅ Accessibility labels and semantic structure
9. ✅ Code reviewed and approved
10. ✅ Sprint log updated with implementation notes

---

## 🚀 Post-Sprint 3 Roadmap

### Sprint 4 Priorities (Week 13 - Nov 4-10)
- Resume editing interface (modify generated content)
- Cover letter generation UI
- Job application tracking dashboard
- Notifications system (generation complete, application deadlines)
- Settings and preferences screen

### Sprint 5 Priorities (Week 14 - Nov 11-17)
- End-to-end integration testing
- Performance optimization and profiling
- Offline mode with sync strategy
- Advanced error handling and recovery
- UI/UX final polish and animations

### Sprint 6 Priorities (Week 15 - Nov 18-24)
- Final bug fixes and testing
- Documentation completion
- Demo video creation
- Presentation preparation
- Portfolio deployment

---

## 📐 UI/UX Design Specifications

### Color Scheme (Material Design 3)
```dart
// Primary Colors
primaryColor: Color(0xFF6200EE),       // Deep Purple
primaryVariant: Color(0xFF3700B3),
secondaryColor: Color(0xFF03DAC6),     // Teal

// Status Colors
successColor: Color(0xFF4CAF50),       // Green
warningColor: Color(0xFFFFC107),       // Amber
errorColor: Color(0xFFB00020),         // Red
infoColor: Color(0xFF2196F3),          // Blue

// Neutral Colors
surface: Color(0xFFFFFFFF),
background: Color(0xFFF5F5F5),
onSurface: Color(0xFF000000),
```

### Typography
```dart
// Headings
headline1: TextStyle(fontSize: 32, fontWeight: FontWeight.bold),
headline2: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
headline3: TextStyle(fontSize: 20, fontWeight: FontWeight.w600),

// Body Text
bodyText1: TextStyle(fontSize: 16, fontWeight: FontWeight.normal),
bodyText2: TextStyle(fontSize: 14, fontWeight: FontWeight.normal),
caption: TextStyle(fontSize: 12, fontWeight: FontWeight.normal),
```

### Spacing System
```dart
// Consistent spacing scale
spacing4: 4.0,
spacing8: 8.0,
spacing12: 12.0,
spacing16: 16.0,   // Default content padding
spacing24: 24.0,
spacing32: 32.0,
spacing48: 48.0,
```

### Component Specifications

**Job Card:**
- Height: 500px (swipeable), 120px (list)
- Border Radius: 16px
- Shadow: elevation 4
- Padding: 16px
- Image Aspect Ratio: 16:9 (if company logo)

**Generation Progress:**
- Circular Progress: 200px diameter
- Stage Icons: 48px
- Progress Bar: 4px height
- Connecting Lines: 2px dashed

**Document Card:**
- Grid: 2 columns on phone, 3 on tablet
- Card Height: 240px
- Thumbnail: 16:9 aspect ratio
- Badge Size: 24px

---

## 🔧 Development Tools & Packages

### Required Dependencies
```yaml
dependencies:
  flutter:
    sdk: flutter
  
  # State Management
  flutter_riverpod: ^2.6.1
  riverpod_annotation: ^2.3.5
  
  # API Integration
  dio: ^5.7.0
  retrofit: ^4.4.1
  json_annotation: ^4.9.0
  
  # UI Components
  flutter_card_swiper: ^7.0.1
  syncfusion_flutter_pdfviewer: ^27.2.2
  shimmer: ^3.0.0
  lottie: ^3.1.2
  
  # File Management
  path_provider: ^2.1.5
  share_plus: ^10.1.1
  open_filex: ^4.5.0
  
  # Storage
  flutter_secure_storage: ^9.2.2
  shared_preferences: ^2.3.3
  
  # Routing
  go_router: ^14.6.2
  
  # Utils
  intl: ^0.19.0
  collection: ^1.18.0
  equatable: ^2.0.7

dev_dependencies:
  flutter_test:
    sdk: flutter
  
  # Code Generation
  build_runner: ^2.4.14
  riverpod_generator: ^2.4.3
  retrofit_generator: ^9.1.4
  json_serializable: ^6.8.0
  
  # Testing
  mockito: ^5.4.4
  integration_test:
    sdk: flutter
  
  # Linting
  flutter_lints: ^5.0.0
```

---

**Sprint 3 Start Date**: Monday, October 28, 2025  
**Sprint 3 End Date**: Friday, November 1, 2025  
**Review & Documentation**: Weekend, November 2-3, 2025  
**Sprint 3 Demo**: Monday, November 4, 2025

**Prepared by**: Mobile Developer Agent + Solutions Architect Agent  
**Last Updated**: October 27, 2025

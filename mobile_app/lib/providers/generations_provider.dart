// lib/providers/generations_provider.dart

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/generation.dart';
import '../services/api/generations_api_client.dart';

/// State class for generations management
class GenerationsState {
  final List<GenerationListItem> history;
  final Generation? currentGeneration;
  final bool isGenerating;
  final double progress;
  final String? currentStage;
  final String? errorMessage;

  GenerationsState({
    this.history = const [],
    this.currentGeneration,
    this.isGenerating = false,
    this.progress = 0.0,
    this.currentStage,
    this.errorMessage,
  });

  GenerationsState copyWith({
    List<GenerationListItem>? history,
    Generation? currentGeneration,
    bool? isGenerating,
    double? progress,
    String? currentStage,
    String? errorMessage,
  }) {
    return GenerationsState(
      history: history ?? this.history,
      currentGeneration: currentGeneration ?? this.currentGeneration,
      isGenerating: isGenerating ?? this.isGenerating,
      progress: progress ?? this.progress,
      currentStage: currentStage ?? this.currentStage,
      errorMessage: errorMessage,
    );
  }

  /// Get resume generations only
  List<GenerationListItem> get resumeHistory =>
      history.where((g) => g.documentType == DocumentType.resume).toList();

  /// Get cover letter generations only
  List<GenerationListItem> get coverLetterHistory =>
      history.where((g) => g.documentType == DocumentType.coverLetter).toList();

  /// Check if currently generating
  bool get hasActiveGeneration => isGenerating;
}

/// Notifier for managing document generations (resumes and cover letters)
/// Handles generation requests, progress tracking, and history
class GenerationsNotifier extends StateNotifier<GenerationsState> {
  final GenerationsApiClient _apiClient;

  GenerationsNotifier(this._apiClient) : super(GenerationsState());

  /// Generate resume for a job
  /// Parameters:
  /// - [jobId]: Job posting ID
  /// - [maxExperiences]: Maximum experiences to include (default 5)
  /// - [maxProjects]: Maximum projects to include (default 3)
  /// - [includeSummary]: Include professional summary (default true)
  Future<Generation?> generateResume({
    required String jobId,
    int maxExperiences = 5,
    int maxProjects = 3,
    bool includeSummary = true,
  }) async {
    state = state.copyWith(
      isGenerating: true,
      progress: 0.0,
      currentStage: 'Analyzing job requirements...',
      errorMessage: null,
    );

    try {
      // Stage 1: Analyzing (20%)
      state = state.copyWith(
        progress: 0.2,
        currentStage: 'Analyzing job requirements...',
      );

      // TODO: Call ranking API if needed
      await Future.delayed(const Duration(milliseconds: 500));

      // Stage 2: Selecting content (60%)
      state = state.copyWith(
        progress: 0.6,
        currentStage: 'Selecting relevant content...',
      );

      // Call generation API
      final generation = await _apiClient.generateResume(
        jobId: jobId,
        maxExperiences: maxExperiences,
        maxProjects: maxProjects,
        includeSummary: includeSummary,
      );

      // Stage 3: Compiling (80%)
      state = state.copyWith(
        progress: 0.8,
        currentStage: 'Compiling resume...',
      );

      await Future.delayed(const Duration(milliseconds: 300));

      // Stage 4: Calculating ATS score (100%)
      state = state.copyWith(
        progress: 1.0,
        currentStage: 'Calculating ATS score...',
      );

      await Future.delayed(const Duration(milliseconds: 200));

      // Complete
      state = state.copyWith(
        currentGeneration: generation,
        isGenerating: false,
        progress: 1.0,
        currentStage: 'Completed',
      );

      return generation;
    } catch (e) {
      state = state.copyWith(
        isGenerating: false,
        progress: 0.0,
        errorMessage: e.toString(),
      );
      return null;
    }
  }

  /// Generate cover letter for a job
  /// Parameters:
  /// - [jobId]: Job posting ID
  /// - [tone]: Writing tone ('professional', 'enthusiastic', 'formal')
  /// - [length]: Cover letter length ('short', 'medium', 'long')
  Future<Generation?> generateCoverLetter({
    required String jobId,
    String tone = 'professional',
    String length = 'medium',
  }) async {
    state = state.copyWith(
      isGenerating: true,
      progress: 0.0,
      currentStage: 'Analyzing job requirements...',
      errorMessage: null,
    );

    try {
      // Stage 1: Analyzing (20%)
      state = state.copyWith(
        progress: 0.2,
        currentStage: 'Analyzing job requirements...',
      );

      await Future.delayed(const Duration(milliseconds: 500));

      // Stage 2: Extracting writing style (40%)
      state = state.copyWith(
        progress: 0.4,
        currentStage: 'Extracting writing style...',
      );

      await Future.delayed(const Duration(milliseconds: 1000));

      // Stage 3: Generating with LLM (80%)
      state = state.copyWith(
        progress: 0.8,
        currentStage: 'Generating cover letter...',
      );

      // Call generation API (LLM call takes 3-5 seconds)
      final generation = await _apiClient.generateCoverLetter(
        jobId: jobId,
        tone: tone,
        length: length,
      );

      // Stage 4: Calculating ATS score (100%)
      state = state.copyWith(
        progress: 1.0,
        currentStage: 'Calculating ATS score...',
      );

      await Future.delayed(const Duration(milliseconds: 300));

      // Complete
      state = state.copyWith(
        currentGeneration: generation,
        isGenerating: false,
        progress: 1.0,
        currentStage: 'Completed',
      );

      return generation;
    } catch (e) {
      state = state.copyWith(
        isGenerating: false,
        progress: 0.0,
        errorMessage: e.toString(),
      );
      return null;
    }
  }

  /// Fetch generation history
  /// Parameters:
  /// - [documentType]: Filter by document type ('resume' or 'cover_letter')
  /// - [limit]: Maximum number of items to fetch
  /// - [offset]: Offset for pagination
  Future<void> fetchHistory({
    String? documentType,
    int limit = 20,
    int offset = 0,
  }) async {
    try {
      // TODO: Implement when generation history endpoint is available
      // final response = await _apiClient.getGenerationHistory(
      //   documentType: documentType,
      //   limit: limit,
      //   offset: offset,
      // );
      // state = state.copyWith(history: response.items);
    } catch (e) {
      state = state.copyWith(errorMessage: e.toString());
    }
  }

  /// Clear error message
  void clearError() {
    state = state.copyWith(errorMessage: null);
  }

  /// Reset generation state
  void reset() {
    state = state.copyWith(
      currentGeneration: null,
      isGenerating: false,
      progress: 0.0,
      currentStage: null,
      errorMessage: null,
    );
  }
}

/// Provider for generations notifier
final generationsProvider =
    StateNotifierProvider<GenerationsNotifier, GenerationsState>((ref) {
  final apiClient = ref.watch(generationsApiClientProvider);
  return GenerationsNotifier(apiClient);
});

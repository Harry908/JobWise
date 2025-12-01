import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api/generations_api_client.dart';

/// State for generation operations
class GenerationsState {
  final bool isEnhancing;
  final bool isGenerating;
  final double progress;
  final String? currentStage;
  final String? errorMessage;
  final Map<String, dynamic>? lastGeneration;
  final List<Map<String, dynamic>> history;

  const GenerationsState({
    this.isEnhancing = false,
    this.isGenerating = false,
    this.progress = 0.0,
    this.currentStage,
    this.errorMessage,
    this.lastGeneration,
    this.history = const [],
  });

  GenerationsState copyWith({
    bool? isEnhancing,
    bool? isGenerating,
    double? progress,
    String? currentStage,
    String? errorMessage,
    Map<String, dynamic>? lastGeneration,
    List<Map<String, dynamic>>? history,
  }) {
    return GenerationsState(
      isEnhancing: isEnhancing ?? this.isEnhancing,
      isGenerating: isGenerating ?? this.isGenerating,
      progress: progress ?? this.progress,
      currentStage: currentStage ?? this.currentStage,
      errorMessage: errorMessage,
      lastGeneration: lastGeneration ?? this.lastGeneration,
      history: history ?? this.history,
    );
  }
}

/// Notifier for generation operations
class GenerationsNotifier extends StateNotifier<GenerationsState> {
  final GenerationsApiClient _apiClient;

  GenerationsNotifier(this._apiClient) : super(const GenerationsState());

  /// Enhance profile with AI
  Future<bool> enhanceProfile({
    required String profileId,
    String? customPrompt,
  }) async {
    state = state.copyWith(isEnhancing: true, errorMessage: null);

    try {
      await _apiClient.enhanceProfile(
        profileId: profileId,
        customPrompt: customPrompt,
      );
      state = state.copyWith(isEnhancing: false);
      return true;
    } catch (e) {
      state = state.copyWith(
        isEnhancing: false,
        errorMessage: e.toString(),
      );
      return false;
    }
  }

  /// Generate resume for a specific job
  Future<Map<String, dynamic>?> generateResume({
    required String jobId,
    int maxExperiences = 5,
    int maxProjects = 3,
    bool includeSummary = true,
  }) async {
    state = state.copyWith(
      isGenerating: true,
      progress: 0.0,
      currentStage: 'Starting...',
      errorMessage: null,
    );

    try {
      // Stage 1: Check/create rankings
      state = state.copyWith(
        progress: 0.2,
        currentStage: 'Analyzing job requirements...',
      );

      try {
        await _apiClient.getRankingsForJob(jobId);
      } catch (e) {
        // Ranking doesn't exist, create it
        await _apiClient.createRankings(jobId: jobId);
      }

      // Stage 2: Generate resume
      state = state.copyWith(
        progress: 0.6,
        currentStage: 'Generating resume...',
      );

      final generation = await _apiClient.generateResume(
        jobId: jobId,
        maxExperiences: maxExperiences,
        maxProjects: maxProjects,
        includeSummary: includeSummary,
      );

      state = state.copyWith(
        isGenerating: false,
        progress: 1.0,
        currentStage: 'Completed',
        lastGeneration: generation,
      );

      return generation;
    } catch (e) {
      state = state.copyWith(
        isGenerating: false,
        progress: 0.0,
        currentStage: null,
        errorMessage: e.toString(),
      );
      return null;
    }
  }

  /// Generate cover letter for a specific job
  Future<Map<String, dynamic>?> generateCoverLetter({
    required String jobId,
    String? companyName,
    String? hiringManagerName,
    int maxParagraphs = 4,
  }) async {
    state = state.copyWith(
      isGenerating: true,
      progress: 0.0,
      currentStage: 'Starting...',
      errorMessage: null,
    );

    try {
      // Stage 1: Check/create rankings
      state = state.copyWith(
        progress: 0.2,
        currentStage: 'Analyzing job requirements...',
      );

      try {
        await _apiClient.getRankingsForJob(jobId);
      } catch (e) {
        await _apiClient.createRankings(jobId: jobId);
      }

      // Stage 2: Generate cover letter
      state = state.copyWith(
        progress: 0.4,
        currentStage: 'Generating cover letter...',
      );

      final generation = await _apiClient.generateCoverLetter(
        jobId: jobId,
        companyName: companyName,
        hiringManagerName: hiringManagerName,
        maxParagraphs: maxParagraphs,
      );

      state = state.copyWith(
        isGenerating: false,
        progress: 1.0,
        currentStage: 'Completed',
        lastGeneration: generation,
      );

      return generation;
    } catch (e) {
      state = state.copyWith(
        isGenerating: false,
        progress: 0.0,
        currentStage: null,
        errorMessage: e.toString(),
      );
      return null;
    }
  }

  /// Fetch generation history for a specific job
  Future<void> fetchHistoryForJob(String jobId) async {
    try {
      final response = await _apiClient.getGenerationHistory(jobId: jobId);
      final generations = response['generations'] as List<dynamic>?;
      
      state = state.copyWith(
        history: generations?.map((e) => e as Map<String, dynamic>).toList() ?? [],
      );
    } catch (e) {
      state = state.copyWith(errorMessage: e.toString());
    }
  }

  void clearError() {
    state = state.copyWith(errorMessage: null);
  }

  void reset() {
    state = const GenerationsState();
  }
}

/// Provider for generations state
final generationsProvider =
    StateNotifierProvider<GenerationsNotifier, GenerationsState>((ref) {
  final apiClient = ref.watch(generationsApiClientProvider);
  return GenerationsNotifier(apiClient);
});

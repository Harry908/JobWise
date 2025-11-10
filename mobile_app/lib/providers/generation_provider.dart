import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import '../models/generation.dart';
import '../services/api/generation_api_client.dart';

part 'generation_provider.freezed.dart';

/// Generation state using Freezed for immutability
@freezed
class GenerationState with _$GenerationState {
  const factory GenerationState({
    @Default([]) List<GenerationListItem> generations,
    Generation? activeGeneration, // Currently creating or viewing
    GenerationStatistics? statistics,
    Pagination? pagination,
    @Default([]) List<Template> templates,
    @Default(false) bool isLoading,
    @Default(false) bool isLoadingMore,
    @Default(false) bool isPolling,
    String? error,
    @Default(0) int total,
    @Default(true) bool hasMore,
  }) = _GenerationState;
}

/// Generation Notifier for managing generation-related state
class GenerationNotifier extends StateNotifier<GenerationState> {
  final GenerationApiClient _generationApi;

  GenerationNotifier(this._generationApi) : super(const GenerationState());

  /// Load templates (cached in state)
  Future<void> loadTemplates() async {
    if (state.templates.isNotEmpty) {
      return; // Already loaded
    }

    try {
      state = state.copyWith(isLoading: true, error: null);

      final templates = await _generationApi.getTemplates();

      state = state.copyWith(
        templates: templates,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// Start resume generation
  Future<Generation> startResumeGeneration({
    required String profileId,
    required String jobId,
    GenerationOptions? options,
  }) async {
    try {
      state = state.copyWith(isLoading: true, error: null);

      final generation = await _generationApi.startResumeGeneration(
        profileId: profileId,
        jobId: jobId,
        options: options,
      );

      state = state.copyWith(
        activeGeneration: generation,
        isLoading: false,
      );

      return generation;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
      rethrow;
    }
  }

  /// Start cover letter generation
  Future<Generation> startCoverLetterGeneration({
    required String profileId,
    required String jobId,
    GenerationOptions? options,
  }) async {
    try {
      state = state.copyWith(isLoading: true, error: null);

      final generation = await _generationApi.startCoverLetterGeneration(
        profileId: profileId,
        jobId: jobId,
        options: options,
      );

      state = state.copyWith(
        activeGeneration: generation,
        isLoading: false,
      );

      return generation;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
      rethrow;
    }
  }

  /// Load user's generations with optional filters
  Future<void> loadGenerations({
    String? jobId,
    GenerationStatus? status,
    DocumentType? documentType,
    bool refresh = false,
  }) async {
    if (refresh) {
      state = state.copyWith(
        isLoading: true,
        error: null,
        generations: [],
      );
    } else if (state.isLoading) {
      return; // Already loading
    }

    try {
      state = state.copyWith(isLoading: true, error: null);

      final (generations, pagination, statistics) =
          await _generationApi.getGenerations(
        jobId: jobId,
        status: status,
        documentType: documentType,
        limit: 20,
        offset: 0,
      );

      state = state.copyWith(
        generations: generations,
        pagination: pagination,
        statistics: statistics,
        total: pagination.total,
        hasMore: pagination.hasNext,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// Load more generations (pagination)
  Future<void> loadMoreGenerations({
    String? jobId,
    GenerationStatus? status,
    DocumentType? documentType,
  }) async {
    if (state.isLoadingMore || !state.hasMore) {
      return;
    }

    try {
      state = state.copyWith(isLoadingMore: true);

      final (generations, pagination, statistics) =
          await _generationApi.getGenerations(
        jobId: jobId,
        status: status,
        documentType: documentType,
        limit: 20,
        offset: state.generations.length,
      );

      state = state.copyWith(
        generations: [...state.generations, ...generations],
        pagination: pagination,
        statistics: statistics,
        total: pagination.total,
        hasMore: pagination.hasNext,
        isLoadingMore: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoadingMore: false,
        error: e.toString(),
      );
    }
  }

  /// Cancel ongoing generation
  Future<void> cancelGeneration(String id) async {
    try {
      await _generationApi.cancelGeneration(id);

      // Clear active generation if it matches
      if (state.activeGeneration?.id == id) {
        state = state.copyWith(activeGeneration: null);
      }

      // Refresh list
      await loadGenerations(refresh: true);
    } catch (e) {
      state = state.copyWith(error: e.toString());
      rethrow;
    }
  }

  /// Regenerate with new options
  Future<Generation> regenerate({
    required String id,
    GenerationOptions? options,
  }) async {
    try {
      state = state.copyWith(isLoading: true, error: null);

      final generation = await _generationApi.regenerateGeneration(
        id: id,
        options: options,
      );

      state = state.copyWith(
        activeGeneration: generation,
        isLoading: false,
      );

      return generation;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
      rethrow;
    }
  }

  /// Update active generation (used during polling)
  void updateActiveGeneration(Generation generation) {
    state = state.copyWith(activeGeneration: generation);
  }

  /// Clear active generation
  void clearActiveGeneration() {
    state = state.copyWith(activeGeneration: null);
  }

  /// Set polling state
  void setPolling(bool polling) {
    state = state.copyWith(isPolling: polling);
  }
}

// ============================================================================
// PROVIDERS
// ============================================================================

/// Provider for GenerationNotifier
final generationProvider =
    StateNotifierProvider<GenerationNotifier, GenerationState>((ref) {
  final apiClient = ref.watch(generationApiClientProvider);
  return GenerationNotifier(apiClient);
});

/// Provider for templates (auto-load on first access)
final templatesProvider = FutureProvider<List<Template>>((ref) async {
  final apiClient = ref.watch(generationApiClientProvider);
  return apiClient.getTemplates();
});

/// Provider for polling a specific generation
/// Usage: ref.watch(generationStreamProvider(generationId))
final generationStreamProvider = StreamProvider.autoDispose
    .family<Generation, String>((ref, generationId) {
  final apiClient = ref.watch(generationApiClientProvider);
  return apiClient.pollGeneration(generationId);
});

/// Provider for a single generation status
/// Useful for one-time checks without polling
final generationStatusProvider =
    FutureProvider.autoDispose.family<Generation, String>((ref, generationId) async {
  final apiClient = ref.watch(generationApiClientProvider);
  return apiClient.getGenerationStatus(generationId);
});

/// Provider for generation result
final generationResultProvider = FutureProvider.autoDispose
    .family<Map<String, dynamic>, String>((ref, generationId) async {
  final apiClient = ref.watch(generationApiClientProvider);
  return apiClient.getGenerationResult(generationId);
});

/// Provider for generation list with filters
class GenerationFilters {
  final String? jobId;
  final GenerationStatus? status;
  final DocumentType? documentType;
  final int limit;
  final int offset;

  const GenerationFilters({
    this.jobId,
    this.status,
    this.documentType,
    this.limit = 20,
    this.offset = 0,
  });

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is GenerationFilters &&
          runtimeType == other.runtimeType &&
          jobId == other.jobId &&
          status == other.status &&
          documentType == other.documentType &&
          limit == other.limit &&
          offset == other.offset;

  @override
  int get hashCode =>
      jobId.hashCode ^
      status.hashCode ^
      documentType.hashCode ^
      limit.hashCode ^
      offset.hashCode;
}

final generationsListProvider = FutureProvider.autoDispose
    .family<(List<GenerationListItem>, Pagination, GenerationStatistics),
        GenerationFilters>((ref, filters) async {
  final apiClient = ref.watch(generationApiClientProvider);
  return apiClient.getGenerations(
    jobId: filters.jobId,
    status: filters.status,
    documentType: filters.documentType,
    limit: filters.limit,
    offset: filters.offset,
  );
});

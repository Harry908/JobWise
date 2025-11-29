// lib/providers/samples_provider.dart

import 'package:file_picker/file_picker.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/sample.dart';
import '../services/api/generations_api_client.dart';

/// State class for samples management
class SamplesState {
  final List<Sample> samples;
  final bool isLoading;
  final String? errorMessage;

  SamplesState({
    this.samples = const [],
    this.isLoading = false,
    this.errorMessage,
  });

  SamplesState copyWith({
    List<Sample>? samples,
    bool? isLoading,
    String? errorMessage,
  }) {
    return SamplesState(
      samples: samples ?? this.samples,
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage,
    );
  }

  /// Get active resume sample (most recent)
  Sample? get activeResumeSample {
    final resumeSamples = samples
        .where((s) => s.documentType == 'resume' && s.isActive)
        .toList()
      ..sort((a, b) => b.createdAt.compareTo(a.createdAt));
    return resumeSamples.isEmpty ? null : resumeSamples.first;
  }

  /// Get active cover letter sample (most recent)
  Sample? get activeCoverLetterSample {
    final coverLetterSamples = samples
        .where((s) => s.documentType == 'cover_letter' && s.isActive)
        .toList()
      ..sort((a, b) => b.createdAt.compareTo(a.createdAt));
    return coverLetterSamples.isEmpty ? null : coverLetterSamples.first;
  }

  /// Get all resume samples
  List<Sample> get resumeSamples =>
      samples.where((s) => s.documentType == 'resume').toList();

  /// Get all cover letter samples
  List<Sample> get coverLetterSamples =>
      samples.where((s) => s.documentType == 'cover_letter').toList();

  /// Check if user has uploaded any samples
  bool get hasSamples => samples.isNotEmpty;

  /// Check if user has resume sample
  bool get hasResumeSample => resumeSamples.isNotEmpty;

  /// Check if user has cover letter sample
  bool get hasCoverLetterSample => coverLetterSamples.isNotEmpty;
}

/// Notifier for managing sample documents (resumes and cover letters)
/// Handles upload, retrieval, and deletion of sample documents
class SamplesNotifier extends StateNotifier<SamplesState> {
  final GenerationsApiClient _apiClient;

  SamplesNotifier(this._apiClient) : super(SamplesState());

  /// Load all samples from API
  Future<void> loadSamples() async {
    state = state.copyWith(isLoading: true, errorMessage: null);
    try {
      final response = await _apiClient.getSamples();
      state = state.copyWith(
        samples: response.items,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: e.toString(),
      );
    }
  }

  /// Upload a sample document
  /// Parameters:
  /// - [file]: PlatformFile from file_picker (must be .txt file)
  /// - [documentType]: 'resume' or 'cover_letter'
  Future<Sample?> uploadSample({
    required PlatformFile file,
    required String documentType,
  }) async {
    state = state.copyWith(isLoading: true, errorMessage: null);
    try {
      final uploadedSample = await _apiClient.uploadSample(
        file: file,
        documentType: documentType,
      );

      // Add to local list
      final updatedSamples = [...state.samples, uploadedSample];
      state = state.copyWith(
        samples: updatedSamples,
        isLoading: false,
      );

      return uploadedSample;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: e.toString(),
      );
      return null;
    }
  }

  /// Delete a sample document
  Future<bool> deleteSample(String sampleId) async {
    state = state.copyWith(isLoading: true, errorMessage: null);
    try {
      await _apiClient.deleteSample(sampleId);

      // Remove from local list
      final updatedSamples =
          state.samples.where((s) => s.id != sampleId).toList();
      state = state.copyWith(
        samples: updatedSamples,
        isLoading: false,
      );

      return true;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: e.toString(),
      );
      return false;
    }
  }

  /// Clear error message
  void clearError() {
    state = state.copyWith(errorMessage: null);
  }
}

/// Provider for samples notifier
final samplesProvider =
    StateNotifierProvider<SamplesNotifier, SamplesState>((ref) {
  final apiClient = ref.watch(generationsApiClientProvider);
  return SamplesNotifier(apiClient);
});

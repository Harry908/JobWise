import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/generation.dart';
import 'api/generation_api_client.dart';

final generationServiceProvider = Provider<GenerationService>((ref) {
  final apiClient = ref.watch(generationApiClientProvider);
  return GenerationService(apiClient);
});

class GenerationService {
  final GenerationApiClient _apiClient;

  GenerationService(this._apiClient);

  Future<List<Template>> getTemplates() async {
    return await _apiClient.getTemplates();
  }

  Future<Generation> startResumeGeneration({
    required String profileId,
    required String jobId,
    required GenerationOptions options,
  }) async {
    return await _apiClient.startResumeGeneration(
      profileId: profileId,
      jobId: jobId,
      options: options,
    );
  }

  Future<Generation> startCoverLetterGeneration({
    required String profileId,
    required String jobId,
    required GenerationOptions options,
  }) async {
    return await _apiClient.startCoverLetterGeneration(
      profileId: profileId,
      jobId: jobId,
      options: options,
    );
  }

  Stream<Generation> getGenerationStream(String generationId) {
    // This would typically connect to a WebSocket or use polling.
    // For now, we'll poll the API.
    return Stream.periodic(const Duration(seconds: 3), (_) {
      return _apiClient.getGenerationStatus(generationId);
    }).asyncMap((event) async => await event);
  }

  Future<Generation> getGenerationResult(String generationId) async {
    final json = await _apiClient.getGenerationResult(generationId);
    return Generation.fromJson(json);
  }

  Future<Map<String, dynamic>> getRawGenerationResult(String generationId) async {
    return await _apiClient.getGenerationResult(generationId);
  }

  Future<void> cancelGeneration(String generationId) async {
    await _apiClient.cancelGeneration(generationId);
  }

  Future<(List<GenerationListItem>, Pagination, GenerationStatistics)> getGenerations({
    String? jobId,
    GenerationStatus? status,
    DocumentType? documentType,
    int limit = 20,
    int offset = 0,
  }) async {
    return await _apiClient.getGenerations(
      jobId: jobId,
      status: status,
      documentType: documentType,
      limit: limit,
      offset: offset,
    );
  }
}

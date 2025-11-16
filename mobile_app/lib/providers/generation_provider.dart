import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../models/generation.dart';
import '../services/generation_service.dart';

part 'generation_provider.g.dart';

@riverpod
Future<List<Template>> generationTemplates(Ref ref) async {
  final generationService = ref.watch(generationServiceProvider);
  return await generationService.getTemplates();
}

@riverpod
Future<(List<GenerationListItem>, Pagination, GenerationStatistics)> generationHistory(
  Ref ref, {
  String? jobId,
  GenerationStatus? status,
  DocumentType? documentType,
  int limit = 20,
  int offset = 0,
}) async {
  final generationService = ref.watch(generationServiceProvider);
  return await generationService.getGenerations(
    jobId: jobId,
    status: status,
    documentType: documentType,
    limit: limit,
    offset: offset,
  );
}

@riverpod
class GenerationActions extends _$GenerationActions {
  @override
  void build() {
    // This provider is for actions, not state.
  }

  Future<Generation> startResumeGeneration({
    required String profileId,
    required String jobId,
    required GenerationOptions options,
  }) {
    final service = ref.read(generationServiceProvider);
    return service.startResumeGeneration(
        profileId: profileId, jobId: jobId, options: options);
  }

  Future<Generation> startCoverLetterGeneration({
    required String profileId,
    required String jobId,
    required GenerationOptions options,
  }) {
    final service = ref.read(generationServiceProvider);
    return service.startCoverLetterGeneration(
        profileId: profileId, jobId: jobId, options: options);
  }
}

@riverpod
class ActiveGeneration extends _$ActiveGeneration {
  @override
  Future<Generation> build(String generationId) async {
    final service = ref.read(generationServiceProvider);
    return service.getGenerationResult(generationId);
  }

  Future<void> getResult() async {
    final service = ref.read(generationServiceProvider);
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => service.getGenerationResult(state.value!.id));
  }

  Future<Map<String, dynamic>> getRawResult() async {
    final service = ref.read(generationServiceProvider);
    return service.getRawGenerationResult(state.value!.id);
  }

  Stream<Generation> getGenerationStream() {
    final service = ref.read(generationServiceProvider);
    return service.getGenerationStream(state.value!.id);
  }

  Future<void> cancel() async {
    final service = ref.read(generationServiceProvider);
    await service.cancelGeneration(state.value!.id);
    ref.invalidateSelf();
  }
}

// lib/providers/preference_provider.dart

import 'dart:io';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../models/preferences/user_generation_profile.dart' as model_user_gen_profile;
import '../models/preferences/example_resume.dart' as model_resume;
import '../models/preferences/writing_style_config.dart' as model_cover_letter;
import '../services/api/preference_api_client.dart';
import 'auth_provider.dart';

part 'preference_provider.g.dart';

@riverpod
PreferenceApiClient preferenceApiClient(Ref ref) {
  return PreferenceApiClient(ref.watch(baseHttpClientProvider));
}

@Riverpod(keepAlive: true)
class GenerationProfile extends _$GenerationProfile {
  @override
  Future<model_user_gen_profile.UserGenerationProfile> build() async {
    final userId = ref.watch(authProvider).value?.id;
    if (userId == null) {
      throw Exception('User not authenticated');
    }
    return ref.read(preferenceApiClientProvider).getGenerationProfile();
  }

  Future<void> updatePreferences({
    String? writingStyleConfigId,
    String? layoutConfigId,
    int? maxBulletsPerRole,
    double? targetAtsScore,
  }) async {
    if (state.value == null) return;
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final currentProfile = await future;
      await ref.read(preferenceApiClientProvider).updateGenerationProfile(
            writingStyleConfigId:
                writingStyleConfigId ?? currentProfile.writingStyleConfigId,
            layoutConfigId: layoutConfigId ?? currentProfile.layoutConfigId,
            maxBulletsPerRole:
                maxBulletsPerRole ?? currentProfile.maxBulletsPerRole,
            targetAtsScore: targetAtsScore ?? currentProfile.targetAtsScore,
          );
      // Refetch the profile to ensure the state is up-to-date
      return ref.read(preferenceApiClientProvider).getGenerationProfile();
    });
  }
}

@Riverpod(keepAlive: true)
class ExampleResumes extends _$ExampleResumes {
  @override
  Future<List<model_resume.ExampleResume>> build() async {
    final userId = ref.watch(authProvider).value?.id;
    if (userId == null) {
      return [];
    }
    return ref.read(preferenceApiClientProvider).getExampleResumes();
  }

  Future<void> upload(String filePath, {bool isPrimary = false}) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      await ref
          .read(preferenceApiClientProvider)
          .uploadSampleResume(file: File(filePath), isPrimary: isPrimary);
      return ref.read(preferenceApiClientProvider).getExampleResumes();
    });
  }

  Future<void> delete(String resumeId) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      await ref.read(preferenceApiClientProvider).deleteExampleResume(resumeId);
      return ref.read(preferenceApiClientProvider).getExampleResumes();
    });
  }

  Future<void> setPrimary(String resumeId) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      await ref.read(preferenceApiClientProvider).setPrimaryExampleResume(resumeId);
      return ref.read(preferenceApiClientProvider).getExampleResumes();
    });
  }
}

@Riverpod(keepAlive: true)
class SampleCoverLetters extends _$SampleCoverLetters {
  @override
  Future<List<model_cover_letter.WritingStyleConfig>> build() async {
    final userId = ref.watch(authProvider).value?.id;
    if (userId == null) {
      return [];
    }
    // API for listing cover letters does not exist yet.
    // return ref.read(preferenceApiClientProvider).getSampleCoverLetters();
    return [];
  }

  Future<void> upload(String filePath) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      await ref
          .read(preferenceApiClientProvider)
          .uploadCoverLetter(file: File(filePath));
      // API for listing cover letters does not exist yet, return empty list.
      return <model_cover_letter.WritingStyleConfig>[];
    });
  }

  Future<void> delete(String coverLetterId) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      // API for deleting cover letters does not exist yet.
      // await ref.read(preferenceApiClientProvider).deleteSampleCoverLetter(coverLetterId);
      return <model_cover_letter.WritingStyleConfig>[];
    });
  }
}

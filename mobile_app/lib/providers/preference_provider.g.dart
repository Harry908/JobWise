// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'preference_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

String _$preferenceApiClientHash() =>
    r'3fb3d2dbc5dd65dae0b9f05f84339d59e91bca30';

/// See also [preferenceApiClient].
@ProviderFor(preferenceApiClient)
final preferenceApiClientProvider =
    AutoDisposeProvider<PreferenceApiClient>.internal(
      preferenceApiClient,
      name: r'preferenceApiClientProvider',
      debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
          ? null
          : _$preferenceApiClientHash,
      dependencies: null,
      allTransitiveDependencies: null,
    );

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef PreferenceApiClientRef = AutoDisposeProviderRef<PreferenceApiClient>;
String _$generationProfileHash() => r'75a6369d9ff9c55a4057ead522136195e33db4a8';

/// See also [GenerationProfile].
@ProviderFor(GenerationProfile)
final generationProfileProvider =
    AsyncNotifierProvider<
      GenerationProfile,
      model_user_gen_profile.UserGenerationProfile
    >.internal(
      GenerationProfile.new,
      name: r'generationProfileProvider',
      debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
          ? null
          : _$generationProfileHash,
      dependencies: null,
      allTransitiveDependencies: null,
    );

typedef _$GenerationProfile =
    AsyncNotifier<model_user_gen_profile.UserGenerationProfile>;
String _$exampleResumesHash() => r'6e71882a3a154c85abfac50f0ac552c772082134';

/// See also [ExampleResumes].
@ProviderFor(ExampleResumes)
final exampleResumesProvider =
    AsyncNotifierProvider<
      ExampleResumes,
      List<model_resume.ExampleResume>
    >.internal(
      ExampleResumes.new,
      name: r'exampleResumesProvider',
      debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
          ? null
          : _$exampleResumesHash,
      dependencies: null,
      allTransitiveDependencies: null,
    );

typedef _$ExampleResumes = AsyncNotifier<List<model_resume.ExampleResume>>;
String _$sampleCoverLettersHash() =>
    r'ddf7b15c4155f0ec93b2528304476cd260535bc1';

/// See also [SampleCoverLetters].
@ProviderFor(SampleCoverLetters)
final sampleCoverLettersProvider =
    AsyncNotifierProvider<
      SampleCoverLetters,
      List<model_cover_letter.WritingStyleConfig>
    >.internal(
      SampleCoverLetters.new,
      name: r'sampleCoverLettersProvider',
      debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
          ? null
          : _$sampleCoverLettersHash,
      dependencies: null,
      allTransitiveDependencies: null,
    );

typedef _$SampleCoverLetters =
    AsyncNotifier<List<model_cover_letter.WritingStyleConfig>>;
// ignore_for_file: type=lint
// ignore_for_file: subtype_of_sealed_class, invalid_use_of_internal_member, invalid_use_of_visible_for_testing_member, deprecated_member_use_from_same_package

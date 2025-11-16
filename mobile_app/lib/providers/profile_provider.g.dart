// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'profile_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

String _$profilesApiClientHash() => r'9640eba1e47c6a06d1b9cd12d03045660f7c3230';

/// See also [profilesApiClient].
@ProviderFor(profilesApiClient)
final profilesApiClientProvider =
    AutoDisposeProvider<ProfilesApiClient>.internal(
      profilesApiClient,
      name: r'profilesApiClientProvider',
      debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
          ? null
          : _$profilesApiClientHash,
      dependencies: null,
      allTransitiveDependencies: null,
    );

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef ProfilesApiClientRef = AutoDisposeProviderRef<ProfilesApiClient>;
String _$profileHash() => r'daccc25aa7eb3d407c0fa866c36a2fc078348bfb';

/// See also [Profile].
@ProviderFor(Profile)
final profileProvider = AsyncNotifierProvider<Profile, model.Profile?>.internal(
  Profile.new,
  name: r'profileProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$profileHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

typedef _$Profile = AsyncNotifier<model.Profile?>;
// ignore_for_file: type=lint
// ignore_for_file: subtype_of_sealed_class, invalid_use_of_internal_member, invalid_use_of_visible_for_testing_member, deprecated_member_use_from_same_package

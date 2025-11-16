// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'auth_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

String _$storageServiceHash() => r'62cbe9319bc400f2f78b16bce45d667585b592a2';

/// See also [storageService].
@ProviderFor(storageService)
final storageServiceProvider = Provider<StorageService>.internal(
  storageService,
  name: r'storageServiceProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$storageServiceHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef StorageServiceRef = ProviderRef<StorageService>;
String _$baseHttpClientHash() => r'4a72f1ac59457fa5fee15d07fd670d8715eb53f6';

/// See also [baseHttpClient].
@ProviderFor(baseHttpClient)
final baseHttpClientProvider = Provider<BaseHttpClient>.internal(
  baseHttpClient,
  name: r'baseHttpClientProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$baseHttpClientHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef BaseHttpClientRef = ProviderRef<BaseHttpClient>;
String _$authApiClientHash() => r'64374ed32d2c4c6ab54b40b2c546de9d32ed41f6';

/// See also [authApiClient].
@ProviderFor(authApiClient)
final authApiClientProvider = Provider<AuthApiClient>.internal(
  authApiClient,
  name: r'authApiClientProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$authApiClientHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef AuthApiClientRef = ProviderRef<AuthApiClient>;
String _$authHash() => r'df03c089fe5bcc63d7e21fbf9c7ae91d612cae53';

/// See also [Auth].
@ProviderFor(Auth)
final authProvider = AsyncNotifierProvider<Auth, User?>.internal(
  Auth.new,
  name: r'authProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$authHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

typedef _$Auth = AsyncNotifier<User?>;
// ignore_for_file: type=lint
// ignore_for_file: subtype_of_sealed_class, invalid_use_of_internal_member, invalid_use_of_visible_for_testing_member, deprecated_member_use_from_same_package

// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'settings_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

String _$settingsServiceHash() => r'626173756d1be84bec56f4e54c791f6675823426';

/// See also [settingsService].
@ProviderFor(settingsService)
final settingsServiceProvider = AutoDisposeProvider<SettingsService>.internal(
  settingsService,
  name: r'settingsServiceProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$settingsServiceHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef SettingsServiceRef = AutoDisposeProviderRef<SettingsService>;
String _$dateFormatSettingHash() => r'62c5f4e1554e861729ab28ecb08c28f458c698d5';

/// See also [DateFormatSetting].
@ProviderFor(DateFormatSetting)
final dateFormatSettingProvider =
    AutoDisposeAsyncNotifierProvider<DateFormatSetting, String>.internal(
      DateFormatSetting.new,
      name: r'dateFormatSettingProvider',
      debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
          ? null
          : _$dateFormatSettingHash,
      dependencies: null,
      allTransitiveDependencies: null,
    );

typedef _$DateFormatSetting = AutoDisposeAsyncNotifier<String>;
// ignore_for_file: type=lint
// ignore_for_file: subtype_of_sealed_class, invalid_use_of_internal_member, invalid_use_of_visible_for_testing_member, deprecated_member_use_from_same_package

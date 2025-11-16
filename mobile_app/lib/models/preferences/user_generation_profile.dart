// lib/models/preferences/user_generation_profile.dart

import 'package:freezed_annotation/freezed_annotation.dart';

part 'user_generation_profile.freezed.dart';
part 'user_generation_profile.g.dart';

@freezed
class UserGenerationProfile with _$UserGenerationProfile {
  const UserGenerationProfile._();
  
  const factory UserGenerationProfile({
    required String id,
    required int userId,
    String? layoutConfigId,
    String? writingStyleConfigId,
    required double targetAtsScore,
    required int maxBulletsPerRole,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _UserGenerationProfile;

  factory UserGenerationProfile.fromJson(Map<String, dynamic> json) =>
      _$UserGenerationProfileFromJson(json);


  bool get hasLayoutPreferences => layoutConfigId != null;
  bool get hasStylePreferences => writingStyleConfigId != null;
  bool get isFullyConfigured => hasLayoutPreferences && hasStylePreferences;

  String get setupStatusDisplay {
    if (isFullyConfigured) return 'Setup Complete';
    if (hasLayoutPreferences) return 'Layout Configured - Add Writing Style';
    if (hasStylePreferences) return 'Writing Style Configured - Add Layout';
    return 'Setup Required';
  }

  double get setupProgress {
    if (isFullyConfigured) return 1.0;
    if (hasLayoutPreferences || hasStylePreferences) return 0.5;
    return 0.0;
  }
}

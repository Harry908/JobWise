import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../services/settings_service.dart';

part 'settings_provider.g.dart';

@riverpod
SettingsService settingsService(Ref ref) {
  return SettingsService();
}

@riverpod
class DateFormatSetting extends _$DateFormatSetting {
  @override
  Future<String> build() async {
    return ref.watch(settingsServiceProvider).getDateFormat();
  }

  Future<void> setDateFormat(String format) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      await ref.read(settingsServiceProvider).setDateFormat(format);
      return format;
    });
  }
}

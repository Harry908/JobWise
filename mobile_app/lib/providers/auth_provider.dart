import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../config/app_config.dart';
import '../models/user.dart';
import '../services/api/auth_api_client.dart';
import '../services/api/base_http_client.dart';
import '../services/storage_service.dart';

part 'auth_provider.g.dart';

@Riverpod(keepAlive: true)
StorageService storageService(Ref ref) {
  return StorageService();
}

@Riverpod(keepAlive: true)
BaseHttpClient baseHttpClient(Ref ref) {
  final storage = ref.watch(storageServiceProvider);
  return BaseHttpClient(
    baseUrl: AppConfig.apiBaseUrl,
    storage: storage,
  );
}

@Riverpod(keepAlive: true)
AuthApiClient authApiClient(Ref ref) {
  return AuthApiClient(
    ref.watch(baseHttpClientProvider),
    ref.watch(storageServiceProvider),
  );
}

@Riverpod(keepAlive: true)
class Auth extends _$Auth {
  AuthApiClient get _api => ref.read(authApiClientProvider);
  StorageService get _storage => ref.read(storageServiceProvider);

  @override
  Future<User?> build() async {
    final hasTokens = await _storage.hasTokens();
    if (hasTokens) {
      try {
        return await _api.getCurrentUser();
      } catch (e) {
        await _storage.clearTokens();
        return null;
      }
    }
    return null;
  }

  Future<void> login(String email, String password) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final authResponse = await _api.login(email, password);
      return authResponse.user;
    });
  }

  Future<void> register(String email, String password, String fullName) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final authResponse = await _api.register(email, password, fullName);
      return authResponse.user;
    });
  }

  Future<void> logout() async {
    state = const AsyncValue.loading();
    try {
      await _api.logout();
    } catch (_) {
      // Ignore errors on logout, just clear tokens
    } finally {
      await _storage.clearTokens();
      state = const AsyncValue.data(null);
    }
  }

  Future<bool> checkEmailAvailability(String email) async {
    try {
      return await _api.checkEmailAvailability(email);
    } catch (e) {
      return false;
    }
  }
}

// Convenience provider for checking authentication status
final isAuthenticatedProvider = Provider<bool>((ref) {
  final authState = ref.watch(authProvider);
  return authState.hasValue && authState.value != null;
});
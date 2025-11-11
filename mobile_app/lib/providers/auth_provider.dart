import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../config/app_config.dart';
import '../models/user.dart';
import '../services/api/auth_api_client.dart';
import '../services/api/base_http_client.dart';
import '../services/storage_service.dart';

class AuthState {
  final User? user;
  final bool isLoading;
  final bool isAuthenticated;
  final String? error;

  const AuthState({
    this.user,
    this.isLoading = false,
    this.isAuthenticated = false,
    this.error,
  });

  factory AuthState.initial() => const AuthState();

  AuthState copyWith({
    User? user,
    bool? isLoading,
    bool? isAuthenticated,
    String? error,
  }) {
    return AuthState(
      user: user ?? this.user,
      isLoading: isLoading ?? this.isLoading,
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
      error: error ?? this.error,
    );
  }
}

class AuthNotifier extends StateNotifier<AuthState> {
  final AuthApiClient _authApi;
  final StorageService _storage;

  AuthNotifier(this._authApi, this._storage) : super(AuthState.initial()) {
    // Check if user is already logged in
    _checkAuthStatus();
  }

  Future<void> _checkAuthStatus() async {
    state = state.copyWith(isLoading: true);

    try {
      final hasTokens = await _storage.hasTokens();
      if (hasTokens) {
        final user = await _authApi.getCurrentUser();
        state = state.copyWith(
          user: user,
          isAuthenticated: true,
          isLoading: false,
        );
      } else {
        state = state.copyWith(isLoading: false);
      }
    } catch (e) {
      // Token might be expired, clear storage
      await _storage.clearTokens();
      state = state.copyWith(
        isLoading: false,
        error: 'Session expired. Please log in again.',
      );
    }
  }

  Future<void> login(String email, String password) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final authResponse = await _authApi.login(email, password);
      state = state.copyWith(
        user: authResponse.user,
        isAuthenticated: true,
        isLoading: false,
      );
    } catch (e) {
      String errorMessage = 'Login failed. Please check your credentials.';
      if (e is DioException && e.error is String) {
        errorMessage = e.error as String;
      }
      state = state.copyWith(
        isLoading: false,
        error: errorMessage,
      );
      rethrow;
    }
  }

  Future<void> register(String email, String password, String fullName) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final authResponse = await _authApi.register(email, password, fullName);
      state = state.copyWith(
        user: authResponse.user,
        isAuthenticated: true,
        isLoading: false,
      );
    } catch (e) {
      String errorMessage = 'Registration failed. Please try again.';
      if (e is DioException && e.error is String) {
        errorMessage = e.error as String;
      }
      state = state.copyWith(
        isLoading: false,
        error: errorMessage,
      );
      rethrow;
    }
  }

  Future<void> logout() async {
    state = state.copyWith(isLoading: true);

    try {
      await _authApi.logout();
    } finally {
      await _storage.clearTokens();
      state = AuthState.initial();
    }
  }

  Future<void> refreshToken() async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final authResponse = await _authApi.refreshToken();
      state = state.copyWith(
        user: authResponse.user,
        isLoading: false,
      );
    } catch (e) {
      // Refresh failed, logout user
      await logout();
      rethrow;
    }
  }

  Future<bool> checkEmailAvailability(String email) async {
    try {
      return await _authApi.checkEmailAvailability(email);
    } catch (e) {
      // Return false on error (assume unavailable)
      return false;
    }
  }

  void clearError() {
    state = state.copyWith(error: null);
  }
}

// Providers
final storageServiceProvider = Provider<StorageService>((ref) {
  return StorageService();
});

final baseHttpClientProvider = Provider<BaseHttpClient>((ref) {
  return BaseHttpClient(
    baseUrl: AppConfig.apiBaseUrl,
    storage: ref.watch(storageServiceProvider),
  );
});

final authApiClientProvider = Provider<AuthApiClient>((ref) {
  return AuthApiClient(
    ref.watch(baseHttpClientProvider),
    ref.watch(storageServiceProvider),
  );
});

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(
    ref.watch(authApiClientProvider),
    ref.watch(storageServiceProvider),
  );
});
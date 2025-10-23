import 'package:flutter_test/flutter_test.dart';
import 'package:mobile_app/providers/auth_provider.dart';
import 'package:mobile_app/models/user.dart';

void main() {
  group('AuthState', () {
    test('initial state is correct', () {
      final initialState = AuthState.initial();

      expect(initialState.user, null);
      expect(initialState.isLoading, false);
      expect(initialState.isAuthenticated, false);
      expect(initialState.error, null);
    });

    test('copyWith creates new state with updated fields', () {
      final initialState = AuthState.initial();

      final updatedState = initialState.copyWith(
        isLoading: true,
        error: 'Test error',
      );

      expect(updatedState.user, null);
      expect(updatedState.isLoading, true);
      expect(updatedState.isAuthenticated, false);
      expect(updatedState.error, 'Test error');
    });

    test('authenticated state has correct values', () {
      final testUser = User(
        id: '123',
        email: 'test@example.com',
        fullName: 'John Doe',
      );

      final authState = AuthState(
        user: testUser,
        isLoading: false,
        isAuthenticated: true,
        error: null,
      );

      expect(authState.user, testUser);
      expect(authState.isLoading, false);
      expect(authState.isAuthenticated, true);
      expect(authState.error, null);
    });

    test('loading state has correct values', () {
      final loadingState = AuthState.initial().copyWith(isLoading: true);

      expect(loadingState.user, null);
      expect(loadingState.isLoading, true);
      expect(loadingState.isAuthenticated, false);
      expect(loadingState.error, null);
    });

    test('error state has correct values', () {
      final errorState = AuthState.initial().copyWith(
        error: 'Authentication failed',
      );

      expect(errorState.user, null);
      expect(errorState.isLoading, false);
      expect(errorState.isAuthenticated, false);
      expect(errorState.error, 'Authentication failed');
    });
  });

  // Note: AuthNotifier tests would require mocking the AuthApiClient and StorageService.
  // For now, we test the AuthState class which is the core state management logic.
  // Full AuthNotifier integration tests would be added with proper mocking setup.
}
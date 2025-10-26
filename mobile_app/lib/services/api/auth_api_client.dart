import '../../models/auth_response.dart';
import '../../models/user.dart';
import '../storage_service.dart';
import 'base_http_client.dart';

class AuthApiClient {
  final BaseHttpClient _client;
  final StorageService _storage;

  AuthApiClient(this._client, this._storage);

  Future<AuthResponse> login(String email, String password) async {
    final response = await _client.post('/auth/login', data: {
      'email': email,
      'password': password,
    });

    final authResponse = AuthResponse.fromJson(response.data);

    // Save tokens
    await _storage.saveTokens(
      authResponse.accessToken,
      authResponse.refreshToken,
    );

    return authResponse;
  }

  Future<AuthResponse> register(String email, String password, String fullName) async {
    print('AuthApiClient: Making register request');
    final response = await _client.post('/auth/register', data: {
      'email': email,
      'password': password,
      'full_name': fullName,
    });
    print('AuthApiClient: Register response received: ${response.statusCode}');
    print('AuthApiClient: Response data type: ${response.data.runtimeType}');
    print('AuthApiClient: Response data: ${response.data}');

    print('AuthApiClient: Parsing AuthResponse');
    final authResponse = AuthResponse.fromJson(response.data);
    print('AuthApiClient: AuthResponse parsed successfully: ${authResponse.user}');

    // Auto-login after registration
    await _storage.saveTokens(
      authResponse.accessToken,
      authResponse.refreshToken,
    );
    print('AuthApiClient: Tokens saved successfully');

    return authResponse;
  }

  Future<AuthResponse> refreshToken() async {
    final refreshToken = await _storage.getRefreshToken();
    if (refreshToken == null) {
      throw Exception('No refresh token available');
    }

    final response = await _client.post('/auth/refresh', data: {
      'refresh_token': refreshToken,
    });

    final authResponse = AuthResponse.fromJson(response.data);

    // Save new tokens
    await _storage.saveTokens(
      authResponse.accessToken,
      authResponse.refreshToken,
    );

    return authResponse;
  }

  Future<void> logout() async {
    try {
      await _client.post('/auth/logout');
    } finally {
      await _storage.clearTokens();
    }
  }

  Future<User> getCurrentUser() async {
    final response = await _client.get('/auth/me');
    return User.fromJson(response.data);
  }

  Future<void> changePassword(String currentPassword, String newPassword) async {
    await _client.post('/auth/change-password', data: {
      'current_password': currentPassword,
      'new_password': newPassword,
    });
  }

  Future<bool> checkEmailAvailability(String email) async {
    final response = await _client.get('/auth/check-email', queryParameters: {
      'email': email,
    });
    return response.data['available'] as bool;
  }
}
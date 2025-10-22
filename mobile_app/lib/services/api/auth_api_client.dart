import '../../models/user.dart';
import '../storage_service.dart';
import 'base_http_client.dart';

class AuthApiClient {
  final BaseHttpClient _client;
  final StorageService _storage;

  AuthApiClient(this._client, this._storage);

  Future<User> login(String email, String password) async {
    final response = await _client.post('/auth/login', data: {
      'email': email,
      'password': password,
    });

    // Save tokens
    await _storage.saveTokens(
      response.data['access_token'],
      response.data['refresh_token'],
    );

    return User.fromJson(response.data['user']);
  }

  Future<User> register(String email, String password, String fullName) async {
    final response = await _client.post('/auth/register', data: {
      'email': email,
      'password': password,
      'full_name': fullName,
    });

    // Auto-login after registration
    await _storage.saveTokens(
      response.data['access_token'],
      response.data['refresh_token'],
    );

    return User.fromJson(response.data['user']);
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
}
import 'lib/models/auth_response.dart';

void main() {
  // Test data from the backend response
  final testResponse = {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5NyIsImV4cCI6MTc2MTQ3MTgwMiwidHlwZSI6ImFjY2VzcyJ9.3YsYNyQDA8-Qvb4PCWuwSX-XXd8lvaFaZZBjYm9xW5c",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5NyIsImV4cCI6MTc2MjA3MzAwMiwidHlwZSI6InJlZnJlc2gifQ.9PWfu_zGkbnSrxRs70ouqDm_uwPAaTYHh12xivLTf1A",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user": {
      "id": 97,
      "email": "test5@example.com",
      "full_name": "Test User 5",
      "created_at": "2025-10-26T08:43:22.521926"
    }
  };

  try {
    print('Testing AuthResponse parsing...');
    final authResponse = AuthResponse.fromJson(testResponse);
    print('SUCCESS: AuthResponse parsed successfully');
    print('User: ${authResponse.user}');
    print('Email: ${authResponse.user.email}');
    print('Full Name: ${authResponse.user.fullName}');
  } catch (e) {
    print('ERROR: Failed to parse AuthResponse: $e');
  }
}
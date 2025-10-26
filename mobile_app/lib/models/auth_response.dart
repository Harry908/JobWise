import 'package:freezed_annotation/freezed_annotation.dart';
import 'user.dart';

part 'auth_response.freezed.dart';

@freezed
class AuthResponse with _$AuthResponse {
  const factory AuthResponse({
    required String accessToken,
    required String refreshToken,
    String? tokenType,
    int? expiresIn,
    required User user,
  }) = _AuthResponse;

  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    print('AuthResponse.fromJson: Parsing response: $json');
    try {
      final result = AuthResponse(
        accessToken: json['access_token'] as String,
        refreshToken: json['refresh_token'] as String,
        tokenType: json['token_type'] as String?,
        expiresIn: json['expires_in'] as int?,
        user: User.fromJson(json['user'] as Map<String, dynamic>),
      );
      print('AuthResponse.fromJson: Successfully parsed: ${result.user}');
      return result;
    } catch (e) {
      print('AuthResponse.fromJson: Failed to parse: $e');
      rethrow;
    }
  }
}
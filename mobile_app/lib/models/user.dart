import 'package:freezed_annotation/freezed_annotation.dart';

part 'user.freezed.dart';
part 'user.g.dart';

@freezed
@JsonSerializable()
class User with _$User {
  const factory User({
    required String id,
    required String email,
    required String fullName,
    @Default(true) bool isActive,
    @Default(false) bool isVerified,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) = _User;

  factory User.fromJson(Map<String, dynamic> json) {
    print('User.fromJson: Parsing user: $json');
    // Convert id to string if it's an integer
    if (json['id'] is int) {
      json = Map<String, dynamic>.from(json)..['id'] = json['id'].toString();
      print('User.fromJson: Converted id to string: ${json['id']}');
    }

    // Parse DateTime fields manually
    DateTime? createdAt;
    DateTime? updatedAt;

    if (json['created_at'] is String) {
      try {
        createdAt = DateTime.parse(json['created_at']);
        print('User.fromJson: Parsed created_at: $createdAt');
      } catch (e) {
        print('User.fromJson: Failed to parse created_at: $e');
      }
    }

    if (json['updated_at'] is String) {
      try {
        updatedAt = DateTime.parse(json['updated_at']);
        print('User.fromJson: Parsed updated_at: $updatedAt');
      } catch (e) {
        print('User.fromJson: Failed to parse updated_at: $e');
      }
    }

    try {
      final user = User(
        id: json['id'] as String,
        email: json['email'] as String,
        fullName: json['full_name'] as String,
        isActive: json['is_active'] as bool? ?? true,
        isVerified: json['is_verified'] as bool? ?? false,
        createdAt: createdAt,
        updatedAt: updatedAt,
      );
      print('User.fromJson: Successfully created user: $user');
      return user;
    } catch (e) {
      print('User.fromJson: Failed to create user: $e');
      rethrow;
    }
  }
}
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
    // Convert id to string if it's an integer
    if (json['id'] is int) {
      json = Map<String, dynamic>.from(json)..['id'] = json['id'].toString();
    }
    return _$UserFromJson(json);
  }
}
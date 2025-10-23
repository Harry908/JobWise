import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:json_annotation/json_annotation.dart';

part 'user.freezed.dart';
part 'user.g.dart';

@freezed
@JsonSerializable()
class User with _$User {
  const factory User({
    required String id,
    required String email,
    // ignore: invalid_annotation_target
    @JsonKey(name: 'full_name') required String fullName,
    // ignore: invalid_annotation_target
    @JsonKey(name: 'is_active') @Default(true) bool isActive,
    // ignore: invalid_annotation_target
    @JsonKey(name: 'is_verified') @Default(false) bool isVerified,
    // ignore: invalid_annotation_target
    @JsonKey(name: 'created_at') DateTime? createdAt,
    // ignore: invalid_annotation_target
    @JsonKey(name: 'updated_at') DateTime? updatedAt,
  }) = _User;

  factory User.fromJson(Map<String, dynamic> json) {
    // Convert id to string if it's an integer
    if (json['id'] is int) {
      json = Map<String, dynamic>.from(json)..['id'] = json['id'].toString();
    }
    return _$UserFromJson(json);
  }

  Map<String, dynamic> toJson() => _$UserToJson(this);
}
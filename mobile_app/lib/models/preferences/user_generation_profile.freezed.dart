// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'user_generation_profile.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
  'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models',
);

UserGenerationProfile _$UserGenerationProfileFromJson(
  Map<String, dynamic> json,
) {
  return _UserGenerationProfile.fromJson(json);
}

/// @nodoc
mixin _$UserGenerationProfile {
  String get id => throw _privateConstructorUsedError;
  int get userId => throw _privateConstructorUsedError;
  String? get layoutConfigId => throw _privateConstructorUsedError;
  String? get writingStyleConfigId => throw _privateConstructorUsedError;
  double get targetAtsScore => throw _privateConstructorUsedError;
  int get maxBulletsPerRole => throw _privateConstructorUsedError;
  DateTime get createdAt => throw _privateConstructorUsedError;
  DateTime get updatedAt => throw _privateConstructorUsedError;

  /// Serializes this UserGenerationProfile to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of UserGenerationProfile
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $UserGenerationProfileCopyWith<UserGenerationProfile> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $UserGenerationProfileCopyWith<$Res> {
  factory $UserGenerationProfileCopyWith(
    UserGenerationProfile value,
    $Res Function(UserGenerationProfile) then,
  ) = _$UserGenerationProfileCopyWithImpl<$Res, UserGenerationProfile>;
  @useResult
  $Res call({
    String id,
    int userId,
    String? layoutConfigId,
    String? writingStyleConfigId,
    double targetAtsScore,
    int maxBulletsPerRole,
    DateTime createdAt,
    DateTime updatedAt,
  });
}

/// @nodoc
class _$UserGenerationProfileCopyWithImpl<
  $Res,
  $Val extends UserGenerationProfile
>
    implements $UserGenerationProfileCopyWith<$Res> {
  _$UserGenerationProfileCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of UserGenerationProfile
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? userId = null,
    Object? layoutConfigId = freezed,
    Object? writingStyleConfigId = freezed,
    Object? targetAtsScore = null,
    Object? maxBulletsPerRole = null,
    Object? createdAt = null,
    Object? updatedAt = null,
  }) {
    return _then(
      _value.copyWith(
            id: null == id
                ? _value.id
                : id // ignore: cast_nullable_to_non_nullable
                      as String,
            userId: null == userId
                ? _value.userId
                : userId // ignore: cast_nullable_to_non_nullable
                      as int,
            layoutConfigId: freezed == layoutConfigId
                ? _value.layoutConfigId
                : layoutConfigId // ignore: cast_nullable_to_non_nullable
                      as String?,
            writingStyleConfigId: freezed == writingStyleConfigId
                ? _value.writingStyleConfigId
                : writingStyleConfigId // ignore: cast_nullable_to_non_nullable
                      as String?,
            targetAtsScore: null == targetAtsScore
                ? _value.targetAtsScore
                : targetAtsScore // ignore: cast_nullable_to_non_nullable
                      as double,
            maxBulletsPerRole: null == maxBulletsPerRole
                ? _value.maxBulletsPerRole
                : maxBulletsPerRole // ignore: cast_nullable_to_non_nullable
                      as int,
            createdAt: null == createdAt
                ? _value.createdAt
                : createdAt // ignore: cast_nullable_to_non_nullable
                      as DateTime,
            updatedAt: null == updatedAt
                ? _value.updatedAt
                : updatedAt // ignore: cast_nullable_to_non_nullable
                      as DateTime,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$UserGenerationProfileImplCopyWith<$Res>
    implements $UserGenerationProfileCopyWith<$Res> {
  factory _$$UserGenerationProfileImplCopyWith(
    _$UserGenerationProfileImpl value,
    $Res Function(_$UserGenerationProfileImpl) then,
  ) = __$$UserGenerationProfileImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    String id,
    int userId,
    String? layoutConfigId,
    String? writingStyleConfigId,
    double targetAtsScore,
    int maxBulletsPerRole,
    DateTime createdAt,
    DateTime updatedAt,
  });
}

/// @nodoc
class __$$UserGenerationProfileImplCopyWithImpl<$Res>
    extends
        _$UserGenerationProfileCopyWithImpl<$Res, _$UserGenerationProfileImpl>
    implements _$$UserGenerationProfileImplCopyWith<$Res> {
  __$$UserGenerationProfileImplCopyWithImpl(
    _$UserGenerationProfileImpl _value,
    $Res Function(_$UserGenerationProfileImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of UserGenerationProfile
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? userId = null,
    Object? layoutConfigId = freezed,
    Object? writingStyleConfigId = freezed,
    Object? targetAtsScore = null,
    Object? maxBulletsPerRole = null,
    Object? createdAt = null,
    Object? updatedAt = null,
  }) {
    return _then(
      _$UserGenerationProfileImpl(
        id: null == id
            ? _value.id
            : id // ignore: cast_nullable_to_non_nullable
                  as String,
        userId: null == userId
            ? _value.userId
            : userId // ignore: cast_nullable_to_non_nullable
                  as int,
        layoutConfigId: freezed == layoutConfigId
            ? _value.layoutConfigId
            : layoutConfigId // ignore: cast_nullable_to_non_nullable
                  as String?,
        writingStyleConfigId: freezed == writingStyleConfigId
            ? _value.writingStyleConfigId
            : writingStyleConfigId // ignore: cast_nullable_to_non_nullable
                  as String?,
        targetAtsScore: null == targetAtsScore
            ? _value.targetAtsScore
            : targetAtsScore // ignore: cast_nullable_to_non_nullable
                  as double,
        maxBulletsPerRole: null == maxBulletsPerRole
            ? _value.maxBulletsPerRole
            : maxBulletsPerRole // ignore: cast_nullable_to_non_nullable
                  as int,
        createdAt: null == createdAt
            ? _value.createdAt
            : createdAt // ignore: cast_nullable_to_non_nullable
                  as DateTime,
        updatedAt: null == updatedAt
            ? _value.updatedAt
            : updatedAt // ignore: cast_nullable_to_non_nullable
                  as DateTime,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$UserGenerationProfileImpl extends _UserGenerationProfile {
  const _$UserGenerationProfileImpl({
    required this.id,
    required this.userId,
    this.layoutConfigId,
    this.writingStyleConfigId,
    required this.targetAtsScore,
    required this.maxBulletsPerRole,
    required this.createdAt,
    required this.updatedAt,
  }) : super._();

  factory _$UserGenerationProfileImpl.fromJson(Map<String, dynamic> json) =>
      _$$UserGenerationProfileImplFromJson(json);

  @override
  final String id;
  @override
  final int userId;
  @override
  final String? layoutConfigId;
  @override
  final String? writingStyleConfigId;
  @override
  final double targetAtsScore;
  @override
  final int maxBulletsPerRole;
  @override
  final DateTime createdAt;
  @override
  final DateTime updatedAt;

  @override
  String toString() {
    return 'UserGenerationProfile(id: $id, userId: $userId, layoutConfigId: $layoutConfigId, writingStyleConfigId: $writingStyleConfigId, targetAtsScore: $targetAtsScore, maxBulletsPerRole: $maxBulletsPerRole, createdAt: $createdAt, updatedAt: $updatedAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$UserGenerationProfileImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.userId, userId) || other.userId == userId) &&
            (identical(other.layoutConfigId, layoutConfigId) ||
                other.layoutConfigId == layoutConfigId) &&
            (identical(other.writingStyleConfigId, writingStyleConfigId) ||
                other.writingStyleConfigId == writingStyleConfigId) &&
            (identical(other.targetAtsScore, targetAtsScore) ||
                other.targetAtsScore == targetAtsScore) &&
            (identical(other.maxBulletsPerRole, maxBulletsPerRole) ||
                other.maxBulletsPerRole == maxBulletsPerRole) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.updatedAt, updatedAt) ||
                other.updatedAt == updatedAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
    runtimeType,
    id,
    userId,
    layoutConfigId,
    writingStyleConfigId,
    targetAtsScore,
    maxBulletsPerRole,
    createdAt,
    updatedAt,
  );

  /// Create a copy of UserGenerationProfile
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$UserGenerationProfileImplCopyWith<_$UserGenerationProfileImpl>
  get copyWith =>
      __$$UserGenerationProfileImplCopyWithImpl<_$UserGenerationProfileImpl>(
        this,
        _$identity,
      );

  @override
  Map<String, dynamic> toJson() {
    return _$$UserGenerationProfileImplToJson(this);
  }
}

abstract class _UserGenerationProfile extends UserGenerationProfile {
  const factory _UserGenerationProfile({
    required final String id,
    required final int userId,
    final String? layoutConfigId,
    final String? writingStyleConfigId,
    required final double targetAtsScore,
    required final int maxBulletsPerRole,
    required final DateTime createdAt,
    required final DateTime updatedAt,
  }) = _$UserGenerationProfileImpl;
  const _UserGenerationProfile._() : super._();

  factory _UserGenerationProfile.fromJson(Map<String, dynamic> json) =
      _$UserGenerationProfileImpl.fromJson;

  @override
  String get id;
  @override
  int get userId;
  @override
  String? get layoutConfigId;
  @override
  String? get writingStyleConfigId;
  @override
  double get targetAtsScore;
  @override
  int get maxBulletsPerRole;
  @override
  DateTime get createdAt;
  @override
  DateTime get updatedAt;

  /// Create a copy of UserGenerationProfile
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$UserGenerationProfileImplCopyWith<_$UserGenerationProfileImpl>
  get copyWith => throw _privateConstructorUsedError;
}

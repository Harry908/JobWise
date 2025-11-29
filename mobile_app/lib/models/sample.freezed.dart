// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'sample.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
  'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models',
);

Sample _$SampleFromJson(Map<String, dynamic> json) {
  return _Sample.fromJson(json);
}

/// @nodoc
mixin _$Sample {
  String get id => throw _privateConstructorUsedError;
  @JsonKey(name: 'user_id')
  int get userId => throw _privateConstructorUsedError;
  @JsonKey(name: 'document_type')
  String get documentType => throw _privateConstructorUsedError; // 'resume' or 'cover_letter'
  @JsonKey(name: 'original_filename')
  String get originalFilename => throw _privateConstructorUsedError;
  @JsonKey(name: 'content_text')
  String? get contentText => throw _privateConstructorUsedError; // Full text content
  @JsonKey(name: 'word_count')
  int get wordCount => throw _privateConstructorUsedError;
  @JsonKey(name: 'character_count')
  int get characterCount => throw _privateConstructorUsedError;
  @JsonKey(name: 'is_active')
  bool get isActive => throw _privateConstructorUsedError;
  @JsonKey(name: 'created_at')
  DateTime get createdAt => throw _privateConstructorUsedError;
  @JsonKey(name: 'updated_at')
  DateTime? get updatedAt => throw _privateConstructorUsedError;

  /// Serializes this Sample to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of Sample
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $SampleCopyWith<Sample> get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $SampleCopyWith<$Res> {
  factory $SampleCopyWith(Sample value, $Res Function(Sample) then) =
      _$SampleCopyWithImpl<$Res, Sample>;
  @useResult
  $Res call({
    String id,
    @JsonKey(name: 'user_id') int userId,
    @JsonKey(name: 'document_type') String documentType,
    @JsonKey(name: 'original_filename') String originalFilename,
    @JsonKey(name: 'content_text') String? contentText,
    @JsonKey(name: 'word_count') int wordCount,
    @JsonKey(name: 'character_count') int characterCount,
    @JsonKey(name: 'is_active') bool isActive,
    @JsonKey(name: 'created_at') DateTime createdAt,
    @JsonKey(name: 'updated_at') DateTime? updatedAt,
  });
}

/// @nodoc
class _$SampleCopyWithImpl<$Res, $Val extends Sample>
    implements $SampleCopyWith<$Res> {
  _$SampleCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of Sample
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? userId = null,
    Object? documentType = null,
    Object? originalFilename = null,
    Object? contentText = freezed,
    Object? wordCount = null,
    Object? characterCount = null,
    Object? isActive = null,
    Object? createdAt = null,
    Object? updatedAt = freezed,
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
            documentType: null == documentType
                ? _value.documentType
                : documentType // ignore: cast_nullable_to_non_nullable
                      as String,
            originalFilename: null == originalFilename
                ? _value.originalFilename
                : originalFilename // ignore: cast_nullable_to_non_nullable
                      as String,
            contentText: freezed == contentText
                ? _value.contentText
                : contentText // ignore: cast_nullable_to_non_nullable
                      as String?,
            wordCount: null == wordCount
                ? _value.wordCount
                : wordCount // ignore: cast_nullable_to_non_nullable
                      as int,
            characterCount: null == characterCount
                ? _value.characterCount
                : characterCount // ignore: cast_nullable_to_non_nullable
                      as int,
            isActive: null == isActive
                ? _value.isActive
                : isActive // ignore: cast_nullable_to_non_nullable
                      as bool,
            createdAt: null == createdAt
                ? _value.createdAt
                : createdAt // ignore: cast_nullable_to_non_nullable
                      as DateTime,
            updatedAt: freezed == updatedAt
                ? _value.updatedAt
                : updatedAt // ignore: cast_nullable_to_non_nullable
                      as DateTime?,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$SampleImplCopyWith<$Res> implements $SampleCopyWith<$Res> {
  factory _$$SampleImplCopyWith(
    _$SampleImpl value,
    $Res Function(_$SampleImpl) then,
  ) = __$$SampleImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    String id,
    @JsonKey(name: 'user_id') int userId,
    @JsonKey(name: 'document_type') String documentType,
    @JsonKey(name: 'original_filename') String originalFilename,
    @JsonKey(name: 'content_text') String? contentText,
    @JsonKey(name: 'word_count') int wordCount,
    @JsonKey(name: 'character_count') int characterCount,
    @JsonKey(name: 'is_active') bool isActive,
    @JsonKey(name: 'created_at') DateTime createdAt,
    @JsonKey(name: 'updated_at') DateTime? updatedAt,
  });
}

/// @nodoc
class __$$SampleImplCopyWithImpl<$Res>
    extends _$SampleCopyWithImpl<$Res, _$SampleImpl>
    implements _$$SampleImplCopyWith<$Res> {
  __$$SampleImplCopyWithImpl(
    _$SampleImpl _value,
    $Res Function(_$SampleImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of Sample
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? userId = null,
    Object? documentType = null,
    Object? originalFilename = null,
    Object? contentText = freezed,
    Object? wordCount = null,
    Object? characterCount = null,
    Object? isActive = null,
    Object? createdAt = null,
    Object? updatedAt = freezed,
  }) {
    return _then(
      _$SampleImpl(
        id: null == id
            ? _value.id
            : id // ignore: cast_nullable_to_non_nullable
                  as String,
        userId: null == userId
            ? _value.userId
            : userId // ignore: cast_nullable_to_non_nullable
                  as int,
        documentType: null == documentType
            ? _value.documentType
            : documentType // ignore: cast_nullable_to_non_nullable
                  as String,
        originalFilename: null == originalFilename
            ? _value.originalFilename
            : originalFilename // ignore: cast_nullable_to_non_nullable
                  as String,
        contentText: freezed == contentText
            ? _value.contentText
            : contentText // ignore: cast_nullable_to_non_nullable
                  as String?,
        wordCount: null == wordCount
            ? _value.wordCount
            : wordCount // ignore: cast_nullable_to_non_nullable
                  as int,
        characterCount: null == characterCount
            ? _value.characterCount
            : characterCount // ignore: cast_nullable_to_non_nullable
                  as int,
        isActive: null == isActive
            ? _value.isActive
            : isActive // ignore: cast_nullable_to_non_nullable
                  as bool,
        createdAt: null == createdAt
            ? _value.createdAt
            : createdAt // ignore: cast_nullable_to_non_nullable
                  as DateTime,
        updatedAt: freezed == updatedAt
            ? _value.updatedAt
            : updatedAt // ignore: cast_nullable_to_non_nullable
                  as DateTime?,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$SampleImpl implements _Sample {
  const _$SampleImpl({
    required this.id,
    @JsonKey(name: 'user_id') required this.userId,
    @JsonKey(name: 'document_type') required this.documentType,
    @JsonKey(name: 'original_filename') required this.originalFilename,
    @JsonKey(name: 'content_text') this.contentText,
    @JsonKey(name: 'word_count') required this.wordCount,
    @JsonKey(name: 'character_count') required this.characterCount,
    @JsonKey(name: 'is_active') this.isActive = true,
    @JsonKey(name: 'created_at') required this.createdAt,
    @JsonKey(name: 'updated_at') this.updatedAt,
  });

  factory _$SampleImpl.fromJson(Map<String, dynamic> json) =>
      _$$SampleImplFromJson(json);

  @override
  final String id;
  @override
  @JsonKey(name: 'user_id')
  final int userId;
  @override
  @JsonKey(name: 'document_type')
  final String documentType;
  // 'resume' or 'cover_letter'
  @override
  @JsonKey(name: 'original_filename')
  final String originalFilename;
  @override
  @JsonKey(name: 'content_text')
  final String? contentText;
  // Full text content
  @override
  @JsonKey(name: 'word_count')
  final int wordCount;
  @override
  @JsonKey(name: 'character_count')
  final int characterCount;
  @override
  @JsonKey(name: 'is_active')
  final bool isActive;
  @override
  @JsonKey(name: 'created_at')
  final DateTime createdAt;
  @override
  @JsonKey(name: 'updated_at')
  final DateTime? updatedAt;

  @override
  String toString() {
    return 'Sample(id: $id, userId: $userId, documentType: $documentType, originalFilename: $originalFilename, contentText: $contentText, wordCount: $wordCount, characterCount: $characterCount, isActive: $isActive, createdAt: $createdAt, updatedAt: $updatedAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$SampleImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.userId, userId) || other.userId == userId) &&
            (identical(other.documentType, documentType) ||
                other.documentType == documentType) &&
            (identical(other.originalFilename, originalFilename) ||
                other.originalFilename == originalFilename) &&
            (identical(other.contentText, contentText) ||
                other.contentText == contentText) &&
            (identical(other.wordCount, wordCount) ||
                other.wordCount == wordCount) &&
            (identical(other.characterCount, characterCount) ||
                other.characterCount == characterCount) &&
            (identical(other.isActive, isActive) ||
                other.isActive == isActive) &&
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
    documentType,
    originalFilename,
    contentText,
    wordCount,
    characterCount,
    isActive,
    createdAt,
    updatedAt,
  );

  /// Create a copy of Sample
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$SampleImplCopyWith<_$SampleImpl> get copyWith =>
      __$$SampleImplCopyWithImpl<_$SampleImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$SampleImplToJson(this);
  }
}

abstract class _Sample implements Sample {
  const factory _Sample({
    required final String id,
    @JsonKey(name: 'user_id') required final int userId,
    @JsonKey(name: 'document_type') required final String documentType,
    @JsonKey(name: 'original_filename') required final String originalFilename,
    @JsonKey(name: 'content_text') final String? contentText,
    @JsonKey(name: 'word_count') required final int wordCount,
    @JsonKey(name: 'character_count') required final int characterCount,
    @JsonKey(name: 'is_active') final bool isActive,
    @JsonKey(name: 'created_at') required final DateTime createdAt,
    @JsonKey(name: 'updated_at') final DateTime? updatedAt,
  }) = _$SampleImpl;

  factory _Sample.fromJson(Map<String, dynamic> json) = _$SampleImpl.fromJson;

  @override
  String get id;
  @override
  @JsonKey(name: 'user_id')
  int get userId;
  @override
  @JsonKey(name: 'document_type')
  String get documentType; // 'resume' or 'cover_letter'
  @override
  @JsonKey(name: 'original_filename')
  String get originalFilename;
  @override
  @JsonKey(name: 'content_text')
  String? get contentText; // Full text content
  @override
  @JsonKey(name: 'word_count')
  int get wordCount;
  @override
  @JsonKey(name: 'character_count')
  int get characterCount;
  @override
  @JsonKey(name: 'is_active')
  bool get isActive;
  @override
  @JsonKey(name: 'created_at')
  DateTime get createdAt;
  @override
  @JsonKey(name: 'updated_at')
  DateTime? get updatedAt;

  /// Create a copy of Sample
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$SampleImplCopyWith<_$SampleImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

SampleListResponse _$SampleListResponseFromJson(Map<String, dynamic> json) {
  return _SampleListResponse.fromJson(json);
}

/// @nodoc
mixin _$SampleListResponse {
  List<Sample> get items => throw _privateConstructorUsedError;
  int get total => throw _privateConstructorUsedError;

  /// Serializes this SampleListResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of SampleListResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $SampleListResponseCopyWith<SampleListResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $SampleListResponseCopyWith<$Res> {
  factory $SampleListResponseCopyWith(
    SampleListResponse value,
    $Res Function(SampleListResponse) then,
  ) = _$SampleListResponseCopyWithImpl<$Res, SampleListResponse>;
  @useResult
  $Res call({List<Sample> items, int total});
}

/// @nodoc
class _$SampleListResponseCopyWithImpl<$Res, $Val extends SampleListResponse>
    implements $SampleListResponseCopyWith<$Res> {
  _$SampleListResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of SampleListResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? items = null, Object? total = null}) {
    return _then(
      _value.copyWith(
            items: null == items
                ? _value.items
                : items // ignore: cast_nullable_to_non_nullable
                      as List<Sample>,
            total: null == total
                ? _value.total
                : total // ignore: cast_nullable_to_non_nullable
                      as int,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$SampleListResponseImplCopyWith<$Res>
    implements $SampleListResponseCopyWith<$Res> {
  factory _$$SampleListResponseImplCopyWith(
    _$SampleListResponseImpl value,
    $Res Function(_$SampleListResponseImpl) then,
  ) = __$$SampleListResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({List<Sample> items, int total});
}

/// @nodoc
class __$$SampleListResponseImplCopyWithImpl<$Res>
    extends _$SampleListResponseCopyWithImpl<$Res, _$SampleListResponseImpl>
    implements _$$SampleListResponseImplCopyWith<$Res> {
  __$$SampleListResponseImplCopyWithImpl(
    _$SampleListResponseImpl _value,
    $Res Function(_$SampleListResponseImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of SampleListResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? items = null, Object? total = null}) {
    return _then(
      _$SampleListResponseImpl(
        items: null == items
            ? _value._items
            : items // ignore: cast_nullable_to_non_nullable
                  as List<Sample>,
        total: null == total
            ? _value.total
            : total // ignore: cast_nullable_to_non_nullable
                  as int,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$SampleListResponseImpl implements _SampleListResponse {
  const _$SampleListResponseImpl({
    required final List<Sample> items,
    required this.total,
  }) : _items = items;

  factory _$SampleListResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$SampleListResponseImplFromJson(json);

  final List<Sample> _items;
  @override
  List<Sample> get items {
    if (_items is EqualUnmodifiableListView) return _items;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_items);
  }

  @override
  final int total;

  @override
  String toString() {
    return 'SampleListResponse(items: $items, total: $total)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$SampleListResponseImpl &&
            const DeepCollectionEquality().equals(other._items, _items) &&
            (identical(other.total, total) || other.total == total));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
    runtimeType,
    const DeepCollectionEquality().hash(_items),
    total,
  );

  /// Create a copy of SampleListResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$SampleListResponseImplCopyWith<_$SampleListResponseImpl> get copyWith =>
      __$$SampleListResponseImplCopyWithImpl<_$SampleListResponseImpl>(
        this,
        _$identity,
      );

  @override
  Map<String, dynamic> toJson() {
    return _$$SampleListResponseImplToJson(this);
  }
}

abstract class _SampleListResponse implements SampleListResponse {
  const factory _SampleListResponse({
    required final List<Sample> items,
    required final int total,
  }) = _$SampleListResponseImpl;

  factory _SampleListResponse.fromJson(Map<String, dynamic> json) =
      _$SampleListResponseImpl.fromJson;

  @override
  List<Sample> get items;
  @override
  int get total;

  /// Create a copy of SampleListResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$SampleListResponseImplCopyWith<_$SampleListResponseImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

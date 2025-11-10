// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'generation.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
  'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models',
);

Generation _$GenerationFromJson(Map<String, dynamic> json) {
  return _Generation.fromJson(json);
}

/// @nodoc
mixin _$Generation {
  String get id => throw _privateConstructorUsedError;
  String get profileId => throw _privateConstructorUsedError;
  String get jobId => throw _privateConstructorUsedError;
  DocumentType get documentType => throw _privateConstructorUsedError;
  GenerationStatus get status => throw _privateConstructorUsedError;
  GenerationProgress get progress => throw _privateConstructorUsedError;
  GenerationResult? get result => throw _privateConstructorUsedError;
  String? get errorMessage => throw _privateConstructorUsedError;
  int get tokensUsed => throw _privateConstructorUsedError;
  double? get generationTime => throw _privateConstructorUsedError;
  DateTime get createdAt => throw _privateConstructorUsedError;
  DateTime? get completedAt => throw _privateConstructorUsedError;
  DateTime? get startedAt => throw _privateConstructorUsedError;
  DateTime? get updatedAt => throw _privateConstructorUsedError;
  String? get estimatedCompletion => throw _privateConstructorUsedError;

  /// Serializes this Generation to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of Generation
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $GenerationCopyWith<Generation> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $GenerationCopyWith<$Res> {
  factory $GenerationCopyWith(
    Generation value,
    $Res Function(Generation) then,
  ) = _$GenerationCopyWithImpl<$Res, Generation>;
  @useResult
  $Res call({
    String id,
    String profileId,
    String jobId,
    DocumentType documentType,
    GenerationStatus status,
    GenerationProgress progress,
    GenerationResult? result,
    String? errorMessage,
    int tokensUsed,
    double? generationTime,
    DateTime createdAt,
    DateTime? completedAt,
    DateTime? startedAt,
    DateTime? updatedAt,
    String? estimatedCompletion,
  });

  $GenerationProgressCopyWith<$Res> get progress;
  $GenerationResultCopyWith<$Res>? get result;
}

/// @nodoc
class _$GenerationCopyWithImpl<$Res, $Val extends Generation>
    implements $GenerationCopyWith<$Res> {
  _$GenerationCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of Generation
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? profileId = null,
    Object? jobId = null,
    Object? documentType = null,
    Object? status = null,
    Object? progress = null,
    Object? result = freezed,
    Object? errorMessage = freezed,
    Object? tokensUsed = null,
    Object? generationTime = freezed,
    Object? createdAt = null,
    Object? completedAt = freezed,
    Object? startedAt = freezed,
    Object? updatedAt = freezed,
    Object? estimatedCompletion = freezed,
  }) {
    return _then(
      _value.copyWith(
            id: null == id
                ? _value.id
                : id // ignore: cast_nullable_to_non_nullable
                      as String,
            profileId: null == profileId
                ? _value.profileId
                : profileId // ignore: cast_nullable_to_non_nullable
                      as String,
            jobId: null == jobId
                ? _value.jobId
                : jobId // ignore: cast_nullable_to_non_nullable
                      as String,
            documentType: null == documentType
                ? _value.documentType
                : documentType // ignore: cast_nullable_to_non_nullable
                      as DocumentType,
            status: null == status
                ? _value.status
                : status // ignore: cast_nullable_to_non_nullable
                      as GenerationStatus,
            progress: null == progress
                ? _value.progress
                : progress // ignore: cast_nullable_to_non_nullable
                      as GenerationProgress,
            result: freezed == result
                ? _value.result
                : result // ignore: cast_nullable_to_non_nullable
                      as GenerationResult?,
            errorMessage: freezed == errorMessage
                ? _value.errorMessage
                : errorMessage // ignore: cast_nullable_to_non_nullable
                      as String?,
            tokensUsed: null == tokensUsed
                ? _value.tokensUsed
                : tokensUsed // ignore: cast_nullable_to_non_nullable
                      as int,
            generationTime: freezed == generationTime
                ? _value.generationTime
                : generationTime // ignore: cast_nullable_to_non_nullable
                      as double?,
            createdAt: null == createdAt
                ? _value.createdAt
                : createdAt // ignore: cast_nullable_to_non_nullable
                      as DateTime,
            completedAt: freezed == completedAt
                ? _value.completedAt
                : completedAt // ignore: cast_nullable_to_non_nullable
                      as DateTime?,
            startedAt: freezed == startedAt
                ? _value.startedAt
                : startedAt // ignore: cast_nullable_to_non_nullable
                      as DateTime?,
            updatedAt: freezed == updatedAt
                ? _value.updatedAt
                : updatedAt // ignore: cast_nullable_to_non_nullable
                      as DateTime?,
            estimatedCompletion: freezed == estimatedCompletion
                ? _value.estimatedCompletion
                : estimatedCompletion // ignore: cast_nullable_to_non_nullable
                      as String?,
          )
          as $Val,
    );
  }

  /// Create a copy of Generation
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $GenerationProgressCopyWith<$Res> get progress {
    return $GenerationProgressCopyWith<$Res>(_value.progress, (value) {
      return _then(_value.copyWith(progress: value) as $Val);
    });
  }

  /// Create a copy of Generation
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $GenerationResultCopyWith<$Res>? get result {
    if (_value.result == null) {
      return null;
    }

    return $GenerationResultCopyWith<$Res>(_value.result!, (value) {
      return _then(_value.copyWith(result: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$GenerationImplCopyWith<$Res>
    implements $GenerationCopyWith<$Res> {
  factory _$$GenerationImplCopyWith(
    _$GenerationImpl value,
    $Res Function(_$GenerationImpl) then,
  ) = __$$GenerationImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    String id,
    String profileId,
    String jobId,
    DocumentType documentType,
    GenerationStatus status,
    GenerationProgress progress,
    GenerationResult? result,
    String? errorMessage,
    int tokensUsed,
    double? generationTime,
    DateTime createdAt,
    DateTime? completedAt,
    DateTime? startedAt,
    DateTime? updatedAt,
    String? estimatedCompletion,
  });

  @override
  $GenerationProgressCopyWith<$Res> get progress;
  @override
  $GenerationResultCopyWith<$Res>? get result;
}

/// @nodoc
class __$$GenerationImplCopyWithImpl<$Res>
    extends _$GenerationCopyWithImpl<$Res, _$GenerationImpl>
    implements _$$GenerationImplCopyWith<$Res> {
  __$$GenerationImplCopyWithImpl(
    _$GenerationImpl _value,
    $Res Function(_$GenerationImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of Generation
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? profileId = null,
    Object? jobId = null,
    Object? documentType = null,
    Object? status = null,
    Object? progress = null,
    Object? result = freezed,
    Object? errorMessage = freezed,
    Object? tokensUsed = null,
    Object? generationTime = freezed,
    Object? createdAt = null,
    Object? completedAt = freezed,
    Object? startedAt = freezed,
    Object? updatedAt = freezed,
    Object? estimatedCompletion = freezed,
  }) {
    return _then(
      _$GenerationImpl(
        id: null == id
            ? _value.id
            : id // ignore: cast_nullable_to_non_nullable
                  as String,
        profileId: null == profileId
            ? _value.profileId
            : profileId // ignore: cast_nullable_to_non_nullable
                  as String,
        jobId: null == jobId
            ? _value.jobId
            : jobId // ignore: cast_nullable_to_non_nullable
                  as String,
        documentType: null == documentType
            ? _value.documentType
            : documentType // ignore: cast_nullable_to_non_nullable
                  as DocumentType,
        status: null == status
            ? _value.status
            : status // ignore: cast_nullable_to_non_nullable
                  as GenerationStatus,
        progress: null == progress
            ? _value.progress
            : progress // ignore: cast_nullable_to_non_nullable
                  as GenerationProgress,
        result: freezed == result
            ? _value.result
            : result // ignore: cast_nullable_to_non_nullable
                  as GenerationResult?,
        errorMessage: freezed == errorMessage
            ? _value.errorMessage
            : errorMessage // ignore: cast_nullable_to_non_nullable
                  as String?,
        tokensUsed: null == tokensUsed
            ? _value.tokensUsed
            : tokensUsed // ignore: cast_nullable_to_non_nullable
                  as int,
        generationTime: freezed == generationTime
            ? _value.generationTime
            : generationTime // ignore: cast_nullable_to_non_nullable
                  as double?,
        createdAt: null == createdAt
            ? _value.createdAt
            : createdAt // ignore: cast_nullable_to_non_nullable
                  as DateTime,
        completedAt: freezed == completedAt
            ? _value.completedAt
            : completedAt // ignore: cast_nullable_to_non_nullable
                  as DateTime?,
        startedAt: freezed == startedAt
            ? _value.startedAt
            : startedAt // ignore: cast_nullable_to_non_nullable
                  as DateTime?,
        updatedAt: freezed == updatedAt
            ? _value.updatedAt
            : updatedAt // ignore: cast_nullable_to_non_nullable
                  as DateTime?,
        estimatedCompletion: freezed == estimatedCompletion
            ? _value.estimatedCompletion
            : estimatedCompletion // ignore: cast_nullable_to_non_nullable
                  as String?,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$GenerationImpl implements _Generation {
  const _$GenerationImpl({
    required this.id,
    required this.profileId,
    required this.jobId,
    required this.documentType,
    required this.status,
    required this.progress,
    this.result,
    this.errorMessage,
    this.tokensUsed = 0,
    this.generationTime,
    required this.createdAt,
    this.completedAt,
    this.startedAt,
    this.updatedAt,
    this.estimatedCompletion,
  });

  factory _$GenerationImpl.fromJson(Map<String, dynamic> json) =>
      _$$GenerationImplFromJson(json);

  @override
  final String id;
  @override
  final String profileId;
  @override
  final String jobId;
  @override
  final DocumentType documentType;
  @override
  final GenerationStatus status;
  @override
  final GenerationProgress progress;
  @override
  final GenerationResult? result;
  @override
  final String? errorMessage;
  @override
  @JsonKey()
  final int tokensUsed;
  @override
  final double? generationTime;
  @override
  final DateTime createdAt;
  @override
  final DateTime? completedAt;
  @override
  final DateTime? startedAt;
  @override
  final DateTime? updatedAt;
  @override
  final String? estimatedCompletion;

  @override
  String toString() {
    return 'Generation(id: $id, profileId: $profileId, jobId: $jobId, documentType: $documentType, status: $status, progress: $progress, result: $result, errorMessage: $errorMessage, tokensUsed: $tokensUsed, generationTime: $generationTime, createdAt: $createdAt, completedAt: $completedAt, startedAt: $startedAt, updatedAt: $updatedAt, estimatedCompletion: $estimatedCompletion)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$GenerationImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.profileId, profileId) ||
                other.profileId == profileId) &&
            (identical(other.jobId, jobId) || other.jobId == jobId) &&
            (identical(other.documentType, documentType) ||
                other.documentType == documentType) &&
            (identical(other.status, status) || other.status == status) &&
            (identical(other.progress, progress) ||
                other.progress == progress) &&
            (identical(other.result, result) || other.result == result) &&
            (identical(other.errorMessage, errorMessage) ||
                other.errorMessage == errorMessage) &&
            (identical(other.tokensUsed, tokensUsed) ||
                other.tokensUsed == tokensUsed) &&
            (identical(other.generationTime, generationTime) ||
                other.generationTime == generationTime) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.completedAt, completedAt) ||
                other.completedAt == completedAt) &&
            (identical(other.startedAt, startedAt) ||
                other.startedAt == startedAt) &&
            (identical(other.updatedAt, updatedAt) ||
                other.updatedAt == updatedAt) &&
            (identical(other.estimatedCompletion, estimatedCompletion) ||
                other.estimatedCompletion == estimatedCompletion));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
    runtimeType,
    id,
    profileId,
    jobId,
    documentType,
    status,
    progress,
    result,
    errorMessage,
    tokensUsed,
    generationTime,
    createdAt,
    completedAt,
    startedAt,
    updatedAt,
    estimatedCompletion,
  );

  /// Create a copy of Generation
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$GenerationImplCopyWith<_$GenerationImpl> get copyWith =>
      __$$GenerationImplCopyWithImpl<_$GenerationImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$GenerationImplToJson(this);
  }
}

abstract class _Generation implements Generation {
  const factory _Generation({
    required final String id,
    required final String profileId,
    required final String jobId,
    required final DocumentType documentType,
    required final GenerationStatus status,
    required final GenerationProgress progress,
    final GenerationResult? result,
    final String? errorMessage,
    final int tokensUsed,
    final double? generationTime,
    required final DateTime createdAt,
    final DateTime? completedAt,
    final DateTime? startedAt,
    final DateTime? updatedAt,
    final String? estimatedCompletion,
  }) = _$GenerationImpl;

  factory _Generation.fromJson(Map<String, dynamic> json) =
      _$GenerationImpl.fromJson;

  @override
  String get id;
  @override
  String get profileId;
  @override
  String get jobId;
  @override
  DocumentType get documentType;
  @override
  GenerationStatus get status;
  @override
  GenerationProgress get progress;
  @override
  GenerationResult? get result;
  @override
  String? get errorMessage;
  @override
  int get tokensUsed;
  @override
  double? get generationTime;
  @override
  DateTime get createdAt;
  @override
  DateTime? get completedAt;
  @override
  DateTime? get startedAt;
  @override
  DateTime? get updatedAt;
  @override
  String? get estimatedCompletion;

  /// Create a copy of Generation
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$GenerationImplCopyWith<_$GenerationImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

Pagination _$PaginationFromJson(Map<String, dynamic> json) {
  return _Pagination.fromJson(json);
}

/// @nodoc
mixin _$Pagination {
  int get total => throw _privateConstructorUsedError;
  int get limit => throw _privateConstructorUsedError;
  int get offset => throw _privateConstructorUsedError;
  bool get hasNext => throw _privateConstructorUsedError;
  bool get hasPrevious => throw _privateConstructorUsedError;

  /// Serializes this Pagination to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of Pagination
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $PaginationCopyWith<Pagination> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $PaginationCopyWith<$Res> {
  factory $PaginationCopyWith(
    Pagination value,
    $Res Function(Pagination) then,
  ) = _$PaginationCopyWithImpl<$Res, Pagination>;
  @useResult
  $Res call({int total, int limit, int offset, bool hasNext, bool hasPrevious});
}

/// @nodoc
class _$PaginationCopyWithImpl<$Res, $Val extends Pagination>
    implements $PaginationCopyWith<$Res> {
  _$PaginationCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of Pagination
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? total = null,
    Object? limit = null,
    Object? offset = null,
    Object? hasNext = null,
    Object? hasPrevious = null,
  }) {
    return _then(
      _value.copyWith(
            total: null == total
                ? _value.total
                : total // ignore: cast_nullable_to_non_nullable
                      as int,
            limit: null == limit
                ? _value.limit
                : limit // ignore: cast_nullable_to_non_nullable
                      as int,
            offset: null == offset
                ? _value.offset
                : offset // ignore: cast_nullable_to_non_nullable
                      as int,
            hasNext: null == hasNext
                ? _value.hasNext
                : hasNext // ignore: cast_nullable_to_non_nullable
                      as bool,
            hasPrevious: null == hasPrevious
                ? _value.hasPrevious
                : hasPrevious // ignore: cast_nullable_to_non_nullable
                      as bool,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$PaginationImplCopyWith<$Res>
    implements $PaginationCopyWith<$Res> {
  factory _$$PaginationImplCopyWith(
    _$PaginationImpl value,
    $Res Function(_$PaginationImpl) then,
  ) = __$$PaginationImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({int total, int limit, int offset, bool hasNext, bool hasPrevious});
}

/// @nodoc
class __$$PaginationImplCopyWithImpl<$Res>
    extends _$PaginationCopyWithImpl<$Res, _$PaginationImpl>
    implements _$$PaginationImplCopyWith<$Res> {
  __$$PaginationImplCopyWithImpl(
    _$PaginationImpl _value,
    $Res Function(_$PaginationImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of Pagination
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? total = null,
    Object? limit = null,
    Object? offset = null,
    Object? hasNext = null,
    Object? hasPrevious = null,
  }) {
    return _then(
      _$PaginationImpl(
        total: null == total
            ? _value.total
            : total // ignore: cast_nullable_to_non_nullable
                  as int,
        limit: null == limit
            ? _value.limit
            : limit // ignore: cast_nullable_to_non_nullable
                  as int,
        offset: null == offset
            ? _value.offset
            : offset // ignore: cast_nullable_to_non_nullable
                  as int,
        hasNext: null == hasNext
            ? _value.hasNext
            : hasNext // ignore: cast_nullable_to_non_nullable
                  as bool,
        hasPrevious: null == hasPrevious
            ? _value.hasPrevious
            : hasPrevious // ignore: cast_nullable_to_non_nullable
                  as bool,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$PaginationImpl implements _Pagination {
  const _$PaginationImpl({
    required this.total,
    required this.limit,
    required this.offset,
    required this.hasNext,
    required this.hasPrevious,
  });

  factory _$PaginationImpl.fromJson(Map<String, dynamic> json) =>
      _$$PaginationImplFromJson(json);

  @override
  final int total;
  @override
  final int limit;
  @override
  final int offset;
  @override
  final bool hasNext;
  @override
  final bool hasPrevious;

  @override
  String toString() {
    return 'Pagination(total: $total, limit: $limit, offset: $offset, hasNext: $hasNext, hasPrevious: $hasPrevious)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$PaginationImpl &&
            (identical(other.total, total) || other.total == total) &&
            (identical(other.limit, limit) || other.limit == limit) &&
            (identical(other.offset, offset) || other.offset == offset) &&
            (identical(other.hasNext, hasNext) || other.hasNext == hasNext) &&
            (identical(other.hasPrevious, hasPrevious) ||
                other.hasPrevious == hasPrevious));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, total, limit, offset, hasNext, hasPrevious);

  /// Create a copy of Pagination
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$PaginationImplCopyWith<_$PaginationImpl> get copyWith =>
      __$$PaginationImplCopyWithImpl<_$PaginationImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$PaginationImplToJson(this);
  }
}

abstract class _Pagination implements Pagination {
  const factory _Pagination({
    required final int total,
    required final int limit,
    required final int offset,
    required final bool hasNext,
    required final bool hasPrevious,
  }) = _$PaginationImpl;

  factory _Pagination.fromJson(Map<String, dynamic> json) =
      _$PaginationImpl.fromJson;

  @override
  int get total;
  @override
  int get limit;
  @override
  int get offset;
  @override
  bool get hasNext;
  @override
  bool get hasPrevious;

  /// Create a copy of Pagination
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$PaginationImplCopyWith<_$PaginationImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

GenerationProgress _$GenerationProgressFromJson(Map<String, dynamic> json) {
  return _GenerationProgress.fromJson(json);
}

/// @nodoc
mixin _$GenerationProgress {
  int get currentStage => throw _privateConstructorUsedError;
  int get totalStages => throw _privateConstructorUsedError;
  int get percentage => throw _privateConstructorUsedError;
  String? get stageName => throw _privateConstructorUsedError;
  String? get stageDescription => throw _privateConstructorUsedError;

  /// Serializes this GenerationProgress to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of GenerationProgress
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $GenerationProgressCopyWith<GenerationProgress> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $GenerationProgressCopyWith<$Res> {
  factory $GenerationProgressCopyWith(
    GenerationProgress value,
    $Res Function(GenerationProgress) then,
  ) = _$GenerationProgressCopyWithImpl<$Res, GenerationProgress>;
  @useResult
  $Res call({
    int currentStage,
    int totalStages,
    int percentage,
    String? stageName,
    String? stageDescription,
  });
}

/// @nodoc
class _$GenerationProgressCopyWithImpl<$Res, $Val extends GenerationProgress>
    implements $GenerationProgressCopyWith<$Res> {
  _$GenerationProgressCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of GenerationProgress
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? currentStage = null,
    Object? totalStages = null,
    Object? percentage = null,
    Object? stageName = freezed,
    Object? stageDescription = freezed,
  }) {
    return _then(
      _value.copyWith(
            currentStage: null == currentStage
                ? _value.currentStage
                : currentStage // ignore: cast_nullable_to_non_nullable
                      as int,
            totalStages: null == totalStages
                ? _value.totalStages
                : totalStages // ignore: cast_nullable_to_non_nullable
                      as int,
            percentage: null == percentage
                ? _value.percentage
                : percentage // ignore: cast_nullable_to_non_nullable
                      as int,
            stageName: freezed == stageName
                ? _value.stageName
                : stageName // ignore: cast_nullable_to_non_nullable
                      as String?,
            stageDescription: freezed == stageDescription
                ? _value.stageDescription
                : stageDescription // ignore: cast_nullable_to_non_nullable
                      as String?,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$GenerationProgressImplCopyWith<$Res>
    implements $GenerationProgressCopyWith<$Res> {
  factory _$$GenerationProgressImplCopyWith(
    _$GenerationProgressImpl value,
    $Res Function(_$GenerationProgressImpl) then,
  ) = __$$GenerationProgressImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    int currentStage,
    int totalStages,
    int percentage,
    String? stageName,
    String? stageDescription,
  });
}

/// @nodoc
class __$$GenerationProgressImplCopyWithImpl<$Res>
    extends _$GenerationProgressCopyWithImpl<$Res, _$GenerationProgressImpl>
    implements _$$GenerationProgressImplCopyWith<$Res> {
  __$$GenerationProgressImplCopyWithImpl(
    _$GenerationProgressImpl _value,
    $Res Function(_$GenerationProgressImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of GenerationProgress
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? currentStage = null,
    Object? totalStages = null,
    Object? percentage = null,
    Object? stageName = freezed,
    Object? stageDescription = freezed,
  }) {
    return _then(
      _$GenerationProgressImpl(
        currentStage: null == currentStage
            ? _value.currentStage
            : currentStage // ignore: cast_nullable_to_non_nullable
                  as int,
        totalStages: null == totalStages
            ? _value.totalStages
            : totalStages // ignore: cast_nullable_to_non_nullable
                  as int,
        percentage: null == percentage
            ? _value.percentage
            : percentage // ignore: cast_nullable_to_non_nullable
                  as int,
        stageName: freezed == stageName
            ? _value.stageName
            : stageName // ignore: cast_nullable_to_non_nullable
                  as String?,
        stageDescription: freezed == stageDescription
            ? _value.stageDescription
            : stageDescription // ignore: cast_nullable_to_non_nullable
                  as String?,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$GenerationProgressImpl implements _GenerationProgress {
  const _$GenerationProgressImpl({
    required this.currentStage,
    required this.totalStages,
    required this.percentage,
    this.stageName,
    this.stageDescription,
  });

  factory _$GenerationProgressImpl.fromJson(Map<String, dynamic> json) =>
      _$$GenerationProgressImplFromJson(json);

  @override
  final int currentStage;
  @override
  final int totalStages;
  @override
  final int percentage;
  @override
  final String? stageName;
  @override
  final String? stageDescription;

  @override
  String toString() {
    return 'GenerationProgress(currentStage: $currentStage, totalStages: $totalStages, percentage: $percentage, stageName: $stageName, stageDescription: $stageDescription)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$GenerationProgressImpl &&
            (identical(other.currentStage, currentStage) ||
                other.currentStage == currentStage) &&
            (identical(other.totalStages, totalStages) ||
                other.totalStages == totalStages) &&
            (identical(other.percentage, percentage) ||
                other.percentage == percentage) &&
            (identical(other.stageName, stageName) ||
                other.stageName == stageName) &&
            (identical(other.stageDescription, stageDescription) ||
                other.stageDescription == stageDescription));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
    runtimeType,
    currentStage,
    totalStages,
    percentage,
    stageName,
    stageDescription,
  );

  /// Create a copy of GenerationProgress
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$GenerationProgressImplCopyWith<_$GenerationProgressImpl> get copyWith =>
      __$$GenerationProgressImplCopyWithImpl<_$GenerationProgressImpl>(
        this,
        _$identity,
      );

  @override
  Map<String, dynamic> toJson() {
    return _$$GenerationProgressImplToJson(this);
  }
}

abstract class _GenerationProgress implements GenerationProgress {
  const factory _GenerationProgress({
    required final int currentStage,
    required final int totalStages,
    required final int percentage,
    final String? stageName,
    final String? stageDescription,
  }) = _$GenerationProgressImpl;

  factory _GenerationProgress.fromJson(Map<String, dynamic> json) =
      _$GenerationProgressImpl.fromJson;

  @override
  int get currentStage;
  @override
  int get totalStages;
  @override
  int get percentage;
  @override
  String? get stageName;
  @override
  String? get stageDescription;

  /// Create a copy of GenerationProgress
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$GenerationProgressImplCopyWith<_$GenerationProgressImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

GenerationResult _$GenerationResultFromJson(Map<String, dynamic> json) {
  return _GenerationResult.fromJson(json);
}

/// @nodoc
mixin _$GenerationResult {
  String get documentId => throw _privateConstructorUsedError;
  double get atsScore => throw _privateConstructorUsedError;
  int get matchPercentage => throw _privateConstructorUsedError;
  double get keywordCoverage => throw _privateConstructorUsedError;
  int get keywordsMatched => throw _privateConstructorUsedError;
  int get keywordsTotal => throw _privateConstructorUsedError;
  String get pdfUrl => throw _privateConstructorUsedError;
  List<String> get recommendations => throw _privateConstructorUsedError;

  /// Serializes this GenerationResult to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of GenerationResult
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $GenerationResultCopyWith<GenerationResult> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $GenerationResultCopyWith<$Res> {
  factory $GenerationResultCopyWith(
    GenerationResult value,
    $Res Function(GenerationResult) then,
  ) = _$GenerationResultCopyWithImpl<$Res, GenerationResult>;
  @useResult
  $Res call({
    String documentId,
    double atsScore,
    int matchPercentage,
    double keywordCoverage,
    int keywordsMatched,
    int keywordsTotal,
    String pdfUrl,
    List<String> recommendations,
  });
}

/// @nodoc
class _$GenerationResultCopyWithImpl<$Res, $Val extends GenerationResult>
    implements $GenerationResultCopyWith<$Res> {
  _$GenerationResultCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of GenerationResult
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? documentId = null,
    Object? atsScore = null,
    Object? matchPercentage = null,
    Object? keywordCoverage = null,
    Object? keywordsMatched = null,
    Object? keywordsTotal = null,
    Object? pdfUrl = null,
    Object? recommendations = null,
  }) {
    return _then(
      _value.copyWith(
            documentId: null == documentId
                ? _value.documentId
                : documentId // ignore: cast_nullable_to_non_nullable
                      as String,
            atsScore: null == atsScore
                ? _value.atsScore
                : atsScore // ignore: cast_nullable_to_non_nullable
                      as double,
            matchPercentage: null == matchPercentage
                ? _value.matchPercentage
                : matchPercentage // ignore: cast_nullable_to_non_nullable
                      as int,
            keywordCoverage: null == keywordCoverage
                ? _value.keywordCoverage
                : keywordCoverage // ignore: cast_nullable_to_non_nullable
                      as double,
            keywordsMatched: null == keywordsMatched
                ? _value.keywordsMatched
                : keywordsMatched // ignore: cast_nullable_to_non_nullable
                      as int,
            keywordsTotal: null == keywordsTotal
                ? _value.keywordsTotal
                : keywordsTotal // ignore: cast_nullable_to_non_nullable
                      as int,
            pdfUrl: null == pdfUrl
                ? _value.pdfUrl
                : pdfUrl // ignore: cast_nullable_to_non_nullable
                      as String,
            recommendations: null == recommendations
                ? _value.recommendations
                : recommendations // ignore: cast_nullable_to_non_nullable
                      as List<String>,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$GenerationResultImplCopyWith<$Res>
    implements $GenerationResultCopyWith<$Res> {
  factory _$$GenerationResultImplCopyWith(
    _$GenerationResultImpl value,
    $Res Function(_$GenerationResultImpl) then,
  ) = __$$GenerationResultImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    String documentId,
    double atsScore,
    int matchPercentage,
    double keywordCoverage,
    int keywordsMatched,
    int keywordsTotal,
    String pdfUrl,
    List<String> recommendations,
  });
}

/// @nodoc
class __$$GenerationResultImplCopyWithImpl<$Res>
    extends _$GenerationResultCopyWithImpl<$Res, _$GenerationResultImpl>
    implements _$$GenerationResultImplCopyWith<$Res> {
  __$$GenerationResultImplCopyWithImpl(
    _$GenerationResultImpl _value,
    $Res Function(_$GenerationResultImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of GenerationResult
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? documentId = null,
    Object? atsScore = null,
    Object? matchPercentage = null,
    Object? keywordCoverage = null,
    Object? keywordsMatched = null,
    Object? keywordsTotal = null,
    Object? pdfUrl = null,
    Object? recommendations = null,
  }) {
    return _then(
      _$GenerationResultImpl(
        documentId: null == documentId
            ? _value.documentId
            : documentId // ignore: cast_nullable_to_non_nullable
                  as String,
        atsScore: null == atsScore
            ? _value.atsScore
            : atsScore // ignore: cast_nullable_to_non_nullable
                  as double,
        matchPercentage: null == matchPercentage
            ? _value.matchPercentage
            : matchPercentage // ignore: cast_nullable_to_non_nullable
                  as int,
        keywordCoverage: null == keywordCoverage
            ? _value.keywordCoverage
            : keywordCoverage // ignore: cast_nullable_to_non_nullable
                  as double,
        keywordsMatched: null == keywordsMatched
            ? _value.keywordsMatched
            : keywordsMatched // ignore: cast_nullable_to_non_nullable
                  as int,
        keywordsTotal: null == keywordsTotal
            ? _value.keywordsTotal
            : keywordsTotal // ignore: cast_nullable_to_non_nullable
                  as int,
        pdfUrl: null == pdfUrl
            ? _value.pdfUrl
            : pdfUrl // ignore: cast_nullable_to_non_nullable
                  as String,
        recommendations: null == recommendations
            ? _value._recommendations
            : recommendations // ignore: cast_nullable_to_non_nullable
                  as List<String>,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$GenerationResultImpl implements _GenerationResult {
  const _$GenerationResultImpl({
    required this.documentId,
    required this.atsScore,
    required this.matchPercentage,
    required this.keywordCoverage,
    required this.keywordsMatched,
    required this.keywordsTotal,
    required this.pdfUrl,
    final List<String> recommendations = const [],
  }) : _recommendations = recommendations;

  factory _$GenerationResultImpl.fromJson(Map<String, dynamic> json) =>
      _$$GenerationResultImplFromJson(json);

  @override
  final String documentId;
  @override
  final double atsScore;
  @override
  final int matchPercentage;
  @override
  final double keywordCoverage;
  @override
  final int keywordsMatched;
  @override
  final int keywordsTotal;
  @override
  final String pdfUrl;
  final List<String> _recommendations;
  @override
  @JsonKey()
  List<String> get recommendations {
    if (_recommendations is EqualUnmodifiableListView) return _recommendations;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_recommendations);
  }

  @override
  String toString() {
    return 'GenerationResult(documentId: $documentId, atsScore: $atsScore, matchPercentage: $matchPercentage, keywordCoverage: $keywordCoverage, keywordsMatched: $keywordsMatched, keywordsTotal: $keywordsTotal, pdfUrl: $pdfUrl, recommendations: $recommendations)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$GenerationResultImpl &&
            (identical(other.documentId, documentId) ||
                other.documentId == documentId) &&
            (identical(other.atsScore, atsScore) ||
                other.atsScore == atsScore) &&
            (identical(other.matchPercentage, matchPercentage) ||
                other.matchPercentage == matchPercentage) &&
            (identical(other.keywordCoverage, keywordCoverage) ||
                other.keywordCoverage == keywordCoverage) &&
            (identical(other.keywordsMatched, keywordsMatched) ||
                other.keywordsMatched == keywordsMatched) &&
            (identical(other.keywordsTotal, keywordsTotal) ||
                other.keywordsTotal == keywordsTotal) &&
            (identical(other.pdfUrl, pdfUrl) || other.pdfUrl == pdfUrl) &&
            const DeepCollectionEquality().equals(
              other._recommendations,
              _recommendations,
            ));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
    runtimeType,
    documentId,
    atsScore,
    matchPercentage,
    keywordCoverage,
    keywordsMatched,
    keywordsTotal,
    pdfUrl,
    const DeepCollectionEquality().hash(_recommendations),
  );

  /// Create a copy of GenerationResult
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$GenerationResultImplCopyWith<_$GenerationResultImpl> get copyWith =>
      __$$GenerationResultImplCopyWithImpl<_$GenerationResultImpl>(
        this,
        _$identity,
      );

  @override
  Map<String, dynamic> toJson() {
    return _$$GenerationResultImplToJson(this);
  }
}

abstract class _GenerationResult implements GenerationResult {
  const factory _GenerationResult({
    required final String documentId,
    required final double atsScore,
    required final int matchPercentage,
    required final double keywordCoverage,
    required final int keywordsMatched,
    required final int keywordsTotal,
    required final String pdfUrl,
    final List<String> recommendations,
  }) = _$GenerationResultImpl;

  factory _GenerationResult.fromJson(Map<String, dynamic> json) =
      _$GenerationResultImpl.fromJson;

  @override
  String get documentId;
  @override
  double get atsScore;
  @override
  int get matchPercentage;
  @override
  double get keywordCoverage;
  @override
  int get keywordsMatched;
  @override
  int get keywordsTotal;
  @override
  String get pdfUrl;
  @override
  List<String> get recommendations;

  /// Create a copy of GenerationResult
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$GenerationResultImplCopyWith<_$GenerationResultImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

GenerationOptions _$GenerationOptionsFromJson(Map<String, dynamic> json) {
  return _GenerationOptions.fromJson(json);
}

/// @nodoc
mixin _$GenerationOptions {
  String get template => throw _privateConstructorUsedError;
  String get length => throw _privateConstructorUsedError;
  List<String> get focusAreas => throw _privateConstructorUsedError;
  bool get includeCoverLetter => throw _privateConstructorUsedError;
  String? get customInstructions => throw _privateConstructorUsedError;

  /// Serializes this GenerationOptions to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of GenerationOptions
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $GenerationOptionsCopyWith<GenerationOptions> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $GenerationOptionsCopyWith<$Res> {
  factory $GenerationOptionsCopyWith(
    GenerationOptions value,
    $Res Function(GenerationOptions) then,
  ) = _$GenerationOptionsCopyWithImpl<$Res, GenerationOptions>;
  @useResult
  $Res call({
    String template,
    String length,
    List<String> focusAreas,
    bool includeCoverLetter,
    String? customInstructions,
  });
}

/// @nodoc
class _$GenerationOptionsCopyWithImpl<$Res, $Val extends GenerationOptions>
    implements $GenerationOptionsCopyWith<$Res> {
  _$GenerationOptionsCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of GenerationOptions
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? template = null,
    Object? length = null,
    Object? focusAreas = null,
    Object? includeCoverLetter = null,
    Object? customInstructions = freezed,
  }) {
    return _then(
      _value.copyWith(
            template: null == template
                ? _value.template
                : template // ignore: cast_nullable_to_non_nullable
                      as String,
            length: null == length
                ? _value.length
                : length // ignore: cast_nullable_to_non_nullable
                      as String,
            focusAreas: null == focusAreas
                ? _value.focusAreas
                : focusAreas // ignore: cast_nullable_to_non_nullable
                      as List<String>,
            includeCoverLetter: null == includeCoverLetter
                ? _value.includeCoverLetter
                : includeCoverLetter // ignore: cast_nullable_to_non_nullable
                      as bool,
            customInstructions: freezed == customInstructions
                ? _value.customInstructions
                : customInstructions // ignore: cast_nullable_to_non_nullable
                      as String?,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$GenerationOptionsImplCopyWith<$Res>
    implements $GenerationOptionsCopyWith<$Res> {
  factory _$$GenerationOptionsImplCopyWith(
    _$GenerationOptionsImpl value,
    $Res Function(_$GenerationOptionsImpl) then,
  ) = __$$GenerationOptionsImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    String template,
    String length,
    List<String> focusAreas,
    bool includeCoverLetter,
    String? customInstructions,
  });
}

/// @nodoc
class __$$GenerationOptionsImplCopyWithImpl<$Res>
    extends _$GenerationOptionsCopyWithImpl<$Res, _$GenerationOptionsImpl>
    implements _$$GenerationOptionsImplCopyWith<$Res> {
  __$$GenerationOptionsImplCopyWithImpl(
    _$GenerationOptionsImpl _value,
    $Res Function(_$GenerationOptionsImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of GenerationOptions
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? template = null,
    Object? length = null,
    Object? focusAreas = null,
    Object? includeCoverLetter = null,
    Object? customInstructions = freezed,
  }) {
    return _then(
      _$GenerationOptionsImpl(
        template: null == template
            ? _value.template
            : template // ignore: cast_nullable_to_non_nullable
                  as String,
        length: null == length
            ? _value.length
            : length // ignore: cast_nullable_to_non_nullable
                  as String,
        focusAreas: null == focusAreas
            ? _value._focusAreas
            : focusAreas // ignore: cast_nullable_to_non_nullable
                  as List<String>,
        includeCoverLetter: null == includeCoverLetter
            ? _value.includeCoverLetter
            : includeCoverLetter // ignore: cast_nullable_to_non_nullable
                  as bool,
        customInstructions: freezed == customInstructions
            ? _value.customInstructions
            : customInstructions // ignore: cast_nullable_to_non_nullable
                  as String?,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$GenerationOptionsImpl implements _GenerationOptions {
  const _$GenerationOptionsImpl({
    this.template = 'modern',
    this.length = 'one_page',
    final List<String> focusAreas = const [],
    this.includeCoverLetter = false,
    this.customInstructions,
  }) : _focusAreas = focusAreas;

  factory _$GenerationOptionsImpl.fromJson(Map<String, dynamic> json) =>
      _$$GenerationOptionsImplFromJson(json);

  @override
  @JsonKey()
  final String template;
  @override
  @JsonKey()
  final String length;
  final List<String> _focusAreas;
  @override
  @JsonKey()
  List<String> get focusAreas {
    if (_focusAreas is EqualUnmodifiableListView) return _focusAreas;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_focusAreas);
  }

  @override
  @JsonKey()
  final bool includeCoverLetter;
  @override
  final String? customInstructions;

  @override
  String toString() {
    return 'GenerationOptions(template: $template, length: $length, focusAreas: $focusAreas, includeCoverLetter: $includeCoverLetter, customInstructions: $customInstructions)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$GenerationOptionsImpl &&
            (identical(other.template, template) ||
                other.template == template) &&
            (identical(other.length, length) || other.length == length) &&
            const DeepCollectionEquality().equals(
              other._focusAreas,
              _focusAreas,
            ) &&
            (identical(other.includeCoverLetter, includeCoverLetter) ||
                other.includeCoverLetter == includeCoverLetter) &&
            (identical(other.customInstructions, customInstructions) ||
                other.customInstructions == customInstructions));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
    runtimeType,
    template,
    length,
    const DeepCollectionEquality().hash(_focusAreas),
    includeCoverLetter,
    customInstructions,
  );

  /// Create a copy of GenerationOptions
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$GenerationOptionsImplCopyWith<_$GenerationOptionsImpl> get copyWith =>
      __$$GenerationOptionsImplCopyWithImpl<_$GenerationOptionsImpl>(
        this,
        _$identity,
      );

  @override
  Map<String, dynamic> toJson() {
    return _$$GenerationOptionsImplToJson(this);
  }
}

abstract class _GenerationOptions implements GenerationOptions {
  const factory _GenerationOptions({
    final String template,
    final String length,
    final List<String> focusAreas,
    final bool includeCoverLetter,
    final String? customInstructions,
  }) = _$GenerationOptionsImpl;

  factory _GenerationOptions.fromJson(Map<String, dynamic> json) =
      _$GenerationOptionsImpl.fromJson;

  @override
  String get template;
  @override
  String get length;
  @override
  List<String> get focusAreas;
  @override
  bool get includeCoverLetter;
  @override
  String? get customInstructions;

  /// Create a copy of GenerationOptions
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$GenerationOptionsImplCopyWith<_$GenerationOptionsImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

Template _$TemplateFromJson(Map<String, dynamic> json) {
  return _Template.fromJson(json);
}

/// @nodoc
mixin _$Template {
  String get id => throw _privateConstructorUsedError;
  String get name => throw _privateConstructorUsedError;
  String get description => throw _privateConstructorUsedError;
  String get previewUrl => throw _privateConstructorUsedError;
  List<String> get recommendedFor => throw _privateConstructorUsedError;
  bool get atsFriendly => throw _privateConstructorUsedError;

  /// Serializes this Template to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of Template
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $TemplateCopyWith<Template> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $TemplateCopyWith<$Res> {
  factory $TemplateCopyWith(Template value, $Res Function(Template) then) =
      _$TemplateCopyWithImpl<$Res, Template>;
  @useResult
  $Res call({
    String id,
    String name,
    String description,
    String previewUrl,
    List<String> recommendedFor,
    bool atsFriendly,
  });
}

/// @nodoc
class _$TemplateCopyWithImpl<$Res, $Val extends Template>
    implements $TemplateCopyWith<$Res> {
  _$TemplateCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of Template
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? description = null,
    Object? previewUrl = null,
    Object? recommendedFor = null,
    Object? atsFriendly = null,
  }) {
    return _then(
      _value.copyWith(
            id: null == id
                ? _value.id
                : id // ignore: cast_nullable_to_non_nullable
                      as String,
            name: null == name
                ? _value.name
                : name // ignore: cast_nullable_to_non_nullable
                      as String,
            description: null == description
                ? _value.description
                : description // ignore: cast_nullable_to_non_nullable
                      as String,
            previewUrl: null == previewUrl
                ? _value.previewUrl
                : previewUrl // ignore: cast_nullable_to_non_nullable
                      as String,
            recommendedFor: null == recommendedFor
                ? _value.recommendedFor
                : recommendedFor // ignore: cast_nullable_to_non_nullable
                      as List<String>,
            atsFriendly: null == atsFriendly
                ? _value.atsFriendly
                : atsFriendly // ignore: cast_nullable_to_non_nullable
                      as bool,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$TemplateImplCopyWith<$Res>
    implements $TemplateCopyWith<$Res> {
  factory _$$TemplateImplCopyWith(
    _$TemplateImpl value,
    $Res Function(_$TemplateImpl) then,
  ) = __$$TemplateImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    String id,
    String name,
    String description,
    String previewUrl,
    List<String> recommendedFor,
    bool atsFriendly,
  });
}

/// @nodoc
class __$$TemplateImplCopyWithImpl<$Res>
    extends _$TemplateCopyWithImpl<$Res, _$TemplateImpl>
    implements _$$TemplateImplCopyWith<$Res> {
  __$$TemplateImplCopyWithImpl(
    _$TemplateImpl _value,
    $Res Function(_$TemplateImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of Template
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? description = null,
    Object? previewUrl = null,
    Object? recommendedFor = null,
    Object? atsFriendly = null,
  }) {
    return _then(
      _$TemplateImpl(
        id: null == id
            ? _value.id
            : id // ignore: cast_nullable_to_non_nullable
                  as String,
        name: null == name
            ? _value.name
            : name // ignore: cast_nullable_to_non_nullable
                  as String,
        description: null == description
            ? _value.description
            : description // ignore: cast_nullable_to_non_nullable
                  as String,
        previewUrl: null == previewUrl
            ? _value.previewUrl
            : previewUrl // ignore: cast_nullable_to_non_nullable
                  as String,
        recommendedFor: null == recommendedFor
            ? _value._recommendedFor
            : recommendedFor // ignore: cast_nullable_to_non_nullable
                  as List<String>,
        atsFriendly: null == atsFriendly
            ? _value.atsFriendly
            : atsFriendly // ignore: cast_nullable_to_non_nullable
                  as bool,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$TemplateImpl implements _Template {
  const _$TemplateImpl({
    required this.id,
    required this.name,
    required this.description,
    required this.previewUrl,
    required final List<String> recommendedFor,
    required this.atsFriendly,
  }) : _recommendedFor = recommendedFor;

  factory _$TemplateImpl.fromJson(Map<String, dynamic> json) =>
      _$$TemplateImplFromJson(json);

  @override
  final String id;
  @override
  final String name;
  @override
  final String description;
  @override
  final String previewUrl;
  final List<String> _recommendedFor;
  @override
  List<String> get recommendedFor {
    if (_recommendedFor is EqualUnmodifiableListView) return _recommendedFor;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_recommendedFor);
  }

  @override
  final bool atsFriendly;

  @override
  String toString() {
    return 'Template(id: $id, name: $name, description: $description, previewUrl: $previewUrl, recommendedFor: $recommendedFor, atsFriendly: $atsFriendly)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$TemplateImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.description, description) ||
                other.description == description) &&
            (identical(other.previewUrl, previewUrl) ||
                other.previewUrl == previewUrl) &&
            const DeepCollectionEquality().equals(
              other._recommendedFor,
              _recommendedFor,
            ) &&
            (identical(other.atsFriendly, atsFriendly) ||
                other.atsFriendly == atsFriendly));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
    runtimeType,
    id,
    name,
    description,
    previewUrl,
    const DeepCollectionEquality().hash(_recommendedFor),
    atsFriendly,
  );

  /// Create a copy of Template
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$TemplateImplCopyWith<_$TemplateImpl> get copyWith =>
      __$$TemplateImplCopyWithImpl<_$TemplateImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$TemplateImplToJson(this);
  }
}

abstract class _Template implements Template {
  const factory _Template({
    required final String id,
    required final String name,
    required final String description,
    required final String previewUrl,
    required final List<String> recommendedFor,
    required final bool atsFriendly,
  }) = _$TemplateImpl;

  factory _Template.fromJson(Map<String, dynamic> json) =
      _$TemplateImpl.fromJson;

  @override
  String get id;
  @override
  String get name;
  @override
  String get description;
  @override
  String get previewUrl;
  @override
  List<String> get recommendedFor;
  @override
  bool get atsFriendly;

  /// Create a copy of Template
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$TemplateImplCopyWith<_$TemplateImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

GenerationListItem _$GenerationListItemFromJson(Map<String, dynamic> json) {
  return _GenerationListItem.fromJson(json);
}

/// @nodoc
mixin _$GenerationListItem {
  String get id => throw _privateConstructorUsedError;
  GenerationStatus get status => throw _privateConstructorUsedError;
  DocumentType get documentType => throw _privateConstructorUsedError;
  String get jobTitle => throw _privateConstructorUsedError;
  String get company => throw _privateConstructorUsedError;
  double? get atsScore => throw _privateConstructorUsedError;
  DateTime get createdAt => throw _privateConstructorUsedError;
  DateTime? get completedAt => throw _privateConstructorUsedError;

  /// Serializes this GenerationListItem to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of GenerationListItem
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $GenerationListItemCopyWith<GenerationListItem> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $GenerationListItemCopyWith<$Res> {
  factory $GenerationListItemCopyWith(
    GenerationListItem value,
    $Res Function(GenerationListItem) then,
  ) = _$GenerationListItemCopyWithImpl<$Res, GenerationListItem>;
  @useResult
  $Res call({
    String id,
    GenerationStatus status,
    DocumentType documentType,
    String jobTitle,
    String company,
    double? atsScore,
    DateTime createdAt,
    DateTime? completedAt,
  });
}

/// @nodoc
class _$GenerationListItemCopyWithImpl<$Res, $Val extends GenerationListItem>
    implements $GenerationListItemCopyWith<$Res> {
  _$GenerationListItemCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of GenerationListItem
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? status = null,
    Object? documentType = null,
    Object? jobTitle = null,
    Object? company = null,
    Object? atsScore = freezed,
    Object? createdAt = null,
    Object? completedAt = freezed,
  }) {
    return _then(
      _value.copyWith(
            id: null == id
                ? _value.id
                : id // ignore: cast_nullable_to_non_nullable
                      as String,
            status: null == status
                ? _value.status
                : status // ignore: cast_nullable_to_non_nullable
                      as GenerationStatus,
            documentType: null == documentType
                ? _value.documentType
                : documentType // ignore: cast_nullable_to_non_nullable
                      as DocumentType,
            jobTitle: null == jobTitle
                ? _value.jobTitle
                : jobTitle // ignore: cast_nullable_to_non_nullable
                      as String,
            company: null == company
                ? _value.company
                : company // ignore: cast_nullable_to_non_nullable
                      as String,
            atsScore: freezed == atsScore
                ? _value.atsScore
                : atsScore // ignore: cast_nullable_to_non_nullable
                      as double?,
            createdAt: null == createdAt
                ? _value.createdAt
                : createdAt // ignore: cast_nullable_to_non_nullable
                      as DateTime,
            completedAt: freezed == completedAt
                ? _value.completedAt
                : completedAt // ignore: cast_nullable_to_non_nullable
                      as DateTime?,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$GenerationListItemImplCopyWith<$Res>
    implements $GenerationListItemCopyWith<$Res> {
  factory _$$GenerationListItemImplCopyWith(
    _$GenerationListItemImpl value,
    $Res Function(_$GenerationListItemImpl) then,
  ) = __$$GenerationListItemImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    String id,
    GenerationStatus status,
    DocumentType documentType,
    String jobTitle,
    String company,
    double? atsScore,
    DateTime createdAt,
    DateTime? completedAt,
  });
}

/// @nodoc
class __$$GenerationListItemImplCopyWithImpl<$Res>
    extends _$GenerationListItemCopyWithImpl<$Res, _$GenerationListItemImpl>
    implements _$$GenerationListItemImplCopyWith<$Res> {
  __$$GenerationListItemImplCopyWithImpl(
    _$GenerationListItemImpl _value,
    $Res Function(_$GenerationListItemImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of GenerationListItem
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? status = null,
    Object? documentType = null,
    Object? jobTitle = null,
    Object? company = null,
    Object? atsScore = freezed,
    Object? createdAt = null,
    Object? completedAt = freezed,
  }) {
    return _then(
      _$GenerationListItemImpl(
        id: null == id
            ? _value.id
            : id // ignore: cast_nullable_to_non_nullable
                  as String,
        status: null == status
            ? _value.status
            : status // ignore: cast_nullable_to_non_nullable
                  as GenerationStatus,
        documentType: null == documentType
            ? _value.documentType
            : documentType // ignore: cast_nullable_to_non_nullable
                  as DocumentType,
        jobTitle: null == jobTitle
            ? _value.jobTitle
            : jobTitle // ignore: cast_nullable_to_non_nullable
                  as String,
        company: null == company
            ? _value.company
            : company // ignore: cast_nullable_to_non_nullable
                  as String,
        atsScore: freezed == atsScore
            ? _value.atsScore
            : atsScore // ignore: cast_nullable_to_non_nullable
                  as double?,
        createdAt: null == createdAt
            ? _value.createdAt
            : createdAt // ignore: cast_nullable_to_non_nullable
                  as DateTime,
        completedAt: freezed == completedAt
            ? _value.completedAt
            : completedAt // ignore: cast_nullable_to_non_nullable
                  as DateTime?,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$GenerationListItemImpl implements _GenerationListItem {
  const _$GenerationListItemImpl({
    required this.id,
    required this.status,
    required this.documentType,
    required this.jobTitle,
    required this.company,
    this.atsScore,
    required this.createdAt,
    this.completedAt,
  });

  factory _$GenerationListItemImpl.fromJson(Map<String, dynamic> json) =>
      _$$GenerationListItemImplFromJson(json);

  @override
  final String id;
  @override
  final GenerationStatus status;
  @override
  final DocumentType documentType;
  @override
  final String jobTitle;
  @override
  final String company;
  @override
  final double? atsScore;
  @override
  final DateTime createdAt;
  @override
  final DateTime? completedAt;

  @override
  String toString() {
    return 'GenerationListItem(id: $id, status: $status, documentType: $documentType, jobTitle: $jobTitle, company: $company, atsScore: $atsScore, createdAt: $createdAt, completedAt: $completedAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$GenerationListItemImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.status, status) || other.status == status) &&
            (identical(other.documentType, documentType) ||
                other.documentType == documentType) &&
            (identical(other.jobTitle, jobTitle) ||
                other.jobTitle == jobTitle) &&
            (identical(other.company, company) || other.company == company) &&
            (identical(other.atsScore, atsScore) ||
                other.atsScore == atsScore) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.completedAt, completedAt) ||
                other.completedAt == completedAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
    runtimeType,
    id,
    status,
    documentType,
    jobTitle,
    company,
    atsScore,
    createdAt,
    completedAt,
  );

  /// Create a copy of GenerationListItem
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$GenerationListItemImplCopyWith<_$GenerationListItemImpl> get copyWith =>
      __$$GenerationListItemImplCopyWithImpl<_$GenerationListItemImpl>(
        this,
        _$identity,
      );

  @override
  Map<String, dynamic> toJson() {
    return _$$GenerationListItemImplToJson(this);
  }
}

abstract class _GenerationListItem implements GenerationListItem {
  const factory _GenerationListItem({
    required final String id,
    required final GenerationStatus status,
    required final DocumentType documentType,
    required final String jobTitle,
    required final String company,
    final double? atsScore,
    required final DateTime createdAt,
    final DateTime? completedAt,
  }) = _$GenerationListItemImpl;

  factory _GenerationListItem.fromJson(Map<String, dynamic> json) =
      _$GenerationListItemImpl.fromJson;

  @override
  String get id;
  @override
  GenerationStatus get status;
  @override
  DocumentType get documentType;
  @override
  String get jobTitle;
  @override
  String get company;
  @override
  double? get atsScore;
  @override
  DateTime get createdAt;
  @override
  DateTime? get completedAt;

  /// Create a copy of GenerationListItem
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$GenerationListItemImplCopyWith<_$GenerationListItemImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

GenerationStatistics _$GenerationStatisticsFromJson(Map<String, dynamic> json) {
  return _GenerationStatistics.fromJson(json);
}

/// @nodoc
mixin _$GenerationStatistics {
  int get totalGenerations => throw _privateConstructorUsedError;
  int get completed => throw _privateConstructorUsedError;
  int get failed => throw _privateConstructorUsedError;
  int get inProgress => throw _privateConstructorUsedError;
  double get averageAtsScore => throw _privateConstructorUsedError;

  /// Serializes this GenerationStatistics to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of GenerationStatistics
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $GenerationStatisticsCopyWith<GenerationStatistics> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $GenerationStatisticsCopyWith<$Res> {
  factory $GenerationStatisticsCopyWith(
    GenerationStatistics value,
    $Res Function(GenerationStatistics) then,
  ) = _$GenerationStatisticsCopyWithImpl<$Res, GenerationStatistics>;
  @useResult
  $Res call({
    int totalGenerations,
    int completed,
    int failed,
    int inProgress,
    double averageAtsScore,
  });
}

/// @nodoc
class _$GenerationStatisticsCopyWithImpl<
  $Res,
  $Val extends GenerationStatistics
>
    implements $GenerationStatisticsCopyWith<$Res> {
  _$GenerationStatisticsCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of GenerationStatistics
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? totalGenerations = null,
    Object? completed = null,
    Object? failed = null,
    Object? inProgress = null,
    Object? averageAtsScore = null,
  }) {
    return _then(
      _value.copyWith(
            totalGenerations: null == totalGenerations
                ? _value.totalGenerations
                : totalGenerations // ignore: cast_nullable_to_non_nullable
                      as int,
            completed: null == completed
                ? _value.completed
                : completed // ignore: cast_nullable_to_non_nullable
                      as int,
            failed: null == failed
                ? _value.failed
                : failed // ignore: cast_nullable_to_non_nullable
                      as int,
            inProgress: null == inProgress
                ? _value.inProgress
                : inProgress // ignore: cast_nullable_to_non_nullable
                      as int,
            averageAtsScore: null == averageAtsScore
                ? _value.averageAtsScore
                : averageAtsScore // ignore: cast_nullable_to_non_nullable
                      as double,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$GenerationStatisticsImplCopyWith<$Res>
    implements $GenerationStatisticsCopyWith<$Res> {
  factory _$$GenerationStatisticsImplCopyWith(
    _$GenerationStatisticsImpl value,
    $Res Function(_$GenerationStatisticsImpl) then,
  ) = __$$GenerationStatisticsImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    int totalGenerations,
    int completed,
    int failed,
    int inProgress,
    double averageAtsScore,
  });
}

/// @nodoc
class __$$GenerationStatisticsImplCopyWithImpl<$Res>
    extends _$GenerationStatisticsCopyWithImpl<$Res, _$GenerationStatisticsImpl>
    implements _$$GenerationStatisticsImplCopyWith<$Res> {
  __$$GenerationStatisticsImplCopyWithImpl(
    _$GenerationStatisticsImpl _value,
    $Res Function(_$GenerationStatisticsImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of GenerationStatistics
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? totalGenerations = null,
    Object? completed = null,
    Object? failed = null,
    Object? inProgress = null,
    Object? averageAtsScore = null,
  }) {
    return _then(
      _$GenerationStatisticsImpl(
        totalGenerations: null == totalGenerations
            ? _value.totalGenerations
            : totalGenerations // ignore: cast_nullable_to_non_nullable
                  as int,
        completed: null == completed
            ? _value.completed
            : completed // ignore: cast_nullable_to_non_nullable
                  as int,
        failed: null == failed
            ? _value.failed
            : failed // ignore: cast_nullable_to_non_nullable
                  as int,
        inProgress: null == inProgress
            ? _value.inProgress
            : inProgress // ignore: cast_nullable_to_non_nullable
                  as int,
        averageAtsScore: null == averageAtsScore
            ? _value.averageAtsScore
            : averageAtsScore // ignore: cast_nullable_to_non_nullable
                  as double,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$GenerationStatisticsImpl implements _GenerationStatistics {
  const _$GenerationStatisticsImpl({
    required this.totalGenerations,
    required this.completed,
    required this.failed,
    required this.inProgress,
    required this.averageAtsScore,
  });

  factory _$GenerationStatisticsImpl.fromJson(Map<String, dynamic> json) =>
      _$$GenerationStatisticsImplFromJson(json);

  @override
  final int totalGenerations;
  @override
  final int completed;
  @override
  final int failed;
  @override
  final int inProgress;
  @override
  final double averageAtsScore;

  @override
  String toString() {
    return 'GenerationStatistics(totalGenerations: $totalGenerations, completed: $completed, failed: $failed, inProgress: $inProgress, averageAtsScore: $averageAtsScore)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$GenerationStatisticsImpl &&
            (identical(other.totalGenerations, totalGenerations) ||
                other.totalGenerations == totalGenerations) &&
            (identical(other.completed, completed) ||
                other.completed == completed) &&
            (identical(other.failed, failed) || other.failed == failed) &&
            (identical(other.inProgress, inProgress) ||
                other.inProgress == inProgress) &&
            (identical(other.averageAtsScore, averageAtsScore) ||
                other.averageAtsScore == averageAtsScore));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
    runtimeType,
    totalGenerations,
    completed,
    failed,
    inProgress,
    averageAtsScore,
  );

  /// Create a copy of GenerationStatistics
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$GenerationStatisticsImplCopyWith<_$GenerationStatisticsImpl>
  get copyWith =>
      __$$GenerationStatisticsImplCopyWithImpl<_$GenerationStatisticsImpl>(
        this,
        _$identity,
      );

  @override
  Map<String, dynamic> toJson() {
    return _$$GenerationStatisticsImplToJson(this);
  }
}

abstract class _GenerationStatistics implements GenerationStatistics {
  const factory _GenerationStatistics({
    required final int totalGenerations,
    required final int completed,
    required final int failed,
    required final int inProgress,
    required final double averageAtsScore,
  }) = _$GenerationStatisticsImpl;

  factory _GenerationStatistics.fromJson(Map<String, dynamic> json) =
      _$GenerationStatisticsImpl.fromJson;

  @override
  int get totalGenerations;
  @override
  int get completed;
  @override
  int get failed;
  @override
  int get inProgress;
  @override
  double get averageAtsScore;

  /// Create a copy of GenerationStatistics
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$GenerationStatisticsImplCopyWith<_$GenerationStatisticsImpl>
  get copyWith => throw _privateConstructorUsedError;
}

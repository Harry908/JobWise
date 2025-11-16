// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'job.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
  'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models',
);

Job _$JobFromJson(Map<String, dynamic> json) {
  return _Job.fromJson(json);
}

/// @nodoc
mixin _$Job {
  String get id => throw _privateConstructorUsedError;
  String? get userId => throw _privateConstructorUsedError;
  JobSource get source => throw _privateConstructorUsedError;
  String get title => throw _privateConstructorUsedError;
  String get company => throw _privateConstructorUsedError;
  String? get location => throw _privateConstructorUsedError;
  String? get description => throw _privateConstructorUsedError;
  String? get rawText => throw _privateConstructorUsedError;
  List<String> get parsedKeywords => throw _privateConstructorUsedError;
  List<String> get requirements => throw _privateConstructorUsedError;
  List<String> get benefits => throw _privateConstructorUsedError;
  String? get salaryRange => throw _privateConstructorUsedError;
  bool get remote => throw _privateConstructorUsedError;
  JobStatus get status => throw _privateConstructorUsedError;
  ApplicationStatus get applicationStatus => throw _privateConstructorUsedError;
  DateTime get createdAt => throw _privateConstructorUsedError;
  DateTime get updatedAt => throw _privateConstructorUsedError;

  /// Serializes this Job to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of Job
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $JobCopyWith<Job> get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $JobCopyWith<$Res> {
  factory $JobCopyWith(Job value, $Res Function(Job) then) =
      _$JobCopyWithImpl<$Res, Job>;
  @useResult
  $Res call({
    String id,
    String? userId,
    JobSource source,
    String title,
    String company,
    String? location,
    String? description,
    String? rawText,
    List<String> parsedKeywords,
    List<String> requirements,
    List<String> benefits,
    String? salaryRange,
    bool remote,
    JobStatus status,
    ApplicationStatus applicationStatus,
    DateTime createdAt,
    DateTime updatedAt,
  });
}

/// @nodoc
class _$JobCopyWithImpl<$Res, $Val extends Job> implements $JobCopyWith<$Res> {
  _$JobCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of Job
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? userId = freezed,
    Object? source = null,
    Object? title = null,
    Object? company = null,
    Object? location = freezed,
    Object? description = freezed,
    Object? rawText = freezed,
    Object? parsedKeywords = null,
    Object? requirements = null,
    Object? benefits = null,
    Object? salaryRange = freezed,
    Object? remote = null,
    Object? status = null,
    Object? applicationStatus = null,
    Object? createdAt = null,
    Object? updatedAt = null,
  }) {
    return _then(
      _value.copyWith(
            id: null == id
                ? _value.id
                : id // ignore: cast_nullable_to_non_nullable
                      as String,
            userId: freezed == userId
                ? _value.userId
                : userId // ignore: cast_nullable_to_non_nullable
                      as String?,
            source: null == source
                ? _value.source
                : source // ignore: cast_nullable_to_non_nullable
                      as JobSource,
            title: null == title
                ? _value.title
                : title // ignore: cast_nullable_to_non_nullable
                      as String,
            company: null == company
                ? _value.company
                : company // ignore: cast_nullable_to_non_nullable
                      as String,
            location: freezed == location
                ? _value.location
                : location // ignore: cast_nullable_to_non_nullable
                      as String?,
            description: freezed == description
                ? _value.description
                : description // ignore: cast_nullable_to_non_nullable
                      as String?,
            rawText: freezed == rawText
                ? _value.rawText
                : rawText // ignore: cast_nullable_to_non_nullable
                      as String?,
            parsedKeywords: null == parsedKeywords
                ? _value.parsedKeywords
                : parsedKeywords // ignore: cast_nullable_to_non_nullable
                      as List<String>,
            requirements: null == requirements
                ? _value.requirements
                : requirements // ignore: cast_nullable_to_non_nullable
                      as List<String>,
            benefits: null == benefits
                ? _value.benefits
                : benefits // ignore: cast_nullable_to_non_nullable
                      as List<String>,
            salaryRange: freezed == salaryRange
                ? _value.salaryRange
                : salaryRange // ignore: cast_nullable_to_non_nullable
                      as String?,
            remote: null == remote
                ? _value.remote
                : remote // ignore: cast_nullable_to_non_nullable
                      as bool,
            status: null == status
                ? _value.status
                : status // ignore: cast_nullable_to_non_nullable
                      as JobStatus,
            applicationStatus: null == applicationStatus
                ? _value.applicationStatus
                : applicationStatus // ignore: cast_nullable_to_non_nullable
                      as ApplicationStatus,
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
abstract class _$$JobImplCopyWith<$Res> implements $JobCopyWith<$Res> {
  factory _$$JobImplCopyWith(_$JobImpl value, $Res Function(_$JobImpl) then) =
      __$$JobImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    String id,
    String? userId,
    JobSource source,
    String title,
    String company,
    String? location,
    String? description,
    String? rawText,
    List<String> parsedKeywords,
    List<String> requirements,
    List<String> benefits,
    String? salaryRange,
    bool remote,
    JobStatus status,
    ApplicationStatus applicationStatus,
    DateTime createdAt,
    DateTime updatedAt,
  });
}

/// @nodoc
class __$$JobImplCopyWithImpl<$Res> extends _$JobCopyWithImpl<$Res, _$JobImpl>
    implements _$$JobImplCopyWith<$Res> {
  __$$JobImplCopyWithImpl(_$JobImpl _value, $Res Function(_$JobImpl) _then)
    : super(_value, _then);

  /// Create a copy of Job
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? userId = freezed,
    Object? source = null,
    Object? title = null,
    Object? company = null,
    Object? location = freezed,
    Object? description = freezed,
    Object? rawText = freezed,
    Object? parsedKeywords = null,
    Object? requirements = null,
    Object? benefits = null,
    Object? salaryRange = freezed,
    Object? remote = null,
    Object? status = null,
    Object? applicationStatus = null,
    Object? createdAt = null,
    Object? updatedAt = null,
  }) {
    return _then(
      _$JobImpl(
        id: null == id
            ? _value.id
            : id // ignore: cast_nullable_to_non_nullable
                  as String,
        userId: freezed == userId
            ? _value.userId
            : userId // ignore: cast_nullable_to_non_nullable
                  as String?,
        source: null == source
            ? _value.source
            : source // ignore: cast_nullable_to_non_nullable
                  as JobSource,
        title: null == title
            ? _value.title
            : title // ignore: cast_nullable_to_non_nullable
                  as String,
        company: null == company
            ? _value.company
            : company // ignore: cast_nullable_to_non_nullable
                  as String,
        location: freezed == location
            ? _value.location
            : location // ignore: cast_nullable_to_non_nullable
                  as String?,
        description: freezed == description
            ? _value.description
            : description // ignore: cast_nullable_to_non_nullable
                  as String?,
        rawText: freezed == rawText
            ? _value.rawText
            : rawText // ignore: cast_nullable_to_non_nullable
                  as String?,
        parsedKeywords: null == parsedKeywords
            ? _value._parsedKeywords
            : parsedKeywords // ignore: cast_nullable_to_non_nullable
                  as List<String>,
        requirements: null == requirements
            ? _value._requirements
            : requirements // ignore: cast_nullable_to_non_nullable
                  as List<String>,
        benefits: null == benefits
            ? _value._benefits
            : benefits // ignore: cast_nullable_to_non_nullable
                  as List<String>,
        salaryRange: freezed == salaryRange
            ? _value.salaryRange
            : salaryRange // ignore: cast_nullable_to_non_nullable
                  as String?,
        remote: null == remote
            ? _value.remote
            : remote // ignore: cast_nullable_to_non_nullable
                  as bool,
        status: null == status
            ? _value.status
            : status // ignore: cast_nullable_to_non_nullable
                  as JobStatus,
        applicationStatus: null == applicationStatus
            ? _value.applicationStatus
            : applicationStatus // ignore: cast_nullable_to_non_nullable
                  as ApplicationStatus,
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
class _$JobImpl implements _Job {
  const _$JobImpl({
    required this.id,
    this.userId,
    required this.source,
    required this.title,
    required this.company,
    this.location,
    this.description,
    this.rawText,
    final List<String> parsedKeywords = const [],
    final List<String> requirements = const [],
    final List<String> benefits = const [],
    this.salaryRange,
    this.remote = false,
    this.status = JobStatus.active,
    this.applicationStatus = ApplicationStatus.notApplied,
    required this.createdAt,
    required this.updatedAt,
  }) : _parsedKeywords = parsedKeywords,
       _requirements = requirements,
       _benefits = benefits;

  factory _$JobImpl.fromJson(Map<String, dynamic> json) =>
      _$$JobImplFromJson(json);

  @override
  final String id;
  @override
  final String? userId;
  @override
  final JobSource source;
  @override
  final String title;
  @override
  final String company;
  @override
  final String? location;
  @override
  final String? description;
  @override
  final String? rawText;
  final List<String> _parsedKeywords;
  @override
  @JsonKey()
  List<String> get parsedKeywords {
    if (_parsedKeywords is EqualUnmodifiableListView) return _parsedKeywords;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_parsedKeywords);
  }

  final List<String> _requirements;
  @override
  @JsonKey()
  List<String> get requirements {
    if (_requirements is EqualUnmodifiableListView) return _requirements;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_requirements);
  }

  final List<String> _benefits;
  @override
  @JsonKey()
  List<String> get benefits {
    if (_benefits is EqualUnmodifiableListView) return _benefits;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_benefits);
  }

  @override
  final String? salaryRange;
  @override
  @JsonKey()
  final bool remote;
  @override
  @JsonKey()
  final JobStatus status;
  @override
  @JsonKey()
  final ApplicationStatus applicationStatus;
  @override
  final DateTime createdAt;
  @override
  final DateTime updatedAt;

  @override
  String toString() {
    return 'Job(id: $id, userId: $userId, source: $source, title: $title, company: $company, location: $location, description: $description, rawText: $rawText, parsedKeywords: $parsedKeywords, requirements: $requirements, benefits: $benefits, salaryRange: $salaryRange, remote: $remote, status: $status, applicationStatus: $applicationStatus, createdAt: $createdAt, updatedAt: $updatedAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$JobImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.userId, userId) || other.userId == userId) &&
            (identical(other.source, source) || other.source == source) &&
            (identical(other.title, title) || other.title == title) &&
            (identical(other.company, company) || other.company == company) &&
            (identical(other.location, location) ||
                other.location == location) &&
            (identical(other.description, description) ||
                other.description == description) &&
            (identical(other.rawText, rawText) || other.rawText == rawText) &&
            const DeepCollectionEquality().equals(
              other._parsedKeywords,
              _parsedKeywords,
            ) &&
            const DeepCollectionEquality().equals(
              other._requirements,
              _requirements,
            ) &&
            const DeepCollectionEquality().equals(other._benefits, _benefits) &&
            (identical(other.salaryRange, salaryRange) ||
                other.salaryRange == salaryRange) &&
            (identical(other.remote, remote) || other.remote == remote) &&
            (identical(other.status, status) || other.status == status) &&
            (identical(other.applicationStatus, applicationStatus) ||
                other.applicationStatus == applicationStatus) &&
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
    source,
    title,
    company,
    location,
    description,
    rawText,
    const DeepCollectionEquality().hash(_parsedKeywords),
    const DeepCollectionEquality().hash(_requirements),
    const DeepCollectionEquality().hash(_benefits),
    salaryRange,
    remote,
    status,
    applicationStatus,
    createdAt,
    updatedAt,
  );

  /// Create a copy of Job
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$JobImplCopyWith<_$JobImpl> get copyWith =>
      __$$JobImplCopyWithImpl<_$JobImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$JobImplToJson(this);
  }
}

abstract class _Job implements Job {
  const factory _Job({
    required final String id,
    final String? userId,
    required final JobSource source,
    required final String title,
    required final String company,
    final String? location,
    final String? description,
    final String? rawText,
    final List<String> parsedKeywords,
    final List<String> requirements,
    final List<String> benefits,
    final String? salaryRange,
    final bool remote,
    final JobStatus status,
    final ApplicationStatus applicationStatus,
    required final DateTime createdAt,
    required final DateTime updatedAt,
  }) = _$JobImpl;

  factory _Job.fromJson(Map<String, dynamic> json) = _$JobImpl.fromJson;

  @override
  String get id;
  @override
  String? get userId;
  @override
  JobSource get source;
  @override
  String get title;
  @override
  String get company;
  @override
  String? get location;
  @override
  String? get description;
  @override
  String? get rawText;
  @override
  List<String> get parsedKeywords;
  @override
  List<String> get requirements;
  @override
  List<String> get benefits;
  @override
  String? get salaryRange;
  @override
  bool get remote;
  @override
  JobStatus get status;
  @override
  ApplicationStatus get applicationStatus;
  @override
  DateTime get createdAt;
  @override
  DateTime get updatedAt;

  /// Create a copy of Job
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$JobImplCopyWith<_$JobImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

BrowseJob _$BrowseJobFromJson(Map<String, dynamic> json) {
  return _BrowseJob.fromJson(json);
}

/// @nodoc
mixin _$BrowseJob {
  String get id => throw _privateConstructorUsedError;
  JobSource get source => throw _privateConstructorUsedError;
  String get title => throw _privateConstructorUsedError;
  String get company => throw _privateConstructorUsedError;
  String? get location => throw _privateConstructorUsedError;
  String? get description => throw _privateConstructorUsedError;
  List<String> get parsedKeywords => throw _privateConstructorUsedError;
  List<String> get requirements => throw _privateConstructorUsedError;
  List<String> get benefits => throw _privateConstructorUsedError;
  String? get salaryRange => throw _privateConstructorUsedError;
  bool get remote => throw _privateConstructorUsedError;

  /// Serializes this BrowseJob to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of BrowseJob
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $BrowseJobCopyWith<BrowseJob> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $BrowseJobCopyWith<$Res> {
  factory $BrowseJobCopyWith(BrowseJob value, $Res Function(BrowseJob) then) =
      _$BrowseJobCopyWithImpl<$Res, BrowseJob>;
  @useResult
  $Res call({
    String id,
    JobSource source,
    String title,
    String company,
    String? location,
    String? description,
    List<String> parsedKeywords,
    List<String> requirements,
    List<String> benefits,
    String? salaryRange,
    bool remote,
  });
}

/// @nodoc
class _$BrowseJobCopyWithImpl<$Res, $Val extends BrowseJob>
    implements $BrowseJobCopyWith<$Res> {
  _$BrowseJobCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of BrowseJob
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? source = null,
    Object? title = null,
    Object? company = null,
    Object? location = freezed,
    Object? description = freezed,
    Object? parsedKeywords = null,
    Object? requirements = null,
    Object? benefits = null,
    Object? salaryRange = freezed,
    Object? remote = null,
  }) {
    return _then(
      _value.copyWith(
            id: null == id
                ? _value.id
                : id // ignore: cast_nullable_to_non_nullable
                      as String,
            source: null == source
                ? _value.source
                : source // ignore: cast_nullable_to_non_nullable
                      as JobSource,
            title: null == title
                ? _value.title
                : title // ignore: cast_nullable_to_non_nullable
                      as String,
            company: null == company
                ? _value.company
                : company // ignore: cast_nullable_to_non_nullable
                      as String,
            location: freezed == location
                ? _value.location
                : location // ignore: cast_nullable_to_non_nullable
                      as String?,
            description: freezed == description
                ? _value.description
                : description // ignore: cast_nullable_to_non_nullable
                      as String?,
            parsedKeywords: null == parsedKeywords
                ? _value.parsedKeywords
                : parsedKeywords // ignore: cast_nullable_to_non_nullable
                      as List<String>,
            requirements: null == requirements
                ? _value.requirements
                : requirements // ignore: cast_nullable_to_non_nullable
                      as List<String>,
            benefits: null == benefits
                ? _value.benefits
                : benefits // ignore: cast_nullable_to_non_nullable
                      as List<String>,
            salaryRange: freezed == salaryRange
                ? _value.salaryRange
                : salaryRange // ignore: cast_nullable_to_non_nullable
                      as String?,
            remote: null == remote
                ? _value.remote
                : remote // ignore: cast_nullable_to_non_nullable
                      as bool,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$BrowseJobImplCopyWith<$Res>
    implements $BrowseJobCopyWith<$Res> {
  factory _$$BrowseJobImplCopyWith(
    _$BrowseJobImpl value,
    $Res Function(_$BrowseJobImpl) then,
  ) = __$$BrowseJobImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    String id,
    JobSource source,
    String title,
    String company,
    String? location,
    String? description,
    List<String> parsedKeywords,
    List<String> requirements,
    List<String> benefits,
    String? salaryRange,
    bool remote,
  });
}

/// @nodoc
class __$$BrowseJobImplCopyWithImpl<$Res>
    extends _$BrowseJobCopyWithImpl<$Res, _$BrowseJobImpl>
    implements _$$BrowseJobImplCopyWith<$Res> {
  __$$BrowseJobImplCopyWithImpl(
    _$BrowseJobImpl _value,
    $Res Function(_$BrowseJobImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of BrowseJob
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? source = null,
    Object? title = null,
    Object? company = null,
    Object? location = freezed,
    Object? description = freezed,
    Object? parsedKeywords = null,
    Object? requirements = null,
    Object? benefits = null,
    Object? salaryRange = freezed,
    Object? remote = null,
  }) {
    return _then(
      _$BrowseJobImpl(
        id: null == id
            ? _value.id
            : id // ignore: cast_nullable_to_non_nullable
                  as String,
        source: null == source
            ? _value.source
            : source // ignore: cast_nullable_to_non_nullable
                  as JobSource,
        title: null == title
            ? _value.title
            : title // ignore: cast_nullable_to_non_nullable
                  as String,
        company: null == company
            ? _value.company
            : company // ignore: cast_nullable_to_non_nullable
                  as String,
        location: freezed == location
            ? _value.location
            : location // ignore: cast_nullable_to_non_nullable
                  as String?,
        description: freezed == description
            ? _value.description
            : description // ignore: cast_nullable_to_non_nullable
                  as String?,
        parsedKeywords: null == parsedKeywords
            ? _value._parsedKeywords
            : parsedKeywords // ignore: cast_nullable_to_non_nullable
                  as List<String>,
        requirements: null == requirements
            ? _value._requirements
            : requirements // ignore: cast_nullable_to_non_nullable
                  as List<String>,
        benefits: null == benefits
            ? _value._benefits
            : benefits // ignore: cast_nullable_to_non_nullable
                  as List<String>,
        salaryRange: freezed == salaryRange
            ? _value.salaryRange
            : salaryRange // ignore: cast_nullable_to_non_nullable
                  as String?,
        remote: null == remote
            ? _value.remote
            : remote // ignore: cast_nullable_to_non_nullable
                  as bool,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$BrowseJobImpl implements _BrowseJob {
  const _$BrowseJobImpl({
    required this.id,
    required this.source,
    required this.title,
    required this.company,
    this.location,
    this.description,
    final List<String> parsedKeywords = const [],
    final List<String> requirements = const [],
    final List<String> benefits = const [],
    this.salaryRange,
    this.remote = false,
  }) : _parsedKeywords = parsedKeywords,
       _requirements = requirements,
       _benefits = benefits;

  factory _$BrowseJobImpl.fromJson(Map<String, dynamic> json) =>
      _$$BrowseJobImplFromJson(json);

  @override
  final String id;
  @override
  final JobSource source;
  @override
  final String title;
  @override
  final String company;
  @override
  final String? location;
  @override
  final String? description;
  final List<String> _parsedKeywords;
  @override
  @JsonKey()
  List<String> get parsedKeywords {
    if (_parsedKeywords is EqualUnmodifiableListView) return _parsedKeywords;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_parsedKeywords);
  }

  final List<String> _requirements;
  @override
  @JsonKey()
  List<String> get requirements {
    if (_requirements is EqualUnmodifiableListView) return _requirements;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_requirements);
  }

  final List<String> _benefits;
  @override
  @JsonKey()
  List<String> get benefits {
    if (_benefits is EqualUnmodifiableListView) return _benefits;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_benefits);
  }

  @override
  final String? salaryRange;
  @override
  @JsonKey()
  final bool remote;

  @override
  String toString() {
    return 'BrowseJob(id: $id, source: $source, title: $title, company: $company, location: $location, description: $description, parsedKeywords: $parsedKeywords, requirements: $requirements, benefits: $benefits, salaryRange: $salaryRange, remote: $remote)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$BrowseJobImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.source, source) || other.source == source) &&
            (identical(other.title, title) || other.title == title) &&
            (identical(other.company, company) || other.company == company) &&
            (identical(other.location, location) ||
                other.location == location) &&
            (identical(other.description, description) ||
                other.description == description) &&
            const DeepCollectionEquality().equals(
              other._parsedKeywords,
              _parsedKeywords,
            ) &&
            const DeepCollectionEquality().equals(
              other._requirements,
              _requirements,
            ) &&
            const DeepCollectionEquality().equals(other._benefits, _benefits) &&
            (identical(other.salaryRange, salaryRange) ||
                other.salaryRange == salaryRange) &&
            (identical(other.remote, remote) || other.remote == remote));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
    runtimeType,
    id,
    source,
    title,
    company,
    location,
    description,
    const DeepCollectionEquality().hash(_parsedKeywords),
    const DeepCollectionEquality().hash(_requirements),
    const DeepCollectionEquality().hash(_benefits),
    salaryRange,
    remote,
  );

  /// Create a copy of BrowseJob
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$BrowseJobImplCopyWith<_$BrowseJobImpl> get copyWith =>
      __$$BrowseJobImplCopyWithImpl<_$BrowseJobImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$BrowseJobImplToJson(this);
  }
}

abstract class _BrowseJob implements BrowseJob {
  const factory _BrowseJob({
    required final String id,
    required final JobSource source,
    required final String title,
    required final String company,
    final String? location,
    final String? description,
    final List<String> parsedKeywords,
    final List<String> requirements,
    final List<String> benefits,
    final String? salaryRange,
    final bool remote,
  }) = _$BrowseJobImpl;

  factory _BrowseJob.fromJson(Map<String, dynamic> json) =
      _$BrowseJobImpl.fromJson;

  @override
  String get id;
  @override
  JobSource get source;
  @override
  String get title;
  @override
  String get company;
  @override
  String? get location;
  @override
  String? get description;
  @override
  List<String> get parsedKeywords;
  @override
  List<String> get requirements;
  @override
  List<String> get benefits;
  @override
  String? get salaryRange;
  @override
  bool get remote;

  /// Create a copy of BrowseJob
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$BrowseJobImplCopyWith<_$BrowseJobImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

JobListResponse _$JobListResponseFromJson(Map<String, dynamic> json) {
  return _JobListResponse.fromJson(json);
}

/// @nodoc
mixin _$JobListResponse {
  List<Job> get jobs => throw _privateConstructorUsedError;
  int get total => throw _privateConstructorUsedError;
  PaginationMeta get pagination => throw _privateConstructorUsedError;

  /// Serializes this JobListResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of JobListResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $JobListResponseCopyWith<JobListResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $JobListResponseCopyWith<$Res> {
  factory $JobListResponseCopyWith(
    JobListResponse value,
    $Res Function(JobListResponse) then,
  ) = _$JobListResponseCopyWithImpl<$Res, JobListResponse>;
  @useResult
  $Res call({List<Job> jobs, int total, PaginationMeta pagination});

  $PaginationMetaCopyWith<$Res> get pagination;
}

/// @nodoc
class _$JobListResponseCopyWithImpl<$Res, $Val extends JobListResponse>
    implements $JobListResponseCopyWith<$Res> {
  _$JobListResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of JobListResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? jobs = null,
    Object? total = null,
    Object? pagination = null,
  }) {
    return _then(
      _value.copyWith(
            jobs: null == jobs
                ? _value.jobs
                : jobs // ignore: cast_nullable_to_non_nullable
                      as List<Job>,
            total: null == total
                ? _value.total
                : total // ignore: cast_nullable_to_non_nullable
                      as int,
            pagination: null == pagination
                ? _value.pagination
                : pagination // ignore: cast_nullable_to_non_nullable
                      as PaginationMeta,
          )
          as $Val,
    );
  }

  /// Create a copy of JobListResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $PaginationMetaCopyWith<$Res> get pagination {
    return $PaginationMetaCopyWith<$Res>(_value.pagination, (value) {
      return _then(_value.copyWith(pagination: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$JobListResponseImplCopyWith<$Res>
    implements $JobListResponseCopyWith<$Res> {
  factory _$$JobListResponseImplCopyWith(
    _$JobListResponseImpl value,
    $Res Function(_$JobListResponseImpl) then,
  ) = __$$JobListResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({List<Job> jobs, int total, PaginationMeta pagination});

  @override
  $PaginationMetaCopyWith<$Res> get pagination;
}

/// @nodoc
class __$$JobListResponseImplCopyWithImpl<$Res>
    extends _$JobListResponseCopyWithImpl<$Res, _$JobListResponseImpl>
    implements _$$JobListResponseImplCopyWith<$Res> {
  __$$JobListResponseImplCopyWithImpl(
    _$JobListResponseImpl _value,
    $Res Function(_$JobListResponseImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of JobListResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? jobs = null,
    Object? total = null,
    Object? pagination = null,
  }) {
    return _then(
      _$JobListResponseImpl(
        jobs: null == jobs
            ? _value._jobs
            : jobs // ignore: cast_nullable_to_non_nullable
                  as List<Job>,
        total: null == total
            ? _value.total
            : total // ignore: cast_nullable_to_non_nullable
                  as int,
        pagination: null == pagination
            ? _value.pagination
            : pagination // ignore: cast_nullable_to_non_nullable
                  as PaginationMeta,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$JobListResponseImpl implements _JobListResponse {
  const _$JobListResponseImpl({
    required final List<Job> jobs,
    required this.total,
    required this.pagination,
  }) : _jobs = jobs;

  factory _$JobListResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$JobListResponseImplFromJson(json);

  final List<Job> _jobs;
  @override
  List<Job> get jobs {
    if (_jobs is EqualUnmodifiableListView) return _jobs;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_jobs);
  }

  @override
  final int total;
  @override
  final PaginationMeta pagination;

  @override
  String toString() {
    return 'JobListResponse(jobs: $jobs, total: $total, pagination: $pagination)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$JobListResponseImpl &&
            const DeepCollectionEquality().equals(other._jobs, _jobs) &&
            (identical(other.total, total) || other.total == total) &&
            (identical(other.pagination, pagination) ||
                other.pagination == pagination));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
    runtimeType,
    const DeepCollectionEquality().hash(_jobs),
    total,
    pagination,
  );

  /// Create a copy of JobListResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$JobListResponseImplCopyWith<_$JobListResponseImpl> get copyWith =>
      __$$JobListResponseImplCopyWithImpl<_$JobListResponseImpl>(
        this,
        _$identity,
      );

  @override
  Map<String, dynamic> toJson() {
    return _$$JobListResponseImplToJson(this);
  }
}

abstract class _JobListResponse implements JobListResponse {
  const factory _JobListResponse({
    required final List<Job> jobs,
    required final int total,
    required final PaginationMeta pagination,
  }) = _$JobListResponseImpl;

  factory _JobListResponse.fromJson(Map<String, dynamic> json) =
      _$JobListResponseImpl.fromJson;

  @override
  List<Job> get jobs;
  @override
  int get total;
  @override
  PaginationMeta get pagination;

  /// Create a copy of JobListResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$JobListResponseImplCopyWith<_$JobListResponseImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

BrowseJobListResponse _$BrowseJobListResponseFromJson(
  Map<String, dynamic> json,
) {
  return _BrowseJobListResponse.fromJson(json);
}

/// @nodoc
mixin _$BrowseJobListResponse {
  List<BrowseJob> get jobs => throw _privateConstructorUsedError;
  int get total => throw _privateConstructorUsedError;
  PaginationMeta get pagination => throw _privateConstructorUsedError;

  /// Serializes this BrowseJobListResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of BrowseJobListResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $BrowseJobListResponseCopyWith<BrowseJobListResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $BrowseJobListResponseCopyWith<$Res> {
  factory $BrowseJobListResponseCopyWith(
    BrowseJobListResponse value,
    $Res Function(BrowseJobListResponse) then,
  ) = _$BrowseJobListResponseCopyWithImpl<$Res, BrowseJobListResponse>;
  @useResult
  $Res call({List<BrowseJob> jobs, int total, PaginationMeta pagination});

  $PaginationMetaCopyWith<$Res> get pagination;
}

/// @nodoc
class _$BrowseJobListResponseCopyWithImpl<
  $Res,
  $Val extends BrowseJobListResponse
>
    implements $BrowseJobListResponseCopyWith<$Res> {
  _$BrowseJobListResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of BrowseJobListResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? jobs = null,
    Object? total = null,
    Object? pagination = null,
  }) {
    return _then(
      _value.copyWith(
            jobs: null == jobs
                ? _value.jobs
                : jobs // ignore: cast_nullable_to_non_nullable
                      as List<BrowseJob>,
            total: null == total
                ? _value.total
                : total // ignore: cast_nullable_to_non_nullable
                      as int,
            pagination: null == pagination
                ? _value.pagination
                : pagination // ignore: cast_nullable_to_non_nullable
                      as PaginationMeta,
          )
          as $Val,
    );
  }

  /// Create a copy of BrowseJobListResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $PaginationMetaCopyWith<$Res> get pagination {
    return $PaginationMetaCopyWith<$Res>(_value.pagination, (value) {
      return _then(_value.copyWith(pagination: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$BrowseJobListResponseImplCopyWith<$Res>
    implements $BrowseJobListResponseCopyWith<$Res> {
  factory _$$BrowseJobListResponseImplCopyWith(
    _$BrowseJobListResponseImpl value,
    $Res Function(_$BrowseJobListResponseImpl) then,
  ) = __$$BrowseJobListResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({List<BrowseJob> jobs, int total, PaginationMeta pagination});

  @override
  $PaginationMetaCopyWith<$Res> get pagination;
}

/// @nodoc
class __$$BrowseJobListResponseImplCopyWithImpl<$Res>
    extends
        _$BrowseJobListResponseCopyWithImpl<$Res, _$BrowseJobListResponseImpl>
    implements _$$BrowseJobListResponseImplCopyWith<$Res> {
  __$$BrowseJobListResponseImplCopyWithImpl(
    _$BrowseJobListResponseImpl _value,
    $Res Function(_$BrowseJobListResponseImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of BrowseJobListResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? jobs = null,
    Object? total = null,
    Object? pagination = null,
  }) {
    return _then(
      _$BrowseJobListResponseImpl(
        jobs: null == jobs
            ? _value._jobs
            : jobs // ignore: cast_nullable_to_non_nullable
                  as List<BrowseJob>,
        total: null == total
            ? _value.total
            : total // ignore: cast_nullable_to_non_nullable
                  as int,
        pagination: null == pagination
            ? _value.pagination
            : pagination // ignore: cast_nullable_to_non_nullable
                  as PaginationMeta,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$BrowseJobListResponseImpl implements _BrowseJobListResponse {
  const _$BrowseJobListResponseImpl({
    required final List<BrowseJob> jobs,
    required this.total,
    required this.pagination,
  }) : _jobs = jobs;

  factory _$BrowseJobListResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$BrowseJobListResponseImplFromJson(json);

  final List<BrowseJob> _jobs;
  @override
  List<BrowseJob> get jobs {
    if (_jobs is EqualUnmodifiableListView) return _jobs;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_jobs);
  }

  @override
  final int total;
  @override
  final PaginationMeta pagination;

  @override
  String toString() {
    return 'BrowseJobListResponse(jobs: $jobs, total: $total, pagination: $pagination)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$BrowseJobListResponseImpl &&
            const DeepCollectionEquality().equals(other._jobs, _jobs) &&
            (identical(other.total, total) || other.total == total) &&
            (identical(other.pagination, pagination) ||
                other.pagination == pagination));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
    runtimeType,
    const DeepCollectionEquality().hash(_jobs),
    total,
    pagination,
  );

  /// Create a copy of BrowseJobListResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$BrowseJobListResponseImplCopyWith<_$BrowseJobListResponseImpl>
  get copyWith =>
      __$$BrowseJobListResponseImplCopyWithImpl<_$BrowseJobListResponseImpl>(
        this,
        _$identity,
      );

  @override
  Map<String, dynamic> toJson() {
    return _$$BrowseJobListResponseImplToJson(this);
  }
}

abstract class _BrowseJobListResponse implements BrowseJobListResponse {
  const factory _BrowseJobListResponse({
    required final List<BrowseJob> jobs,
    required final int total,
    required final PaginationMeta pagination,
  }) = _$BrowseJobListResponseImpl;

  factory _BrowseJobListResponse.fromJson(Map<String, dynamic> json) =
      _$BrowseJobListResponseImpl.fromJson;

  @override
  List<BrowseJob> get jobs;
  @override
  int get total;
  @override
  PaginationMeta get pagination;

  /// Create a copy of BrowseJobListResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$BrowseJobListResponseImplCopyWith<_$BrowseJobListResponseImpl>
  get copyWith => throw _privateConstructorUsedError;
}

PaginationMeta _$PaginationMetaFromJson(Map<String, dynamic> json) {
  return _PaginationMeta.fromJson(json);
}

/// @nodoc
mixin _$PaginationMeta {
  int get limit => throw _privateConstructorUsedError;
  int get offset => throw _privateConstructorUsedError;
  int get total => throw _privateConstructorUsedError;
  bool get hasMore => throw _privateConstructorUsedError;

  /// Serializes this PaginationMeta to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of PaginationMeta
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $PaginationMetaCopyWith<PaginationMeta> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $PaginationMetaCopyWith<$Res> {
  factory $PaginationMetaCopyWith(
    PaginationMeta value,
    $Res Function(PaginationMeta) then,
  ) = _$PaginationMetaCopyWithImpl<$Res, PaginationMeta>;
  @useResult
  $Res call({int limit, int offset, int total, bool hasMore});
}

/// @nodoc
class _$PaginationMetaCopyWithImpl<$Res, $Val extends PaginationMeta>
    implements $PaginationMetaCopyWith<$Res> {
  _$PaginationMetaCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of PaginationMeta
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? limit = null,
    Object? offset = null,
    Object? total = null,
    Object? hasMore = null,
  }) {
    return _then(
      _value.copyWith(
            limit: null == limit
                ? _value.limit
                : limit // ignore: cast_nullable_to_non_nullable
                      as int,
            offset: null == offset
                ? _value.offset
                : offset // ignore: cast_nullable_to_non_nullable
                      as int,
            total: null == total
                ? _value.total
                : total // ignore: cast_nullable_to_non_nullable
                      as int,
            hasMore: null == hasMore
                ? _value.hasMore
                : hasMore // ignore: cast_nullable_to_non_nullable
                      as bool,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$PaginationMetaImplCopyWith<$Res>
    implements $PaginationMetaCopyWith<$Res> {
  factory _$$PaginationMetaImplCopyWith(
    _$PaginationMetaImpl value,
    $Res Function(_$PaginationMetaImpl) then,
  ) = __$$PaginationMetaImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({int limit, int offset, int total, bool hasMore});
}

/// @nodoc
class __$$PaginationMetaImplCopyWithImpl<$Res>
    extends _$PaginationMetaCopyWithImpl<$Res, _$PaginationMetaImpl>
    implements _$$PaginationMetaImplCopyWith<$Res> {
  __$$PaginationMetaImplCopyWithImpl(
    _$PaginationMetaImpl _value,
    $Res Function(_$PaginationMetaImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of PaginationMeta
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? limit = null,
    Object? offset = null,
    Object? total = null,
    Object? hasMore = null,
  }) {
    return _then(
      _$PaginationMetaImpl(
        limit: null == limit
            ? _value.limit
            : limit // ignore: cast_nullable_to_non_nullable
                  as int,
        offset: null == offset
            ? _value.offset
            : offset // ignore: cast_nullable_to_non_nullable
                  as int,
        total: null == total
            ? _value.total
            : total // ignore: cast_nullable_to_non_nullable
                  as int,
        hasMore: null == hasMore
            ? _value.hasMore
            : hasMore // ignore: cast_nullable_to_non_nullable
                  as bool,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$PaginationMetaImpl implements _PaginationMeta {
  const _$PaginationMetaImpl({
    required this.limit,
    required this.offset,
    required this.total,
    required this.hasMore,
  });

  factory _$PaginationMetaImpl.fromJson(Map<String, dynamic> json) =>
      _$$PaginationMetaImplFromJson(json);

  @override
  final int limit;
  @override
  final int offset;
  @override
  final int total;
  @override
  final bool hasMore;

  @override
  String toString() {
    return 'PaginationMeta(limit: $limit, offset: $offset, total: $total, hasMore: $hasMore)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$PaginationMetaImpl &&
            (identical(other.limit, limit) || other.limit == limit) &&
            (identical(other.offset, offset) || other.offset == offset) &&
            (identical(other.total, total) || other.total == total) &&
            (identical(other.hasMore, hasMore) || other.hasMore == hasMore));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, limit, offset, total, hasMore);

  /// Create a copy of PaginationMeta
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$PaginationMetaImplCopyWith<_$PaginationMetaImpl> get copyWith =>
      __$$PaginationMetaImplCopyWithImpl<_$PaginationMetaImpl>(
        this,
        _$identity,
      );

  @override
  Map<String, dynamic> toJson() {
    return _$$PaginationMetaImplToJson(this);
  }
}

abstract class _PaginationMeta implements PaginationMeta {
  const factory _PaginationMeta({
    required final int limit,
    required final int offset,
    required final int total,
    required final bool hasMore,
  }) = _$PaginationMetaImpl;

  factory _PaginationMeta.fromJson(Map<String, dynamic> json) =
      _$PaginationMetaImpl.fromJson;

  @override
  int get limit;
  @override
  int get offset;
  @override
  int get total;
  @override
  bool get hasMore;

  /// Create a copy of PaginationMeta
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$PaginationMetaImplCopyWith<_$PaginationMetaImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

CreateJobFromTextRequest _$CreateJobFromTextRequestFromJson(
  Map<String, dynamic> json,
) {
  return _CreateJobFromTextRequest.fromJson(json);
}

/// @nodoc
mixin _$CreateJobFromTextRequest {
  JobSource get source => throw _privateConstructorUsedError;
  String get rawText => throw _privateConstructorUsedError;

  /// Serializes this CreateJobFromTextRequest to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of CreateJobFromTextRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $CreateJobFromTextRequestCopyWith<CreateJobFromTextRequest> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $CreateJobFromTextRequestCopyWith<$Res> {
  factory $CreateJobFromTextRequestCopyWith(
    CreateJobFromTextRequest value,
    $Res Function(CreateJobFromTextRequest) then,
  ) = _$CreateJobFromTextRequestCopyWithImpl<$Res, CreateJobFromTextRequest>;
  @useResult
  $Res call({JobSource source, String rawText});
}

/// @nodoc
class _$CreateJobFromTextRequestCopyWithImpl<
  $Res,
  $Val extends CreateJobFromTextRequest
>
    implements $CreateJobFromTextRequestCopyWith<$Res> {
  _$CreateJobFromTextRequestCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of CreateJobFromTextRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? source = null, Object? rawText = null}) {
    return _then(
      _value.copyWith(
            source: null == source
                ? _value.source
                : source // ignore: cast_nullable_to_non_nullable
                      as JobSource,
            rawText: null == rawText
                ? _value.rawText
                : rawText // ignore: cast_nullable_to_non_nullable
                      as String,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$CreateJobFromTextRequestImplCopyWith<$Res>
    implements $CreateJobFromTextRequestCopyWith<$Res> {
  factory _$$CreateJobFromTextRequestImplCopyWith(
    _$CreateJobFromTextRequestImpl value,
    $Res Function(_$CreateJobFromTextRequestImpl) then,
  ) = __$$CreateJobFromTextRequestImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({JobSource source, String rawText});
}

/// @nodoc
class __$$CreateJobFromTextRequestImplCopyWithImpl<$Res>
    extends
        _$CreateJobFromTextRequestCopyWithImpl<
          $Res,
          _$CreateJobFromTextRequestImpl
        >
    implements _$$CreateJobFromTextRequestImplCopyWith<$Res> {
  __$$CreateJobFromTextRequestImplCopyWithImpl(
    _$CreateJobFromTextRequestImpl _value,
    $Res Function(_$CreateJobFromTextRequestImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of CreateJobFromTextRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? source = null, Object? rawText = null}) {
    return _then(
      _$CreateJobFromTextRequestImpl(
        source: null == source
            ? _value.source
            : source // ignore: cast_nullable_to_non_nullable
                  as JobSource,
        rawText: null == rawText
            ? _value.rawText
            : rawText // ignore: cast_nullable_to_non_nullable
                  as String,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$CreateJobFromTextRequestImpl implements _CreateJobFromTextRequest {
  const _$CreateJobFromTextRequestImpl({
    this.source = JobSource.userCreated,
    required this.rawText,
  });

  factory _$CreateJobFromTextRequestImpl.fromJson(Map<String, dynamic> json) =>
      _$$CreateJobFromTextRequestImplFromJson(json);

  @override
  @JsonKey()
  final JobSource source;
  @override
  final String rawText;

  @override
  String toString() {
    return 'CreateJobFromTextRequest(source: $source, rawText: $rawText)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$CreateJobFromTextRequestImpl &&
            (identical(other.source, source) || other.source == source) &&
            (identical(other.rawText, rawText) || other.rawText == rawText));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, source, rawText);

  /// Create a copy of CreateJobFromTextRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$CreateJobFromTextRequestImplCopyWith<_$CreateJobFromTextRequestImpl>
  get copyWith =>
      __$$CreateJobFromTextRequestImplCopyWithImpl<
        _$CreateJobFromTextRequestImpl
      >(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$CreateJobFromTextRequestImplToJson(this);
  }
}

abstract class _CreateJobFromTextRequest implements CreateJobFromTextRequest {
  const factory _CreateJobFromTextRequest({
    final JobSource source,
    required final String rawText,
  }) = _$CreateJobFromTextRequestImpl;

  factory _CreateJobFromTextRequest.fromJson(Map<String, dynamic> json) =
      _$CreateJobFromTextRequestImpl.fromJson;

  @override
  JobSource get source;
  @override
  String get rawText;

  /// Create a copy of CreateJobFromTextRequest
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$CreateJobFromTextRequestImplCopyWith<_$CreateJobFromTextRequestImpl>
  get copyWith => throw _privateConstructorUsedError;
}

CreateJobFromUrlRequest _$CreateJobFromUrlRequestFromJson(
  Map<String, dynamic> json,
) {
  return _CreateJobFromUrlRequest.fromJson(json);
}

/// @nodoc
mixin _$CreateJobFromUrlRequest {
  JobSource get source => throw _privateConstructorUsedError;
  String get url => throw _privateConstructorUsedError;

  /// Serializes this CreateJobFromUrlRequest to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of CreateJobFromUrlRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $CreateJobFromUrlRequestCopyWith<CreateJobFromUrlRequest> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $CreateJobFromUrlRequestCopyWith<$Res> {
  factory $CreateJobFromUrlRequestCopyWith(
    CreateJobFromUrlRequest value,
    $Res Function(CreateJobFromUrlRequest) then,
  ) = _$CreateJobFromUrlRequestCopyWithImpl<$Res, CreateJobFromUrlRequest>;
  @useResult
  $Res call({JobSource source, String url});
}

/// @nodoc
class _$CreateJobFromUrlRequestCopyWithImpl<
  $Res,
  $Val extends CreateJobFromUrlRequest
>
    implements $CreateJobFromUrlRequestCopyWith<$Res> {
  _$CreateJobFromUrlRequestCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of CreateJobFromUrlRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? source = null, Object? url = null}) {
    return _then(
      _value.copyWith(
            source: null == source
                ? _value.source
                : source // ignore: cast_nullable_to_non_nullable
                      as JobSource,
            url: null == url
                ? _value.url
                : url // ignore: cast_nullable_to_non_nullable
                      as String,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$CreateJobFromUrlRequestImplCopyWith<$Res>
    implements $CreateJobFromUrlRequestCopyWith<$Res> {
  factory _$$CreateJobFromUrlRequestImplCopyWith(
    _$CreateJobFromUrlRequestImpl value,
    $Res Function(_$CreateJobFromUrlRequestImpl) then,
  ) = __$$CreateJobFromUrlRequestImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({JobSource source, String url});
}

/// @nodoc
class __$$CreateJobFromUrlRequestImplCopyWithImpl<$Res>
    extends
        _$CreateJobFromUrlRequestCopyWithImpl<
          $Res,
          _$CreateJobFromUrlRequestImpl
        >
    implements _$$CreateJobFromUrlRequestImplCopyWith<$Res> {
  __$$CreateJobFromUrlRequestImplCopyWithImpl(
    _$CreateJobFromUrlRequestImpl _value,
    $Res Function(_$CreateJobFromUrlRequestImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of CreateJobFromUrlRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? source = null, Object? url = null}) {
    return _then(
      _$CreateJobFromUrlRequestImpl(
        source: null == source
            ? _value.source
            : source // ignore: cast_nullable_to_non_nullable
                  as JobSource,
        url: null == url
            ? _value.url
            : url // ignore: cast_nullable_to_non_nullable
                  as String,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$CreateJobFromUrlRequestImpl implements _CreateJobFromUrlRequest {
  const _$CreateJobFromUrlRequestImpl({
    this.source = JobSource.urlImport,
    required this.url,
  });

  factory _$CreateJobFromUrlRequestImpl.fromJson(Map<String, dynamic> json) =>
      _$$CreateJobFromUrlRequestImplFromJson(json);

  @override
  @JsonKey()
  final JobSource source;
  @override
  final String url;

  @override
  String toString() {
    return 'CreateJobFromUrlRequest(source: $source, url: $url)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$CreateJobFromUrlRequestImpl &&
            (identical(other.source, source) || other.source == source) &&
            (identical(other.url, url) || other.url == url));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, source, url);

  /// Create a copy of CreateJobFromUrlRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$CreateJobFromUrlRequestImplCopyWith<_$CreateJobFromUrlRequestImpl>
  get copyWith =>
      __$$CreateJobFromUrlRequestImplCopyWithImpl<
        _$CreateJobFromUrlRequestImpl
      >(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$CreateJobFromUrlRequestImplToJson(this);
  }
}

abstract class _CreateJobFromUrlRequest implements CreateJobFromUrlRequest {
  const factory _CreateJobFromUrlRequest({
    final JobSource source,
    required final String url,
  }) = _$CreateJobFromUrlRequestImpl;

  factory _CreateJobFromUrlRequest.fromJson(Map<String, dynamic> json) =
      _$CreateJobFromUrlRequestImpl.fromJson;

  @override
  JobSource get source;
  @override
  String get url;

  /// Create a copy of CreateJobFromUrlRequest
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$CreateJobFromUrlRequestImplCopyWith<_$CreateJobFromUrlRequestImpl>
  get copyWith => throw _privateConstructorUsedError;
}

UpdateJobRequest _$UpdateJobRequestFromJson(Map<String, dynamic> json) {
  return _UpdateJobRequest.fromJson(json);
}

/// @nodoc
mixin _$UpdateJobRequest {
  List<String>? get parsedKeywords =>
      throw _privateConstructorUsedError; // User can refine AI-extracted keywords
  JobStatus? get status =>
      throw _privateConstructorUsedError; // User workflow management (active/archived/draft)
  ApplicationStatus? get applicationStatus =>
      throw _privateConstructorUsedError;

  /// Serializes this UpdateJobRequest to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of UpdateJobRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $UpdateJobRequestCopyWith<UpdateJobRequest> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $UpdateJobRequestCopyWith<$Res> {
  factory $UpdateJobRequestCopyWith(
    UpdateJobRequest value,
    $Res Function(UpdateJobRequest) then,
  ) = _$UpdateJobRequestCopyWithImpl<$Res, UpdateJobRequest>;
  @useResult
  $Res call({
    List<String>? parsedKeywords,
    JobStatus? status,
    ApplicationStatus? applicationStatus,
  });
}

/// @nodoc
class _$UpdateJobRequestCopyWithImpl<$Res, $Val extends UpdateJobRequest>
    implements $UpdateJobRequestCopyWith<$Res> {
  _$UpdateJobRequestCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of UpdateJobRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? parsedKeywords = freezed,
    Object? status = freezed,
    Object? applicationStatus = freezed,
  }) {
    return _then(
      _value.copyWith(
            parsedKeywords: freezed == parsedKeywords
                ? _value.parsedKeywords
                : parsedKeywords // ignore: cast_nullable_to_non_nullable
                      as List<String>?,
            status: freezed == status
                ? _value.status
                : status // ignore: cast_nullable_to_non_nullable
                      as JobStatus?,
            applicationStatus: freezed == applicationStatus
                ? _value.applicationStatus
                : applicationStatus // ignore: cast_nullable_to_non_nullable
                      as ApplicationStatus?,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$UpdateJobRequestImplCopyWith<$Res>
    implements $UpdateJobRequestCopyWith<$Res> {
  factory _$$UpdateJobRequestImplCopyWith(
    _$UpdateJobRequestImpl value,
    $Res Function(_$UpdateJobRequestImpl) then,
  ) = __$$UpdateJobRequestImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    List<String>? parsedKeywords,
    JobStatus? status,
    ApplicationStatus? applicationStatus,
  });
}

/// @nodoc
class __$$UpdateJobRequestImplCopyWithImpl<$Res>
    extends _$UpdateJobRequestCopyWithImpl<$Res, _$UpdateJobRequestImpl>
    implements _$$UpdateJobRequestImplCopyWith<$Res> {
  __$$UpdateJobRequestImplCopyWithImpl(
    _$UpdateJobRequestImpl _value,
    $Res Function(_$UpdateJobRequestImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of UpdateJobRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? parsedKeywords = freezed,
    Object? status = freezed,
    Object? applicationStatus = freezed,
  }) {
    return _then(
      _$UpdateJobRequestImpl(
        parsedKeywords: freezed == parsedKeywords
            ? _value._parsedKeywords
            : parsedKeywords // ignore: cast_nullable_to_non_nullable
                  as List<String>?,
        status: freezed == status
            ? _value.status
            : status // ignore: cast_nullable_to_non_nullable
                  as JobStatus?,
        applicationStatus: freezed == applicationStatus
            ? _value.applicationStatus
            : applicationStatus // ignore: cast_nullable_to_non_nullable
                  as ApplicationStatus?,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$UpdateJobRequestImpl implements _UpdateJobRequest {
  const _$UpdateJobRequestImpl({
    final List<String>? parsedKeywords,
    this.status,
    this.applicationStatus,
  }) : _parsedKeywords = parsedKeywords;

  factory _$UpdateJobRequestImpl.fromJson(Map<String, dynamic> json) =>
      _$$UpdateJobRequestImplFromJson(json);

  final List<String>? _parsedKeywords;
  @override
  List<String>? get parsedKeywords {
    final value = _parsedKeywords;
    if (value == null) return null;
    if (_parsedKeywords is EqualUnmodifiableListView) return _parsedKeywords;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(value);
  }

  // User can refine AI-extracted keywords
  @override
  final JobStatus? status;
  // User workflow management (active/archived/draft)
  @override
  final ApplicationStatus? applicationStatus;

  @override
  String toString() {
    return 'UpdateJobRequest(parsedKeywords: $parsedKeywords, status: $status, applicationStatus: $applicationStatus)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$UpdateJobRequestImpl &&
            const DeepCollectionEquality().equals(
              other._parsedKeywords,
              _parsedKeywords,
            ) &&
            (identical(other.status, status) || other.status == status) &&
            (identical(other.applicationStatus, applicationStatus) ||
                other.applicationStatus == applicationStatus));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
    runtimeType,
    const DeepCollectionEquality().hash(_parsedKeywords),
    status,
    applicationStatus,
  );

  /// Create a copy of UpdateJobRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$UpdateJobRequestImplCopyWith<_$UpdateJobRequestImpl> get copyWith =>
      __$$UpdateJobRequestImplCopyWithImpl<_$UpdateJobRequestImpl>(
        this,
        _$identity,
      );

  @override
  Map<String, dynamic> toJson() {
    return _$$UpdateJobRequestImplToJson(this);
  }
}

abstract class _UpdateJobRequest implements UpdateJobRequest {
  const factory _UpdateJobRequest({
    final List<String>? parsedKeywords,
    final JobStatus? status,
    final ApplicationStatus? applicationStatus,
  }) = _$UpdateJobRequestImpl;

  factory _UpdateJobRequest.fromJson(Map<String, dynamic> json) =
      _$UpdateJobRequestImpl.fromJson;

  @override
  List<String>? get parsedKeywords; // User can refine AI-extracted keywords
  @override
  JobStatus? get status; // User workflow management (active/archived/draft)
  @override
  ApplicationStatus? get applicationStatus;

  /// Create a copy of UpdateJobRequest
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$UpdateJobRequestImplCopyWith<_$UpdateJobRequestImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

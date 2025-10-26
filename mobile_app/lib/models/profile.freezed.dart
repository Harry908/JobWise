// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'profile.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
  'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models',
);

/// @nodoc
mixin _$Profile {
  String get id =>
      throw _privateConstructorUsedError; // ignore: invalid_annotation_target
  @JsonKey(name: 'user_id')
  String get userId => throw _privateConstructorUsedError;
  PersonalInfo get personalInfo =>
      throw _privateConstructorUsedError; // ignore: invalid_annotation_target
  @JsonKey(name: 'professional_summary')
  String? get professionalSummary => throw _privateConstructorUsedError;
  List<Experience> get experiences => throw _privateConstructorUsedError;
  List<Education> get education => throw _privateConstructorUsedError;
  Skills get skills => throw _privateConstructorUsedError;
  List<Project> get projects => throw _privateConstructorUsedError;
  Map<String, dynamic> get customFields => throw _privateConstructorUsedError;
  int get version =>
      throw _privateConstructorUsedError; // ignore: invalid_annotation_target
  @JsonKey(name: 'created_at')
  DateTime get createdAt => throw _privateConstructorUsedError; // ignore: invalid_annotation_target
  @JsonKey(name: 'updated_at')
  DateTime get updatedAt => throw _privateConstructorUsedError;

  /// Create a copy of Profile
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ProfileCopyWith<Profile> get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ProfileCopyWith<$Res> {
  factory $ProfileCopyWith(Profile value, $Res Function(Profile) then) =
      _$ProfileCopyWithImpl<$Res, Profile>;
  @useResult
  $Res call({
    String id,
    @JsonKey(name: 'user_id') String userId,
    PersonalInfo personalInfo,
    @JsonKey(name: 'professional_summary') String? professionalSummary,
    List<Experience> experiences,
    List<Education> education,
    Skills skills,
    List<Project> projects,
    Map<String, dynamic> customFields,
    int version,
    @JsonKey(name: 'created_at') DateTime createdAt,
    @JsonKey(name: 'updated_at') DateTime updatedAt,
  });

  $PersonalInfoCopyWith<$Res> get personalInfo;
  $SkillsCopyWith<$Res> get skills;
}

/// @nodoc
class _$ProfileCopyWithImpl<$Res, $Val extends Profile>
    implements $ProfileCopyWith<$Res> {
  _$ProfileCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of Profile
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? userId = null,
    Object? personalInfo = null,
    Object? professionalSummary = freezed,
    Object? experiences = null,
    Object? education = null,
    Object? skills = null,
    Object? projects = null,
    Object? customFields = null,
    Object? version = null,
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
                      as String,
            personalInfo: null == personalInfo
                ? _value.personalInfo
                : personalInfo // ignore: cast_nullable_to_non_nullable
                      as PersonalInfo,
            professionalSummary: freezed == professionalSummary
                ? _value.professionalSummary
                : professionalSummary // ignore: cast_nullable_to_non_nullable
                      as String?,
            experiences: null == experiences
                ? _value.experiences
                : experiences // ignore: cast_nullable_to_non_nullable
                      as List<Experience>,
            education: null == education
                ? _value.education
                : education // ignore: cast_nullable_to_non_nullable
                      as List<Education>,
            skills: null == skills
                ? _value.skills
                : skills // ignore: cast_nullable_to_non_nullable
                      as Skills,
            projects: null == projects
                ? _value.projects
                : projects // ignore: cast_nullable_to_non_nullable
                      as List<Project>,
            customFields: null == customFields
                ? _value.customFields
                : customFields // ignore: cast_nullable_to_non_nullable
                      as Map<String, dynamic>,
            version: null == version
                ? _value.version
                : version // ignore: cast_nullable_to_non_nullable
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

  /// Create a copy of Profile
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $PersonalInfoCopyWith<$Res> get personalInfo {
    return $PersonalInfoCopyWith<$Res>(_value.personalInfo, (value) {
      return _then(_value.copyWith(personalInfo: value) as $Val);
    });
  }

  /// Create a copy of Profile
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $SkillsCopyWith<$Res> get skills {
    return $SkillsCopyWith<$Res>(_value.skills, (value) {
      return _then(_value.copyWith(skills: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$ProfileImplCopyWith<$Res> implements $ProfileCopyWith<$Res> {
  factory _$$ProfileImplCopyWith(
    _$ProfileImpl value,
    $Res Function(_$ProfileImpl) then,
  ) = __$$ProfileImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    String id,
    @JsonKey(name: 'user_id') String userId,
    PersonalInfo personalInfo,
    @JsonKey(name: 'professional_summary') String? professionalSummary,
    List<Experience> experiences,
    List<Education> education,
    Skills skills,
    List<Project> projects,
    Map<String, dynamic> customFields,
    int version,
    @JsonKey(name: 'created_at') DateTime createdAt,
    @JsonKey(name: 'updated_at') DateTime updatedAt,
  });

  @override
  $PersonalInfoCopyWith<$Res> get personalInfo;
  @override
  $SkillsCopyWith<$Res> get skills;
}

/// @nodoc
class __$$ProfileImplCopyWithImpl<$Res>
    extends _$ProfileCopyWithImpl<$Res, _$ProfileImpl>
    implements _$$ProfileImplCopyWith<$Res> {
  __$$ProfileImplCopyWithImpl(
    _$ProfileImpl _value,
    $Res Function(_$ProfileImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of Profile
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? userId = null,
    Object? personalInfo = null,
    Object? professionalSummary = freezed,
    Object? experiences = null,
    Object? education = null,
    Object? skills = null,
    Object? projects = null,
    Object? customFields = null,
    Object? version = null,
    Object? createdAt = null,
    Object? updatedAt = null,
  }) {
    return _then(
      _$ProfileImpl(
        id: null == id
            ? _value.id
            : id // ignore: cast_nullable_to_non_nullable
                  as String,
        userId: null == userId
            ? _value.userId
            : userId // ignore: cast_nullable_to_non_nullable
                  as String,
        personalInfo: null == personalInfo
            ? _value.personalInfo
            : personalInfo // ignore: cast_nullable_to_non_nullable
                  as PersonalInfo,
        professionalSummary: freezed == professionalSummary
            ? _value.professionalSummary
            : professionalSummary // ignore: cast_nullable_to_non_nullable
                  as String?,
        experiences: null == experiences
            ? _value._experiences
            : experiences // ignore: cast_nullable_to_non_nullable
                  as List<Experience>,
        education: null == education
            ? _value._education
            : education // ignore: cast_nullable_to_non_nullable
                  as List<Education>,
        skills: null == skills
            ? _value.skills
            : skills // ignore: cast_nullable_to_non_nullable
                  as Skills,
        projects: null == projects
            ? _value._projects
            : projects // ignore: cast_nullable_to_non_nullable
                  as List<Project>,
        customFields: null == customFields
            ? _value._customFields
            : customFields // ignore: cast_nullable_to_non_nullable
                  as Map<String, dynamic>,
        version: null == version
            ? _value.version
            : version // ignore: cast_nullable_to_non_nullable
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

class _$ProfileImpl implements _Profile {
  const _$ProfileImpl({
    required this.id,
    @JsonKey(name: 'user_id') required this.userId,
    required this.personalInfo,
    @JsonKey(name: 'professional_summary') this.professionalSummary,
    final List<Experience> experiences = const [],
    final List<Education> education = const [],
    required this.skills,
    final List<Project> projects = const [],
    final Map<String, dynamic> customFields = const {},
    required this.version,
    @JsonKey(name: 'created_at') required this.createdAt,
    @JsonKey(name: 'updated_at') required this.updatedAt,
  }) : _experiences = experiences,
       _education = education,
       _projects = projects,
       _customFields = customFields;

  @override
  final String id;
  // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'user_id')
  final String userId;
  @override
  final PersonalInfo personalInfo;
  // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'professional_summary')
  final String? professionalSummary;
  final List<Experience> _experiences;
  @override
  @JsonKey()
  List<Experience> get experiences {
    if (_experiences is EqualUnmodifiableListView) return _experiences;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_experiences);
  }

  final List<Education> _education;
  @override
  @JsonKey()
  List<Education> get education {
    if (_education is EqualUnmodifiableListView) return _education;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_education);
  }

  @override
  final Skills skills;
  final List<Project> _projects;
  @override
  @JsonKey()
  List<Project> get projects {
    if (_projects is EqualUnmodifiableListView) return _projects;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_projects);
  }

  final Map<String, dynamic> _customFields;
  @override
  @JsonKey()
  Map<String, dynamic> get customFields {
    if (_customFields is EqualUnmodifiableMapView) return _customFields;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_customFields);
  }

  @override
  final int version;
  // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'created_at')
  final DateTime createdAt;
  // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'updated_at')
  final DateTime updatedAt;

  @override
  String toString() {
    return 'Profile(id: $id, userId: $userId, personalInfo: $personalInfo, professionalSummary: $professionalSummary, experiences: $experiences, education: $education, skills: $skills, projects: $projects, customFields: $customFields, version: $version, createdAt: $createdAt, updatedAt: $updatedAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ProfileImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.userId, userId) || other.userId == userId) &&
            (identical(other.personalInfo, personalInfo) ||
                other.personalInfo == personalInfo) &&
            (identical(other.professionalSummary, professionalSummary) ||
                other.professionalSummary == professionalSummary) &&
            const DeepCollectionEquality().equals(
              other._experiences,
              _experiences,
            ) &&
            const DeepCollectionEquality().equals(
              other._education,
              _education,
            ) &&
            (identical(other.skills, skills) || other.skills == skills) &&
            const DeepCollectionEquality().equals(other._projects, _projects) &&
            const DeepCollectionEquality().equals(
              other._customFields,
              _customFields,
            ) &&
            (identical(other.version, version) || other.version == version) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.updatedAt, updatedAt) ||
                other.updatedAt == updatedAt));
  }

  @override
  int get hashCode => Object.hash(
    runtimeType,
    id,
    userId,
    personalInfo,
    professionalSummary,
    const DeepCollectionEquality().hash(_experiences),
    const DeepCollectionEquality().hash(_education),
    skills,
    const DeepCollectionEquality().hash(_projects),
    const DeepCollectionEquality().hash(_customFields),
    version,
    createdAt,
    updatedAt,
  );

  /// Create a copy of Profile
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ProfileImplCopyWith<_$ProfileImpl> get copyWith =>
      __$$ProfileImplCopyWithImpl<_$ProfileImpl>(this, _$identity);
}

abstract class _Profile implements Profile {
  const factory _Profile({
    required final String id,
    @JsonKey(name: 'user_id') required final String userId,
    required final PersonalInfo personalInfo,
    required final Skills skills,
    required final int version,
    @JsonKey(name: 'created_at') required final DateTime createdAt,
    @JsonKey(name: 'updated_at') required final DateTime updatedAt,
  }) = _$ProfileImpl;

  @override
  String get id; // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'user_id')
  String get userId;
  @override
  PersonalInfo get personalInfo; // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'professional_summary')
  String? get professionalSummary;
  @override
  List<Experience> get experiences;
  @override
  List<Education> get education;
  @override
  Skills get skills;
  @override
  List<Project> get projects;
  @override
  Map<String, dynamic> get customFields;
  @override
  int get version; // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'created_at')
  DateTime get createdAt; // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'updated_at')
  DateTime get updatedAt;

  /// Create a copy of Profile
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ProfileImplCopyWith<_$ProfileImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

PersonalInfo _$PersonalInfoFromJson(Map<String, dynamic> json) {
  return _PersonalInfo.fromJson(json);
}

/// @nodoc
mixin _$PersonalInfo {
  // ignore: invalid_annotation_target
  @JsonKey(name: 'full_name')
  String get fullName => throw _privateConstructorUsedError;
  String get email => throw _privateConstructorUsedError;
  String? get phone => throw _privateConstructorUsedError;
  String? get location => throw _privateConstructorUsedError;
  String? get linkedin => throw _privateConstructorUsedError;
  String? get github => throw _privateConstructorUsedError;
  String? get website => throw _privateConstructorUsedError;

  /// Serializes this PersonalInfo to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of PersonalInfo
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $PersonalInfoCopyWith<PersonalInfo> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $PersonalInfoCopyWith<$Res> {
  factory $PersonalInfoCopyWith(
    PersonalInfo value,
    $Res Function(PersonalInfo) then,
  ) = _$PersonalInfoCopyWithImpl<$Res, PersonalInfo>;
  @useResult
  $Res call({
    @JsonKey(name: 'full_name') String fullName,
    String email,
    String? phone,
    String? location,
    String? linkedin,
    String? github,
    String? website,
  });
}

/// @nodoc
class _$PersonalInfoCopyWithImpl<$Res, $Val extends PersonalInfo>
    implements $PersonalInfoCopyWith<$Res> {
  _$PersonalInfoCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of PersonalInfo
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? fullName = null,
    Object? email = null,
    Object? phone = freezed,
    Object? location = freezed,
    Object? linkedin = freezed,
    Object? github = freezed,
    Object? website = freezed,
  }) {
    return _then(
      _value.copyWith(
            fullName: null == fullName
                ? _value.fullName
                : fullName // ignore: cast_nullable_to_non_nullable
                      as String,
            email: null == email
                ? _value.email
                : email // ignore: cast_nullable_to_non_nullable
                      as String,
            phone: freezed == phone
                ? _value.phone
                : phone // ignore: cast_nullable_to_non_nullable
                      as String?,
            location: freezed == location
                ? _value.location
                : location // ignore: cast_nullable_to_non_nullable
                      as String?,
            linkedin: freezed == linkedin
                ? _value.linkedin
                : linkedin // ignore: cast_nullable_to_non_nullable
                      as String?,
            github: freezed == github
                ? _value.github
                : github // ignore: cast_nullable_to_non_nullable
                      as String?,
            website: freezed == website
                ? _value.website
                : website // ignore: cast_nullable_to_non_nullable
                      as String?,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$PersonalInfoImplCopyWith<$Res>
    implements $PersonalInfoCopyWith<$Res> {
  factory _$$PersonalInfoImplCopyWith(
    _$PersonalInfoImpl value,
    $Res Function(_$PersonalInfoImpl) then,
  ) = __$$PersonalInfoImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    @JsonKey(name: 'full_name') String fullName,
    String email,
    String? phone,
    String? location,
    String? linkedin,
    String? github,
    String? website,
  });
}

/// @nodoc
class __$$PersonalInfoImplCopyWithImpl<$Res>
    extends _$PersonalInfoCopyWithImpl<$Res, _$PersonalInfoImpl>
    implements _$$PersonalInfoImplCopyWith<$Res> {
  __$$PersonalInfoImplCopyWithImpl(
    _$PersonalInfoImpl _value,
    $Res Function(_$PersonalInfoImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of PersonalInfo
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? fullName = null,
    Object? email = null,
    Object? phone = freezed,
    Object? location = freezed,
    Object? linkedin = freezed,
    Object? github = freezed,
    Object? website = freezed,
  }) {
    return _then(
      _$PersonalInfoImpl(
        fullName: null == fullName
            ? _value.fullName
            : fullName // ignore: cast_nullable_to_non_nullable
                  as String,
        email: null == email
            ? _value.email
            : email // ignore: cast_nullable_to_non_nullable
                  as String,
        phone: freezed == phone
            ? _value.phone
            : phone // ignore: cast_nullable_to_non_nullable
                  as String?,
        location: freezed == location
            ? _value.location
            : location // ignore: cast_nullable_to_non_nullable
                  as String?,
        linkedin: freezed == linkedin
            ? _value.linkedin
            : linkedin // ignore: cast_nullable_to_non_nullable
                  as String?,
        github: freezed == github
            ? _value.github
            : github // ignore: cast_nullable_to_non_nullable
                  as String?,
        website: freezed == website
            ? _value.website
            : website // ignore: cast_nullable_to_non_nullable
                  as String?,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$PersonalInfoImpl implements _PersonalInfo {
  const _$PersonalInfoImpl({
    @JsonKey(name: 'full_name') required this.fullName,
    required this.email,
    this.phone,
    this.location,
    this.linkedin,
    this.github,
    this.website,
  });

  factory _$PersonalInfoImpl.fromJson(Map<String, dynamic> json) =>
      _$$PersonalInfoImplFromJson(json);

  // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'full_name')
  final String fullName;
  @override
  final String email;
  @override
  final String? phone;
  @override
  final String? location;
  @override
  final String? linkedin;
  @override
  final String? github;
  @override
  final String? website;

  @override
  String toString() {
    return 'PersonalInfo(fullName: $fullName, email: $email, phone: $phone, location: $location, linkedin: $linkedin, github: $github, website: $website)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$PersonalInfoImpl &&
            (identical(other.fullName, fullName) ||
                other.fullName == fullName) &&
            (identical(other.email, email) || other.email == email) &&
            (identical(other.phone, phone) || other.phone == phone) &&
            (identical(other.location, location) ||
                other.location == location) &&
            (identical(other.linkedin, linkedin) ||
                other.linkedin == linkedin) &&
            (identical(other.github, github) || other.github == github) &&
            (identical(other.website, website) || other.website == website));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
    runtimeType,
    fullName,
    email,
    phone,
    location,
    linkedin,
    github,
    website,
  );

  /// Create a copy of PersonalInfo
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$PersonalInfoImplCopyWith<_$PersonalInfoImpl> get copyWith =>
      __$$PersonalInfoImplCopyWithImpl<_$PersonalInfoImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$PersonalInfoImplToJson(this);
  }
}

abstract class _PersonalInfo implements PersonalInfo {
  const factory _PersonalInfo({
    @JsonKey(name: 'full_name') required final String fullName,
    required final String email,
    final String? phone,
    final String? location,
    final String? linkedin,
    final String? github,
    final String? website,
  }) = _$PersonalInfoImpl;

  factory _PersonalInfo.fromJson(Map<String, dynamic> json) =
      _$PersonalInfoImpl.fromJson;

  // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'full_name')
  String get fullName;
  @override
  String get email;
  @override
  String? get phone;
  @override
  String? get location;
  @override
  String? get linkedin;
  @override
  String? get github;
  @override
  String? get website;

  /// Create a copy of PersonalInfo
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$PersonalInfoImplCopyWith<_$PersonalInfoImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

Experience _$ExperienceFromJson(Map<String, dynamic> json) {
  return _Experience.fromJson(json);
}

/// @nodoc
mixin _$Experience {
  String? get id => throw _privateConstructorUsedError;
  String get title => throw _privateConstructorUsedError;
  String get company => throw _privateConstructorUsedError;
  String? get location =>
      throw _privateConstructorUsedError; // ignore: invalid_annotation_target
  @JsonKey(name: 'start_date')
  String get startDate => throw _privateConstructorUsedError; // ignore: invalid_annotation_target
  @JsonKey(name: 'end_date')
  String? get endDate => throw _privateConstructorUsedError; // ignore: invalid_annotation_target
  @JsonKey(name: 'is_current')
  bool get isCurrent => throw _privateConstructorUsedError;
  String? get description => throw _privateConstructorUsedError;
  List<String> get achievements =>
      throw _privateConstructorUsedError; // ignore: invalid_annotation_target
  @JsonKey(name: 'employment_type')
  String? get employmentType => throw _privateConstructorUsedError;
  String? get industry => throw _privateConstructorUsedError;

  /// Serializes this Experience to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of Experience
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ExperienceCopyWith<Experience> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ExperienceCopyWith<$Res> {
  factory $ExperienceCopyWith(
    Experience value,
    $Res Function(Experience) then,
  ) = _$ExperienceCopyWithImpl<$Res, Experience>;
  @useResult
  $Res call({
    String? id,
    String title,
    String company,
    String? location,
    @JsonKey(name: 'start_date') String startDate,
    @JsonKey(name: 'end_date') String? endDate,
    @JsonKey(name: 'is_current') bool isCurrent,
    String? description,
    List<String> achievements,
    @JsonKey(name: 'employment_type') String? employmentType,
    String? industry,
  });
}

/// @nodoc
class _$ExperienceCopyWithImpl<$Res, $Val extends Experience>
    implements $ExperienceCopyWith<$Res> {
  _$ExperienceCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of Experience
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = freezed,
    Object? title = null,
    Object? company = null,
    Object? location = freezed,
    Object? startDate = null,
    Object? endDate = freezed,
    Object? isCurrent = null,
    Object? description = freezed,
    Object? achievements = null,
    Object? employmentType = freezed,
    Object? industry = freezed,
  }) {
    return _then(
      _value.copyWith(
            id: freezed == id
                ? _value.id
                : id // ignore: cast_nullable_to_non_nullable
                      as String?,
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
            startDate: null == startDate
                ? _value.startDate
                : startDate // ignore: cast_nullable_to_non_nullable
                      as String,
            endDate: freezed == endDate
                ? _value.endDate
                : endDate // ignore: cast_nullable_to_non_nullable
                      as String?,
            isCurrent: null == isCurrent
                ? _value.isCurrent
                : isCurrent // ignore: cast_nullable_to_non_nullable
                      as bool,
            description: freezed == description
                ? _value.description
                : description // ignore: cast_nullable_to_non_nullable
                      as String?,
            achievements: null == achievements
                ? _value.achievements
                : achievements // ignore: cast_nullable_to_non_nullable
                      as List<String>,
            employmentType: freezed == employmentType
                ? _value.employmentType
                : employmentType // ignore: cast_nullable_to_non_nullable
                      as String?,
            industry: freezed == industry
                ? _value.industry
                : industry // ignore: cast_nullable_to_non_nullable
                      as String?,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$ExperienceImplCopyWith<$Res>
    implements $ExperienceCopyWith<$Res> {
  factory _$$ExperienceImplCopyWith(
    _$ExperienceImpl value,
    $Res Function(_$ExperienceImpl) then,
  ) = __$$ExperienceImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    String? id,
    String title,
    String company,
    String? location,
    @JsonKey(name: 'start_date') String startDate,
    @JsonKey(name: 'end_date') String? endDate,
    @JsonKey(name: 'is_current') bool isCurrent,
    String? description,
    List<String> achievements,
    @JsonKey(name: 'employment_type') String? employmentType,
    String? industry,
  });
}

/// @nodoc
class __$$ExperienceImplCopyWithImpl<$Res>
    extends _$ExperienceCopyWithImpl<$Res, _$ExperienceImpl>
    implements _$$ExperienceImplCopyWith<$Res> {
  __$$ExperienceImplCopyWithImpl(
    _$ExperienceImpl _value,
    $Res Function(_$ExperienceImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of Experience
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = freezed,
    Object? title = null,
    Object? company = null,
    Object? location = freezed,
    Object? startDate = null,
    Object? endDate = freezed,
    Object? isCurrent = null,
    Object? description = freezed,
    Object? achievements = null,
    Object? employmentType = freezed,
    Object? industry = freezed,
  }) {
    return _then(
      _$ExperienceImpl(
        id: freezed == id
            ? _value.id
            : id // ignore: cast_nullable_to_non_nullable
                  as String?,
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
        startDate: null == startDate
            ? _value.startDate
            : startDate // ignore: cast_nullable_to_non_nullable
                  as String,
        endDate: freezed == endDate
            ? _value.endDate
            : endDate // ignore: cast_nullable_to_non_nullable
                  as String?,
        isCurrent: null == isCurrent
            ? _value.isCurrent
            : isCurrent // ignore: cast_nullable_to_non_nullable
                  as bool,
        description: freezed == description
            ? _value.description
            : description // ignore: cast_nullable_to_non_nullable
                  as String?,
        achievements: null == achievements
            ? _value._achievements
            : achievements // ignore: cast_nullable_to_non_nullable
                  as List<String>,
        employmentType: freezed == employmentType
            ? _value.employmentType
            : employmentType // ignore: cast_nullable_to_non_nullable
                  as String?,
        industry: freezed == industry
            ? _value.industry
            : industry // ignore: cast_nullable_to_non_nullable
                  as String?,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$ExperienceImpl implements _Experience {
  const _$ExperienceImpl({
    this.id,
    required this.title,
    required this.company,
    this.location,
    @JsonKey(name: 'start_date') required this.startDate,
    @JsonKey(name: 'end_date') this.endDate,
    @JsonKey(name: 'is_current') this.isCurrent = false,
    this.description,
    final List<String> achievements = const [],
    @JsonKey(name: 'employment_type') this.employmentType,
    this.industry,
  }) : _achievements = achievements;

  factory _$ExperienceImpl.fromJson(Map<String, dynamic> json) =>
      _$$ExperienceImplFromJson(json);

  @override
  final String? id;
  @override
  final String title;
  @override
  final String company;
  @override
  final String? location;
  // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'start_date')
  final String startDate;
  // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'end_date')
  final String? endDate;
  // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'is_current')
  final bool isCurrent;
  @override
  final String? description;
  final List<String> _achievements;
  @override
  @JsonKey()
  List<String> get achievements {
    if (_achievements is EqualUnmodifiableListView) return _achievements;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_achievements);
  }

  // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'employment_type')
  final String? employmentType;
  @override
  final String? industry;

  @override
  String toString() {
    return 'Experience(id: $id, title: $title, company: $company, location: $location, startDate: $startDate, endDate: $endDate, isCurrent: $isCurrent, description: $description, achievements: $achievements, employmentType: $employmentType, industry: $industry)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ExperienceImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.title, title) || other.title == title) &&
            (identical(other.company, company) || other.company == company) &&
            (identical(other.location, location) ||
                other.location == location) &&
            (identical(other.startDate, startDate) ||
                other.startDate == startDate) &&
            (identical(other.endDate, endDate) || other.endDate == endDate) &&
            (identical(other.isCurrent, isCurrent) ||
                other.isCurrent == isCurrent) &&
            (identical(other.description, description) ||
                other.description == description) &&
            const DeepCollectionEquality().equals(
              other._achievements,
              _achievements,
            ) &&
            (identical(other.employmentType, employmentType) ||
                other.employmentType == employmentType) &&
            (identical(other.industry, industry) ||
                other.industry == industry));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
    runtimeType,
    id,
    title,
    company,
    location,
    startDate,
    endDate,
    isCurrent,
    description,
    const DeepCollectionEquality().hash(_achievements),
    employmentType,
    industry,
  );

  /// Create a copy of Experience
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ExperienceImplCopyWith<_$ExperienceImpl> get copyWith =>
      __$$ExperienceImplCopyWithImpl<_$ExperienceImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ExperienceImplToJson(this);
  }
}

abstract class _Experience implements Experience {
  const factory _Experience({
    final String? id,
    required final String title,
    required final String company,
    final String? location,
    @JsonKey(name: 'start_date') required final String startDate,
    @JsonKey(name: 'end_date') final String? endDate,
    @JsonKey(name: 'is_current') final bool isCurrent,
    final String? description,
    final List<String> achievements,
    @JsonKey(name: 'employment_type') final String? employmentType,
    final String? industry,
  }) = _$ExperienceImpl;

  factory _Experience.fromJson(Map<String, dynamic> json) =
      _$ExperienceImpl.fromJson;

  @override
  String? get id;
  @override
  String get title;
  @override
  String get company;
  @override
  String? get location; // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'start_date')
  String get startDate; // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'end_date')
  String? get endDate; // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'is_current')
  bool get isCurrent;
  @override
  String? get description;
  @override
  List<String> get achievements; // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'employment_type')
  String? get employmentType;
  @override
  String? get industry;

  /// Create a copy of Experience
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ExperienceImplCopyWith<_$ExperienceImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

Education _$EducationFromJson(Map<String, dynamic> json) {
  return _Education.fromJson(json);
}

/// @nodoc
mixin _$Education {
  String? get id => throw _privateConstructorUsedError;
  String get institution => throw _privateConstructorUsedError;
  String get degree =>
      throw _privateConstructorUsedError; // ignore: invalid_annotation_target
  @JsonKey(name: 'field_of_study')
  String get fieldOfStudy => throw _privateConstructorUsedError; // ignore: invalid_annotation_target
  @JsonKey(name: 'start_date')
  String get startDate => throw _privateConstructorUsedError; // ignore: invalid_annotation_target
  @JsonKey(name: 'end_date')
  String? get endDate => throw _privateConstructorUsedError; // ignore: invalid_annotation_target
  @JsonKey(name: 'is_current')
  bool get isCurrent => throw _privateConstructorUsedError;
  double? get gpa => throw _privateConstructorUsedError;
  List<String> get honors => throw _privateConstructorUsedError;
  String? get description => throw _privateConstructorUsedError;

  /// Serializes this Education to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of Education
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $EducationCopyWith<Education> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $EducationCopyWith<$Res> {
  factory $EducationCopyWith(Education value, $Res Function(Education) then) =
      _$EducationCopyWithImpl<$Res, Education>;
  @useResult
  $Res call({
    String? id,
    String institution,
    String degree,
    @JsonKey(name: 'field_of_study') String fieldOfStudy,
    @JsonKey(name: 'start_date') String startDate,
    @JsonKey(name: 'end_date') String? endDate,
    @JsonKey(name: 'is_current') bool isCurrent,
    double? gpa,
    List<String> honors,
    String? description,
  });
}

/// @nodoc
class _$EducationCopyWithImpl<$Res, $Val extends Education>
    implements $EducationCopyWith<$Res> {
  _$EducationCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of Education
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = freezed,
    Object? institution = null,
    Object? degree = null,
    Object? fieldOfStudy = null,
    Object? startDate = null,
    Object? endDate = freezed,
    Object? isCurrent = null,
    Object? gpa = freezed,
    Object? honors = null,
    Object? description = freezed,
  }) {
    return _then(
      _value.copyWith(
            id: freezed == id
                ? _value.id
                : id // ignore: cast_nullable_to_non_nullable
                      as String?,
            institution: null == institution
                ? _value.institution
                : institution // ignore: cast_nullable_to_non_nullable
                      as String,
            degree: null == degree
                ? _value.degree
                : degree // ignore: cast_nullable_to_non_nullable
                      as String,
            fieldOfStudy: null == fieldOfStudy
                ? _value.fieldOfStudy
                : fieldOfStudy // ignore: cast_nullable_to_non_nullable
                      as String,
            startDate: null == startDate
                ? _value.startDate
                : startDate // ignore: cast_nullable_to_non_nullable
                      as String,
            endDate: freezed == endDate
                ? _value.endDate
                : endDate // ignore: cast_nullable_to_non_nullable
                      as String?,
            isCurrent: null == isCurrent
                ? _value.isCurrent
                : isCurrent // ignore: cast_nullable_to_non_nullable
                      as bool,
            gpa: freezed == gpa
                ? _value.gpa
                : gpa // ignore: cast_nullable_to_non_nullable
                      as double?,
            honors: null == honors
                ? _value.honors
                : honors // ignore: cast_nullable_to_non_nullable
                      as List<String>,
            description: freezed == description
                ? _value.description
                : description // ignore: cast_nullable_to_non_nullable
                      as String?,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$EducationImplCopyWith<$Res>
    implements $EducationCopyWith<$Res> {
  factory _$$EducationImplCopyWith(
    _$EducationImpl value,
    $Res Function(_$EducationImpl) then,
  ) = __$$EducationImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    String? id,
    String institution,
    String degree,
    @JsonKey(name: 'field_of_study') String fieldOfStudy,
    @JsonKey(name: 'start_date') String startDate,
    @JsonKey(name: 'end_date') String? endDate,
    @JsonKey(name: 'is_current') bool isCurrent,
    double? gpa,
    List<String> honors,
    String? description,
  });
}

/// @nodoc
class __$$EducationImplCopyWithImpl<$Res>
    extends _$EducationCopyWithImpl<$Res, _$EducationImpl>
    implements _$$EducationImplCopyWith<$Res> {
  __$$EducationImplCopyWithImpl(
    _$EducationImpl _value,
    $Res Function(_$EducationImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of Education
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = freezed,
    Object? institution = null,
    Object? degree = null,
    Object? fieldOfStudy = null,
    Object? startDate = null,
    Object? endDate = freezed,
    Object? isCurrent = null,
    Object? gpa = freezed,
    Object? honors = null,
    Object? description = freezed,
  }) {
    return _then(
      _$EducationImpl(
        id: freezed == id
            ? _value.id
            : id // ignore: cast_nullable_to_non_nullable
                  as String?,
        institution: null == institution
            ? _value.institution
            : institution // ignore: cast_nullable_to_non_nullable
                  as String,
        degree: null == degree
            ? _value.degree
            : degree // ignore: cast_nullable_to_non_nullable
                  as String,
        fieldOfStudy: null == fieldOfStudy
            ? _value.fieldOfStudy
            : fieldOfStudy // ignore: cast_nullable_to_non_nullable
                  as String,
        startDate: null == startDate
            ? _value.startDate
            : startDate // ignore: cast_nullable_to_non_nullable
                  as String,
        endDate: freezed == endDate
            ? _value.endDate
            : endDate // ignore: cast_nullable_to_non_nullable
                  as String?,
        isCurrent: null == isCurrent
            ? _value.isCurrent
            : isCurrent // ignore: cast_nullable_to_non_nullable
                  as bool,
        gpa: freezed == gpa
            ? _value.gpa
            : gpa // ignore: cast_nullable_to_non_nullable
                  as double?,
        honors: null == honors
            ? _value._honors
            : honors // ignore: cast_nullable_to_non_nullable
                  as List<String>,
        description: freezed == description
            ? _value.description
            : description // ignore: cast_nullable_to_non_nullable
                  as String?,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$EducationImpl implements _Education {
  const _$EducationImpl({
    this.id,
    required this.institution,
    required this.degree,
    @JsonKey(name: 'field_of_study') required this.fieldOfStudy,
    @JsonKey(name: 'start_date') required this.startDate,
    @JsonKey(name: 'end_date') this.endDate,
    @JsonKey(name: 'is_current') this.isCurrent = false,
    this.gpa,
    final List<String> honors = const [],
    this.description,
  }) : _honors = honors;

  factory _$EducationImpl.fromJson(Map<String, dynamic> json) =>
      _$$EducationImplFromJson(json);

  @override
  final String? id;
  @override
  final String institution;
  @override
  final String degree;
  // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'field_of_study')
  final String fieldOfStudy;
  // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'start_date')
  final String startDate;
  // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'end_date')
  final String? endDate;
  // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'is_current')
  final bool isCurrent;
  @override
  final double? gpa;
  final List<String> _honors;
  @override
  @JsonKey()
  List<String> get honors {
    if (_honors is EqualUnmodifiableListView) return _honors;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_honors);
  }

  @override
  final String? description;

  @override
  String toString() {
    return 'Education(id: $id, institution: $institution, degree: $degree, fieldOfStudy: $fieldOfStudy, startDate: $startDate, endDate: $endDate, isCurrent: $isCurrent, gpa: $gpa, honors: $honors, description: $description)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$EducationImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.institution, institution) ||
                other.institution == institution) &&
            (identical(other.degree, degree) || other.degree == degree) &&
            (identical(other.fieldOfStudy, fieldOfStudy) ||
                other.fieldOfStudy == fieldOfStudy) &&
            (identical(other.startDate, startDate) ||
                other.startDate == startDate) &&
            (identical(other.endDate, endDate) || other.endDate == endDate) &&
            (identical(other.isCurrent, isCurrent) ||
                other.isCurrent == isCurrent) &&
            (identical(other.gpa, gpa) || other.gpa == gpa) &&
            const DeepCollectionEquality().equals(other._honors, _honors) &&
            (identical(other.description, description) ||
                other.description == description));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
    runtimeType,
    id,
    institution,
    degree,
    fieldOfStudy,
    startDate,
    endDate,
    isCurrent,
    gpa,
    const DeepCollectionEquality().hash(_honors),
    description,
  );

  /// Create a copy of Education
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$EducationImplCopyWith<_$EducationImpl> get copyWith =>
      __$$EducationImplCopyWithImpl<_$EducationImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$EducationImplToJson(this);
  }
}

abstract class _Education implements Education {
  const factory _Education({
    final String? id,
    required final String institution,
    required final String degree,
    @JsonKey(name: 'field_of_study') required final String fieldOfStudy,
    @JsonKey(name: 'start_date') required final String startDate,
    @JsonKey(name: 'end_date') final String? endDate,
    @JsonKey(name: 'is_current') final bool isCurrent,
    final double? gpa,
    final List<String> honors,
    final String? description,
  }) = _$EducationImpl;

  factory _Education.fromJson(Map<String, dynamic> json) =
      _$EducationImpl.fromJson;

  @override
  String? get id;
  @override
  String get institution;
  @override
  String get degree; // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'field_of_study')
  String get fieldOfStudy; // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'start_date')
  String get startDate; // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'end_date')
  String? get endDate; // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'is_current')
  bool get isCurrent;
  @override
  double? get gpa;
  @override
  List<String> get honors;
  @override
  String? get description;

  /// Create a copy of Education
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$EducationImplCopyWith<_$EducationImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

Skills _$SkillsFromJson(Map<String, dynamic> json) {
  return _Skills.fromJson(json);
}

/// @nodoc
mixin _$Skills {
  List<String> get technical => throw _privateConstructorUsedError;
  List<String> get soft => throw _privateConstructorUsedError;
  List<Language> get languages => throw _privateConstructorUsedError;
  List<Certification> get certifications => throw _privateConstructorUsedError;

  /// Serializes this Skills to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of Skills
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $SkillsCopyWith<Skills> get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $SkillsCopyWith<$Res> {
  factory $SkillsCopyWith(Skills value, $Res Function(Skills) then) =
      _$SkillsCopyWithImpl<$Res, Skills>;
  @useResult
  $Res call({
    List<String> technical,
    List<String> soft,
    List<Language> languages,
    List<Certification> certifications,
  });
}

/// @nodoc
class _$SkillsCopyWithImpl<$Res, $Val extends Skills>
    implements $SkillsCopyWith<$Res> {
  _$SkillsCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of Skills
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? technical = null,
    Object? soft = null,
    Object? languages = null,
    Object? certifications = null,
  }) {
    return _then(
      _value.copyWith(
            technical: null == technical
                ? _value.technical
                : technical // ignore: cast_nullable_to_non_nullable
                      as List<String>,
            soft: null == soft
                ? _value.soft
                : soft // ignore: cast_nullable_to_non_nullable
                      as List<String>,
            languages: null == languages
                ? _value.languages
                : languages // ignore: cast_nullable_to_non_nullable
                      as List<Language>,
            certifications: null == certifications
                ? _value.certifications
                : certifications // ignore: cast_nullable_to_non_nullable
                      as List<Certification>,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$SkillsImplCopyWith<$Res> implements $SkillsCopyWith<$Res> {
  factory _$$SkillsImplCopyWith(
    _$SkillsImpl value,
    $Res Function(_$SkillsImpl) then,
  ) = __$$SkillsImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    List<String> technical,
    List<String> soft,
    List<Language> languages,
    List<Certification> certifications,
  });
}

/// @nodoc
class __$$SkillsImplCopyWithImpl<$Res>
    extends _$SkillsCopyWithImpl<$Res, _$SkillsImpl>
    implements _$$SkillsImplCopyWith<$Res> {
  __$$SkillsImplCopyWithImpl(
    _$SkillsImpl _value,
    $Res Function(_$SkillsImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of Skills
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? technical = null,
    Object? soft = null,
    Object? languages = null,
    Object? certifications = null,
  }) {
    return _then(
      _$SkillsImpl(
        technical: null == technical
            ? _value._technical
            : technical // ignore: cast_nullable_to_non_nullable
                  as List<String>,
        soft: null == soft
            ? _value._soft
            : soft // ignore: cast_nullable_to_non_nullable
                  as List<String>,
        languages: null == languages
            ? _value._languages
            : languages // ignore: cast_nullable_to_non_nullable
                  as List<Language>,
        certifications: null == certifications
            ? _value._certifications
            : certifications // ignore: cast_nullable_to_non_nullable
                  as List<Certification>,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$SkillsImpl implements _Skills {
  const _$SkillsImpl({
    final List<String> technical = const [],
    final List<String> soft = const [],
    final List<Language> languages = const [],
    final List<Certification> certifications = const [],
  }) : _technical = technical,
       _soft = soft,
       _languages = languages,
       _certifications = certifications;

  factory _$SkillsImpl.fromJson(Map<String, dynamic> json) =>
      _$$SkillsImplFromJson(json);

  final List<String> _technical;
  @override
  @JsonKey()
  List<String> get technical {
    if (_technical is EqualUnmodifiableListView) return _technical;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_technical);
  }

  final List<String> _soft;
  @override
  @JsonKey()
  List<String> get soft {
    if (_soft is EqualUnmodifiableListView) return _soft;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_soft);
  }

  final List<Language> _languages;
  @override
  @JsonKey()
  List<Language> get languages {
    if (_languages is EqualUnmodifiableListView) return _languages;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_languages);
  }

  final List<Certification> _certifications;
  @override
  @JsonKey()
  List<Certification> get certifications {
    if (_certifications is EqualUnmodifiableListView) return _certifications;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_certifications);
  }

  @override
  String toString() {
    return 'Skills(technical: $technical, soft: $soft, languages: $languages, certifications: $certifications)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$SkillsImpl &&
            const DeepCollectionEquality().equals(
              other._technical,
              _technical,
            ) &&
            const DeepCollectionEquality().equals(other._soft, _soft) &&
            const DeepCollectionEquality().equals(
              other._languages,
              _languages,
            ) &&
            const DeepCollectionEquality().equals(
              other._certifications,
              _certifications,
            ));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
    runtimeType,
    const DeepCollectionEquality().hash(_technical),
    const DeepCollectionEquality().hash(_soft),
    const DeepCollectionEquality().hash(_languages),
    const DeepCollectionEquality().hash(_certifications),
  );

  /// Create a copy of Skills
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$SkillsImplCopyWith<_$SkillsImpl> get copyWith =>
      __$$SkillsImplCopyWithImpl<_$SkillsImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$SkillsImplToJson(this);
  }
}

abstract class _Skills implements Skills {
  const factory _Skills({
    final List<String> technical,
    final List<String> soft,
    final List<Language> languages,
    final List<Certification> certifications,
  }) = _$SkillsImpl;

  factory _Skills.fromJson(Map<String, dynamic> json) = _$SkillsImpl.fromJson;

  @override
  List<String> get technical;
  @override
  List<String> get soft;
  @override
  List<Language> get languages;
  @override
  List<Certification> get certifications;

  /// Create a copy of Skills
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$SkillsImplCopyWith<_$SkillsImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

Language _$LanguageFromJson(Map<String, dynamic> json) {
  return _Language.fromJson(json);
}

/// @nodoc
mixin _$Language {
  String get name => throw _privateConstructorUsedError;
  String get proficiency => throw _privateConstructorUsedError;

  /// Serializes this Language to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of Language
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $LanguageCopyWith<Language> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $LanguageCopyWith<$Res> {
  factory $LanguageCopyWith(Language value, $Res Function(Language) then) =
      _$LanguageCopyWithImpl<$Res, Language>;
  @useResult
  $Res call({String name, String proficiency});
}

/// @nodoc
class _$LanguageCopyWithImpl<$Res, $Val extends Language>
    implements $LanguageCopyWith<$Res> {
  _$LanguageCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of Language
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? name = null, Object? proficiency = null}) {
    return _then(
      _value.copyWith(
            name: null == name
                ? _value.name
                : name // ignore: cast_nullable_to_non_nullable
                      as String,
            proficiency: null == proficiency
                ? _value.proficiency
                : proficiency // ignore: cast_nullable_to_non_nullable
                      as String,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$LanguageImplCopyWith<$Res>
    implements $LanguageCopyWith<$Res> {
  factory _$$LanguageImplCopyWith(
    _$LanguageImpl value,
    $Res Function(_$LanguageImpl) then,
  ) = __$$LanguageImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({String name, String proficiency});
}

/// @nodoc
class __$$LanguageImplCopyWithImpl<$Res>
    extends _$LanguageCopyWithImpl<$Res, _$LanguageImpl>
    implements _$$LanguageImplCopyWith<$Res> {
  __$$LanguageImplCopyWithImpl(
    _$LanguageImpl _value,
    $Res Function(_$LanguageImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of Language
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? name = null, Object? proficiency = null}) {
    return _then(
      _$LanguageImpl(
        name: null == name
            ? _value.name
            : name // ignore: cast_nullable_to_non_nullable
                  as String,
        proficiency: null == proficiency
            ? _value.proficiency
            : proficiency // ignore: cast_nullable_to_non_nullable
                  as String,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$LanguageImpl implements _Language {
  const _$LanguageImpl({required this.name, required this.proficiency});

  factory _$LanguageImpl.fromJson(Map<String, dynamic> json) =>
      _$$LanguageImplFromJson(json);

  @override
  final String name;
  @override
  final String proficiency;

  @override
  String toString() {
    return 'Language(name: $name, proficiency: $proficiency)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$LanguageImpl &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.proficiency, proficiency) ||
                other.proficiency == proficiency));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, name, proficiency);

  /// Create a copy of Language
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$LanguageImplCopyWith<_$LanguageImpl> get copyWith =>
      __$$LanguageImplCopyWithImpl<_$LanguageImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$LanguageImplToJson(this);
  }
}

abstract class _Language implements Language {
  const factory _Language({
    required final String name,
    required final String proficiency,
  }) = _$LanguageImpl;

  factory _Language.fromJson(Map<String, dynamic> json) =
      _$LanguageImpl.fromJson;

  @override
  String get name;
  @override
  String get proficiency;

  /// Create a copy of Language
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$LanguageImplCopyWith<_$LanguageImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

Certification _$CertificationFromJson(Map<String, dynamic> json) {
  return _Certification.fromJson(json);
}

/// @nodoc
mixin _$Certification {
  String? get id => throw _privateConstructorUsedError;
  String get name => throw _privateConstructorUsedError;
  String get issuer =>
      throw _privateConstructorUsedError; // ignore: invalid_annotation_target
  @JsonKey(name: 'date_obtained')
  String get dateObtained => throw _privateConstructorUsedError; // ignore: invalid_annotation_target
  @JsonKey(name: 'expiry_date')
  String? get expiryDate => throw _privateConstructorUsedError; // ignore: invalid_annotation_target
  @JsonKey(name: 'credential_id')
  String? get credentialId => throw _privateConstructorUsedError;

  /// Serializes this Certification to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of Certification
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $CertificationCopyWith<Certification> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $CertificationCopyWith<$Res> {
  factory $CertificationCopyWith(
    Certification value,
    $Res Function(Certification) then,
  ) = _$CertificationCopyWithImpl<$Res, Certification>;
  @useResult
  $Res call({
    String? id,
    String name,
    String issuer,
    @JsonKey(name: 'date_obtained') String dateObtained,
    @JsonKey(name: 'expiry_date') String? expiryDate,
    @JsonKey(name: 'credential_id') String? credentialId,
  });
}

/// @nodoc
class _$CertificationCopyWithImpl<$Res, $Val extends Certification>
    implements $CertificationCopyWith<$Res> {
  _$CertificationCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of Certification
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = freezed,
    Object? name = null,
    Object? issuer = null,
    Object? dateObtained = null,
    Object? expiryDate = freezed,
    Object? credentialId = freezed,
  }) {
    return _then(
      _value.copyWith(
            id: freezed == id
                ? _value.id
                : id // ignore: cast_nullable_to_non_nullable
                      as String?,
            name: null == name
                ? _value.name
                : name // ignore: cast_nullable_to_non_nullable
                      as String,
            issuer: null == issuer
                ? _value.issuer
                : issuer // ignore: cast_nullable_to_non_nullable
                      as String,
            dateObtained: null == dateObtained
                ? _value.dateObtained
                : dateObtained // ignore: cast_nullable_to_non_nullable
                      as String,
            expiryDate: freezed == expiryDate
                ? _value.expiryDate
                : expiryDate // ignore: cast_nullable_to_non_nullable
                      as String?,
            credentialId: freezed == credentialId
                ? _value.credentialId
                : credentialId // ignore: cast_nullable_to_non_nullable
                      as String?,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$CertificationImplCopyWith<$Res>
    implements $CertificationCopyWith<$Res> {
  factory _$$CertificationImplCopyWith(
    _$CertificationImpl value,
    $Res Function(_$CertificationImpl) then,
  ) = __$$CertificationImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    String? id,
    String name,
    String issuer,
    @JsonKey(name: 'date_obtained') String dateObtained,
    @JsonKey(name: 'expiry_date') String? expiryDate,
    @JsonKey(name: 'credential_id') String? credentialId,
  });
}

/// @nodoc
class __$$CertificationImplCopyWithImpl<$Res>
    extends _$CertificationCopyWithImpl<$Res, _$CertificationImpl>
    implements _$$CertificationImplCopyWith<$Res> {
  __$$CertificationImplCopyWithImpl(
    _$CertificationImpl _value,
    $Res Function(_$CertificationImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of Certification
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = freezed,
    Object? name = null,
    Object? issuer = null,
    Object? dateObtained = null,
    Object? expiryDate = freezed,
    Object? credentialId = freezed,
  }) {
    return _then(
      _$CertificationImpl(
        id: freezed == id
            ? _value.id
            : id // ignore: cast_nullable_to_non_nullable
                  as String?,
        name: null == name
            ? _value.name
            : name // ignore: cast_nullable_to_non_nullable
                  as String,
        issuer: null == issuer
            ? _value.issuer
            : issuer // ignore: cast_nullable_to_non_nullable
                  as String,
        dateObtained: null == dateObtained
            ? _value.dateObtained
            : dateObtained // ignore: cast_nullable_to_non_nullable
                  as String,
        expiryDate: freezed == expiryDate
            ? _value.expiryDate
            : expiryDate // ignore: cast_nullable_to_non_nullable
                  as String?,
        credentialId: freezed == credentialId
            ? _value.credentialId
            : credentialId // ignore: cast_nullable_to_non_nullable
                  as String?,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$CertificationImpl implements _Certification {
  const _$CertificationImpl({
    this.id,
    required this.name,
    required this.issuer,
    @JsonKey(name: 'date_obtained') required this.dateObtained,
    @JsonKey(name: 'expiry_date') this.expiryDate,
    @JsonKey(name: 'credential_id') this.credentialId,
  });

  factory _$CertificationImpl.fromJson(Map<String, dynamic> json) =>
      _$$CertificationImplFromJson(json);

  @override
  final String? id;
  @override
  final String name;
  @override
  final String issuer;
  // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'date_obtained')
  final String dateObtained;
  // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'expiry_date')
  final String? expiryDate;
  // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'credential_id')
  final String? credentialId;

  @override
  String toString() {
    return 'Certification(id: $id, name: $name, issuer: $issuer, dateObtained: $dateObtained, expiryDate: $expiryDate, credentialId: $credentialId)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$CertificationImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.issuer, issuer) || other.issuer == issuer) &&
            (identical(other.dateObtained, dateObtained) ||
                other.dateObtained == dateObtained) &&
            (identical(other.expiryDate, expiryDate) ||
                other.expiryDate == expiryDate) &&
            (identical(other.credentialId, credentialId) ||
                other.credentialId == credentialId));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
    runtimeType,
    id,
    name,
    issuer,
    dateObtained,
    expiryDate,
    credentialId,
  );

  /// Create a copy of Certification
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$CertificationImplCopyWith<_$CertificationImpl> get copyWith =>
      __$$CertificationImplCopyWithImpl<_$CertificationImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$CertificationImplToJson(this);
  }
}

abstract class _Certification implements Certification {
  const factory _Certification({
    final String? id,
    required final String name,
    required final String issuer,
    @JsonKey(name: 'date_obtained') required final String dateObtained,
    @JsonKey(name: 'expiry_date') final String? expiryDate,
    @JsonKey(name: 'credential_id') final String? credentialId,
  }) = _$CertificationImpl;

  factory _Certification.fromJson(Map<String, dynamic> json) =
      _$CertificationImpl.fromJson;

  @override
  String? get id;
  @override
  String get name;
  @override
  String get issuer; // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'date_obtained')
  String get dateObtained; // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'expiry_date')
  String? get expiryDate; // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'credential_id')
  String? get credentialId;

  /// Create a copy of Certification
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$CertificationImplCopyWith<_$CertificationImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

Project _$ProjectFromJson(Map<String, dynamic> json) {
  return _Project.fromJson(json);
}

/// @nodoc
mixin _$Project {
  String? get id => throw _privateConstructorUsedError;
  String get name => throw _privateConstructorUsedError;
  String get description => throw _privateConstructorUsedError;
  List<String> get technologies => throw _privateConstructorUsedError;
  String? get url =>
      throw _privateConstructorUsedError; // ignore: invalid_annotation_target
  @JsonKey(name: 'repository_url')
  String? get repositoryUrl => throw _privateConstructorUsedError; // ignore: invalid_annotation_target
  @JsonKey(name: 'start_date')
  String? get startDate => throw _privateConstructorUsedError; // ignore: invalid_annotation_target
  @JsonKey(name: 'end_date')
  String? get endDate => throw _privateConstructorUsedError; // ignore: invalid_annotation_target
  @JsonKey(name: 'is_ongoing')
  bool get isOngoing => throw _privateConstructorUsedError;
  List<String> get highlights => throw _privateConstructorUsedError;

  /// Serializes this Project to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of Project
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ProjectCopyWith<Project> get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ProjectCopyWith<$Res> {
  factory $ProjectCopyWith(Project value, $Res Function(Project) then) =
      _$ProjectCopyWithImpl<$Res, Project>;
  @useResult
  $Res call({
    String? id,
    String name,
    String description,
    List<String> technologies,
    String? url,
    @JsonKey(name: 'repository_url') String? repositoryUrl,
    @JsonKey(name: 'start_date') String? startDate,
    @JsonKey(name: 'end_date') String? endDate,
    @JsonKey(name: 'is_ongoing') bool isOngoing,
    List<String> highlights,
  });
}

/// @nodoc
class _$ProjectCopyWithImpl<$Res, $Val extends Project>
    implements $ProjectCopyWith<$Res> {
  _$ProjectCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of Project
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = freezed,
    Object? name = null,
    Object? description = null,
    Object? technologies = null,
    Object? url = freezed,
    Object? repositoryUrl = freezed,
    Object? startDate = freezed,
    Object? endDate = freezed,
    Object? isOngoing = null,
    Object? highlights = null,
  }) {
    return _then(
      _value.copyWith(
            id: freezed == id
                ? _value.id
                : id // ignore: cast_nullable_to_non_nullable
                      as String?,
            name: null == name
                ? _value.name
                : name // ignore: cast_nullable_to_non_nullable
                      as String,
            description: null == description
                ? _value.description
                : description // ignore: cast_nullable_to_non_nullable
                      as String,
            technologies: null == technologies
                ? _value.technologies
                : technologies // ignore: cast_nullable_to_non_nullable
                      as List<String>,
            url: freezed == url
                ? _value.url
                : url // ignore: cast_nullable_to_non_nullable
                      as String?,
            repositoryUrl: freezed == repositoryUrl
                ? _value.repositoryUrl
                : repositoryUrl // ignore: cast_nullable_to_non_nullable
                      as String?,
            startDate: freezed == startDate
                ? _value.startDate
                : startDate // ignore: cast_nullable_to_non_nullable
                      as String?,
            endDate: freezed == endDate
                ? _value.endDate
                : endDate // ignore: cast_nullable_to_non_nullable
                      as String?,
            isOngoing: null == isOngoing
                ? _value.isOngoing
                : isOngoing // ignore: cast_nullable_to_non_nullable
                      as bool,
            highlights: null == highlights
                ? _value.highlights
                : highlights // ignore: cast_nullable_to_non_nullable
                      as List<String>,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$ProjectImplCopyWith<$Res> implements $ProjectCopyWith<$Res> {
  factory _$$ProjectImplCopyWith(
    _$ProjectImpl value,
    $Res Function(_$ProjectImpl) then,
  ) = __$$ProjectImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    String? id,
    String name,
    String description,
    List<String> technologies,
    String? url,
    @JsonKey(name: 'repository_url') String? repositoryUrl,
    @JsonKey(name: 'start_date') String? startDate,
    @JsonKey(name: 'end_date') String? endDate,
    @JsonKey(name: 'is_ongoing') bool isOngoing,
    List<String> highlights,
  });
}

/// @nodoc
class __$$ProjectImplCopyWithImpl<$Res>
    extends _$ProjectCopyWithImpl<$Res, _$ProjectImpl>
    implements _$$ProjectImplCopyWith<$Res> {
  __$$ProjectImplCopyWithImpl(
    _$ProjectImpl _value,
    $Res Function(_$ProjectImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of Project
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = freezed,
    Object? name = null,
    Object? description = null,
    Object? technologies = null,
    Object? url = freezed,
    Object? repositoryUrl = freezed,
    Object? startDate = freezed,
    Object? endDate = freezed,
    Object? isOngoing = null,
    Object? highlights = null,
  }) {
    return _then(
      _$ProjectImpl(
        id: freezed == id
            ? _value.id
            : id // ignore: cast_nullable_to_non_nullable
                  as String?,
        name: null == name
            ? _value.name
            : name // ignore: cast_nullable_to_non_nullable
                  as String,
        description: null == description
            ? _value.description
            : description // ignore: cast_nullable_to_non_nullable
                  as String,
        technologies: null == technologies
            ? _value._technologies
            : technologies // ignore: cast_nullable_to_non_nullable
                  as List<String>,
        url: freezed == url
            ? _value.url
            : url // ignore: cast_nullable_to_non_nullable
                  as String?,
        repositoryUrl: freezed == repositoryUrl
            ? _value.repositoryUrl
            : repositoryUrl // ignore: cast_nullable_to_non_nullable
                  as String?,
        startDate: freezed == startDate
            ? _value.startDate
            : startDate // ignore: cast_nullable_to_non_nullable
                  as String?,
        endDate: freezed == endDate
            ? _value.endDate
            : endDate // ignore: cast_nullable_to_non_nullable
                  as String?,
        isOngoing: null == isOngoing
            ? _value.isOngoing
            : isOngoing // ignore: cast_nullable_to_non_nullable
                  as bool,
        highlights: null == highlights
            ? _value._highlights
            : highlights // ignore: cast_nullable_to_non_nullable
                  as List<String>,
      ),
    );
  }
}

/// @nodoc
@JsonSerializable()
class _$ProjectImpl implements _Project {
  const _$ProjectImpl({
    this.id,
    required this.name,
    required this.description,
    final List<String> technologies = const [],
    this.url,
    @JsonKey(name: 'repository_url') this.repositoryUrl,
    @JsonKey(name: 'start_date') this.startDate,
    @JsonKey(name: 'end_date') this.endDate,
    @JsonKey(name: 'is_ongoing') this.isOngoing = false,
    final List<String> highlights = const [],
  }) : _technologies = technologies,
       _highlights = highlights;

  factory _$ProjectImpl.fromJson(Map<String, dynamic> json) =>
      _$$ProjectImplFromJson(json);

  @override
  final String? id;
  @override
  final String name;
  @override
  final String description;
  final List<String> _technologies;
  @override
  @JsonKey()
  List<String> get technologies {
    if (_technologies is EqualUnmodifiableListView) return _technologies;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_technologies);
  }

  @override
  final String? url;
  // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'repository_url')
  final String? repositoryUrl;
  // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'start_date')
  final String? startDate;
  // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'end_date')
  final String? endDate;
  // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'is_ongoing')
  final bool isOngoing;
  final List<String> _highlights;
  @override
  @JsonKey()
  List<String> get highlights {
    if (_highlights is EqualUnmodifiableListView) return _highlights;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_highlights);
  }

  @override
  String toString() {
    return 'Project(id: $id, name: $name, description: $description, technologies: $technologies, url: $url, repositoryUrl: $repositoryUrl, startDate: $startDate, endDate: $endDate, isOngoing: $isOngoing, highlights: $highlights)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ProjectImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.description, description) ||
                other.description == description) &&
            const DeepCollectionEquality().equals(
              other._technologies,
              _technologies,
            ) &&
            (identical(other.url, url) || other.url == url) &&
            (identical(other.repositoryUrl, repositoryUrl) ||
                other.repositoryUrl == repositoryUrl) &&
            (identical(other.startDate, startDate) ||
                other.startDate == startDate) &&
            (identical(other.endDate, endDate) || other.endDate == endDate) &&
            (identical(other.isOngoing, isOngoing) ||
                other.isOngoing == isOngoing) &&
            const DeepCollectionEquality().equals(
              other._highlights,
              _highlights,
            ));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
    runtimeType,
    id,
    name,
    description,
    const DeepCollectionEquality().hash(_technologies),
    url,
    repositoryUrl,
    startDate,
    endDate,
    isOngoing,
    const DeepCollectionEquality().hash(_highlights),
  );

  /// Create a copy of Project
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ProjectImplCopyWith<_$ProjectImpl> get copyWith =>
      __$$ProjectImplCopyWithImpl<_$ProjectImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ProjectImplToJson(this);
  }
}

abstract class _Project implements Project {
  const factory _Project({
    final String? id,
    required final String name,
    required final String description,
    final List<String> technologies,
    final String? url,
    @JsonKey(name: 'repository_url') final String? repositoryUrl,
    @JsonKey(name: 'start_date') final String? startDate,
    @JsonKey(name: 'end_date') final String? endDate,
    @JsonKey(name: 'is_ongoing') final bool isOngoing,
    final List<String> highlights,
  }) = _$ProjectImpl;

  factory _Project.fromJson(Map<String, dynamic> json) = _$ProjectImpl.fromJson;

  @override
  String? get id;
  @override
  String get name;
  @override
  String get description;
  @override
  List<String> get technologies;
  @override
  String? get url; // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'repository_url')
  String? get repositoryUrl; // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'start_date')
  String? get startDate; // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'end_date')
  String? get endDate; // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'is_ongoing')
  bool get isOngoing;
  @override
  List<String> get highlights;

  /// Create a copy of Project
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ProjectImplCopyWith<_$ProjectImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ProfileAnalytics _$ProfileAnalyticsFromJson(Map<String, dynamic> json) {
  return _ProfileAnalytics.fromJson(json);
}

/// @nodoc
mixin _$ProfileAnalytics {
  // ignore: invalid_annotation_target
  @JsonKey(name: 'profile_id')
  String get profileId => throw _privateConstructorUsedError;
  Map<String, int> get completeness => throw _privateConstructorUsedError;
  Map<String, dynamic> get statistics => throw _privateConstructorUsedError;
  List<String> get recommendations => throw _privateConstructorUsedError;

  /// Serializes this ProfileAnalytics to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ProfileAnalytics
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ProfileAnalyticsCopyWith<ProfileAnalytics> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ProfileAnalyticsCopyWith<$Res> {
  factory $ProfileAnalyticsCopyWith(
    ProfileAnalytics value,
    $Res Function(ProfileAnalytics) then,
  ) = _$ProfileAnalyticsCopyWithImpl<$Res, ProfileAnalytics>;
  @useResult
  $Res call({
    @JsonKey(name: 'profile_id') String profileId,
    Map<String, int> completeness,
    Map<String, dynamic> statistics,
    List<String> recommendations,
  });
}

/// @nodoc
class _$ProfileAnalyticsCopyWithImpl<$Res, $Val extends ProfileAnalytics>
    implements $ProfileAnalyticsCopyWith<$Res> {
  _$ProfileAnalyticsCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ProfileAnalytics
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? profileId = null,
    Object? completeness = null,
    Object? statistics = null,
    Object? recommendations = null,
  }) {
    return _then(
      _value.copyWith(
            profileId: null == profileId
                ? _value.profileId
                : profileId // ignore: cast_nullable_to_non_nullable
                      as String,
            completeness: null == completeness
                ? _value.completeness
                : completeness // ignore: cast_nullable_to_non_nullable
                      as Map<String, int>,
            statistics: null == statistics
                ? _value.statistics
                : statistics // ignore: cast_nullable_to_non_nullable
                      as Map<String, dynamic>,
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
abstract class _$$ProfileAnalyticsImplCopyWith<$Res>
    implements $ProfileAnalyticsCopyWith<$Res> {
  factory _$$ProfileAnalyticsImplCopyWith(
    _$ProfileAnalyticsImpl value,
    $Res Function(_$ProfileAnalyticsImpl) then,
  ) = __$$ProfileAnalyticsImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    @JsonKey(name: 'profile_id') String profileId,
    Map<String, int> completeness,
    Map<String, dynamic> statistics,
    List<String> recommendations,
  });
}

/// @nodoc
class __$$ProfileAnalyticsImplCopyWithImpl<$Res>
    extends _$ProfileAnalyticsCopyWithImpl<$Res, _$ProfileAnalyticsImpl>
    implements _$$ProfileAnalyticsImplCopyWith<$Res> {
  __$$ProfileAnalyticsImplCopyWithImpl(
    _$ProfileAnalyticsImpl _value,
    $Res Function(_$ProfileAnalyticsImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of ProfileAnalytics
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? profileId = null,
    Object? completeness = null,
    Object? statistics = null,
    Object? recommendations = null,
  }) {
    return _then(
      _$ProfileAnalyticsImpl(
        profileId: null == profileId
            ? _value.profileId
            : profileId // ignore: cast_nullable_to_non_nullable
                  as String,
        completeness: null == completeness
            ? _value._completeness
            : completeness // ignore: cast_nullable_to_non_nullable
                  as Map<String, int>,
        statistics: null == statistics
            ? _value._statistics
            : statistics // ignore: cast_nullable_to_non_nullable
                  as Map<String, dynamic>,
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
class _$ProfileAnalyticsImpl implements _ProfileAnalytics {
  const _$ProfileAnalyticsImpl({
    @JsonKey(name: 'profile_id') required this.profileId,
    required final Map<String, int> completeness,
    required final Map<String, dynamic> statistics,
    final List<String> recommendations = const [],
  }) : _completeness = completeness,
       _statistics = statistics,
       _recommendations = recommendations;

  factory _$ProfileAnalyticsImpl.fromJson(Map<String, dynamic> json) =>
      _$$ProfileAnalyticsImplFromJson(json);

  // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'profile_id')
  final String profileId;
  final Map<String, int> _completeness;
  @override
  Map<String, int> get completeness {
    if (_completeness is EqualUnmodifiableMapView) return _completeness;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_completeness);
  }

  final Map<String, dynamic> _statistics;
  @override
  Map<String, dynamic> get statistics {
    if (_statistics is EqualUnmodifiableMapView) return _statistics;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_statistics);
  }

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
    return 'ProfileAnalytics(profileId: $profileId, completeness: $completeness, statistics: $statistics, recommendations: $recommendations)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ProfileAnalyticsImpl &&
            (identical(other.profileId, profileId) ||
                other.profileId == profileId) &&
            const DeepCollectionEquality().equals(
              other._completeness,
              _completeness,
            ) &&
            const DeepCollectionEquality().equals(
              other._statistics,
              _statistics,
            ) &&
            const DeepCollectionEquality().equals(
              other._recommendations,
              _recommendations,
            ));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
    runtimeType,
    profileId,
    const DeepCollectionEquality().hash(_completeness),
    const DeepCollectionEquality().hash(_statistics),
    const DeepCollectionEquality().hash(_recommendations),
  );

  /// Create a copy of ProfileAnalytics
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ProfileAnalyticsImplCopyWith<_$ProfileAnalyticsImpl> get copyWith =>
      __$$ProfileAnalyticsImplCopyWithImpl<_$ProfileAnalyticsImpl>(
        this,
        _$identity,
      );

  @override
  Map<String, dynamic> toJson() {
    return _$$ProfileAnalyticsImplToJson(this);
  }
}

abstract class _ProfileAnalytics implements ProfileAnalytics {
  const factory _ProfileAnalytics({
    @JsonKey(name: 'profile_id') required final String profileId,
    required final Map<String, int> completeness,
    required final Map<String, dynamic> statistics,
    final List<String> recommendations,
  }) = _$ProfileAnalyticsImpl;

  factory _ProfileAnalytics.fromJson(Map<String, dynamic> json) =
      _$ProfileAnalyticsImpl.fromJson;

  // ignore: invalid_annotation_target
  @override
  @JsonKey(name: 'profile_id')
  String get profileId;
  @override
  Map<String, int> get completeness;
  @override
  Map<String, dynamic> get statistics;
  @override
  List<String> get recommendations;

  /// Create a copy of ProfileAnalytics
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ProfileAnalyticsImplCopyWith<_$ProfileAnalyticsImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

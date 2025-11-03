// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'job_provider.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
  'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models',
);

/// @nodoc
mixin _$JobState {
  List<Job> get userJobs => throw _privateConstructorUsedError;
  List<BrowseJob> get browseJobs => throw _privateConstructorUsedError;
  Job? get selectedJob => throw _privateConstructorUsedError;
  bool get isLoading => throw _privateConstructorUsedError;
  bool get isLoadingMore => throw _privateConstructorUsedError;
  bool get isBrowseLoading => throw _privateConstructorUsedError;
  String? get error => throw _privateConstructorUsedError;
  int get userJobsTotal => throw _privateConstructorUsedError;
  int get browseJobsTotal => throw _privateConstructorUsedError;
  bool get hasMoreUserJobs => throw _privateConstructorUsedError;
  bool get hasMoreBrowseJobs => throw _privateConstructorUsedError;

  /// Create a copy of JobState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $JobStateCopyWith<JobState> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $JobStateCopyWith<$Res> {
  factory $JobStateCopyWith(JobState value, $Res Function(JobState) then) =
      _$JobStateCopyWithImpl<$Res, JobState>;
  @useResult
  $Res call({
    List<Job> userJobs,
    List<BrowseJob> browseJobs,
    Job? selectedJob,
    bool isLoading,
    bool isLoadingMore,
    bool isBrowseLoading,
    String? error,
    int userJobsTotal,
    int browseJobsTotal,
    bool hasMoreUserJobs,
    bool hasMoreBrowseJobs,
  });

  $JobCopyWith<$Res>? get selectedJob;
}

/// @nodoc
class _$JobStateCopyWithImpl<$Res, $Val extends JobState>
    implements $JobStateCopyWith<$Res> {
  _$JobStateCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of JobState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? userJobs = null,
    Object? browseJobs = null,
    Object? selectedJob = freezed,
    Object? isLoading = null,
    Object? isLoadingMore = null,
    Object? isBrowseLoading = null,
    Object? error = freezed,
    Object? userJobsTotal = null,
    Object? browseJobsTotal = null,
    Object? hasMoreUserJobs = null,
    Object? hasMoreBrowseJobs = null,
  }) {
    return _then(
      _value.copyWith(
            userJobs: null == userJobs
                ? _value.userJobs
                : userJobs // ignore: cast_nullable_to_non_nullable
                      as List<Job>,
            browseJobs: null == browseJobs
                ? _value.browseJobs
                : browseJobs // ignore: cast_nullable_to_non_nullable
                      as List<BrowseJob>,
            selectedJob: freezed == selectedJob
                ? _value.selectedJob
                : selectedJob // ignore: cast_nullable_to_non_nullable
                      as Job?,
            isLoading: null == isLoading
                ? _value.isLoading
                : isLoading // ignore: cast_nullable_to_non_nullable
                      as bool,
            isLoadingMore: null == isLoadingMore
                ? _value.isLoadingMore
                : isLoadingMore // ignore: cast_nullable_to_non_nullable
                      as bool,
            isBrowseLoading: null == isBrowseLoading
                ? _value.isBrowseLoading
                : isBrowseLoading // ignore: cast_nullable_to_non_nullable
                      as bool,
            error: freezed == error
                ? _value.error
                : error // ignore: cast_nullable_to_non_nullable
                      as String?,
            userJobsTotal: null == userJobsTotal
                ? _value.userJobsTotal
                : userJobsTotal // ignore: cast_nullable_to_non_nullable
                      as int,
            browseJobsTotal: null == browseJobsTotal
                ? _value.browseJobsTotal
                : browseJobsTotal // ignore: cast_nullable_to_non_nullable
                      as int,
            hasMoreUserJobs: null == hasMoreUserJobs
                ? _value.hasMoreUserJobs
                : hasMoreUserJobs // ignore: cast_nullable_to_non_nullable
                      as bool,
            hasMoreBrowseJobs: null == hasMoreBrowseJobs
                ? _value.hasMoreBrowseJobs
                : hasMoreBrowseJobs // ignore: cast_nullable_to_non_nullable
                      as bool,
          )
          as $Val,
    );
  }

  /// Create a copy of JobState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $JobCopyWith<$Res>? get selectedJob {
    if (_value.selectedJob == null) {
      return null;
    }

    return $JobCopyWith<$Res>(_value.selectedJob!, (value) {
      return _then(_value.copyWith(selectedJob: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$JobStateImplCopyWith<$Res>
    implements $JobStateCopyWith<$Res> {
  factory _$$JobStateImplCopyWith(
    _$JobStateImpl value,
    $Res Function(_$JobStateImpl) then,
  ) = __$$JobStateImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    List<Job> userJobs,
    List<BrowseJob> browseJobs,
    Job? selectedJob,
    bool isLoading,
    bool isLoadingMore,
    bool isBrowseLoading,
    String? error,
    int userJobsTotal,
    int browseJobsTotal,
    bool hasMoreUserJobs,
    bool hasMoreBrowseJobs,
  });

  @override
  $JobCopyWith<$Res>? get selectedJob;
}

/// @nodoc
class __$$JobStateImplCopyWithImpl<$Res>
    extends _$JobStateCopyWithImpl<$Res, _$JobStateImpl>
    implements _$$JobStateImplCopyWith<$Res> {
  __$$JobStateImplCopyWithImpl(
    _$JobStateImpl _value,
    $Res Function(_$JobStateImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of JobState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? userJobs = null,
    Object? browseJobs = null,
    Object? selectedJob = freezed,
    Object? isLoading = null,
    Object? isLoadingMore = null,
    Object? isBrowseLoading = null,
    Object? error = freezed,
    Object? userJobsTotal = null,
    Object? browseJobsTotal = null,
    Object? hasMoreUserJobs = null,
    Object? hasMoreBrowseJobs = null,
  }) {
    return _then(
      _$JobStateImpl(
        userJobs: null == userJobs
            ? _value._userJobs
            : userJobs // ignore: cast_nullable_to_non_nullable
                  as List<Job>,
        browseJobs: null == browseJobs
            ? _value._browseJobs
            : browseJobs // ignore: cast_nullable_to_non_nullable
                  as List<BrowseJob>,
        selectedJob: freezed == selectedJob
            ? _value.selectedJob
            : selectedJob // ignore: cast_nullable_to_non_nullable
                  as Job?,
        isLoading: null == isLoading
            ? _value.isLoading
            : isLoading // ignore: cast_nullable_to_non_nullable
                  as bool,
        isLoadingMore: null == isLoadingMore
            ? _value.isLoadingMore
            : isLoadingMore // ignore: cast_nullable_to_non_nullable
                  as bool,
        isBrowseLoading: null == isBrowseLoading
            ? _value.isBrowseLoading
            : isBrowseLoading // ignore: cast_nullable_to_non_nullable
                  as bool,
        error: freezed == error
            ? _value.error
            : error // ignore: cast_nullable_to_non_nullable
                  as String?,
        userJobsTotal: null == userJobsTotal
            ? _value.userJobsTotal
            : userJobsTotal // ignore: cast_nullable_to_non_nullable
                  as int,
        browseJobsTotal: null == browseJobsTotal
            ? _value.browseJobsTotal
            : browseJobsTotal // ignore: cast_nullable_to_non_nullable
                  as int,
        hasMoreUserJobs: null == hasMoreUserJobs
            ? _value.hasMoreUserJobs
            : hasMoreUserJobs // ignore: cast_nullable_to_non_nullable
                  as bool,
        hasMoreBrowseJobs: null == hasMoreBrowseJobs
            ? _value.hasMoreBrowseJobs
            : hasMoreBrowseJobs // ignore: cast_nullable_to_non_nullable
                  as bool,
      ),
    );
  }
}

/// @nodoc

class _$JobStateImpl implements _JobState {
  const _$JobStateImpl({
    final List<Job> userJobs = const [],
    final List<BrowseJob> browseJobs = const [],
    this.selectedJob,
    this.isLoading = false,
    this.isLoadingMore = false,
    this.isBrowseLoading = false,
    this.error,
    this.userJobsTotal = 0,
    this.browseJobsTotal = 0,
    this.hasMoreUserJobs = true,
    this.hasMoreBrowseJobs = true,
  }) : _userJobs = userJobs,
       _browseJobs = browseJobs;

  final List<Job> _userJobs;
  @override
  @JsonKey()
  List<Job> get userJobs {
    if (_userJobs is EqualUnmodifiableListView) return _userJobs;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_userJobs);
  }

  final List<BrowseJob> _browseJobs;
  @override
  @JsonKey()
  List<BrowseJob> get browseJobs {
    if (_browseJobs is EqualUnmodifiableListView) return _browseJobs;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_browseJobs);
  }

  @override
  final Job? selectedJob;
  @override
  @JsonKey()
  final bool isLoading;
  @override
  @JsonKey()
  final bool isLoadingMore;
  @override
  @JsonKey()
  final bool isBrowseLoading;
  @override
  final String? error;
  @override
  @JsonKey()
  final int userJobsTotal;
  @override
  @JsonKey()
  final int browseJobsTotal;
  @override
  @JsonKey()
  final bool hasMoreUserJobs;
  @override
  @JsonKey()
  final bool hasMoreBrowseJobs;

  @override
  String toString() {
    return 'JobState(userJobs: $userJobs, browseJobs: $browseJobs, selectedJob: $selectedJob, isLoading: $isLoading, isLoadingMore: $isLoadingMore, isBrowseLoading: $isBrowseLoading, error: $error, userJobsTotal: $userJobsTotal, browseJobsTotal: $browseJobsTotal, hasMoreUserJobs: $hasMoreUserJobs, hasMoreBrowseJobs: $hasMoreBrowseJobs)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$JobStateImpl &&
            const DeepCollectionEquality().equals(other._userJobs, _userJobs) &&
            const DeepCollectionEquality().equals(
              other._browseJobs,
              _browseJobs,
            ) &&
            (identical(other.selectedJob, selectedJob) ||
                other.selectedJob == selectedJob) &&
            (identical(other.isLoading, isLoading) ||
                other.isLoading == isLoading) &&
            (identical(other.isLoadingMore, isLoadingMore) ||
                other.isLoadingMore == isLoadingMore) &&
            (identical(other.isBrowseLoading, isBrowseLoading) ||
                other.isBrowseLoading == isBrowseLoading) &&
            (identical(other.error, error) || other.error == error) &&
            (identical(other.userJobsTotal, userJobsTotal) ||
                other.userJobsTotal == userJobsTotal) &&
            (identical(other.browseJobsTotal, browseJobsTotal) ||
                other.browseJobsTotal == browseJobsTotal) &&
            (identical(other.hasMoreUserJobs, hasMoreUserJobs) ||
                other.hasMoreUserJobs == hasMoreUserJobs) &&
            (identical(other.hasMoreBrowseJobs, hasMoreBrowseJobs) ||
                other.hasMoreBrowseJobs == hasMoreBrowseJobs));
  }

  @override
  int get hashCode => Object.hash(
    runtimeType,
    const DeepCollectionEquality().hash(_userJobs),
    const DeepCollectionEquality().hash(_browseJobs),
    selectedJob,
    isLoading,
    isLoadingMore,
    isBrowseLoading,
    error,
    userJobsTotal,
    browseJobsTotal,
    hasMoreUserJobs,
    hasMoreBrowseJobs,
  );

  /// Create a copy of JobState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$JobStateImplCopyWith<_$JobStateImpl> get copyWith =>
      __$$JobStateImplCopyWithImpl<_$JobStateImpl>(this, _$identity);
}

abstract class _JobState implements JobState {
  const factory _JobState({
    final List<Job> userJobs,
    final List<BrowseJob> browseJobs,
    final Job? selectedJob,
    final bool isLoading,
    final bool isLoadingMore,
    final bool isBrowseLoading,
    final String? error,
    final int userJobsTotal,
    final int browseJobsTotal,
    final bool hasMoreUserJobs,
    final bool hasMoreBrowseJobs,
  }) = _$JobStateImpl;

  @override
  List<Job> get userJobs;
  @override
  List<BrowseJob> get browseJobs;
  @override
  Job? get selectedJob;
  @override
  bool get isLoading;
  @override
  bool get isLoadingMore;
  @override
  bool get isBrowseLoading;
  @override
  String? get error;
  @override
  int get userJobsTotal;
  @override
  int get browseJobsTotal;
  @override
  bool get hasMoreUserJobs;
  @override
  bool get hasMoreBrowseJobs;

  /// Create a copy of JobState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$JobStateImplCopyWith<_$JobStateImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

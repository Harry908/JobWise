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
mixin _$JobFilterState {
  JobStatus? get status => throw _privateConstructorUsedError;
  JobSource? get source => throw _privateConstructorUsedError;

  /// Create a copy of JobFilterState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $JobFilterStateCopyWith<JobFilterState> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $JobFilterStateCopyWith<$Res> {
  factory $JobFilterStateCopyWith(
    JobFilterState value,
    $Res Function(JobFilterState) then,
  ) = _$JobFilterStateCopyWithImpl<$Res, JobFilterState>;
  @useResult
  $Res call({JobStatus? status, JobSource? source});
}

/// @nodoc
class _$JobFilterStateCopyWithImpl<$Res, $Val extends JobFilterState>
    implements $JobFilterStateCopyWith<$Res> {
  _$JobFilterStateCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of JobFilterState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? status = freezed, Object? source = freezed}) {
    return _then(
      _value.copyWith(
            status: freezed == status
                ? _value.status
                : status // ignore: cast_nullable_to_non_nullable
                      as JobStatus?,
            source: freezed == source
                ? _value.source
                : source // ignore: cast_nullable_to_non_nullable
                      as JobSource?,
          )
          as $Val,
    );
  }
}

/// @nodoc
abstract class _$$JobFilterStateImplCopyWith<$Res>
    implements $JobFilterStateCopyWith<$Res> {
  factory _$$JobFilterStateImplCopyWith(
    _$JobFilterStateImpl value,
    $Res Function(_$JobFilterStateImpl) then,
  ) = __$$JobFilterStateImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({JobStatus? status, JobSource? source});
}

/// @nodoc
class __$$JobFilterStateImplCopyWithImpl<$Res>
    extends _$JobFilterStateCopyWithImpl<$Res, _$JobFilterStateImpl>
    implements _$$JobFilterStateImplCopyWith<$Res> {
  __$$JobFilterStateImplCopyWithImpl(
    _$JobFilterStateImpl _value,
    $Res Function(_$JobFilterStateImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of JobFilterState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({Object? status = freezed, Object? source = freezed}) {
    return _then(
      _$JobFilterStateImpl(
        status: freezed == status
            ? _value.status
            : status // ignore: cast_nullable_to_non_nullable
                  as JobStatus?,
        source: freezed == source
            ? _value.source
            : source // ignore: cast_nullable_to_non_nullable
                  as JobSource?,
      ),
    );
  }
}

/// @nodoc

class _$JobFilterStateImpl implements _JobFilterState {
  const _$JobFilterStateImpl({this.status, this.source});

  @override
  final JobStatus? status;
  @override
  final JobSource? source;

  @override
  String toString() {
    return 'JobFilterState(status: $status, source: $source)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$JobFilterStateImpl &&
            (identical(other.status, status) || other.status == status) &&
            (identical(other.source, source) || other.source == source));
  }

  @override
  int get hashCode => Object.hash(runtimeType, status, source);

  /// Create a copy of JobFilterState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$JobFilterStateImplCopyWith<_$JobFilterStateImpl> get copyWith =>
      __$$JobFilterStateImplCopyWithImpl<_$JobFilterStateImpl>(
        this,
        _$identity,
      );
}

abstract class _JobFilterState implements JobFilterState {
  const factory _JobFilterState({
    final JobStatus? status,
    final JobSource? source,
  }) = _$JobFilterStateImpl;

  @override
  JobStatus? get status;
  @override
  JobSource? get source;

  /// Create a copy of JobFilterState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$JobFilterStateImplCopyWith<_$JobFilterStateImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

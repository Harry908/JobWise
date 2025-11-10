// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'generation_provider.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
  'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models',
);

/// @nodoc
mixin _$GenerationState {
  List<GenerationListItem> get generations =>
      throw _privateConstructorUsedError;
  Generation? get activeGeneration =>
      throw _privateConstructorUsedError; // Currently creating or viewing
  GenerationStatistics? get statistics => throw _privateConstructorUsedError;
  Pagination? get pagination => throw _privateConstructorUsedError;
  List<Template> get templates => throw _privateConstructorUsedError;
  bool get isLoading => throw _privateConstructorUsedError;
  bool get isLoadingMore => throw _privateConstructorUsedError;
  bool get isPolling => throw _privateConstructorUsedError;
  String? get error => throw _privateConstructorUsedError;
  int get total => throw _privateConstructorUsedError;
  bool get hasMore => throw _privateConstructorUsedError;

  /// Create a copy of GenerationState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $GenerationStateCopyWith<GenerationState> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $GenerationStateCopyWith<$Res> {
  factory $GenerationStateCopyWith(
    GenerationState value,
    $Res Function(GenerationState) then,
  ) = _$GenerationStateCopyWithImpl<$Res, GenerationState>;
  @useResult
  $Res call({
    List<GenerationListItem> generations,
    Generation? activeGeneration,
    GenerationStatistics? statistics,
    Pagination? pagination,
    List<Template> templates,
    bool isLoading,
    bool isLoadingMore,
    bool isPolling,
    String? error,
    int total,
    bool hasMore,
  });

  $GenerationCopyWith<$Res>? get activeGeneration;
  $GenerationStatisticsCopyWith<$Res>? get statistics;
  $PaginationCopyWith<$Res>? get pagination;
}

/// @nodoc
class _$GenerationStateCopyWithImpl<$Res, $Val extends GenerationState>
    implements $GenerationStateCopyWith<$Res> {
  _$GenerationStateCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of GenerationState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? generations = null,
    Object? activeGeneration = freezed,
    Object? statistics = freezed,
    Object? pagination = freezed,
    Object? templates = null,
    Object? isLoading = null,
    Object? isLoadingMore = null,
    Object? isPolling = null,
    Object? error = freezed,
    Object? total = null,
    Object? hasMore = null,
  }) {
    return _then(
      _value.copyWith(
            generations: null == generations
                ? _value.generations
                : generations // ignore: cast_nullable_to_non_nullable
                      as List<GenerationListItem>,
            activeGeneration: freezed == activeGeneration
                ? _value.activeGeneration
                : activeGeneration // ignore: cast_nullable_to_non_nullable
                      as Generation?,
            statistics: freezed == statistics
                ? _value.statistics
                : statistics // ignore: cast_nullable_to_non_nullable
                      as GenerationStatistics?,
            pagination: freezed == pagination
                ? _value.pagination
                : pagination // ignore: cast_nullable_to_non_nullable
                      as Pagination?,
            templates: null == templates
                ? _value.templates
                : templates // ignore: cast_nullable_to_non_nullable
                      as List<Template>,
            isLoading: null == isLoading
                ? _value.isLoading
                : isLoading // ignore: cast_nullable_to_non_nullable
                      as bool,
            isLoadingMore: null == isLoadingMore
                ? _value.isLoadingMore
                : isLoadingMore // ignore: cast_nullable_to_non_nullable
                      as bool,
            isPolling: null == isPolling
                ? _value.isPolling
                : isPolling // ignore: cast_nullable_to_non_nullable
                      as bool,
            error: freezed == error
                ? _value.error
                : error // ignore: cast_nullable_to_non_nullable
                      as String?,
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

  /// Create a copy of GenerationState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $GenerationCopyWith<$Res>? get activeGeneration {
    if (_value.activeGeneration == null) {
      return null;
    }

    return $GenerationCopyWith<$Res>(_value.activeGeneration!, (value) {
      return _then(_value.copyWith(activeGeneration: value) as $Val);
    });
  }

  /// Create a copy of GenerationState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $GenerationStatisticsCopyWith<$Res>? get statistics {
    if (_value.statistics == null) {
      return null;
    }

    return $GenerationStatisticsCopyWith<$Res>(_value.statistics!, (value) {
      return _then(_value.copyWith(statistics: value) as $Val);
    });
  }

  /// Create a copy of GenerationState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $PaginationCopyWith<$Res>? get pagination {
    if (_value.pagination == null) {
      return null;
    }

    return $PaginationCopyWith<$Res>(_value.pagination!, (value) {
      return _then(_value.copyWith(pagination: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$GenerationStateImplCopyWith<$Res>
    implements $GenerationStateCopyWith<$Res> {
  factory _$$GenerationStateImplCopyWith(
    _$GenerationStateImpl value,
    $Res Function(_$GenerationStateImpl) then,
  ) = __$$GenerationStateImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({
    List<GenerationListItem> generations,
    Generation? activeGeneration,
    GenerationStatistics? statistics,
    Pagination? pagination,
    List<Template> templates,
    bool isLoading,
    bool isLoadingMore,
    bool isPolling,
    String? error,
    int total,
    bool hasMore,
  });

  @override
  $GenerationCopyWith<$Res>? get activeGeneration;
  @override
  $GenerationStatisticsCopyWith<$Res>? get statistics;
  @override
  $PaginationCopyWith<$Res>? get pagination;
}

/// @nodoc
class __$$GenerationStateImplCopyWithImpl<$Res>
    extends _$GenerationStateCopyWithImpl<$Res, _$GenerationStateImpl>
    implements _$$GenerationStateImplCopyWith<$Res> {
  __$$GenerationStateImplCopyWithImpl(
    _$GenerationStateImpl _value,
    $Res Function(_$GenerationStateImpl) _then,
  ) : super(_value, _then);

  /// Create a copy of GenerationState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? generations = null,
    Object? activeGeneration = freezed,
    Object? statistics = freezed,
    Object? pagination = freezed,
    Object? templates = null,
    Object? isLoading = null,
    Object? isLoadingMore = null,
    Object? isPolling = null,
    Object? error = freezed,
    Object? total = null,
    Object? hasMore = null,
  }) {
    return _then(
      _$GenerationStateImpl(
        generations: null == generations
            ? _value._generations
            : generations // ignore: cast_nullable_to_non_nullable
                  as List<GenerationListItem>,
        activeGeneration: freezed == activeGeneration
            ? _value.activeGeneration
            : activeGeneration // ignore: cast_nullable_to_non_nullable
                  as Generation?,
        statistics: freezed == statistics
            ? _value.statistics
            : statistics // ignore: cast_nullable_to_non_nullable
                  as GenerationStatistics?,
        pagination: freezed == pagination
            ? _value.pagination
            : pagination // ignore: cast_nullable_to_non_nullable
                  as Pagination?,
        templates: null == templates
            ? _value._templates
            : templates // ignore: cast_nullable_to_non_nullable
                  as List<Template>,
        isLoading: null == isLoading
            ? _value.isLoading
            : isLoading // ignore: cast_nullable_to_non_nullable
                  as bool,
        isLoadingMore: null == isLoadingMore
            ? _value.isLoadingMore
            : isLoadingMore // ignore: cast_nullable_to_non_nullable
                  as bool,
        isPolling: null == isPolling
            ? _value.isPolling
            : isPolling // ignore: cast_nullable_to_non_nullable
                  as bool,
        error: freezed == error
            ? _value.error
            : error // ignore: cast_nullable_to_non_nullable
                  as String?,
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

class _$GenerationStateImpl implements _GenerationState {
  const _$GenerationStateImpl({
    final List<GenerationListItem> generations = const [],
    this.activeGeneration,
    this.statistics,
    this.pagination,
    final List<Template> templates = const [],
    this.isLoading = false,
    this.isLoadingMore = false,
    this.isPolling = false,
    this.error,
    this.total = 0,
    this.hasMore = true,
  }) : _generations = generations,
       _templates = templates;

  final List<GenerationListItem> _generations;
  @override
  @JsonKey()
  List<GenerationListItem> get generations {
    if (_generations is EqualUnmodifiableListView) return _generations;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_generations);
  }

  @override
  final Generation? activeGeneration;
  // Currently creating or viewing
  @override
  final GenerationStatistics? statistics;
  @override
  final Pagination? pagination;
  final List<Template> _templates;
  @override
  @JsonKey()
  List<Template> get templates {
    if (_templates is EqualUnmodifiableListView) return _templates;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_templates);
  }

  @override
  @JsonKey()
  final bool isLoading;
  @override
  @JsonKey()
  final bool isLoadingMore;
  @override
  @JsonKey()
  final bool isPolling;
  @override
  final String? error;
  @override
  @JsonKey()
  final int total;
  @override
  @JsonKey()
  final bool hasMore;

  @override
  String toString() {
    return 'GenerationState(generations: $generations, activeGeneration: $activeGeneration, statistics: $statistics, pagination: $pagination, templates: $templates, isLoading: $isLoading, isLoadingMore: $isLoadingMore, isPolling: $isPolling, error: $error, total: $total, hasMore: $hasMore)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$GenerationStateImpl &&
            const DeepCollectionEquality().equals(
              other._generations,
              _generations,
            ) &&
            (identical(other.activeGeneration, activeGeneration) ||
                other.activeGeneration == activeGeneration) &&
            (identical(other.statistics, statistics) ||
                other.statistics == statistics) &&
            (identical(other.pagination, pagination) ||
                other.pagination == pagination) &&
            const DeepCollectionEquality().equals(
              other._templates,
              _templates,
            ) &&
            (identical(other.isLoading, isLoading) ||
                other.isLoading == isLoading) &&
            (identical(other.isLoadingMore, isLoadingMore) ||
                other.isLoadingMore == isLoadingMore) &&
            (identical(other.isPolling, isPolling) ||
                other.isPolling == isPolling) &&
            (identical(other.error, error) || other.error == error) &&
            (identical(other.total, total) || other.total == total) &&
            (identical(other.hasMore, hasMore) || other.hasMore == hasMore));
  }

  @override
  int get hashCode => Object.hash(
    runtimeType,
    const DeepCollectionEquality().hash(_generations),
    activeGeneration,
    statistics,
    pagination,
    const DeepCollectionEquality().hash(_templates),
    isLoading,
    isLoadingMore,
    isPolling,
    error,
    total,
    hasMore,
  );

  /// Create a copy of GenerationState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$GenerationStateImplCopyWith<_$GenerationStateImpl> get copyWith =>
      __$$GenerationStateImplCopyWithImpl<_$GenerationStateImpl>(
        this,
        _$identity,
      );
}

abstract class _GenerationState implements GenerationState {
  const factory _GenerationState({
    final List<GenerationListItem> generations,
    final Generation? activeGeneration,
    final GenerationStatistics? statistics,
    final Pagination? pagination,
    final List<Template> templates,
    final bool isLoading,
    final bool isLoadingMore,
    final bool isPolling,
    final String? error,
    final int total,
    final bool hasMore,
  }) = _$GenerationStateImpl;

  @override
  List<GenerationListItem> get generations;
  @override
  Generation? get activeGeneration; // Currently creating or viewing
  @override
  GenerationStatistics? get statistics;
  @override
  Pagination? get pagination;
  @override
  List<Template> get templates;
  @override
  bool get isLoading;
  @override
  bool get isLoadingMore;
  @override
  bool get isPolling;
  @override
  String? get error;
  @override
  int get total;
  @override
  bool get hasMore;

  /// Create a copy of GenerationState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$GenerationStateImplCopyWith<_$GenerationStateImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

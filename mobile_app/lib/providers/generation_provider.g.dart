// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'generation_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

String _$generationTemplatesHash() =>
    r'b681b8cf05416e274be96009d332705ce8282f42';

/// See also [generationTemplates].
@ProviderFor(generationTemplates)
final generationTemplatesProvider =
    AutoDisposeFutureProvider<List<Template>>.internal(
      generationTemplates,
      name: r'generationTemplatesProvider',
      debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
          ? null
          : _$generationTemplatesHash,
      dependencies: null,
      allTransitiveDependencies: null,
    );

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef GenerationTemplatesRef = AutoDisposeFutureProviderRef<List<Template>>;
String _$generationHistoryHash() => r'445da115f6c1b0b52923d9ae55f8a2cb76fa1810';

/// Copied from Dart SDK
class _SystemHash {
  _SystemHash._();

  static int combine(int hash, int value) {
    // ignore: parameter_assignments
    hash = 0x1fffffff & (hash + value);
    // ignore: parameter_assignments
    hash = 0x1fffffff & (hash + ((0x0007ffff & hash) << 10));
    return hash ^ (hash >> 6);
  }

  static int finish(int hash) {
    // ignore: parameter_assignments
    hash = 0x1fffffff & (hash + ((0x03ffffff & hash) << 3));
    // ignore: parameter_assignments
    hash = hash ^ (hash >> 11);
    return 0x1fffffff & (hash + ((0x00003fff & hash) << 15));
  }
}

/// See also [generationHistory].
@ProviderFor(generationHistory)
const generationHistoryProvider = GenerationHistoryFamily();

/// See also [generationHistory].
class GenerationHistoryFamily
    extends
        Family<
          AsyncValue<
            (List<GenerationListItem>, Pagination, GenerationStatistics)
          >
        > {
  /// See also [generationHistory].
  const GenerationHistoryFamily();

  /// See also [generationHistory].
  GenerationHistoryProvider call({
    String? jobId,
    GenerationStatus? status,
    DocumentType? documentType,
    int limit = 20,
    int offset = 0,
  }) {
    return GenerationHistoryProvider(
      jobId: jobId,
      status: status,
      documentType: documentType,
      limit: limit,
      offset: offset,
    );
  }

  @override
  GenerationHistoryProvider getProviderOverride(
    covariant GenerationHistoryProvider provider,
  ) {
    return call(
      jobId: provider.jobId,
      status: provider.status,
      documentType: provider.documentType,
      limit: provider.limit,
      offset: provider.offset,
    );
  }

  static const Iterable<ProviderOrFamily>? _dependencies = null;

  @override
  Iterable<ProviderOrFamily>? get dependencies => _dependencies;

  static const Iterable<ProviderOrFamily>? _allTransitiveDependencies = null;

  @override
  Iterable<ProviderOrFamily>? get allTransitiveDependencies =>
      _allTransitiveDependencies;

  @override
  String? get name => r'generationHistoryProvider';
}

/// See also [generationHistory].
class GenerationHistoryProvider
    extends
        AutoDisposeFutureProvider<
          (List<GenerationListItem>, Pagination, GenerationStatistics)
        > {
  /// See also [generationHistory].
  GenerationHistoryProvider({
    String? jobId,
    GenerationStatus? status,
    DocumentType? documentType,
    int limit = 20,
    int offset = 0,
  }) : this._internal(
         (ref) => generationHistory(
           ref as GenerationHistoryRef,
           jobId: jobId,
           status: status,
           documentType: documentType,
           limit: limit,
           offset: offset,
         ),
         from: generationHistoryProvider,
         name: r'generationHistoryProvider',
         debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
             ? null
             : _$generationHistoryHash,
         dependencies: GenerationHistoryFamily._dependencies,
         allTransitiveDependencies:
             GenerationHistoryFamily._allTransitiveDependencies,
         jobId: jobId,
         status: status,
         documentType: documentType,
         limit: limit,
         offset: offset,
       );

  GenerationHistoryProvider._internal(
    super._createNotifier, {
    required super.name,
    required super.dependencies,
    required super.allTransitiveDependencies,
    required super.debugGetCreateSourceHash,
    required super.from,
    required this.jobId,
    required this.status,
    required this.documentType,
    required this.limit,
    required this.offset,
  }) : super.internal();

  final String? jobId;
  final GenerationStatus? status;
  final DocumentType? documentType;
  final int limit;
  final int offset;

  @override
  Override overrideWith(
    FutureOr<(List<GenerationListItem>, Pagination, GenerationStatistics)>
    Function(GenerationHistoryRef provider)
    create,
  ) {
    return ProviderOverride(
      origin: this,
      override: GenerationHistoryProvider._internal(
        (ref) => create(ref as GenerationHistoryRef),
        from: from,
        name: null,
        dependencies: null,
        allTransitiveDependencies: null,
        debugGetCreateSourceHash: null,
        jobId: jobId,
        status: status,
        documentType: documentType,
        limit: limit,
        offset: offset,
      ),
    );
  }

  @override
  AutoDisposeFutureProviderElement<
    (List<GenerationListItem>, Pagination, GenerationStatistics)
  >
  createElement() {
    return _GenerationHistoryProviderElement(this);
  }

  @override
  bool operator ==(Object other) {
    return other is GenerationHistoryProvider &&
        other.jobId == jobId &&
        other.status == status &&
        other.documentType == documentType &&
        other.limit == limit &&
        other.offset == offset;
  }

  @override
  int get hashCode {
    var hash = _SystemHash.combine(0, runtimeType.hashCode);
    hash = _SystemHash.combine(hash, jobId.hashCode);
    hash = _SystemHash.combine(hash, status.hashCode);
    hash = _SystemHash.combine(hash, documentType.hashCode);
    hash = _SystemHash.combine(hash, limit.hashCode);
    hash = _SystemHash.combine(hash, offset.hashCode);

    return _SystemHash.finish(hash);
  }
}

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
mixin GenerationHistoryRef
    on
        AutoDisposeFutureProviderRef<
          (List<GenerationListItem>, Pagination, GenerationStatistics)
        > {
  /// The parameter `jobId` of this provider.
  String? get jobId;

  /// The parameter `status` of this provider.
  GenerationStatus? get status;

  /// The parameter `documentType` of this provider.
  DocumentType? get documentType;

  /// The parameter `limit` of this provider.
  int get limit;

  /// The parameter `offset` of this provider.
  int get offset;
}

class _GenerationHistoryProviderElement
    extends
        AutoDisposeFutureProviderElement<
          (List<GenerationListItem>, Pagination, GenerationStatistics)
        >
    with GenerationHistoryRef {
  _GenerationHistoryProviderElement(super.provider);

  @override
  String? get jobId => (origin as GenerationHistoryProvider).jobId;
  @override
  GenerationStatus? get status => (origin as GenerationHistoryProvider).status;
  @override
  DocumentType? get documentType =>
      (origin as GenerationHistoryProvider).documentType;
  @override
  int get limit => (origin as GenerationHistoryProvider).limit;
  @override
  int get offset => (origin as GenerationHistoryProvider).offset;
}

String _$generationActionsHash() => r'23fabc00078c332d843d1b311c515c83953a9b3a';

/// See also [GenerationActions].
@ProviderFor(GenerationActions)
final generationActionsProvider =
    AutoDisposeNotifierProvider<GenerationActions, void>.internal(
      GenerationActions.new,
      name: r'generationActionsProvider',
      debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
          ? null
          : _$generationActionsHash,
      dependencies: null,
      allTransitiveDependencies: null,
    );

typedef _$GenerationActions = AutoDisposeNotifier<void>;
String _$activeGenerationHash() => r'daa3ba19abab105da6cee2a73f6f5e3ddae16719';

abstract class _$ActiveGeneration
    extends BuildlessAutoDisposeAsyncNotifier<Generation> {
  late final String generationId;

  FutureOr<Generation> build(String generationId);
}

/// See also [ActiveGeneration].
@ProviderFor(ActiveGeneration)
const activeGenerationProvider = ActiveGenerationFamily();

/// See also [ActiveGeneration].
class ActiveGenerationFamily extends Family<AsyncValue<Generation>> {
  /// See also [ActiveGeneration].
  const ActiveGenerationFamily();

  /// See also [ActiveGeneration].
  ActiveGenerationProvider call(String generationId) {
    return ActiveGenerationProvider(generationId);
  }

  @override
  ActiveGenerationProvider getProviderOverride(
    covariant ActiveGenerationProvider provider,
  ) {
    return call(provider.generationId);
  }

  static const Iterable<ProviderOrFamily>? _dependencies = null;

  @override
  Iterable<ProviderOrFamily>? get dependencies => _dependencies;

  static const Iterable<ProviderOrFamily>? _allTransitiveDependencies = null;

  @override
  Iterable<ProviderOrFamily>? get allTransitiveDependencies =>
      _allTransitiveDependencies;

  @override
  String? get name => r'activeGenerationProvider';
}

/// See also [ActiveGeneration].
class ActiveGenerationProvider
    extends AutoDisposeAsyncNotifierProviderImpl<ActiveGeneration, Generation> {
  /// See also [ActiveGeneration].
  ActiveGenerationProvider(String generationId)
    : this._internal(
        () => ActiveGeneration()..generationId = generationId,
        from: activeGenerationProvider,
        name: r'activeGenerationProvider',
        debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
            ? null
            : _$activeGenerationHash,
        dependencies: ActiveGenerationFamily._dependencies,
        allTransitiveDependencies:
            ActiveGenerationFamily._allTransitiveDependencies,
        generationId: generationId,
      );

  ActiveGenerationProvider._internal(
    super._createNotifier, {
    required super.name,
    required super.dependencies,
    required super.allTransitiveDependencies,
    required super.debugGetCreateSourceHash,
    required super.from,
    required this.generationId,
  }) : super.internal();

  final String generationId;

  @override
  FutureOr<Generation> runNotifierBuild(covariant ActiveGeneration notifier) {
    return notifier.build(generationId);
  }

  @override
  Override overrideWith(ActiveGeneration Function() create) {
    return ProviderOverride(
      origin: this,
      override: ActiveGenerationProvider._internal(
        () => create()..generationId = generationId,
        from: from,
        name: null,
        dependencies: null,
        allTransitiveDependencies: null,
        debugGetCreateSourceHash: null,
        generationId: generationId,
      ),
    );
  }

  @override
  AutoDisposeAsyncNotifierProviderElement<ActiveGeneration, Generation>
  createElement() {
    return _ActiveGenerationProviderElement(this);
  }

  @override
  bool operator ==(Object other) {
    return other is ActiveGenerationProvider &&
        other.generationId == generationId;
  }

  @override
  int get hashCode {
    var hash = _SystemHash.combine(0, runtimeType.hashCode);
    hash = _SystemHash.combine(hash, generationId.hashCode);

    return _SystemHash.finish(hash);
  }
}

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
mixin ActiveGenerationRef on AutoDisposeAsyncNotifierProviderRef<Generation> {
  /// The parameter `generationId` of this provider.
  String get generationId;
}

class _ActiveGenerationProviderElement
    extends
        AutoDisposeAsyncNotifierProviderElement<ActiveGeneration, Generation>
    with ActiveGenerationRef {
  _ActiveGenerationProviderElement(super.provider);

  @override
  String get generationId => (origin as ActiveGenerationProvider).generationId;
}

// ignore_for_file: type=lint
// ignore_for_file: subtype_of_sealed_class, invalid_use_of_internal_member, invalid_use_of_visible_for_testing_member, deprecated_member_use_from_same_package

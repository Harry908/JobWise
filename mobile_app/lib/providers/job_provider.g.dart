// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'job_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

String _$browseJobsHash() => r'e42dc8988b8670f7e03f6ef10706776c83ed171c';

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

/// See also [browseJobs].
@ProviderFor(browseJobs)
const browseJobsProvider = BrowseJobsFamily();

/// See also [browseJobs].
class BrowseJobsFamily extends Family<AsyncValue<List<BrowseJob>>> {
  /// See also [browseJobs].
  const BrowseJobsFamily();

  /// See also [browseJobs].
  BrowseJobsProvider call({
    String? query,
    String? location,
    bool remote = false,
  }) {
    return BrowseJobsProvider(query: query, location: location, remote: remote);
  }

  @override
  BrowseJobsProvider getProviderOverride(
    covariant BrowseJobsProvider provider,
  ) {
    return call(
      query: provider.query,
      location: provider.location,
      remote: provider.remote,
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
  String? get name => r'browseJobsProvider';
}

/// See also [browseJobs].
class BrowseJobsProvider extends AutoDisposeFutureProvider<List<BrowseJob>> {
  /// See also [browseJobs].
  BrowseJobsProvider({String? query, String? location, bool remote = false})
    : this._internal(
        (ref) => browseJobs(
          ref as BrowseJobsRef,
          query: query,
          location: location,
          remote: remote,
        ),
        from: browseJobsProvider,
        name: r'browseJobsProvider',
        debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
            ? null
            : _$browseJobsHash,
        dependencies: BrowseJobsFamily._dependencies,
        allTransitiveDependencies: BrowseJobsFamily._allTransitiveDependencies,
        query: query,
        location: location,
        remote: remote,
      );

  BrowseJobsProvider._internal(
    super._createNotifier, {
    required super.name,
    required super.dependencies,
    required super.allTransitiveDependencies,
    required super.debugGetCreateSourceHash,
    required super.from,
    required this.query,
    required this.location,
    required this.remote,
  }) : super.internal();

  final String? query;
  final String? location;
  final bool remote;

  @override
  Override overrideWith(
    FutureOr<List<BrowseJob>> Function(BrowseJobsRef provider) create,
  ) {
    return ProviderOverride(
      origin: this,
      override: BrowseJobsProvider._internal(
        (ref) => create(ref as BrowseJobsRef),
        from: from,
        name: null,
        dependencies: null,
        allTransitiveDependencies: null,
        debugGetCreateSourceHash: null,
        query: query,
        location: location,
        remote: remote,
      ),
    );
  }

  @override
  AutoDisposeFutureProviderElement<List<BrowseJob>> createElement() {
    return _BrowseJobsProviderElement(this);
  }

  @override
  bool operator ==(Object other) {
    return other is BrowseJobsProvider &&
        other.query == query &&
        other.location == location &&
        other.remote == remote;
  }

  @override
  int get hashCode {
    var hash = _SystemHash.combine(0, runtimeType.hashCode);
    hash = _SystemHash.combine(hash, query.hashCode);
    hash = _SystemHash.combine(hash, location.hashCode);
    hash = _SystemHash.combine(hash, remote.hashCode);

    return _SystemHash.finish(hash);
  }
}

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
mixin BrowseJobsRef on AutoDisposeFutureProviderRef<List<BrowseJob>> {
  /// The parameter `query` of this provider.
  String? get query;

  /// The parameter `location` of this provider.
  String? get location;

  /// The parameter `remote` of this provider.
  bool get remote;
}

class _BrowseJobsProviderElement
    extends AutoDisposeFutureProviderElement<List<BrowseJob>>
    with BrowseJobsRef {
  _BrowseJobsProviderElement(super.provider);

  @override
  String? get query => (origin as BrowseJobsProvider).query;
  @override
  String? get location => (origin as BrowseJobsProvider).location;
  @override
  bool get remote => (origin as BrowseJobsProvider).remote;
}

String _$selectedJobHash() => r'bdbea56ec57df701af2383da082c77e3c23828ae';

/// See also [selectedJob].
@ProviderFor(selectedJob)
const selectedJobProvider = SelectedJobFamily();

/// See also [selectedJob].
class SelectedJobFamily extends Family<AsyncValue<Job?>> {
  /// See also [selectedJob].
  const SelectedJobFamily();

  /// See also [selectedJob].
  SelectedJobProvider call(String jobId) {
    return SelectedJobProvider(jobId);
  }

  @override
  SelectedJobProvider getProviderOverride(
    covariant SelectedJobProvider provider,
  ) {
    return call(provider.jobId);
  }

  static const Iterable<ProviderOrFamily>? _dependencies = null;

  @override
  Iterable<ProviderOrFamily>? get dependencies => _dependencies;

  static const Iterable<ProviderOrFamily>? _allTransitiveDependencies = null;

  @override
  Iterable<ProviderOrFamily>? get allTransitiveDependencies =>
      _allTransitiveDependencies;

  @override
  String? get name => r'selectedJobProvider';
}

/// See also [selectedJob].
class SelectedJobProvider extends AutoDisposeFutureProvider<Job?> {
  /// See also [selectedJob].
  SelectedJobProvider(String jobId)
    : this._internal(
        (ref) => selectedJob(ref as SelectedJobRef, jobId),
        from: selectedJobProvider,
        name: r'selectedJobProvider',
        debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
            ? null
            : _$selectedJobHash,
        dependencies: SelectedJobFamily._dependencies,
        allTransitiveDependencies: SelectedJobFamily._allTransitiveDependencies,
        jobId: jobId,
      );

  SelectedJobProvider._internal(
    super._createNotifier, {
    required super.name,
    required super.dependencies,
    required super.allTransitiveDependencies,
    required super.debugGetCreateSourceHash,
    required super.from,
    required this.jobId,
  }) : super.internal();

  final String jobId;

  @override
  Override overrideWith(
    FutureOr<Job?> Function(SelectedJobRef provider) create,
  ) {
    return ProviderOverride(
      origin: this,
      override: SelectedJobProvider._internal(
        (ref) => create(ref as SelectedJobRef),
        from: from,
        name: null,
        dependencies: null,
        allTransitiveDependencies: null,
        debugGetCreateSourceHash: null,
        jobId: jobId,
      ),
    );
  }

  @override
  AutoDisposeFutureProviderElement<Job?> createElement() {
    return _SelectedJobProviderElement(this);
  }

  @override
  bool operator ==(Object other) {
    return other is SelectedJobProvider && other.jobId == jobId;
  }

  @override
  int get hashCode {
    var hash = _SystemHash.combine(0, runtimeType.hashCode);
    hash = _SystemHash.combine(hash, jobId.hashCode);

    return _SystemHash.finish(hash);
  }
}

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
mixin SelectedJobRef on AutoDisposeFutureProviderRef<Job?> {
  /// The parameter `jobId` of this provider.
  String get jobId;
}

class _SelectedJobProviderElement extends AutoDisposeFutureProviderElement<Job?>
    with SelectedJobRef {
  _SelectedJobProviderElement(super.provider);

  @override
  String get jobId => (origin as SelectedJobProvider).jobId;
}

String _$filteredUserJobsHash() => r'0e048560e9ed575caecfc3b04b8b695db0bfa1ea';

/// See also [filteredUserJobs].
@ProviderFor(filteredUserJobs)
final filteredUserJobsProvider = AutoDisposeProvider<List<Job>>.internal(
  filteredUserJobs,
  name: r'filteredUserJobsProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$filteredUserJobsHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef FilteredUserJobsRef = AutoDisposeProviderRef<List<Job>>;
String _$userJobsHash() => r'be01e6e2cac3485537241cce9a4d9c15d16dadf5';

/// See also [UserJobs].
@ProviderFor(UserJobs)
final userJobsProvider =
    AutoDisposeAsyncNotifierProvider<UserJobs, List<Job>>.internal(
      UserJobs.new,
      name: r'userJobsProvider',
      debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
          ? null
          : _$userJobsHash,
      dependencies: null,
      allTransitiveDependencies: null,
    );

typedef _$UserJobs = AutoDisposeAsyncNotifier<List<Job>>;
String _$jobActionsHash() => r'44ed47d707a3beaaea2e8e6b4c79b08552ad010b';

/// See also [JobActions].
@ProviderFor(JobActions)
final jobActionsProvider =
    AutoDisposeAsyncNotifierProvider<JobActions, void>.internal(
      JobActions.new,
      name: r'jobActionsProvider',
      debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
          ? null
          : _$jobActionsHash,
      dependencies: null,
      allTransitiveDependencies: null,
    );

typedef _$JobActions = AutoDisposeAsyncNotifier<void>;
String _$jobFiltersHash() => r'd9d8d7412bf48cbdc0917e4b88727eadfc9393fa';

/// See also [JobFilters].
@ProviderFor(JobFilters)
final jobFiltersProvider =
    AutoDisposeNotifierProvider<JobFilters, JobFilterState>.internal(
      JobFilters.new,
      name: r'jobFiltersProvider',
      debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
          ? null
          : _$jobFiltersHash,
      dependencies: null,
      allTransitiveDependencies: null,
    );

typedef _$JobFilters = AutoDisposeNotifier<JobFilterState>;
// ignore_for_file: type=lint
// ignore_for_file: subtype_of_sealed_class, invalid_use_of_internal_member, invalid_use_of_visible_for_testing_member, deprecated_member_use_from_same_package

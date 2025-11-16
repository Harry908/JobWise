import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../models/job.dart';
import '../providers/job_provider.dart';
import '../widgets/job_card.dart';

/// Screen for displaying user's saved jobs
class JobListScreen extends ConsumerWidget {
  const JobListScreen({super.key});

  Future<void> _refreshJobs(WidgetRef ref) async {
    ref.invalidate(userJobsProvider);
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final jobsAsync = ref.watch(userJobsProvider);
    final filteredJobs = ref.watch(filteredUserJobsProvider);
    final filters = ref.watch(jobFiltersProvider);
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Jobs'),
        actions: [
          IconButton(
            icon: const Icon(Icons.filter_list),
            tooltip: 'Filter Jobs',
            onPressed: () => _showFilterDialog(context, ref),
          ),
        ],
      ),
      body: Column(
        children: [
          // Active Filters Display
          if (filters.status != null || filters.source != null)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              color: theme.colorScheme.surfaceContainerHighest,
              child: Row(
                children: [
                  const Icon(Icons.filter_alt, size: 16),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Wrap(
                      spacing: 8,
                      runSpacing: 4,
                      children: [
                        if (filters.status != null)
                          Chip(
                            label: Text(_formatStatus(filters.status!)),
                            onDeleted: () => ref
                                .read(jobFiltersProvider.notifier)
                                .setStatus(null),
                          ),
                        if (filters.source != null)
                          Chip(
                            label: Text(_formatSource(filters.source!)),
                            onDeleted: () => ref
                                .read(jobFiltersProvider.notifier)
                                .setSource(null),
                          ),
                      ],
                    ),
                  ),
                  TextButton(
                    onPressed: () =>
                        ref.read(jobFiltersProvider.notifier).clear(),
                    child: const Text('Clear All'),
                  ),
                ],
              ),
            ),

          // Results Count
          jobsAsync.maybeWhen(
            data: (jobs) => Padding(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 0),
              child: Row(
                children: [
                  Text(
                    '${filteredJobs.length} of ${jobs.length} jobs shown',
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurface.withAlpha(178),
                    ),
                  ),
                ],
              ),
            ),
            orElse: () => const SizedBox.shrink(),
          ),

          // Job List
          Expanded(
            child: jobsAsync.when(
              data: (jobs) => _buildJobList(context, ref, jobs, filteredJobs),
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (err, stack) => _buildError(context, ref, err),
            ),
          ),
        ],
      ),
      floatingActionButton: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          FloatingActionButton(
            heroTag: 'paste_job',
            onPressed: () => context.push('/jobs/paste'),
            tooltip: 'Paste Job Description',
            child: const Icon(Icons.edit),
          ),
          const SizedBox(height: 12),
          FloatingActionButton.extended(
            heroTag: 'browse_jobs',
            onPressed: () => context.push('/jobs/browse'),
            icon: const Icon(Icons.search),
            label: const Text('Browse Jobs'),
          ),
        ],
      ),
    );
  }

  Widget _buildJobList(
      BuildContext context, WidgetRef ref, List<Job> allJobs, List<Job> filteredJobs) {
    if (allJobs.isEmpty) {
      return _buildEmptyState(context);
    }

    if (filteredJobs.isEmpty) {
      return _buildNoResultsState(context, ref);
    }

    return RefreshIndicator(
      onRefresh: () => _refreshJobs(ref),
      child: ListView.builder(
        padding: const EdgeInsets.all(8),
        itemCount: filteredJobs.length,
        itemBuilder: (context, index) {
          final job = filteredJobs[index];
          return JobCard(
            job: job,
            onTap: () => context.push('/jobs/${job.id}'),
          );
        },
      ),
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.work_outline,
              size: 80,
              color: Theme.of(context).colorScheme.secondary.withAlpha(128),
            ),
            const SizedBox(height: 24),
            Text(
              'No saved jobs yet',
              style: Theme.of(context).textTheme.headlineSmall,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 12),
            Text(
              'Start by pasting a job description or browsing available jobs',
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                    color:
                        Theme.of(context).colorScheme.onSurface.withAlpha(153),
                  ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 32),
            Wrap(
              spacing: 12,
              runSpacing: 12,
              alignment: WrapAlignment.center,
              children: [
                FilledButton.icon(
                  onPressed: () => context.push('/jobs/paste'),
                  icon: const Icon(Icons.edit),
                  label: const Text('Paste Job'),
                ),
                FilledButton.tonalIcon(
                  onPressed: () => context.push('/jobs/browse'),
                  icon: const Icon(Icons.search),
                  label: const Text('Browse Jobs'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNoResultsState(BuildContext context, WidgetRef ref) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.filter_alt_off_outlined,
              size: 80,
              color: Theme.of(context).colorScheme.secondary.withAlpha(128),
            ),
            const SizedBox(height: 24),
            Text(
              'No jobs match your filters',
              style: Theme.of(context).textTheme.headlineSmall,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 32),
            FilledButton.icon(
              onPressed: () => ref.read(jobFiltersProvider.notifier).clear(),
              icon: const Icon(Icons.clear_all),
              label: const Text('Clear Filters'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildError(BuildContext context, WidgetRef ref, Object err) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 64,
              color: Theme.of(context).colorScheme.error,
            ),
            const SizedBox(height: 16),
            Text(
              'Error loading jobs',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Text(
              err.toString(),
              style: Theme.of(context).textTheme.bodyMedium,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            FilledButton.icon(
              onPressed: () => _refreshJobs(ref),
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
            ),
          ],
        ),
      ),
    );
  }

  void _showFilterDialog(BuildContext context, WidgetRef ref) {
    final currentFilters = ref.read(jobFiltersProvider);

    showDialog(
      context: context,
      builder: (context) {
        // Use a local state provider for the dialog to avoid rebuilding the whole screen on selection
        return _FilterDialog(initialFilters: currentFilters);
      },
    );
  }

  String _formatStatus(JobStatus status) {
    switch (status) {
      case JobStatus.active:
        return 'Active';
      case JobStatus.archived:
        return 'Archived';
      case JobStatus.draft:
        return 'Draft';
    }
  }

  String _formatSource(JobSource source) {
    switch (source) {
      case JobSource.userCreated:
        return 'User Created';
      case JobSource.indeed:
        return 'Indeed';
      case JobSource.linkedin:
        return 'LinkedIn';
      case JobSource.glassdoor:
        return 'Glassdoor';
      case JobSource.mock:
        return 'Mock';
      case JobSource.imported:
        return 'Imported';
      case JobSource.urlImport:
        return 'URL Import';
    }
  }
}

/// A stateful widget to manage the temporary state of the filter dialog
class _FilterDialog extends ConsumerStatefulWidget {
  final JobFilterState initialFilters;
  const _FilterDialog({required this.initialFilters});

  @override
  ConsumerState<_FilterDialog> createState() => _FilterDialogState();
}

class _FilterDialogState extends ConsumerState<_FilterDialog> {
  late JobStatus? _tempStatus;
  late JobSource? _tempSource;

  @override
  void initState() {
    super.initState();
    _tempStatus = widget.initialFilters.status;
    _tempSource = widget.initialFilters.source;
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Filter Jobs'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Status Filter
            Text(
              'Status',
              style: Theme.of(context).textTheme.titleSmall,
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              children: JobStatus.values.map((status) {
                return FilterChip(
                  label: Text(JobListScreen(key: UniqueKey())._formatStatus(status)),
                  selected: _tempStatus == status,
                  onSelected: (selected) {
                    setState(() {
                      _tempStatus = selected ? status : null;
                    });
                  },
                );
              }).toList(),
            ),
            const SizedBox(height: 16),

            // Source Filter
            Text(
              'Source',
              style: Theme.of(context).textTheme.titleSmall,
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: JobSource.values.map((source) {
                return FilterChip(
                  label: Text(JobListScreen(key: UniqueKey())._formatSource(source)),
                  selected: _tempSource == source,
                  onSelected: (selected) {
                    setState(() {
                      _tempSource = selected ? source : null;
                    });
                  },
                );
              }).toList(),
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Cancel'),
        ),
        FilledButton(
          onPressed: () {
            ref.read(jobFiltersProvider.notifier).setStatus(_tempStatus);
            ref.read(jobFiltersProvider.notifier).setSource(_tempSource);
            Navigator.pop(context);
          },
          child: const Text('Apply'),
        ),
      ],
    );
  }
}

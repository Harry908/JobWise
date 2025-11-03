import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../models/job.dart';
import '../providers/job_provider.dart';
import '../widgets/job_card.dart';

/// Screen for displaying user's saved jobs
class JobListScreen extends ConsumerStatefulWidget {
  const JobListScreen({super.key});

  @override
  ConsumerState<JobListScreen> createState() => _JobListScreenState();
}

class _JobListScreenState extends ConsumerState<JobListScreen> {
  final _scrollController = ScrollController();
  JobStatus? _selectedStatus;
  JobSource? _selectedSource;

  @override
  void initState() {
    super.initState();
    // Load user jobs on screen load
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(jobProvider.notifier).loadUserJobs(refresh: true);
    });

    // Setup infinite scroll
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.pixels >=
        _scrollController.position.maxScrollExtent * 0.8) {
      final state = ref.read(jobProvider);
      if (!state.isLoadingMore && state.hasMoreUserJobs) {
        ref.read(jobProvider.notifier).loadMoreUserJobs(
              status: _selectedStatus,
              source: _selectedSource,
            );
      }
    }
  }

  void _applyFilters() {
    ref.read(jobProvider.notifier).loadUserJobs(
          status: _selectedStatus,
          source: _selectedSource,
          refresh: true,
        );
  }

  Future<void> _refreshJobs() async {
    await ref.read(jobProvider.notifier).loadUserJobs(
          status: _selectedStatus,
          source: _selectedSource,
          refresh: true,
        );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(jobProvider);
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Jobs'),
        actions: [
          PopupMenuButton<String>(
            icon: const Icon(Icons.filter_list),
            tooltip: 'Filter Jobs',
            onSelected: (value) {
              if (value == 'filter') {
                _showFilterDialog();
              }
            },
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'filter',
                child: Row(
                  children: [
                    Icon(Icons.filter_alt),
                    SizedBox(width: 8),
                    Text('Filter'),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
      body: Column(
        children: [
          // Active Filters Display
          if (_selectedStatus != null || _selectedSource != null)
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
                      children: [
                        if (_selectedStatus != null)
                          Chip(
                            label: Text(_formatStatus(_selectedStatus!)),
                            onDeleted: () {
                              setState(() => _selectedStatus = null);
                              _applyFilters();
                            },
                            deleteIconColor: theme.colorScheme.onSurfaceVariant,
                          ),
                        if (_selectedSource != null)
                          Chip(
                            label: Text(_formatSource(_selectedSource!)),
                            onDeleted: () {
                              setState(() => _selectedSource = null);
                              _applyFilters();
                            },
                            deleteIconColor: theme.colorScheme.onSurfaceVariant,
                          ),
                      ],
                    ),
                  ),
                  TextButton(
                    onPressed: () {
                      setState(() {
                        _selectedStatus = null;
                        _selectedSource = null;
                      });
                      _applyFilters();
                    },
                    child: const Text('Clear All'),
                  ),
                ],
              ),
            ),

          // Results Count
          if (!state.isLoading && state.userJobs.isNotEmpty)
            Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Text(
                    '${state.userJobsTotal} jobs saved',
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurface.withOpacity(0.7),
                    ),
                  ),
                ],
              ),
            ),

          // Job List
          Expanded(
            child: _buildJobList(state),
          ),
        ],
      ),
      floatingActionButton: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          FloatingActionButton(
            heroTag: 'paste_job',
            onPressed: () {
              context.push('/jobs/paste');
            },
            tooltip: 'Paste Job Description',
            child: const Icon(Icons.edit),
          ),
          const SizedBox(height: 12),
          FloatingActionButton.extended(
            heroTag: 'browse_jobs',
            onPressed: () {
              context.push('/jobs/browse');
            },
            icon: const Icon(Icons.search),
            label: const Text('Browse Jobs'),
          ),
        ],
      ),
    );
  }

  Widget _buildJobList(JobState state) {
    // Loading State (initial)
    if (state.isLoading && state.userJobs.isEmpty) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    // Empty State
    if (state.userJobs.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.work_outline,
                size: 80,
                color: Theme.of(context).colorScheme.secondary.withOpacity(0.5),
              ),
              const SizedBox(height: 24),
              Text(
                'No saved jobs yet',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 12),
              Text(
                'Start by pasting a job description or browsing available jobs',
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
                    ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),
              Wrap(
                spacing: 12,
                alignment: WrapAlignment.center,
                children: [
                  FilledButton.icon(
                    onPressed: () {
                      context.push('/jobs/paste');
                    },
                    icon: const Icon(Icons.edit),
                    label: const Text('Paste Job'),
                  ),
                  FilledButton.tonalIcon(
                    onPressed: () {
                      context.push('/jobs/browse');
                    },
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

    // Job List with Pull to Refresh
    return RefreshIndicator(
      onRefresh: _refreshJobs,
      child: ListView.builder(
        controller: _scrollController,
        itemCount: state.userJobs.length + (state.isLoadingMore ? 1 : 0),
        itemBuilder: (context, index) {
          // Loading More Indicator
          if (index >= state.userJobs.length) {
            return const Padding(
              padding: EdgeInsets.all(16),
              child: Center(child: CircularProgressIndicator()),
            );
          }

          final job = state.userJobs[index];

          return JobCard(
            job: job,
            onTap: () {
              context.push('/jobs/${job.id}');
            },
          );
        },
      ),
    );
  }

  void _showFilterDialog() {
    showDialog(
      context: context,
      builder: (context) {
        JobStatus? tempStatus = _selectedStatus;
        JobSource? tempSource = _selectedSource;

        return StatefulBuilder(
          builder: (context, setState) {
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
                      children: [
                        FilterChip(
                          label: const Text('Active'),
                          selected: tempStatus == JobStatus.active,
                          onSelected: (selected) {
                            setState(() {
                              tempStatus = selected ? JobStatus.active : null;
                            });
                          },
                        ),
                        FilterChip(
                          label: const Text('Archived'),
                          selected: tempStatus == JobStatus.archived,
                          onSelected: (selected) {
                            setState(() {
                              tempStatus = selected ? JobStatus.archived : null;
                            });
                          },
                        ),
                        FilterChip(
                          label: const Text('Draft'),
                          selected: tempStatus == JobStatus.draft,
                          onSelected: (selected) {
                            setState(() {
                              tempStatus = selected ? JobStatus.draft : null;
                            });
                          },
                        ),
                      ],
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
                      children: [
                        FilterChip(
                          label: const Text('User Created'),
                          selected: tempSource == JobSource.userCreated,
                          onSelected: (selected) {
                            setState(() {
                              tempSource = selected ? JobSource.userCreated : null;
                            });
                          },
                        ),
                        FilterChip(
                          label: const Text('Indeed'),
                          selected: tempSource == JobSource.indeed,
                          onSelected: (selected) {
                            setState(() {
                              tempSource = selected ? JobSource.indeed : null;
                            });
                          },
                        ),
                        FilterChip(
                          label: const Text('LinkedIn'),
                          selected: tempSource == JobSource.linkedin,
                          onSelected: (selected) {
                            setState(() {
                              tempSource = selected ? JobSource.linkedin : null;
                            });
                          },
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () {
                    Navigator.pop(context);
                  },
                  child: const Text('Cancel'),
                ),
                FilledButton(
                  onPressed: () {
                    this.setState(() {
                      _selectedStatus = tempStatus;
                      _selectedSource = tempSource;
                    });
                    Navigator.pop(context);
                    _applyFilters();
                  },
                  child: const Text('Apply'),
                ),
              ],
            );
          },
        );
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

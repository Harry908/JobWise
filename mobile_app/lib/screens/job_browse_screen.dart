import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../models/job.dart';
import '../providers/job_provider.dart';
import '../widgets/job_card.dart';

/// Screen for browsing mock job listings
class JobBrowseScreen extends ConsumerStatefulWidget {
  const JobBrowseScreen({super.key});

  @override
  ConsumerState<JobBrowseScreen> createState() => _JobBrowseScreenState();
}

class _JobBrowseScreenState extends ConsumerState<JobBrowseScreen> {
  final _searchController = TextEditingController();
  final _locationController = TextEditingController();
  final _scrollController = ScrollController();
  bool _remoteOnly = false;
  bool _showFilters = false;

  @override
  void initState() {
    super.initState();
    // Load jobs on screen load
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(jobProvider.notifier).browseJobs(refresh: true);
    });

    // Setup infinite scroll
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _searchController.dispose();
    _locationController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.pixels >=
        _scrollController.position.maxScrollExtent * 0.8) {
      final state = ref.read(jobProvider);
      if (!state.isLoadingMore && state.hasMoreBrowseJobs) {
        ref.read(jobProvider.notifier).loadMoreBrowseJobs(
              query: _searchController.text.isEmpty ? null : _searchController.text,
              location: _locationController.text.isEmpty ? null : _locationController.text,
              remote: _remoteOnly ? true : null,
            );
      }
    }
  }

  void _performSearch() {
    ref.read(jobProvider.notifier).browseJobs(
          query: _searchController.text.isEmpty ? null : _searchController.text,
          location: _locationController.text.isEmpty ? null : _locationController.text,
          remote: _remoteOnly ? true : null,
          refresh: true,
        );
  }

  void _clearFilters() {
    setState(() {
      _searchController.clear();
      _locationController.clear();
      _remoteOnly = false;
    });
    _performSearch();
  }

  Future<void> _saveJob(BrowseJob browseJob) async {
    final savedJob = await ref.read(jobProvider.notifier).saveBrowseJob(browseJob);

    if (!mounted) return;

    if (savedJob != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Saved "${browseJob.title}"'),
          action: SnackBarAction(
            label: 'View',
            onPressed: () {
              context.push('/jobs/${savedJob.id}');
            },
          ),
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(ref.read(jobProvider).error ?? 'Failed to save job'),
          backgroundColor: Theme.of(context).colorScheme.error,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(jobProvider);
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Browse Jobs'),
        actions: [
          IconButton(
            icon: Icon(
              _showFilters ? Icons.filter_alt : Icons.filter_alt_outlined,
            ),
            onPressed: () {
              setState(() {
                _showFilters = !_showFilters;
              });
            },
            tooltip: 'Toggle Filters',
          ),
        ],
      ),
      body: Column(
        children: [
          // Search Bar
          Padding(
            padding: const EdgeInsets.all(16),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: 'Search jobs by title, skills, company...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _searchController.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _searchController.clear();
                          _performSearch();
                        },
                      )
                    : null,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              onSubmitted: (_) => _performSearch(),
              textInputAction: TextInputAction.search,
            ),
          ),

          // Filters Section
          if (_showFilters) ...[
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Filters',
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 16),

                      // Location Filter
                      TextField(
                        controller: _locationController,
                        decoration: InputDecoration(
                          labelText: 'Location',
                          hintText: 'City, State, or "Remote"',
                          prefixIcon: const Icon(Icons.location_on),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                        textInputAction: TextInputAction.search,
                        onSubmitted: (_) => _performSearch(),
                      ),
                      const SizedBox(height: 12),

                      // Remote Only Checkbox
                      CheckboxListTile(
                        title: const Text('Remote jobs only'),
                        value: _remoteOnly,
                        onChanged: (value) {
                          setState(() {
                            _remoteOnly = value ?? false;
                          });
                        },
                        contentPadding: EdgeInsets.zero,
                      ),
                      const SizedBox(height: 12),

                      // Filter Action Buttons
                      Row(
                        mainAxisAlignment: MainAxisAlignment.end,
                        children: [
                          TextButton(
                            onPressed: _clearFilters,
                            child: const Text('Clear'),
                          ),
                          const SizedBox(width: 12),
                          FilledButton.icon(
                            onPressed: _performSearch,
                            icon: const Icon(Icons.search),
                            label: const Text('Apply'),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ),
            const SizedBox(height: 8),
          ],

          // Results Count
          if (!state.isBrowseLoading && state.browseJobs.isNotEmpty)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Row(
                children: [
                  Text(
                    '${state.browseJobsTotal} jobs found',
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
    );
  }

  Widget _buildJobList(JobState state) {
    // Loading State (initial)
    if (state.isBrowseLoading && state.browseJobs.isEmpty) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    // Empty State
    if (state.browseJobs.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.work_off_outlined,
                size: 64,
                color: Theme.of(context).colorScheme.secondary.withOpacity(0.5),
              ),
              const SizedBox(height: 16),
              Text(
                'No jobs found',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 8),
              Text(
                'Try adjusting your search or filters',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
                    ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 24),
              FilledButton.icon(
                onPressed: _clearFilters,
                icon: const Icon(Icons.refresh),
                label: const Text('Clear Filters'),
              ),
            ],
          ),
        ),
      );
    }

    // Job List
    return RefreshIndicator(
      onRefresh: () async {
        await ref.read(jobProvider.notifier).browseJobs(
              query: _searchController.text.isEmpty ? null : _searchController.text,
              location: _locationController.text.isEmpty ? null : _locationController.text,
              remote: _remoteOnly ? true : null,
              refresh: true,
            );
      },
      child: ListView.builder(
        controller: _scrollController,
        itemCount: state.browseJobs.length + (state.isLoadingMore ? 1 : 0),
        itemBuilder: (context, index) {
          // Loading More Indicator
          if (index >= state.browseJobs.length) {
            return const Padding(
              padding: EdgeInsets.all(16),
              child: Center(child: CircularProgressIndicator()),
            );
          }

          final browseJob = state.browseJobs[index];

          return JobCard(
            browseJob: browseJob,
            onTap: () {
              _showJobDetailDialog(browseJob);
            },
            onSave: () => _saveJob(browseJob),
            showSaveButton: true,
          );
        },
      ),
    );
  }

  void _showJobDetailDialog(BrowseJob browseJob) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) {
        return DraggableScrollableSheet(
          initialChildSize: 0.9,
          minChildSize: 0.5,
          maxChildSize: 0.95,
          expand: false,
          builder: (context, scrollController) {
            return Container(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Handle Bar
                  Center(
                    child: Container(
                      width: 40,
                      height: 4,
                      margin: const EdgeInsets.only(bottom: 16),
                      decoration: BoxDecoration(
                        color: Colors.grey[300],
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                  ),

                  // Content
                  Expanded(
                    child: SingleChildScrollView(
                      controller: scrollController,
                      child: _buildBrowseJobDetail(browseJob),
                    ),
                  ),

                  // Save Button
                  const SizedBox(height: 16),
                  SizedBox(
                    width: double.infinity,
                    child: FilledButton.icon(
                      onPressed: () {
                        Navigator.pop(context);
                        _saveJob(browseJob);
                      },
                      icon: const Icon(Icons.bookmark),
                      label: const Text('Save Job'),
                    ),
                  ),
                ],
              ),
            );
          },
        );
      },
    );
  }

  Widget _buildBrowseJobDetail(BrowseJob browseJob) {
    final theme = Theme.of(context);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Title
        Text(
          browseJob.title,
          style: theme.textTheme.headlineSmall?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),

        // Company
        Row(
          children: [
            Icon(Icons.business, size: 20, color: theme.colorScheme.primary),
            const SizedBox(width: 8),
            Text(
              browseJob.company,
              style: theme.textTheme.titleMedium?.copyWith(
                color: theme.colorScheme.primary,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),

        // Location
        Row(
          children: [
            Icon(
              browseJob.remote ? Icons.home_work : Icons.location_on,
              size: 18,
              color: theme.colorScheme.secondary,
            ),
            const SizedBox(width: 8),
            Text(
              browseJob.location ?? (browseJob.remote ? 'Remote' : 'N/A'),
              style: theme.textTheme.bodyLarge,
            ),
            if (browseJob.remote) ...[
              const SizedBox(width: 12),
              Chip(
                label: const Text('Remote'),
                backgroundColor: theme.colorScheme.primaryContainer,
                labelStyle: TextStyle(
                  color: theme.colorScheme.onPrimaryContainer,
                ),
              ),
            ],
          ],
        ),

        // Salary
        if (browseJob.salaryRange != null) ...[
          const SizedBox(height: 8),
          Row(
            children: [
              Icon(Icons.attach_money, size: 18, color: theme.colorScheme.secondary),
              const SizedBox(width: 8),
              Text(
                browseJob.salaryRange!,
                style: theme.textTheme.bodyLarge?.copyWith(
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        ],

        const Divider(height: 32),

        // Keywords
        if (browseJob.parsedKeywords.isNotEmpty) ...[
          Text(
            'Key Skills',
            style: theme.textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: browseJob.parsedKeywords.map((keyword) {
              return Chip(
                label: Text(keyword),
                backgroundColor: theme.colorScheme.secondaryContainer,
                labelStyle: TextStyle(
                  color: theme.colorScheme.onSecondaryContainer,
                ),
              );
            }).toList(),
          ),
          const SizedBox(height: 24),
        ],

        // Description
        if (browseJob.description != null) ...[
          Text(
            'Description',
            style: theme.textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            browseJob.description!,
            style: theme.textTheme.bodyMedium?.copyWith(height: 1.5),
          ),
          const SizedBox(height: 24),
        ],

        // Requirements
        if (browseJob.requirements.isNotEmpty) ...[
          Text(
            'Requirements',
            style: theme.textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          ...browseJob.requirements.map((req) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(Icons.check_circle_outline, size: 20, color: theme.colorScheme.primary),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      req,
                      style: theme.textTheme.bodyMedium?.copyWith(height: 1.5),
                    ),
                  ),
                ],
              ),
            );
          }),
          const SizedBox(height: 24),
        ],

        // Benefits
        if (browseJob.benefits.isNotEmpty) ...[
          Text(
            'Benefits',
            style: theme.textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          ...browseJob.benefits.map((benefit) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(Icons.star_outline, size: 20, color: theme.colorScheme.secondary),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      benefit,
                      style: theme.textTheme.bodyMedium?.copyWith(height: 1.5),
                    ),
                  ),
                ],
              ),
            );
          }),
        ],
      ],
    );
  }
}

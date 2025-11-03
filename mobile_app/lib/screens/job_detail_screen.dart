import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../providers/job_provider.dart';
import '../widgets/job_detail_view.dart';

/// Screen for displaying full job details
class JobDetailScreen extends ConsumerStatefulWidget {
  final String jobId;

  const JobDetailScreen({
    super.key,
    required this.jobId,
  });

  @override
  ConsumerState<JobDetailScreen> createState() => _JobDetailScreenState();
}

class _JobDetailScreenState extends ConsumerState<JobDetailScreen> {
  @override
  void initState() {
    super.initState();
    // Load job details on screen load
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(jobProvider.notifier).loadJobById(widget.jobId);
    });
  }

  Future<void> _deleteJob() async {
    // Show confirmation dialog
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Delete Job'),
          content: const Text('Are you sure you want to delete this job? This action cannot be undone.'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('Cancel'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(context, true),
              style: FilledButton.styleFrom(
                backgroundColor: Theme.of(context).colorScheme.error,
              ),
              child: const Text('Delete'),
            ),
          ],
        );
      },
    );

    if (confirmed != true || !mounted) return;

    // Delete the job
    final success = await ref.read(jobProvider.notifier).deleteJob(widget.jobId);

    if (!mounted) return;

    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Job deleted successfully')),
      );
      Navigator.pop(context);
    } else {
      final error = ref.read(jobProvider).error ?? 'Failed to delete job';
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(error),
          backgroundColor: Theme.of(context).colorScheme.error,
        ),
      );
    }
  }

  void _editJob() {
    // Navigate to edit screen (to be implemented)
    context.push('/jobs/${widget.jobId}/edit');
  }

  void _generateResume() {
    // Navigate to resume generation (to be implemented)
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Resume generation feature coming soon'),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(jobProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Job Details'),
        actions: [
          IconButton(
            icon: const Icon(Icons.edit),
            onPressed: state.selectedJob != null ? _editJob : null,
            tooltip: 'Edit Job',
          ),
          IconButton(
            icon: const Icon(Icons.delete),
            onPressed: state.selectedJob != null ? _deleteJob : null,
            tooltip: 'Delete Job',
          ),
        ],
      ),
      body: _buildBody(state),
    );
  }

  Widget _buildBody(JobState state) {
    // Loading State
    if (state.isLoading && state.selectedJob == null) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    // Error State
    if (state.error != null && state.selectedJob == null) {
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
                'Error loading job',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 8),
              Text(
                state.error!,
                style: Theme.of(context).textTheme.bodyMedium,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 24),
              FilledButton.icon(
                onPressed: () {
                  ref.read(jobProvider.notifier).loadJobById(widget.jobId);
                },
                icon: const Icon(Icons.refresh),
                label: const Text('Retry'),
              ),
            ],
          ),
        ),
      );
    }

    // Job Not Found
    if (state.selectedJob == null) {
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
                'Job not found',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 8),
              Text(
                'This job may have been deleted',
                style: Theme.of(context).textTheme.bodyMedium,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 24),
              FilledButton.icon(
                onPressed: () => Navigator.pop(context),
                icon: const Icon(Icons.arrow_back),
                label: const Text('Go Back'),
              ),
            ],
          ),
        ),
      );
    }

    // Job Details View
    return JobDetailView(
      job: state.selectedJob!,
      onEdit: _editJob,
      onDelete: _deleteJob,
      onGenerateResume: _generateResume,
    );
  }
}

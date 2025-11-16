import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../models/job.dart';
import '../providers/job_provider.dart';
import '../widgets/job_detail_view.dart';

/// Screen for displaying full job details
class JobDetailScreen extends ConsumerWidget {
  final String jobId;

  const JobDetailScreen({
    super.key,
    required this.jobId,
  });

  Future<void> _deleteJob(BuildContext context, WidgetRef ref) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Job'),
        content: const Text(
            'Are you sure you want to delete this job? This action cannot be undone.'),
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
      ),
    );

    if (confirmed != true) return;

    try {
      await ref.read(userJobsProvider.notifier).deleteJob(jobId);
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Job deleted successfully')),
        );
        context.pop();
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to delete job: ${e.toString()}'),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      }
    }
  }

  Future<void> _updateApplicationStatus(
      BuildContext context, WidgetRef ref, Job currentJob, ApplicationStatus newStatus) async {
    try {
      final updatedJob = currentJob.copyWith(applicationStatus: newStatus);
      await ref.read(userJobsProvider.notifier).updateJob(updatedJob);
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Application status updated')),
        );
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to update status: ${e.toString()}'),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      }
    }
  }

  void _generateResume(BuildContext context, Job job) {
    context.push('/generations/options', extra: job);
  }

  void _generateCoverLetter(BuildContext context, Job job) {
    context.push(
      '/generations/options?type=cover_letter',
      extra: job,
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final jobAsync = ref.watch(selectedJobProvider(jobId));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Job Details'),
        actions: [
          IconButton(
            icon: const Icon(Icons.delete),
            onPressed: jobAsync.hasValue ? () => _deleteJob(context, ref) : null,
            tooltip: 'Delete Job',
          ),
        ],
      ),
      body: jobAsync.when(
        data: (job) {
          if (job == null) {
            return _buildNotFound(context);
          }
          return JobDetailView(
            job: job,
            onApplicationStatusChanged: (newStatus) =>
                _updateApplicationStatus(context, ref, job, newStatus),
            onDelete: () => _deleteJob(context, ref),
            onGenerateResume: () => _generateResume(context, job),
            onGenerateCoverLetter: () => _generateCoverLetter(context, job),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, stack) => _buildError(context, ref, err),
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
              'Error loading job',
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
              onPressed: () => ref.invalidate(selectedJobProvider(jobId)),
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNotFound(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.work_off_outlined,
              size: 64,
              color: Theme.of(context).colorScheme.secondary.withAlpha(128),
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
              onPressed: () => context.pop(),
              icon: const Icon(Icons.arrow_back),
              label: const Text('Go Back'),
            ),
          ],
        ),
      ),
    );
  }
}

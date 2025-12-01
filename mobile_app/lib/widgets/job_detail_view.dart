import 'package:flutter/material.dart';
import '../models/job.dart';
import 'package:intl/intl.dart';

/// Reusable widget for displaying full job details
class JobDetailView extends StatelessWidget {
  final Job job;
  final VoidCallback? onEdit;
  final VoidCallback? onDelete;
  final VoidCallback? onGenerateResume;
  final VoidCallback? onGenerateCoverLetter;
  final Function(ApplicationStatus)? onApplicationStatusChanged;

  const JobDetailView({
    super.key,
    required this.job,
    this.onEdit,
    this.onDelete,
    this.onGenerateResume,
    this.onGenerateCoverLetter,
    this.onApplicationStatusChanged,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Job Title
          Text(
            job.title,
            style: theme.textTheme.headlineMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),

          // Company
          Row(
            children: [
              Icon(
                Icons.business,
                size: 20,
                color: theme.colorScheme.primary,
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  job.company,
                  style: theme.textTheme.titleLarge?.copyWith(
                    color: theme.colorScheme.primary,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),

          // Location and Remote
          Row(
            children: [
              Icon(
                job.remote ? Icons.home_work : Icons.location_on,
                size: 18,
                color: theme.colorScheme.secondary,
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  job.location ?? (job.remote ? 'Remote' : 'Location not specified'),
                  style: theme.textTheme.bodyLarge,
                ),
              ),
              if (job.remote) ...[
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

          // Salary Range
          if (job.salaryRange != null) ...[
            const SizedBox(height: 8),
            Row(
              children: [
                Icon(
                  Icons.attach_money,
                  size: 18,
                  color: theme.colorScheme.secondary,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    _formatSalaryRange(job.salaryRange!),
                    style: theme.textTheme.bodyLarge?.copyWith(
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ),
          ],

          // Created Date
          const SizedBox(height: 8),
          Row(
            children: [
              Icon(
                Icons.calendar_today,
                size: 16,
                color: theme.colorScheme.secondary,
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Added ${_formatDate(job.createdAt)}',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurface.withValues(alpha: 0.6),
                  ),
                ),
              ),
            ],
          ),

          const Divider(height: 32),

          // Application Status Section
          _buildApplicationStatusSection(context, theme),

          const Divider(height: 32),

          // Action Buttons
          if (onEdit != null || onDelete != null || onGenerateResume != null || onGenerateCoverLetter != null) ...[
            Wrap(
              spacing: 12,
              runSpacing: 12,
              children: [
                if (onGenerateResume != null)
                  FilledButton.icon(
                    onPressed: onGenerateResume,
                    icon: const Icon(Icons.description),
                    label: const Text('Generate Resume'),
                  ),
                if (onGenerateCoverLetter != null)
                  FilledButton.icon(
                    onPressed: onGenerateCoverLetter,
                    icon: const Icon(Icons.mail),
                    label: const Text('Generate Cover Letter'),
                  ),
                if (onEdit != null)
                  FilledButton.tonalIcon(
                    onPressed: onEdit,
                    icon: const Icon(Icons.edit),
                    label: const Text('Edit'),
                  ),
                if (onDelete != null)
                  OutlinedButton.icon(
                    onPressed: onDelete,
                    icon: const Icon(Icons.delete),
                    label: const Text('Delete'),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: theme.colorScheme.error,
                    ),
                  ),
              ],
            ),
            const Divider(height: 32),
          ],

          // Keywords/Skills
          if (job.parsedKeywords.isNotEmpty) ...[
            Text(
              'Key Skills & Technologies',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: job.parsedKeywords.map((keyword) {
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
          if (job.description != null && job.description!.isNotEmpty) ...[
            Text(
              'Job Description',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            Text(
              job.description!,
              style: theme.textTheme.bodyLarge?.copyWith(height: 1.5),
            ),
            const SizedBox(height: 24),
          ],

          // Requirements
          if (job.requirements.isNotEmpty) ...[
            Text(
              'Requirements',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            ...job.requirements.map((req) {
              return Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(
                      Icons.check_circle_outline,
                      size: 20,
                      color: theme.colorScheme.primary,
                    ),
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
          if (job.benefits.isNotEmpty) ...[
            Text(
              'Benefits',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            ...job.benefits.map((benefit) {
              return Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(
                      Icons.star_outline,
                      size: 20,
                      color: theme.colorScheme.secondary,
                    ),
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
            const SizedBox(height: 24),
          ],

          // Source Info
          Card(
            color: theme.colorScheme.surfaceContainerHighest,
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Row(
                children: [
                  Icon(
                    Icons.info_outline,
                    size: 16,
                    color: theme.colorScheme.onSurface.withValues(alpha: 0.6),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'Source: ${_formatSource(job.source)}',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.onSurface.withValues(alpha: 0.6),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildApplicationStatusSection(BuildContext context, ThemeData theme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(
              'Application Status',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            if (onApplicationStatusChanged != null) ...[
              const Spacer(),
              TextButton.icon(
                onPressed: () => _showApplicationStatusPicker(context),
                icon: const Icon(Icons.edit, size: 16),
                label: const Text('Change'),
              ),
            ],
          ],
        ),
        const SizedBox(height: 12),
        InkWell(
          onTap: onApplicationStatusChanged != null
              ? () => _showApplicationStatusPicker(context)
              : null,
          borderRadius: BorderRadius.circular(12),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: _getApplicationStatusColor(job.applicationStatus).withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: _getApplicationStatusColor(job.applicationStatus).withValues(alpha: 0.3),
                width: 2,
              ),
            ),
            child: Row(
              children: [
                Icon(
                  _getApplicationStatusIcon(job.applicationStatus),
                  color: _getApplicationStatusColor(job.applicationStatus),
                  size: 24,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    _formatApplicationStatus(job.applicationStatus),
                    style: theme.textTheme.bodyLarge?.copyWith(
                      color: _getApplicationStatusColor(job.applicationStatus),
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                if (onApplicationStatusChanged != null)
                  Icon(
                    Icons.arrow_forward_ios,
                    size: 16,
                    color: _getApplicationStatusColor(job.applicationStatus).withValues(alpha: 0.5),
                  ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  void _showApplicationStatusPicker(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Application Status'),
          contentPadding: const EdgeInsets.symmetric(vertical: 16),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: ApplicationStatus.values.map((status) {
                final isSelected = status == job.applicationStatus;
                // ignore: deprecated_member_use
                return RadioListTile<ApplicationStatus>(
                  value: status,
                  // ignore: deprecated_member_use
                  groupValue: job.applicationStatus,
                  // ignore: deprecated_member_use
                  onChanged: (value) {
                    if (value != null && onApplicationStatusChanged != null) {
                      Navigator.pop(context);
                      onApplicationStatusChanged!(value);
                    }
                  },
                  title: Row(
                    children: [
                      Icon(
                        _getApplicationStatusIcon(status),
                        color: _getApplicationStatusColor(status),
                        size: 20,
                      ),
                      const SizedBox(width: 12),
                      Text(
                        _formatApplicationStatus(status),
                        style: TextStyle(
                          fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                          color: _getApplicationStatusColor(status),
                        ),
                      ),
                    ],
                  ),
                  activeColor: _getApplicationStatusColor(status),
                );
              }).toList(),
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
          ],
        );
      },
    );
  }

  Color _getApplicationStatusColor(ApplicationStatus status) {
    switch (status) {
      case ApplicationStatus.notApplied:
        return Colors.grey;
      case ApplicationStatus.preparing:
        return Colors.blue;
      case ApplicationStatus.applied:
        return Colors.orange;
      case ApplicationStatus.interviewing:
        return Colors.purple;
      case ApplicationStatus.offerReceived:
        return Colors.green;
      case ApplicationStatus.rejected:
        return Colors.red;
      case ApplicationStatus.accepted:
        return Colors.teal;
      case ApplicationStatus.withdrawn:
        return Colors.blueGrey;
    }
  }

  IconData _getApplicationStatusIcon(ApplicationStatus status) {
    switch (status) {
      case ApplicationStatus.notApplied:
        return Icons.circle_outlined;
      case ApplicationStatus.preparing:
        return Icons.edit_note;
      case ApplicationStatus.applied:
        return Icons.send;
      case ApplicationStatus.interviewing:
        return Icons.person_search;
      case ApplicationStatus.offerReceived:
        return Icons.card_giftcard;
      case ApplicationStatus.rejected:
        return Icons.cancel;
      case ApplicationStatus.accepted:
        return Icons.check_circle;
      case ApplicationStatus.withdrawn:
        return Icons.undo;
    }
  }

  String _formatApplicationStatus(ApplicationStatus status) {
    switch (status) {
      case ApplicationStatus.notApplied:
        return 'Not Applied';
      case ApplicationStatus.preparing:
        return 'Preparing Application';
      case ApplicationStatus.applied:
        return 'Applied';
      case ApplicationStatus.interviewing:
        return 'Interviewing';
      case ApplicationStatus.offerReceived:
        return 'Offer Received';
      case ApplicationStatus.rejected:
        return 'Rejected';
      case ApplicationStatus.accepted:
        return 'Accepted';
      case ApplicationStatus.withdrawn:
        return 'Withdrawn';
    }
  }

  String _formatSalaryRange(String range) {
    if (range.contains('-')) {
      final parts = range.split('-');
      if (parts.length == 2) {
        try {
          final min = int.parse(parts[0]);
          final max = int.parse(parts[1]);
          return '\$${_formatNumber(min)} - \$${_formatNumber(max)}';
        } catch (e) {
          return range;
        }
      }
    }
    return range;
  }

  String _formatNumber(int number) {
    if (number >= 1000) {
      return '${(number / 1000).toStringAsFixed(0)}K';
    }
    return number.toString();
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final difference = now.difference(date);

    if (difference.inDays == 0) {
      return 'today';
    } else if (difference.inDays == 1) {
      return 'yesterday';
    } else if (difference.inDays < 7) {
      return '${difference.inDays} days ago';
    } else {
      return DateFormat('MMM d, yyyy').format(date);
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
        return 'Mock Data';
      case JobSource.imported:
        return 'Imported';
      case JobSource.urlImport:
        return 'URL Import';
    }
  }
}

import 'package:flutter/material.dart';
import '../models/job.dart';
import 'package:intl/intl.dart';

/// Reusable widget for displaying full job details
class JobDetailView extends StatelessWidget {
  final Job job;
  final VoidCallback? onEdit;
  final VoidCallback? onDelete;
  final VoidCallback? onGenerateResume;

  const JobDetailView({
    super.key,
    required this.job,
    this.onEdit,
    this.onDelete,
    this.onGenerateResume,
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
              Text(
                job.company,
                style: theme.textTheme.titleLarge?.copyWith(
                  color: theme.colorScheme.primary,
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
              Text(
                job.location ?? (job.remote ? 'Remote' : 'Location not specified'),
                style: theme.textTheme.bodyLarge,
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
                Text(
                  _formatSalaryRange(job.salaryRange!),
                  style: theme.textTheme.bodyLarge?.copyWith(
                    fontWeight: FontWeight.w500,
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
              Text(
                'Added ${_formatDate(job.createdAt)}',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurface.withOpacity(0.6),
                ),
              ),
            ],
          ),

          const Divider(height: 32),

          // Action Buttons
          if (onEdit != null || onDelete != null || onGenerateResume != null) ...[
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
                    color: theme.colorScheme.onSurface.withOpacity(0.6),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'Source: ${_formatSource(job.source)}',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.onSurface.withOpacity(0.6),
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

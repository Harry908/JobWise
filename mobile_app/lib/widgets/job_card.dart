import 'package:flutter/material.dart';
import '../models/job.dart';

/// Reusable job card widget for displaying job listings
class JobCard extends StatelessWidget {
  final Job? job;
  final BrowseJob? browseJob;
  final VoidCallback onTap;
  final VoidCallback? onSave;
  final bool showSaveButton;

  const JobCard({
    super.key,
    this.job,
    this.browseJob,
    required this.onTap,
    this.onSave,
    this.showSaveButton = false,
  }) : assert(job != null || browseJob != null,
            'Either job or browseJob must be provided');

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final title = job?.title ?? browseJob?.title ?? 'Untitled';
    final company = job?.company ?? browseJob?.company ?? 'Unknown Company';
    final location = job?.location ?? browseJob?.location;
    final remote = job?.remote ?? browseJob?.remote ?? false;
    final keywords = job?.parsedKeywords ?? browseJob?.parsedKeywords ?? [];
    final salaryRange = job?.salaryRange ?? browseJob?.salaryRange;

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      elevation: 2,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Title and Save Button Row
              Row(
                children: [
                  Expanded(
                    child: Text(
                      title,
                      style: theme.textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  if (showSaveButton && onSave != null) ...[
                    const SizedBox(width: 8),
                    IconButton(
                      icon: const Icon(Icons.bookmark_border),
                      onPressed: onSave,
                      tooltip: 'Save Job',
                      color: theme.colorScheme.primary,
                    ),
                  ],
                ],
              ),
              const SizedBox(height: 8),

              // Company
              Row(
                children: [
                  Icon(
                    Icons.business,
                    size: 16,
                    color: theme.colorScheme.secondary,
                  ),
                  const SizedBox(width: 4),
                  Expanded(
                    child: Text(
                      company,
                      style: theme.textTheme.bodyLarge?.copyWith(
                        color: theme.colorScheme.secondary,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 4),

              // Location and Remote Status
              Row(
                children: [
                  Icon(
                    remote ? Icons.home_work : Icons.location_on,
                    size: 16,
                    color: theme.colorScheme.secondary,
                  ),
                  const SizedBox(width: 4),
                  Expanded(
                    child: Text(
                      location ?? (remote ? 'Remote' : 'Location not specified'),
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: theme.colorScheme.onSurface.withValues(alpha: 0.7),
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  if (remote) ...[
                    const SizedBox(width: 8),
                    Chip(
                      label: const Text('Remote'),
                      backgroundColor: theme.colorScheme.primaryContainer,
                      labelStyle: TextStyle(
                        color: theme.colorScheme.onPrimaryContainer,
                        fontSize: 12,
                      ),
                      padding: const EdgeInsets.symmetric(horizontal: 8),
                      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                    ),
                  ],
                ],
              ),

              // Salary Range
              if (salaryRange != null) ...[
                const SizedBox(height: 4),
                Row(
                  children: [
                    Icon(
                      Icons.attach_money,
                      size: 16,
                      color: theme.colorScheme.secondary,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      _formatSalaryRange(salaryRange),
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: theme.colorScheme.onSurface.withValues(alpha: 0.7),
                      ),
                    ),
                  ],
                ),
              ],

              // Keywords/Skills
              if (keywords.isNotEmpty) ...[
                const SizedBox(height: 12),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: keywords.take(5).map((keyword) {
                    return Chip(
                      label: Text(keyword),
                      backgroundColor: theme.colorScheme.surfaceContainerHighest,
                      labelStyle: TextStyle(
                        color: theme.colorScheme.onSurface,
                        fontSize: 12,
                      ),
                      padding: const EdgeInsets.symmetric(horizontal: 8),
                      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                    );
                  }).toList(),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  String _formatSalaryRange(String range) {
    // Try to parse "120000-180000" format
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
}

/// Compact job card for smaller spaces
class JobCardCompact extends StatelessWidget {
  final Job job;
  final VoidCallback onTap;

  const JobCardCompact({
    super.key,
    required this.job,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      child: ListTile(
        onTap: onTap,
        title: Text(
          job.title,
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        subtitle: Text(
          job.company,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        trailing: job.remote
            ? const Icon(Icons.home_work, size: 20)
            : const Icon(Icons.arrow_forward_ios, size: 16),
      ),
    );
  }
}

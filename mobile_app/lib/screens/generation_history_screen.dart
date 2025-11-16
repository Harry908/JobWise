import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../models/generation.dart';
import '../providers/generation_provider.dart';

/// Screen for displaying generation history with filtering options
class GenerationHistoryScreen extends ConsumerStatefulWidget {
  const GenerationHistoryScreen({super.key});

  @override
  ConsumerState<GenerationHistoryScreen> createState() =>
      _GenerationHistoryScreenState();
}

class _GenerationHistoryScreenState extends ConsumerState<GenerationHistoryScreen> {
  GenerationStatus? _selectedStatus;
  DocumentType? _selectedDocumentType;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final generationHistoryAsync = ref.watch(generationHistoryProvider(
      status: _selectedStatus,
      documentType: _selectedDocumentType,
    ));

    void applyFilters() {
      setState(() {
        // The build method will be re-run with the new filter values
      });
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Generation History'),
        actions: [
          IconButton(
            icon: const Icon(Icons.filter_list),
            onPressed: () =>
                _showFilterDialog(context, applyFilters),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(generationHistoryProvider(
            status: _selectedStatus,
            documentType: _selectedDocumentType,
          ));
        },
        child: generationHistoryAsync.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (error, stack) =>
              _buildErrorView(theme, error.toString(), ref),
          data: (data) {
            final (generations, pagination, statistics) = data;
            if (generations.isEmpty) {
              return _buildEmptyView(theme);
            }
            return _buildGenerationsList(
                theme, generations, applyFilters);
          },
        ),
      ),
    );
  }

  Widget _buildGenerationsList(
      ThemeData theme, List<GenerationListItem> generations, VoidCallback applyFilters) {
    return Column(
      children: [
        // Active Filters
        if (_selectedStatus != null || _selectedDocumentType != null)
          _buildActiveFilters(theme, applyFilters),

        // Generation List
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.all(16.0),
            itemCount: generations.length,
            itemBuilder: (context, index) {
              final generation = generations[index];
              return _buildGenerationCard(context, theme, generation);
            },
          ),
        ),
      ],
    );
  }

  Widget _buildActiveFilters(ThemeData theme, VoidCallback applyFilters) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
      child: Wrap(
        spacing: 8,
        runSpacing: 8,
        children: [
          if (_selectedStatus != null)
            Chip(
              label: Text('Status: ${_statusToString(_selectedStatus!)}'),
              onDeleted: () {
                setState(() {
                  _selectedStatus = null;
                });
              },
            ),
          if (_selectedDocumentType != null)
            Chip(
              label:
                  Text('Type: ${_documentTypeToString(_selectedDocumentType!)}'),
              onDeleted: () {
                setState(() {
                  _selectedDocumentType = null;
                });
              },
            ),
        ],
      ),
    );
  }

  Widget _buildGenerationCard(BuildContext context, ThemeData theme, GenerationListItem generation) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12.0),
      child: InkWell(
        onTap: () => _handleGenerationTap(context, generation),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          generation.jobTitle,
                          style: theme.textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          generation.company,
                          style: theme.textTheme.bodyMedium?.copyWith(
                            color: theme.colorScheme.primary,
                          ),
                        ),
                      ],
                    ),
                  ),
                  _buildStatusBadge(theme, generation.status),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Icon(
                    generation.documentType == DocumentType.resume
                        ? Icons.description
                        : Icons.article,
                    size: 16,
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    generation.documentType == DocumentType.resume
                        ? 'Resume'
                        : 'Cover Letter',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                  const Spacer(),
                  Icon(
                    Icons.access_time,
                    size: 16,
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    _formatDate(generation.createdAt),
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                ],
              ),
              if (generation.atsScore != null) ...[
                const SizedBox(height: 12),
                LinearProgressIndicator(
                  value: generation.atsScore! / 100,
                  backgroundColor: theme.colorScheme.surfaceContainerHighest,
                  valueColor: AlwaysStoppedAnimation<Color>(
                    _getScoreColor(generation.atsScore!),
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'ATS Score: ${generation.atsScore!.toInt()}',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: _getScoreColor(generation.atsScore!),
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatusBadge(ThemeData theme, GenerationStatus status) {
    Color color;
    IconData icon;
    String label;

    switch (status) {
      case GenerationStatus.pending:
        color = Colors.grey;
        icon = Icons.schedule;
        label = 'Pending';
        break;
      case GenerationStatus.generating:
        color = Colors.blue;
        icon = Icons.autorenew;
        label = 'Generating';
        break;
      case GenerationStatus.completed:
        color = Colors.green;
        icon = Icons.check_circle;
        label = 'Completed';
        break;
      case GenerationStatus.failed:
        color = Colors.red;
        icon = Icons.error;
        label = 'Failed';
        break;
      case GenerationStatus.cancelled:
        color = Colors.orange;
        icon = Icons.cancel;
        label = 'Cancelled';
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withAlpha(25),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: color),
          const SizedBox(width: 4),
          Text(
            label,
            style: theme.textTheme.labelSmall?.copyWith(
              color: color,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Color _getScoreColor(double score) {
    if (score >= 80) return Colors.green;
    if (score >= 60) return Colors.orange;
    return Colors.red;
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final difference = now.difference(date);

    if (difference.inDays == 0) {
      if (difference.inHours == 0) {
        return '${difference.inMinutes}m ago';
      }
      return '${difference.inHours}h ago';
    } else if (difference.inDays < 7) {
      return '${difference.inDays}d ago';
    } else {
      return '${date.day}/${date.month}/${date.year}';
    }
  }

  Widget _buildEmptyView(ThemeData theme) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.history,
              size: 64,
              color: theme.colorScheme.onSurfaceVariant,
            ),
            const SizedBox(height: 16),
            Text(
              'No Generations Yet',
              style: theme.textTheme.headlineSmall,
            ),
            const SizedBox(height: 8),
            Text(
              'Your generation history will appear here',
              textAlign: TextAlign.center,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorView(ThemeData theme, String error, WidgetRef ref) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 64,
              color: theme.colorScheme.error,
            ),
            const SizedBox(height: 16),
            Text(
              'Error Loading History',
              style: theme.textTheme.headlineSmall?.copyWith(
                color: theme.colorScheme.error,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              error,
              textAlign: TextAlign.center,
              style: theme.textTheme.bodyMedium,
            ),
            const SizedBox(height: 24),
            FilledButton.icon(
              onPressed: () {
                ref.invalidate(generationHistoryProvider(
                  status: _selectedStatus,
                  documentType: _selectedDocumentType,
                ));
              },
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
            ),
          ],
        ),
      ),
    );
  }

  void _showFilterDialog(BuildContext context, VoidCallback applyFilters) {
    showDialog(
      context: context,
      builder: (context) {
        // Use a StatefulWidget for the dialog's content to manage temporary state
        return StatefulBuilder(
          builder: (context, setDialogState) {
            return AlertDialog(
              title: const Text('Filter Generations'),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Status'),
                  const SizedBox(height: 8),
                  DropdownButton<GenerationStatus?>(
                    value: _selectedStatus,
                    isExpanded: true,
                    hint: const Text('All Statuses'),
                    items: [
                      const DropdownMenuItem<GenerationStatus?>(
                        value: null,
                        child: Text('All Statuses'),
                      ),
                      ...GenerationStatus.values.map(
                        (status) => DropdownMenuItem<GenerationStatus?>(
                          value: status,
                          child: Text(_statusToString(status)),
                        ),
                      ),
                    ],
                    onChanged: (newValue) {
                      setDialogState(() {
                        _selectedStatus = newValue;
                      });
                    },
                  ),
                  const SizedBox(height: 16),
                  const Text('Document Type'),
                  const SizedBox(height: 8),
                  DropdownButton<DocumentType?>(
                    value: _selectedDocumentType,
                    isExpanded: true,
                    hint: const Text('All Types'),
                    items: [
                      const DropdownMenuItem<DocumentType?>(
                        value: null,
                        child: Text('All Types'),
                      ),
                      ...DocumentType.values.map(
                        (type) => DropdownMenuItem<DocumentType?>(
                          value: type,
                          child: Text(_documentTypeToString(type)),
                        ),
                      ),
                    ],
                    onChanged: (newValue) {
                      setDialogState(() {
                        _selectedDocumentType = newValue;
                      });
                    },
                  ),
                ],
              ),
              actions: [
                TextButton(
                  onPressed: () {
                    setState(() {
                      _selectedStatus = null;
                      _selectedDocumentType = null;
                    });
                    Navigator.of(context).pop();
                    applyFilters();
                  },
                  child: const Text('Clear'),
                ),
                FilledButton(
                  onPressed: () {
                    Navigator.of(context).pop();
                    applyFilters();
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

  void _handleGenerationTap(BuildContext context, GenerationListItem generation) {
    if (generation.status == GenerationStatus.completed) {
      context.push('/generations/${generation.id}/result');
    } else if (generation.status == GenerationStatus.generating ||
        generation.status == GenerationStatus.pending) {
      context.push('/generations/${generation.id}/progress');
    } else {
      // Failed or cancelled - show detail view
      context.push('/generations/${generation.id}/result');
    }
  }

  String _statusToString(GenerationStatus status) {
    switch (status) {
      case GenerationStatus.pending:
        return 'Pending';
      case GenerationStatus.generating:
        return 'Generating';
      case GenerationStatus.completed:
        return 'Completed';
      case GenerationStatus.failed:
        return 'Failed';
      case GenerationStatus.cancelled:
        return 'Cancelled';
    }
  }

  String _documentTypeToString(DocumentType type) {
    switch (type) {
      case DocumentType.resume:
        return 'Resume';
      case DocumentType.coverLetter:
        return 'Cover Letter';
    }
  }
}

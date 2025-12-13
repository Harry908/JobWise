import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../models/job.dart';
import '../providers/generations_provider.dart';
import 'package:intl/intl.dart';

/// Tab widget for AI generation features on job detail screen
class JobGenerationTab extends ConsumerStatefulWidget {
  final Job job;

  const JobGenerationTab({
    super.key,
    required this.job,
  });

  @override
  ConsumerState<JobGenerationTab> createState() => _JobGenerationTabState();
}

class _JobGenerationTabState extends ConsumerState<JobGenerationTab> {
  // Resume generation options
  int _maxExperiences = 5;
  int _maxProjects = 3;
  bool _includeSummary = true;

  // Cover letter generation options
  final _companyNameController = TextEditingController();
  final _hiringManagerController = TextEditingController();
  int _maxParagraphs = 3;

  @override
  void initState() {
    super.initState();
    // Pre-fill company name from job
    _companyNameController.text = widget.job.company;
    // Load generation history for this job
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(generationsProvider.notifier).fetchHistoryForJob(widget.job.id);
    });
  }

  @override
  void dispose() {
    _companyNameController.dispose();
    _hiringManagerController.dispose();
    super.dispose();
  }

  Future<void> _generateResume() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Generate Resume'),
        content: Text(
          'Generate a tailored resume for ${widget.job.title} at ${widget.job.company}?\n\n'
          'Settings:\n'
          '• Max experiences: $_maxExperiences\n'
          '• Max projects: $_maxProjects\n'
          '• Include summary: ${_includeSummary ? "Yes" : "No"}',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Generate'),
          ),
        ],
      ),
    );

    if (confirmed != true || !mounted) return;

    // Show progress modal
    _showProgressDialog();

    try {
      await ref.read(generationsProvider.notifier).generateResume(
            jobId: widget.job.id,
            maxExperiences: _maxExperiences,
            maxProjects: _maxProjects,
            includeSummary: _includeSummary,
          );

      if (!mounted) return;

      // Close progress dialog
      Navigator.of(context, rootNavigator: true).pop();

      final state = ref.read(generationsProvider);
      if (state.errorMessage != null) {
        _showErrorSnackBar(state.errorMessage!);
      } else if (state.lastGeneration != null) {
        // Refresh history
        ref.read(generationsProvider.notifier).fetchHistoryForJob(widget.job.id);
        // Show result
        _showResultDialog(state.lastGeneration!);
      }
    } catch (e) {
      if (!mounted) return;
      Navigator.of(context, rootNavigator: true).pop();
      _showErrorSnackBar(e.toString());
    }
  }

  Future<void> _generateCoverLetter() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Generate Cover Letter'),
        content: Text(
          'Generate a tailored cover letter for ${widget.job.title} at ${widget.job.company}?\n\n'
          'Settings:\n'
          '• Company: ${_companyNameController.text}\n'
          '• Hiring manager: ${_hiringManagerController.text.isEmpty ? "Not specified" : _hiringManagerController.text}\n'
          '• Max paragraphs: $_maxParagraphs',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Generate'),
          ),
        ],
      ),
    );

    if (confirmed != true || !mounted) return;

    // Show progress modal
    _showProgressDialog();

    try {
      await ref.read(generationsProvider.notifier).generateCoverLetter(
            jobId: widget.job.id,
            companyName: _companyNameController.text.isNotEmpty ? _companyNameController.text : null,
            hiringManagerName: _hiringManagerController.text.isNotEmpty ? _hiringManagerController.text : null,
            maxParagraphs: _maxParagraphs,
          );

      if (!mounted) return;

      // Close progress dialog
      Navigator.of(context, rootNavigator: true).pop();

      final state = ref.read(generationsProvider);
      if (state.errorMessage != null) {
        _showErrorSnackBar(state.errorMessage!);
      } else if (state.lastGeneration != null) {
        // Refresh history
        ref.read(generationsProvider.notifier).fetchHistoryForJob(widget.job.id);
        // Show result
        _showResultDialog(state.lastGeneration!);
      }
    } catch (e) {
      if (!mounted) return;
      Navigator.of(context, rootNavigator: true).pop();
      _showErrorSnackBar(e.toString());
    }
  }

  void _showProgressDialog() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => PopScope(
        canPop: false,
        child: Dialog(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Consumer(
              builder: (context, ref, _) {
                final state = ref.watch(generationsProvider);
                return Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    CircularProgressIndicator(
                      value: state.progress > 0 ? state.progress : null,
                    ),
                    const SizedBox(height: 24),
                    Text(
                      state.currentStage ?? 'Generating...',
                      style: Theme.of(context).textTheme.bodyLarge,
                      textAlign: TextAlign.center,
                    ),
                    if (state.progress > 0) ...[
                      const SizedBox(height: 12),
                      Text(
                        '${(state.progress * 100).toInt()}%',
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              color: Theme.of(context).colorScheme.primary,
                            ),
                      ),
                    ],
                  ],
                );
              },
            ),
          ),
        ),
      ),
    );
  }

  void _showResultDialog(Map<String, dynamic> generation) {
    final documentType = generation['document_type'] as String?;
    final text = generation['content_text'] as String?;
    final atsScore = generation['ats_score'] as num?;

    if (text == null || text.isEmpty) {
      _showErrorSnackBar('No generated text available');
      return;
    }

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Expanded(
              child: Text(
                documentType == 'resume' ? 'Generated Resume' : 'Generated Cover Letter',
              ),
            ),
            if (atsScore != null)
              Chip(
                label: Text('ATS: ${atsScore.toStringAsFixed(0)}'),
                backgroundColor: Theme.of(context).colorScheme.secondaryContainer,
              ),
          ],
        ),
        content: SizedBox(
          width: double.maxFinite,
          child: SingleChildScrollView(
            child: SelectableText(
              text,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(height: 1.5),
            ),
          ),
        ),
        actions: [
          TextButton.icon(
            onPressed: () {
              Clipboard.setData(ClipboardData(text: text));
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Copied to clipboard')),
              );
            },
            icon: const Icon(Icons.copy),
            label: const Text('Copy'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Theme.of(context).colorScheme.error,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Resume Generation Section
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(
                        Icons.description,
                        color: theme.colorScheme.primary,
                        size: 28,
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          'Generate Resume',
                          style: theme.textTheme.titleLarge?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Generate a tailored resume based on this job posting and your profile.',
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurface.withValues(alpha: 0.7),
                    ),
                  ),
                  const SizedBox(height: 20),
                  
                  // Max Experiences Slider
                  Text(
                    'Maximum Experiences: $_maxExperiences',
                    style: theme.textTheme.titleSmall,
                  ),
                  Slider(
                    value: _maxExperiences.toDouble(),
                    min: 1,
                    max: 10,
                    divisions: 9,
                    label: _maxExperiences.toString(),
                    onChanged: (value) {
                      setState(() {
                        _maxExperiences = value.toInt();
                      });
                    },
                  ),
                  const SizedBox(height: 12),
                  
                  // Max Projects Slider
                  Text(
                    'Maximum Projects: $_maxProjects',
                    style: theme.textTheme.titleSmall,
                  ),
                  Slider(
                    value: _maxProjects.toDouble(),
                    min: 0,
                    max: 10,
                    divisions: 10,
                    label: _maxProjects.toString(),
                    onChanged: (value) {
                      setState(() {
                        _maxProjects = value.toInt();
                      });
                    },
                  ),
                  const SizedBox(height: 12),
                  
                  // Include Summary Toggle
                  SwitchListTile(
                    title: const Text('Include Professional Summary'),
                    value: _includeSummary,
                    onChanged: (value) {
                      setState(() {
                        _includeSummary = value;
                      });
                    },
                    contentPadding: EdgeInsets.zero,
                  ),
                  const SizedBox(height: 16),
                  
                  // Generate Button
                  SizedBox(
                    width: double.infinity,
                    child: FilledButton.icon(
                      onPressed: _generateResume,
                      icon: const Icon(Icons.auto_awesome),
                      label: const Text('Generate Resume'),
                    ),
                  ),
                ],
              ),
            ),
          ),
          
          const SizedBox(height: 16),
          
          // Cover Letter Generation Section
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(
                        Icons.mail,
                        color: theme.colorScheme.primary,
                        size: 28,
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          'Generate Cover Letter',
                          style: theme.textTheme.titleLarge?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Generate a personalized cover letter for this position.',
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurface.withValues(alpha: 0.7),
                    ),
                  ),
                  const SizedBox(height: 20),
                  
                  // Company Name Field
                  TextField(
                    controller: _companyNameController,
                    decoration: const InputDecoration(
                      labelText: 'Company Name',
                      border: OutlineInputBorder(),
                      prefixIcon: Icon(Icons.business),
                    ),
                  ),
                  const SizedBox(height: 16),
                  
                  // Hiring Manager Field
                  TextField(
                    controller: _hiringManagerController,
                    decoration: const InputDecoration(
                      labelText: 'Hiring Manager Name (Optional)',
                      border: OutlineInputBorder(),
                      prefixIcon: Icon(Icons.person),
                    ),
                  ),
                  const SizedBox(height: 16),
                  
                  // Max Paragraphs Slider
                  Text(
                    'Maximum Paragraphs: $_maxParagraphs',
                    style: theme.textTheme.titleSmall,
                  ),
                  Slider(
                    value: _maxParagraphs.toDouble(),
                    min: 2,
                    max: 5,
                    divisions: 3,
                    label: _maxParagraphs.toString(),
                    onChanged: (value) {
                      setState(() {
                        _maxParagraphs = value.toInt();
                      });
                    },
                  ),
                  const SizedBox(height: 16),
                  
                  // Generate Button
                  SizedBox(
                    width: double.infinity,
                    child: FilledButton.icon(
                      onPressed: _generateCoverLetter,
                      icon: const Icon(Icons.auto_awesome),
                      label: const Text('Generate Cover Letter'),
                    ),
                  ),
                ],
              ),
            ),
          ),
          
          const SizedBox(height: 24),
          
          // Generation History Section
          _buildHistorySection(theme),
        ],
      ),
    );
  }

  Widget _buildHistorySection(ThemeData theme) {
    final state = ref.watch(generationsProvider);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(
              Icons.history,
              color: theme.colorScheme.secondary,
            ),
            const SizedBox(width: 8),
            Text(
              'Generation History',
              style: theme.textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        
        if (state.history.isEmpty)
          Card(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Center(
                child: Column(
                  children: [
                    Icon(
                      Icons.inbox_outlined,
                      size: 48,
                      color: theme.colorScheme.onSurface.withValues(alpha: 0.3),
                    ),
                    const SizedBox(height: 12),
                    Text(
                      'No generations yet',
                      style: theme.textTheme.bodyLarge?.copyWith(
                        color: theme.colorScheme.onSurface.withValues(alpha: 0.5),
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Generate a resume or cover letter to get started',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSurface.withValues(alpha: 0.5),
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            ),
          )
        else
          ...state.history.map((generation) => _buildHistoryCard(generation, theme)),
      ],
    );
  }

  Widget _buildHistoryCard(Map<String, dynamic> generation, ThemeData theme) {
    final documentType = generation['document_type'] as String?;
    final createdAt = generation['created_at'] as String?;
    final atsScore = generation['ats_score'] as num?;
    final generationId = generation['generation_id'] as String?;

    final isResume = documentType == 'resume';
    final timestamp = createdAt != null ? DateTime.tryParse(createdAt) : null;

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: InkWell(
        onTap: () => _showResultDialog(generation),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: isResume
                      ? theme.colorScheme.primaryContainer
                      : theme.colorScheme.secondaryContainer,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  isResume ? Icons.description : Icons.mail,
                  color: isResume
                      ? theme.colorScheme.onPrimaryContainer
                      : theme.colorScheme.onSecondaryContainer,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      isResume ? 'Resume' : 'Cover Letter',
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      timestamp != null ? _formatTimestamp(timestamp) : 'Unknown date',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSurface.withValues(alpha: 0.6),
                      ),
                    ),
                  ],
                ),
              ),
              if (atsScore != null)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: _getATSScoreColor(atsScore.toDouble()).withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                      color: _getATSScoreColor(atsScore.toDouble()),
                      width: 1.5,
                    ),
                  ),
                  child: Text(
                    'ATS: ${atsScore.toStringAsFixed(0)}',
                    style: theme.textTheme.labelMedium?.copyWith(
                      color: _getATSScoreColor(atsScore.toDouble()),
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              const SizedBox(width: 8),
              // Export Button
              FilledButton.tonalIcon(
                onPressed: () => _navigateToExport(generationId),
                icon: const Icon(Icons.upload_file, size: 18),
                label: const Text('Export'),
                style: FilledButton.styleFrom(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  minimumSize: const Size(0, 36),
                ),
              ),
              const SizedBox(width: 8),
              IconButton(
                icon: const Icon(Icons.delete_outline),
                onPressed: () => _deleteGeneration(generationId, documentType),
                color: theme.colorScheme.error,
                tooltip: 'Delete',
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _navigateToExport(String? generationId) {
    if (generationId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Unable to export: Generation ID not found')),
      );
      return;
    }

    // Navigate to export options screen with generation_id and job_id
    context.push(
      '/export/options',
      extra: {
        'generationId': generationId,
        'jobId': widget.job.id,
        'jobTitle': widget.job.title,
        'company': widget.job.company,
      },
    );
  }

  Future<void> _deleteGeneration(String? generationId, String? documentType) async {
    if (generationId == null) return;

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Generation'),
        content: Text(
          'Are you sure you want to delete this ${documentType == 'resume' ? 'resume' : 'cover letter'}? This action cannot be undone.',
        ),
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

    if (confirmed != true || !mounted) return;

    try {
      final success = await ref.read(generationsProvider.notifier).deleteGeneration(generationId);
      
      if (!mounted) return;
      
      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Generation deleted successfully')),
        );
      } else {
        final state = ref.read(generationsProvider);
        _showErrorSnackBar(state.errorMessage ?? 'Failed to delete generation');
      }
    } catch (e) {
      if (!mounted) return;
      _showErrorSnackBar(e.toString());
    }
  }

  String _formatTimestamp(DateTime timestamp) {
    final now = DateTime.now();
    final difference = now.difference(timestamp);

    if (difference.inMinutes < 1) {
      return 'Just now';
    } else if (difference.inHours < 1) {
      return '${difference.inMinutes}m ago';
    } else if (difference.inDays < 1) {
      return '${difference.inHours}h ago';
    } else if (difference.inDays < 7) {
      return '${difference.inDays}d ago';
    } else {
      return DateFormat('MMM d, yyyy').format(timestamp);
    }
  }

  Color _getATSScoreColor(double score) {
    if (score >= 80) {
      return Colors.green;
    } else if (score >= 60) {
      return Colors.orange;
    } else {
      return Colors.red;
    }
  }
}

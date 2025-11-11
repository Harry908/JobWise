import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/job_provider.dart';

/// Screen for pasting job description text
class JobPasteScreen extends ConsumerStatefulWidget {
  const JobPasteScreen({super.key});

  @override
  ConsumerState<JobPasteScreen> createState() => _JobPasteScreenState();
}

class _JobPasteScreenState extends ConsumerState<JobPasteScreen> {
  final _textController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  bool _isProcessing = false;

  @override
  void dispose() {
    _textController.dispose();
    super.dispose();
  }

  Future<void> _parseAndSave() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isProcessing = true);

    final job = await ref.read(jobProvider.notifier).createJobFromText(
          _textController.text.trim(),
        );

    setState(() => _isProcessing = false);

    if (!mounted) return;

    if (job != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Job saved: ${job.title}'),
          action: SnackBarAction(
            label: 'View',
            onPressed: () {
              Navigator.pushReplacementNamed(context, '/jobs/${job.id}');
            },
          ),
        ),
      );
      Navigator.pop(context);
    } else {
      final error = ref.read(jobProvider).error ?? 'Failed to parse job description';
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(error),
          backgroundColor: Theme.of(context).colorScheme.error,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Paste Job Description'),
      ),
      body: Form(
        key: _formKey,
        child: Column(
          children: [
            // Instructions Card
            Card(
              margin: const EdgeInsets.all(16),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          Icons.info_outline,
                          color: theme.colorScheme.primary,
                        ),
                        const SizedBox(width: 12),
                        Text(
                          'Instructions',
                          style: theme.textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Text(
                      '1. Copy a job description from any job board\n'
                      '2. Paste it in the text area below\n'
                      '3. Tap "Parse & Save" to extract details\n'
                      '4. Review and edit if needed',
                      style: theme.textTheme.bodyMedium?.copyWith(
                        height: 1.5,
                      ),
                    ),
                  ],
                ),
              ),
            ),

            // Text Input Area
            Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: TextFormField(
                  controller: _textController,
                  maxLines: null,
                  expands: true,
                  textAlignVertical: TextAlignVertical.top,
                  decoration: InputDecoration(
                    hintText: 'Paste job description here...\n\n'
                        'Example:\n'
                        'Senior Python Developer\n'
                        'TechCorp Inc.\n'
                        'Seattle, WA (Remote)\n\n'
                        'We are looking for...',
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    alignLabelWithHint: true,
                  ),
                  validator: (value) {
                    if (value == null || value.trim().isEmpty) {
                      return 'Please paste a job description';
                    }
                    if (value.trim().length < 50) {
                      return 'Job description is too short (min 50 characters)';
                    }
                    if (value.trim().length > 15000) {
                      return 'Job description is too long (max 15000 characters)';
                    }
                    return null;
                  },
                ),
              ),
            ),

            // Character Count
            Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Text(
                    '${_textController.text.length} / 15000 characters',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.onSurface.withValues(alpha: 0.6),
                    ),
                  ),
                ],
              ),
            ),

            // Action Buttons
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: theme.colorScheme.surface,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.1),
                    blurRadius: 4,
                    offset: const Offset(0, -2),
                  ),
                ],
              ),
              child: Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: _isProcessing
                          ? null
                          : () {
                              _textController.clear();
                            },
                      child: const Text('Clear'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    flex: 2,
                    child: FilledButton.icon(
                      onPressed: _isProcessing ? null : _parseAndSave,
                      icon: _isProcessing
                          ? const SizedBox(
                              width: 16,
                              height: 16,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                              ),
                            )
                          : const Icon(Icons.check),
                      label: Text(_isProcessing ? 'Processing...' : 'Parse & Save'),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

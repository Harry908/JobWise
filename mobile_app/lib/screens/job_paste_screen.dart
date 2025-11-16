import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../models/job.dart';
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

  @override
  void dispose() {
    _textController.dispose();
    super.dispose();
  }

  Future<void> _parseAndSave() async {
    if (!_formKey.currentState!.validate()) return;

    final jobToCreate = Job(
      id: '', // Handled by backend
      source: JobSource.userCreated,
      title: 'Pasted Job', // Placeholder, will be parsed
      company: 'Unknown', // Placeholder
      rawText: _textController.text.trim(),
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    );

    try {
      await ref.read(userJobsProvider.notifier).addJob(jobToCreate);

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Job saved successfully!'),
        ),
      );
      context.pop();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to save job: ${e.toString()}'),
          backgroundColor: Theme.of(context).colorScheme.error,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    // Listen to the provider state for loading/error feedback
    final userJobsState = ref.watch(userJobsProvider);
    final isProcessing = userJobsState.isLoading;

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
                          style: theme.textTheme.titleMedium
                              ?.copyWith(fontWeight: FontWeight.bold),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Text(
                      '1. Copy a job description from any job board\n'
                      '2. Paste it in the text area below\n'
                      '3. Tap "Save" to add it to your list',
                      style: theme.textTheme.bodyMedium?.copyWith(height: 1.5),
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
                  onChanged: (_) => setState(() {}), // To update character count
                ),
              ),
            ),

            // Character Count
            Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  Text(
                    '${_textController.text.length} / 15000',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.onSurface.withAlpha(153),
                    ),
                  ),
                ],
              ),
            ),

            // Action Buttons
            Container(
              padding: const EdgeInsets.all(16),
              width: double.infinity,
              child: FilledButton.icon(
                onPressed: isProcessing ? null : _parseAndSave,
                icon: isProcessing
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.save),
                label: Text(isProcessing ? 'Saving...' : 'Save Job'),
                style: FilledButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

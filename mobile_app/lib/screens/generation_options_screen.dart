import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../models/job.dart';
import '../models/generation.dart';
import '../providers/generation_provider.dart';
import '../providers/profile_provider.dart';
import '../widgets/loading_overlay.dart';

/// Screen for configuring generation options before starting resume/cover letter generation
class GenerationOptionsScreen extends ConsumerStatefulWidget {
  final Job job;
  final DocumentType documentType;

  const GenerationOptionsScreen({
    super.key,
    required this.job,
    this.documentType = DocumentType.resume,
  });

  @override
  ConsumerState<GenerationOptionsScreen> createState() =>
      _GenerationOptionsScreenState();
}

class _GenerationOptionsScreenState
    extends ConsumerState<GenerationOptionsScreen> {
  final _formKey = GlobalKey<FormState>();

  // Form fields
  String _selectedTemplate = 'modern';
  String _selectedLength = 'one_page';
  final List<String> _focusAreas = [];
  final _focusAreaController = TextEditingController();
  final _customInstructionsController = TextEditingController();

  bool _isGenerating = false;

  @override
  void dispose() {
    _focusAreaController.dispose();
    _customInstructionsController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final templatesAsync = ref.watch(generationTemplatesProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text(
          'Generate ${widget.documentType == DocumentType.resume ? 'Resume' : 'Cover Letter'}',
        ),
      ),
      body: Stack(
        children: [
          Form(
            key: _formKey,
            child: ListView(
              padding: const EdgeInsets.all(16.0),
              children: [
                // Job Info Card
                _buildJobInfoCard(theme),
                const SizedBox(height: 24),

                // Template Selection
                _buildTemplateSection(theme, templatesAsync),
                const SizedBox(height: 24),

                // Length Selection
                _buildLengthSelection(theme),
                const SizedBox(height: 24),

                // Focus Areas
                _buildFocusAreas(theme),
                const SizedBox(height: 24),

                // Custom Instructions
                _buildCustomInstructions(theme),
                const SizedBox(height: 32),

                // Generate Button
                _buildGenerateButton(theme),
                const SizedBox(height: 16),
              ],
            ),
          ),
          if (_isGenerating) const LoadingOverlay(),
        ],
      ),
    );
  }

  Widget _buildJobInfoCard(ThemeData theme) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Target Job',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              widget.job.title,
              style: theme.textTheme.titleLarge,
            ),
            const SizedBox(height: 4),
            Text(
              widget.job.company,
              style: theme.textTheme.bodyLarge?.copyWith(
                color: theme.colorScheme.primary,
              ),
            ),
            if (widget.job.location != null) ...[
              const SizedBox(height: 4),
              Text(
                widget.job.location!,
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildTemplateSection(
      ThemeData theme, AsyncValue<List<Template>> templatesAsync) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Template',
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        templatesAsync.when(
          data: (templates) {
            if (templates.isEmpty) {
              return _buildDefaultTemplates(theme);
            }
            return _buildTemplatesGrid(theme, templates);
          },
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (err, stack) => Column(
            children: [
              const Text('Could not load templates. Using default options.'),
              _buildDefaultTemplates(theme),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildDefaultTemplates(ThemeData theme) {
    final defaultTemplates = [
      {'id': 'modern', 'name': 'Modern'},
      {'id': 'classic', 'name': 'Classic'},
      {'id': 'creative', 'name': 'Creative'},
    ];

    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: defaultTemplates.map((template) {
        final isSelected = _selectedTemplate == template['id'];
        return ChoiceChip(
          label: Text(template['name']!),
          selected: isSelected,
          onSelected: (selected) {
            if (selected) {
              setState(() {
                _selectedTemplate = template['id']!;
              });
            }
          },
        );
      }).toList(),
    );
  }

  Widget _buildTemplatesGrid(ThemeData theme, List<Template> templates) {
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
        childAspectRatio: 1.2,
      ),
      itemCount: templates.length,
      itemBuilder: (context, index) {
        final template = templates[index];
        final isSelected = _selectedTemplate == template.id;

        return InkWell(
          onTap: () {
            setState(() {
              _selectedTemplate = template.id;
            });
          },
          borderRadius: BorderRadius.circular(12),
          child: Container(
            decoration: BoxDecoration(
              border: Border.all(
                color: isSelected
                    ? theme.colorScheme.primary
                    : theme.colorScheme.outline,
                width: isSelected ? 2 : 1,
              ),
              borderRadius: BorderRadius.circular(12),
              color: isSelected
                  ? theme.colorScheme.primaryContainer
                  : theme.colorScheme.surface,
            ),
            padding: const EdgeInsets.all(12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            template.name,
                            style: theme.textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                        if (isSelected)
                          Icon(
                            Icons.check_circle,
                            color: theme.colorScheme.primary,
                            size: 20,
                          ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      template.description,
                      style: theme.textTheme.bodySmall,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
                if (template.atsFriendly)
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: theme.colorScheme.secondaryContainer,
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      'ATS Friendly',
                      style: theme.textTheme.labelSmall?.copyWith(
                        color: theme.colorScheme.onSecondaryContainer,
                      ),
                    ),
                  ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildLengthSelection(ThemeData theme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Resume Length',
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        SegmentedButton<String>(
          segments: const [
            ButtonSegment<String>(
              value: 'one_page',
              label: Text('1 Page'),
              icon: Icon(Icons.description_outlined),
            ),
            ButtonSegment<String>(
              value: 'two_page',
              label: Text('2 Pages'),
              icon: Icon(Icons.description),
            ),
          ],
          selected: {_selectedLength},
          onSelectionChanged: (Set<String> newSelection) {
            setState(() {
              _selectedLength = newSelection.first;
            });
          },
        ),
      ],
    );
  }

  Widget _buildFocusAreas(ThemeData theme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Focus Areas (Optional)',
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          'Emphasize specific skills or experience areas',
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: TextFormField(
                controller: _focusAreaController,
                decoration: const InputDecoration(
                  labelText: 'Add focus area',
                  hintText: 'e.g., Leadership, Cloud Architecture',
                  border: OutlineInputBorder(),
                ),
                onFieldSubmitted: (value) => _addFocusArea(value),
              ),
            ),
            const SizedBox(width: 8),
            IconButton(
              onPressed: () => _addFocusArea(_focusAreaController.text),
              icon: const Icon(Icons.add),
              style: IconButton.styleFrom(
                backgroundColor: theme.colorScheme.primaryContainer,
              ),
            ),
          ],
        ),
        if (_focusAreas.isNotEmpty) ...[
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: _focusAreas.map((area) {
              return Chip(
                label: Text(area),
                onDeleted: () {
                  setState(() {
                    _focusAreas.remove(area);
                  });
                },
              );
            }).toList(),
          ),
        ],
      ],
    );
  }

  void _addFocusArea(String value) {
    final trimmed = value.trim();
    if (trimmed.isNotEmpty && !_focusAreas.contains(trimmed)) {
      if (_focusAreas.length < 5) {
        setState(() {
          _focusAreas.add(trimmed);
          _focusAreaController.clear();
        });
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Maximum 5 focus areas allowed'),
          ),
        );
      }
    }
  }

  Widget _buildCustomInstructions(ThemeData theme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Custom Instructions (Optional)',
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          'Additional tailoring instructions for the AI (max 500 characters)',
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        const SizedBox(height: 12),
        TextFormField(
          controller: _customInstructionsController,
          decoration: const InputDecoration(
            hintText:
                'e.g., Emphasize AWS experience, highlight team management skills',
            border: OutlineInputBorder(),
          ),
          maxLines: 4,
          maxLength: 500,
          validator: (value) {
            if (value != null && value.length > 500) {
              return 'Maximum 500 characters allowed';
            }
            return null;
          },
        ),
      ],
    );
  }

  Widget _buildGenerateButton(ThemeData theme) {
    return FilledButton.icon(
      onPressed: _isGenerating ? null : _handleGenerate,
      icon: const Icon(Icons.auto_awesome),
      label: Text(
        _isGenerating ? 'Generating...' : 'Generate ${widget.documentType == DocumentType.resume ? 'Resume' : 'Cover Letter'}',
      ),
      style: FilledButton.styleFrom(
        padding: const EdgeInsets.all(16),
        textStyle: theme.textTheme.titleMedium,
      ),
    );
  }

  Future<void> _handleGenerate() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    final profile = ref.read(profileProvider).value;
    if (profile == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please create a profile first'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    setState(() {
      _isGenerating = true;
    });

    try {
      final options = GenerationOptions(
        template: _selectedTemplate,
        length: _selectedLength,
        focusAreas: _focusAreas,
        includeCoverLetter: widget.documentType == DocumentType.coverLetter,
        customInstructions: _customInstructionsController.text.trim().isEmpty
            ? null
            : _customInstructionsController.text.trim(),
      );

      final generationNotifier = ref.read(generationActionsProvider.notifier);
      
      Generation generation;
      if (widget.documentType == DocumentType.resume) {
        generation =
            await generationNotifier.startResumeGeneration(
                  profileId: profile.id,
                  jobId: widget.job.id,
                  options: options,
                );
      } else {
        generation = await generationNotifier.startCoverLetterGeneration(
              profileId: profile.id,
              jobId: widget.job.id,
              options: options,
            );
      }

      if (!mounted) return;

      context.push('/generations/${generation.id}/progress');
    } catch (e) {
      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to start generation: ${e.toString()}'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      if (mounted) {
        setState(() {
          _isGenerating = false;
        });
      }
    }
  }
}

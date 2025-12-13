import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/template.dart';
import '../../providers/exports/exports_provider.dart';

class ExportOptionsScreen extends ConsumerStatefulWidget {
  final String? generationId;
  final String? jobId;
  final String? documentType;

  const ExportOptionsScreen({
    super.key,
    this.generationId,
    this.jobId,
    this.documentType,
  });

  @override
  ConsumerState<ExportOptionsScreen> createState() => _ExportOptionsScreenState();
}

class _ExportOptionsScreenState extends ConsumerState<ExportOptionsScreen> {
  String? _selectedTemplateId;
  String _selectedFormat = 'pdf';
  final Map<String, dynamic> _customOptions = {};

  final List<String> _formats = ['pdf', 'docx'];

  bool get _isCoverLetter => widget.documentType == 'cover_letter';

  @override
  void initState() {
    super.initState();
    // Load templates when screen opens (skip for cover letters)
    if (!_isCoverLetter) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        ref.read(exportsNotifierProvider.notifier).loadTemplates();
      });
    } else {
      // For cover letters, auto-select a default template since it won't be used
      _selectedTemplateId = 'modern';
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(exportsNotifierProvider);
    final templates = state.templates;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Export Options'),
      ),
      body: state.isLoading && templates.isEmpty
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Error display
                  if (state.error != null) ...[
                    Card(
                      color: Colors.red.shade50,
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Row(
                          children: [
                            Icon(Icons.error_outline, color: Colors.red.shade700),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    'Failed to load templates',
                                    style: TextStyle(
                                      fontWeight: FontWeight.bold,
                                      color: Colors.red.shade900,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    state.error!,
                                    style: TextStyle(
                                      fontSize: 12,
                                      color: Colors.red.shade700,
                                    ),
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    'Make sure the backend server is running at http://localhost:8000',
                                    style: TextStyle(
                                      fontSize: 11,
                                      color: Colors.red.shade600,
                                      fontStyle: FontStyle.italic,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                  ],
                  // Generation/Job info
                  if (widget.generationId != null) ...[
                    _buildInfoCard(
                      'Generation',
                      'ID: ${widget.generationId}',
                      Icons.document_scanner,
                    ),
                    const SizedBox(height: 16),
                  ],
                  if (widget.jobId != null) ...[
                    _buildInfoCard(
                      'Job',
                      'ID: ${widget.jobId}',
                      Icons.work,
                    ),
                    const SizedBox(height: 16),
                  ],

                  // Template selection (only for resumes)
                  if (!_isCoverLetter) ...[
                    const Text(
                      'Choose Template',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),
                    ...templates.map((template) => _buildTemplateOption(template)),
                    if (templates.isEmpty && state.error == null)
                      const Padding(
                        padding: EdgeInsets.all(16),
                        child: Center(
                          child: Text(
                            'No templates available',
                            style: TextStyle(color: Colors.grey),
                          ),
                        ),
                      ),
                    const SizedBox(height: 24),
                  ],

                  // Cover letter info
                  if (_isCoverLetter) ...[
                    Card(
                      color: Theme.of(context).colorScheme.secondaryContainer,
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Row(
                          children: [
                            Icon(
                              Icons.info_outline,
                              color: Theme.of(context).colorScheme.onSecondaryContainer,
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                'Cover letters are exported as plain text without template styling.',
                                style: TextStyle(
                                  color: Theme.of(context).colorScheme.onSecondaryContainer,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 24),
                  ],

                  // Format selection
                  const Text(
                    'Export Format',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  ..._formats.map((format) => _buildFormatOption(format)),
                  const SizedBox(height: 24),

                  // Custom options (if template supports it and not a cover letter)
                  if (!_isCoverLetter && _selectedTemplateId != null) ...() {
                    final selectedTemplate = templates
                        .where((t) => t.id == _selectedTemplateId)
                        .firstOrNull;
                    if (selectedTemplate?.supportsCustomization != null) {
                      return [
                        const Text(
                          'Customization Options',
                          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 8),
                        _buildCustomizationOptions(selectedTemplate!.supportsCustomization),
                        const SizedBox(height: 24),
                      ];
                    }
                    return <Widget>[];
                  }(),

                  // Export button
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: _canExport ? _exportDocument : null,
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                      ),
                      child: state.isLoading
                          ? const CircularProgressIndicator()
                          : const Text('Export Document'),
                    ),
                  ),
                ],
              ),
            ),
    );
  }

  Widget _buildInfoCard(String title, String subtitle, IconData icon) {
    return Card(
      child: ListTile(
        leading: Icon(icon, color: Theme.of(context).primaryColor),
        title: Text(title),
        subtitle: Text(subtitle),
      ),
    );
  }

  Widget _buildTemplateOption(Template template) {
    final isSelected = _selectedTemplateId == template.id;

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      color: isSelected ? Theme.of(context).primaryColor.withValues(alpha: 0.1) : null,
      child: RadioListTile<String>(
        title: Text(template.name),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(template.description),
            const SizedBox(height: 4),
            Row(
              children: [
                Icon(
                  template.isHighAtsScore ? Icons.check_circle : Icons.info,
                  size: 16,
                  color: template.isHighAtsScore ? Colors.green : Colors.orange,
                ),
                const SizedBox(width: 4),
                Text(
                  template.atsScoreDisplay,
                  style: TextStyle(
                    fontSize: 12,
                    color: template.isHighAtsScore ? Colors.green : Colors.orange,
                  ),
                ),
              ],
            ),
            if (template.industries.isNotEmpty) ...[
              const SizedBox(height: 4),
              Text(
                'Industries: ${template.industries.join(", ")}',
                style: const TextStyle(fontSize: 12, color: Colors.grey),
              ),
            ],
          ],
        ),
        value: template.id,
        groupValue: _selectedTemplateId,
        onChanged: (value) {
          setState(() => _selectedTemplateId = value);
        },
      ),
    );
  }

  Widget _buildFormatOption(String format) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: RadioListTile<String>(
        title: Text(format.toUpperCase()),
        subtitle: Text(_getFormatDescription(format)),
        value: format,
        groupValue: _selectedFormat,
        onChanged: (value) {
          if (value != null) {
            setState(() => _selectedFormat = value);
          }
        },
      ),
    );
  }

  Widget _buildCustomizationOptions(TemplateCustomization customization) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (customization.fontFamily) ...[
              const Text('Font Family'),
              DropdownButton<String>(
                value: _customOptions['font_family'] ?? 'Arial',
                items: ['Arial', 'Times New Roman', 'Calibri', 'Helvetica']
                    .map((font) => DropdownMenuItem(
                          value: font,
                          child: Text(font),
                        ))
                    .toList(),
                onChanged: (value) {
                  if (value != null) {
                    setState(() => _customOptions['font_family'] = value);
                  }
                },
              ),
            ],
            if (customization.accentColor) ...[
              const SizedBox(height: 16),
              const Text('Accent Color'),
              DropdownButton<String>(
                value: _customOptions['accent_color'] ?? 'blue',
                items: ['blue', 'green', 'red', 'purple', 'orange']
                    .map((color) => DropdownMenuItem(
                          value: color,
                          child: Text(color.capitalize()),
                        ))
                    .toList(),
                onChanged: (value) {
                  if (value != null) {
                    setState(() => _customOptions['accent_color'] = value);
                  }
                },
              ),
            ],
          ],
        ),
      ),
    );
  }

  String _getFormatDescription(String format) {
    switch (format) {
      case 'pdf':
        return 'Portable Document Format - Best for printing and sharing';
      case 'docx':
        return 'Microsoft Word Document - Editable format';
      default:
        return '';
    }
  }

  bool get _canExport {
    return widget.generationId != null &&
           (_isCoverLetter || _selectedTemplateId != null) &&
           !ref.read(exportsNotifierProvider).isLoading;
  }

  void _exportDocument() async {
    if (!_canExport) return;

    try {
      final notifier = ref.read(exportsNotifierProvider.notifier);

      if (_selectedFormat == 'pdf') {
        await notifier.exportToPDF(
          generationId: widget.generationId!,
          templateId: _selectedTemplateId!,
          options: _customOptions.isNotEmpty ? _customOptions : null,
        );
      } else if (_selectedFormat == 'docx') {
        await notifier.exportToDOCX(
          generationId: widget.generationId!,
          templateId: _selectedTemplateId!,
          options: _customOptions.isNotEmpty ? _customOptions : null,
        );
      }

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Document exported successfully!')),
        );
        Navigator.of(context).pop();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Export failed: $e')),
        );
      }
    }
  }
}

extension StringExtension on String {
  String capitalize() {
    return "${this[0].toUpperCase()}${substring(1)}";
  }
}

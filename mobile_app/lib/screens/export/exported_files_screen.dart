import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../models/exported_file.dart';
import '../../providers/exports/exports_provider.dart';
import '../../widgets/error_display.dart';
import 'export_actions_sheet.dart';
import 'export_options_screen.dart';

class ExportedFilesScreen extends ConsumerStatefulWidget {
  final String? jobId;

  const ExportedFilesScreen({super.key, this.jobId});

  @override
  ConsumerState<ExportedFilesScreen> createState() => _ExportedFilesScreenState();
}

class _ExportedFilesScreenState extends ConsumerState<ExportedFilesScreen> {
  String? _selectedFormat;
  final List<String> _formats = ['pdf', 'docx', 'zip'];

  @override
  void initState() {
    super.initState();
    // Load exported files when screen opens
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(exportsNotifierProvider.notifier).loadExportedFiles(jobId: widget.jobId);
      ref.read(exportsNotifierProvider.notifier).loadTemplates();
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(exportsNotifierProvider);
    final jobFiles = ref.watch(selectedJobExportedFilesProvider);
    final fileCountByFormat = ref.watch(exportedFilesByFormatProvider);
    final totalSize = ref.watch(totalExportSizeProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text(widget.jobId != null ? 'Job Exports' : 'All Exports'),
        actions: [
          IconButton(
            icon: const Icon(Icons.filter_list),
            onPressed: _showFilterDialog,
          ),
        ],
      ),
      body: Column(
        children: [
          // Summary cards
          _buildSummaryCards(fileCountByFormat, totalSize),

          // Files list
          Expanded(
            child: state.isLoading && jobFiles.isEmpty
                ? const Center(child: CircularProgressIndicator())
                : state.error != null
                    ? ErrorDisplay(
                        message: state.error!,
                        onRetry: () => ref
                            .read(exportsNotifierProvider.notifier)
                            .loadExportedFiles(jobId: widget.jobId),
                      )
                    : jobFiles.isEmpty
                        ? _buildEmptyState()
                        : _buildFilesList(jobFiles),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _showExportOptions,
        tooltip: 'New Export',
        child: const Icon(Icons.add),
      ),
    );
  }

  Widget _buildSummaryCards(Map<String, int> fileCountByFormat, String totalSize) {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          Expanded(
            child: _SummaryCard(
              title: 'Total Files',
              value: fileCountByFormat.values.fold(0, (a, b) => a + b).toString(),
              icon: Icons.file_copy,
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: _SummaryCard(
              title: 'Storage Used',
              value: totalSize,
              icon: Icons.storage,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.file_download_off,
            size: 64,
            color: Colors.grey[400],
          ),
          const SizedBox(height: 16),
          Text(
            widget.jobId != null
                ? 'No exports for this job yet'
                : 'No exported files yet',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 8),
          Text(
            'Create your first export to get started',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Colors.grey[600],
                ),
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: _showExportOptions,
            icon: const Icon(Icons.add),
            label: const Text('Create Export'),
          ),
        ],
      ),
    );
  }

  Widget _buildFilesList(List<ExportedFile> files) {
    final filteredFiles = _selectedFormat != null
        ? files.where((file) => file.format == _selectedFormat).toList()
        : files;

    return RefreshIndicator(
      onRefresh: () => ref
          .read(exportsNotifierProvider.notifier)
          .loadExportedFiles(jobId: widget.jobId),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: filteredFiles.length,
        itemBuilder: (context, index) {
          final file = filteredFiles[index];
          return _ExportedFileCard(
            file: file,
            onTap: () => _showFileActions(file),
          );
        },
      ),
    );
  }

  void _showFilterDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Filter by Format'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            RadioListTile<String?>(
              title: const Text('All Formats'),
              value: null,
              groupValue: _selectedFormat,
              onChanged: (value) {
                setState(() => _selectedFormat = value);
                Navigator.of(context).pop();
              },
            ),
            ..._formats.map((format) => RadioListTile<String?>(
                  title: Text(format.toUpperCase()),
                  value: format,
                  groupValue: _selectedFormat,
                  onChanged: (value) {
                    setState(() => _selectedFormat = value);
                    Navigator.of(context).pop();
                  },
                )),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
        ],
      ),
    );
  }

  void _showExportOptions() {
    // Navigate to export options screen
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => ExportOptionsScreen(
          generationId: null, // TODO: Pass actual generation ID from context
          jobId: widget.jobId,
        ),
      ),
    );
  }

  void _showFileActions(ExportedFile file) {
    showModalBottomSheet(
      context: context,
      builder: (context) => ExportActionsSheet(
        file: file,
        onDownload: () => _downloadFile(file),
        onDelete: () => _deleteFile(file),
        onShare: () => _shareFile(file),
      ),
    );
  }

  void _downloadFile(ExportedFile file) async {
    try {
      // Show download progress
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Downloading ${file.filename}...')),
      );

      // TODO: Implement actual download with progress tracking
      // await ref.read(exportsNotifierProvider.notifier).downloadFile(file);

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Download completed!')),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Download failed: $e')),
      );
    }
  }

  void _deleteFile(ExportedFile file) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete File'),
        content: Text('Are you sure you want to delete "${file.filename}"?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('Delete'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      try {
        await ref.read(exportsNotifierProvider.notifier).deleteFile(file.exportId);
        if (!context.mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('File deleted successfully')),
        );
      } catch (e) {
        if (!context.mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to delete file: $e')),
        );
      }
    }
  }

  void _shareFile(ExportedFile file) {
    // TODO: Implement file sharing
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Sharing feature coming soon!')),
    );
  }
}

class _SummaryCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;

  const _SummaryCard({
    required this.title,
    required this.value,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(icon, size: 32, color: Theme.of(context).primaryColor),
            const SizedBox(height: 8),
            Text(
              value,
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            Text(
              title,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
      ),
    );
  }
}

class _ExportedFileCard extends StatelessWidget {
  final ExportedFile file;
  final VoidCallback onTap;

  const _ExportedFileCard({
    required this.file,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Icon(
          _getFormatIcon(file.format),
          color: _getFormatColor(file.format),
          size: 32,
        ),
        title: Text(
          file.filename,
          maxLines: 2,
          overflow: TextOverflow.ellipsis,
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '${file.formattedFileSize} • ${file.template} • ${DateFormat.yMMMd().format(file.createdAt)}',
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            if (file.isExpired) ...[
              const SizedBox(height: 4),
              Text(
                'Expired',
                style: TextStyle(
                  color: Colors.red[400],
                  fontSize: 12,
                ),
              ),
            ],
          ],
        ),
        trailing: IconButton(
          icon: const Icon(Icons.more_vert),
          onPressed: onTap,
        ),
        onTap: onTap,
      ),
    );
  }

  IconData _getFormatIcon(String format) {
    switch (format.toLowerCase()) {
      case 'pdf':
        return Icons.picture_as_pdf;
      case 'docx':
        return Icons.description;
      case 'zip':
        return Icons.archive;
      default:
        return Icons.insert_drive_file;
    }
  }

  Color _getFormatColor(String format) {
    switch (format.toLowerCase()) {
      case 'pdf':
        return Colors.red;
      case 'docx':
        return Colors.blue;
      case 'zip':
        return Colors.orange;
      default:
        return Colors.grey;
    }
  }
}

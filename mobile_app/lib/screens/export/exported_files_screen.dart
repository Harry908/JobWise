import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import 'package:path_provider/path_provider.dart';
import 'package:open_file/open_file.dart';
import 'dart:io';

import '../../models/exported_file.dart';
import '../../providers/exports/exports_provider.dart';
import '../../providers/job_provider.dart';
import '../../models/job.dart';
import '../../services/export_cache_service.dart';
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

    // Group files by job
    final groupedFiles = <String, List<ExportedFile>>{};
    for (final file in filteredFiles) {
      final jobKey = file.jobId ?? 'no-job';
      if (!groupedFiles.containsKey(jobKey)) {
        groupedFiles[jobKey] = [];
      }
      groupedFiles[jobKey]!.add(file);
    }

    // Preload job details for groups (so we can show job titles when metadata is missing)
    final jobDetails = <String, AsyncValue<Job?>>{};
    for (final jobId in groupedFiles.keys) {
      if (jobId == 'no-job') continue;
      jobDetails[jobId] = ref.watch(selectedJobProvider(jobId));
    }

    return RefreshIndicator(
      onRefresh: () => ref
          .read(exportsNotifierProvider.notifier)
          .loadExportedFiles(jobId: widget.jobId),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: groupedFiles.keys.length,
        itemBuilder: (context, index) {
          final jobId = groupedFiles.keys.elementAt(index);
          final jobFiles = groupedFiles[jobId]!;
          
          // Get job title from metadata (use first file's metadata)
          // Prefer API job title if available, then exported metadata, then fallback
          final metadataTitle = jobFiles.first.metadata?['job_title'] as String?;
          final metadataCompany = jobFiles.first.metadata?['company'] as String?;
          String jobTitle = metadataTitle ?? (jobId != 'no-job' ? jobId : 'Untitled Job');
          String? company = metadataCompany;

          if (jobId != 'no-job') {
            final maybeJob = jobDetails[jobId];
            if (maybeJob != null) {
              maybeJob.maybeWhen(
                data: (job) {
                  if (job != null) {
                    jobTitle = job.title ?? jobTitle;
                    company = job.company ?? company;
                  }
                },
                orElse: () {},
              );
            }
          }
          
          return _JobExportsGroup(
            jobId: jobId == 'no-job' ? null : jobId,
            jobTitle: jobTitle,
            company: company,
            files: jobFiles,
            onFileTap: _showFileActions,
            onFileOpen: (f) async {
              final isDownloaded = f.localCachePath != null && f.cacheExpiresAt != null && DateTime.now().isBefore(f.cacheExpiresAt!);
              if (isDownloaded) {
                await _openFile(f);
              } else {
                await _downloadFile(f);
              }
            },
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
        onSaveAs: () => _saveAs(file),
        onDelete: () => _deleteFile(file),
        onShare: () => _shareFile(file),
      ),
    );
  }

  Future<void> _openFile(ExportedFile file) async {
    try {
      final isCacheValid = await file.isCacheValid();
      if (!isCacheValid) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('File is not downloaded. Please download first.')),
        );
        return;
      }

      final filePath = file.localCachePath!;
      final result = await OpenFile.open(filePath);
      if (!context.mounted) return;
      if (result.type != ResultType.done) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Failed to open file')),
        );
      }
    } catch (e) {
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to open file: $e')),
      );
    }
  }

  Future<void> _downloadFile(ExportedFile file) async {
    try {
      // If cache is valid, open directly
      final isCacheValid = await file.isCacheValid();
      if (isCacheValid) {
        final cachePath = file.localCachePath!;
        final result = await OpenFile.open(cachePath);
        if (!context.mounted) return;
        if (result.type != ResultType.done) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Failed to open cached file')),
          );
        }
        return;
      }

      // Build cache path and prepare directory
      final directory = await getApplicationDocumentsDirectory();
      final cacheDir = Directory('${directory.path}/exports');
      if (!await cacheDir.exists()) {
        await cacheDir.create(recursive: true);
      }
      final cachePath = '${cacheDir.path}/${file.exportId}.${file.format}';

      final progressNotifier = ValueNotifier<double>(0.0);
      final dialogFuture = showDialog<void>(
        context: context,
        barrierDismissible: false,
        builder: (context) => AlertDialog(
          title: Text('Downloading ${file.filename}'),
          content: ValueListenableBuilder<double>(
            valueListenable: progressNotifier,
            builder: (context, value, _) {
              return Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  LinearProgressIndicator(value: value),
                  const SizedBox(height: 12),
                  Text('${(value * 100).round()}%'),
                ],
              );
            },
          ),
        ),
      );

      try {
        await ref.read(exportsNotifierProvider.notifier).downloadExport(
              file.exportId,
              cachePath,
              onProgress: (p) {
                progressNotifier.value = p;
              },
            );
      } finally {
        if (Navigator.of(context).canPop()) Navigator.of(context).pop();
        progressNotifier.dispose();
        await dialogFuture;
      }

      // Reload exports to update UI with downloaded state
      await ref.read(exportsNotifierProvider.notifier).loadExportedFiles(jobId: widget.jobId);

      // Mark as downloaded — do not open automatically
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Download completed')),
      );
      return;
    } catch (e) {
      if (!context.mounted) return;
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

  Future<void> _saveAs(ExportedFile file) async {
    try {
      // First ensure file is downloaded to cache
      final isCacheValid = await file.isCacheValid();
      String sourcePath;

      if (isCacheValid) {
        sourcePath = file.localCachePath!;
      } else {
        // Download to cache first
        final directory = await getApplicationDocumentsDirectory();
        final cacheDir = Directory('${directory.path}/exports');
        if (!await cacheDir.exists()) {
          await cacheDir.create(recursive: true);
        }
        final tempCachePath = '${cacheDir.path}/${file.exportId}.${file.format}';

        final progressNotifier = ValueNotifier<double>(0.0);
        showDialog<void>(
          context: context,
          barrierDismissible: false,
          builder: (context) => AlertDialog(
            title: Text('Downloading ${file.filename}'),
            content: ValueListenableBuilder<double>(
              valueListenable: progressNotifier,
              builder: (context, value, _) => Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  LinearProgressIndicator(value: value),
                  const SizedBox(height: 12),
                  Text('${(value * 100).round()}%'),
                ],
              ),
            ),
          ),
        );

        try {
          await ref.read(exportsNotifierProvider.notifier).downloadExport(
                file.exportId,
                tempCachePath,
                onProgress: (p) => progressNotifier.value = p,
              );
          sourcePath = tempCachePath;
        } finally {
          if (Navigator.of(context).canPop()) Navigator.of(context).pop();
          progressNotifier.dispose();
        }
      }

      // Read file bytes and use saveFile with bytes (required on Android/iOS)
      final sourceFile = File(sourcePath);
      final bytes = await sourceFile.readAsBytes();
      
      final result = await FilePicker.platform.saveFile(
        dialogTitle: 'Save ${file.filename}',
        fileName: file.filename,
        type: FileType.any,
        bytes: bytes,
      );

      if (result == null) {
        return; // User cancelled
      }

      // Update persisted cache with user save path
      final cacheService = ExportCacheService();
      final existingInfo = await cacheService.getCacheInfo(file.exportId);
      if (existingInfo != null) {
        await cacheService.saveCacheInfo(
          file.exportId,
          CachedExportInfo(
            localPath: existingInfo.localPath,
            downloadedAt: existingInfo.downloadedAt,
            expiresAt: existingInfo.expiresAt,
            userSavePath: result,
          ),
        );
      }

      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Saved to: $result')),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Save failed: $e')),
      );
    }
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

class _JobExportsGroup extends StatelessWidget {
  final String jobTitle;
  final String? company;
  final String? jobId;
  final List<ExportedFile> files;
  final void Function(ExportedFile) onFileTap;
  final void Function(ExportedFile) onFileOpen;

  const _JobExportsGroup({
    required this.jobTitle,
    this.company,
    this.jobId,
    required this.files,
    required this.onFileTap,
    required this.onFileOpen,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Job header (clickable, navigates to job detail if available)
          InkWell(
            onTap: jobId == null || jobId == 'no-job'
                ? null
                : () => context.push('/jobs/$jobId'),
            child: Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Theme.of(context).primaryColor.withOpacity(0.1),
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(12),
                topRight: Radius.circular(12),
              ),
            ),
                child: Row(
              children: [
                Icon(
                  Icons.work_outline,
                  color: Theme.of(context).primaryColor,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        jobTitle,
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      if (company != null) ...[
                        const SizedBox(height: 2),
                        Text(
                          company!,
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                color: Colors.grey[600],
                              ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Theme.of(context).primaryColor,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    '${files.length}',
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
            ),
          ),
          // Files list
          ...files.map((file) => _ExportedFileCard(
                file: file,
                onTap: () => onFileTap(file),
                onOpen: () => onFileOpen(file),
              )),
        ],
      ),
    );
  }
}

class _ExportedFileCard extends StatelessWidget {
  final ExportedFile file;
  final VoidCallback onTap;
  final VoidCallback onOpen;

  const _ExportedFileCard({
    required this.file,
    required this.onTap,
    required this.onOpen,
  });

  bool get _isDownloaded {
    return file.localCachePath != null && file.cacheExpiresAt != null && DateTime.now().isBefore(file.cacheExpiresAt!);
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
        leading: Icon(
          _getFormatIcon(file.format),
          color: _getFormatColor(file.format),
          size: 38,
        ),
        title: Text(
          file.filename,
          maxLines: 2,
          overflow: TextOverflow.ellipsis,
          style: Theme.of(context).textTheme.titleMedium,
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    '${file.formattedFileSize} • ${file.template} • ${DateFormat.yMMMd().format(file.createdAt)}',
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                if (_isDownloaded) ...[
                  const SizedBox(width: 8),
                  Chip(
                    label: const Text('Downloaded'),
                    backgroundColor: Colors.green[50],
                    labelStyle: TextStyle(color: Colors.green[800], fontSize: 12),
                  ),
                ],
              ],
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
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            IconButton(
              icon: Icon(_isDownloaded ? Icons.open_in_new : Icons.download),
              onPressed: onOpen,
              tooltip: _isDownloaded ? 'Open' : 'Download',
            ),
            IconButton(
              icon: const Icon(Icons.more_vert),
              onPressed: onTap,
            ),
          ],
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

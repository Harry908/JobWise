import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:open_file/open_file.dart';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';
import '../../models/exported_file.dart';
import '../../providers/exports/exports_provider.dart';

/// Screen showing all exports for a specific job, grouped by date
class JobExportsScreen extends ConsumerStatefulWidget {
  final String jobId;
  final String? jobTitle;
  final String? companyName;

  const JobExportsScreen({
    super.key,
    required this.jobId,
    this.jobTitle,
    this.companyName,
  });

  @override
  ConsumerState<JobExportsScreen> createState() => _JobExportsScreenState();
}

class _JobExportsScreenState extends ConsumerState<JobExportsScreen> {
  bool _isLoading = false;
  Map<String, List<ExportedFile>> _exportsByDate = {};
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadExports();
  }

  Future<void> _loadExports() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final result = await ref
          .read(exportsNotifierProvider.notifier)
          .loadJobExports(widget.jobId);

      setState(() {
        _exportsByDate = result;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _openExport(ExportedFile export) async {
    try {
      // Check if cache is valid and open only if it is cached
      final isCacheValid = await export.isCacheValid();

      if (!isCacheValid) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('File is not downloaded. Please download first.')),
        );
        return;
      }

      final filePath = export.localCachePath!;

      // Open file from cache
      final result = await OpenFile.open(filePath);
      if (!mounted) return;
      if (result.type != ResultType.done) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to open file: ${result.message}'),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error opening file: $e'),
          backgroundColor: Theme.of(context).colorScheme.error,
        ),
      );
    }
  }

  Future<void> _shareExport(ExportedFile export) async {
    try {
      // Ensure file is cached
      final isCacheValid = await export.isCacheValid();
      
      String filePath;
      if (isCacheValid) {
        filePath = export.localCachePath!;
      } else {
        // Download first
        if (!mounted) return;
        
        showDialog(
          context: context,
          barrierDismissible: false,
          builder: (context) => const AlertDialog(
            content: Row(
              children: [
                CircularProgressIndicator(),
                SizedBox(width: 16),
                Text('Preparing to share...'),
              ],
            ),
          ),
        );

        final directory = await getApplicationDocumentsDirectory();
        final cachePath = '${directory.path}/exports/${export.exportId}.${export.format}';
        
        final cacheDir = Directory('${directory.path}/exports');
        if (!await cacheDir.exists()) {
          await cacheDir.create(recursive: true);
        }

        await ref
            .read(exportsNotifierProvider.notifier)
            .downloadExport(export.exportId, cachePath);

        if (!mounted) return;
        Navigator.of(context).pop(); // Close preparing dialog

        filePath = cachePath;
      }

      // Share file
      await Share.shareXFiles(
        [XFile(filePath)],
        subject: export.filename,
      );
    } catch (e) {
      if (!mounted) return;
      
      if (Navigator.of(context).canPop()) {
        Navigator.of(context).pop();
      }
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error sharing file: $e'),
          backgroundColor: Theme.of(context).colorScheme.error,
        ),
      );
    }
  }

  Future<void> _deleteExport(ExportedFile export) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Export'),
        content: Text('Are you sure you want to delete "${export.filename}"?'),
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

    if (confirmed != true) return;

    try {
      await ref
          .read(exportsNotifierProvider.notifier)
          .deleteExport(export.exportId);

      if (!mounted) return;
      
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Export deleted successfully')),
      );

      // Reload exports
      _loadExports();
    } catch (e) {
      if (!mounted) return;
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to delete export: $e'),
          backgroundColor: Theme.of(context).colorScheme.error,
        ),
      );
    }
  }

  Future<void> _downloadExportOnly(ExportedFile export) async {
    try {
      // If already cached, notify
      final isCacheValid = await export.isCacheValid();
      if (isCacheValid) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('File already downloaded')),
        );
        return;
      }

      // Build cache path
      final directory = await getApplicationDocumentsDirectory();
      final cacheDir = Directory('${directory.path}/exports');
      if (!await cacheDir.exists()) {
        await cacheDir.create(recursive: true);
      }
      final cachePath = '${cacheDir.path}/${export.exportId}.${export.format}';

      final progressNotifier = ValueNotifier<double>(0.0);
      final dialogFuture = showDialog<void>(
        context: context,
        barrierDismissible: false,
        builder: (context) => AlertDialog(
          title: Text('Downloading ${export.filename}'),
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
              export.exportId,
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

      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Download completed')),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Download failed: $e')),
      );
    }
  }

  String _formatDate(String dateString) {
    final date = DateTime.parse(dateString);
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final yesterday = today.subtract(const Duration(days: 1));
    final exportDate = DateTime(date.year, date.month, date.day);

    if (exportDate == today) {
      return 'Today';
    } else if (exportDate == yesterday) {
      return 'Yesterday';
    } else {
      return '${_monthName(date.month)} ${date.day}, ${date.year}';
    }
  }

  String _monthName(int month) {
    const months = [
      'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ];
    return months[month - 1];
  }

  int get _totalExports => _exportsByDate.values
      .fold(0, (sum, list) => sum + list.length);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Storage'),
            if (widget.jobTitle != null)
              Text(
                widget.jobTitle!,
                style: Theme.of(context).textTheme.bodySmall,
              ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadExports,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.error_outline,
                        size: 64,
                        color: Theme.of(context).colorScheme.error,
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'Error loading exports',
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      const SizedBox(height: 8),
                      Text(_error!),
                      const SizedBox(height: 16),
                      FilledButton(
                        onPressed: _loadExports,
                        child: const Text('Retry'),
                      ),
                    ],
                  ),
                )
              : _exportsByDate.isEmpty
                  ? _buildEmptyState()
                  : RefreshIndicator(
                      onRefresh: _loadExports,
                      child: ListView(
                        padding: const EdgeInsets.all(16),
                        children: [
                          // Header with stats
                          _buildHeader(),
                          const SizedBox(height: 24),
                          
                          // Exports grouped by date
                          ..._buildExportsList(),
                        ],
                      ),
                    ),
    );
  }

  Widget _buildHeader() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildStat(
                  icon: Icons.file_present,
                  label: 'Total Exports',
                  value: _totalExports.toString(),
                ),
                _buildStat(
                  icon: Icons.work_outline,
                  label: 'Job',
                  value: widget.companyName ?? 'Unknown',
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStat({
    required IconData icon,
    required String label,
    required String value,
  }) {
    return Column(
      children: [
        Icon(icon, size: 32, color: Theme.of(context).colorScheme.primary),
        const SizedBox(height: 8),
        Text(
          value,
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        Text(
          label,
          style: Theme.of(context).textTheme.bodySmall,
        ),
      ],
    );
  }

  List<Widget> _buildExportsList() {
    final sortedDates = _exportsByDate.keys.toList()
      ..sort((a, b) => b.compareTo(a)); // Most recent first

    return sortedDates.expand((date) {
      final exports = _exportsByDate[date]!;
      
      return [
        // Date header
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: Text(
            _formatDate(date),
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
        ),
        
        // Export cards
        ...exports.map((export) => _buildExportCard(export)),
        
        const SizedBox(height: 16),
      ];
    }).toList();
  }

  Widget _buildExportCard(ExportedFile export) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
        leading: CircleAvatar(
          radius: 22,
          child: Text(export.formatIcon),
        ),
        title: Text(
          export.filename,
          maxLines: 2,
          overflow: TextOverflow.ellipsis,
          style: Theme.of(context).textTheme.titleMedium,
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(child: Text('${export.templateDisplayName} • ${export.formattedFileSize}')),
                if (export.localCachePath != null && export.cacheExpiresAt != null && DateTime.now().isBefore(export.cacheExpiresAt!)) ...[
                  const SizedBox(width: 8),
                  Chip(
                    label: const Text('Downloaded'),
                    backgroundColor: Colors.green[50],
                    labelStyle: TextStyle(color: Colors.green[800], fontSize: 12),
                  ),
                ],
              ],
            ),
          ],
        ),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            IconButton(
              icon: Icon((export.localCachePath != null && export.cacheExpiresAt != null && DateTime.now().isBefore(export.cacheExpiresAt!)) ? Icons.open_in_new : Icons.download),
              onPressed: () {
                if (export.localCachePath != null && export.cacheExpiresAt != null && DateTime.now().isBefore(export.cacheExpiresAt!)) {
                  _openExport(export);
                } else {
                  _downloadExportOnly(export);
                }
              },
              tooltip: (export.localCachePath != null && export.cacheExpiresAt != null && DateTime.now().isBefore(export.cacheExpiresAt!)) ? 'Open' : 'Download',
            ),
            PopupMenuButton<String>(
          onSelected: (value) {
            switch (value) {
              case 'open':
                _openExport(export);
                break;
              case 'share':
                _shareExport(export);
                break;
              case 'delete':
                _deleteExport(export);
                break;
            }
          },
          itemBuilder: (context) => [
            const PopupMenuItem(
              value: 'open',
              child: Row(
                children: [
                  Icon(Icons.open_in_new),
                  SizedBox(width: 8),
                  Text('Open'),
                ],
              ),
            ),
            const PopupMenuItem(
              value: 'share',
              child: Row(
                children: [
                  Icon(Icons.share),
                  SizedBox(width: 8),
                  Text('Share'),
                ],
              ),
            ),
            const PopupMenuItem(
              value: 'delete',
              child: Row(
                children: [
                  Icon(Icons.delete, color: Colors.red),
                  SizedBox(width: 8),
                  Text('Delete', style: TextStyle(color: Colors.red)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.cloud_upload_outlined,
              size: 80,
              color: Theme.of(context).colorScheme.secondary,
            ),
            const SizedBox(height: 24),
            Text(
              'No exports yet for this job',
              style: Theme.of(context).textTheme.titleLarge,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              'Generate and export a document to get started',
              style: Theme.of(context).textTheme.bodyMedium,
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

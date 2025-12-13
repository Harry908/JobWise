import 'package:flutter/material.dart';
import '../../models/exported_file.dart';

class ExportActionsSheet extends StatelessWidget {
  final ExportedFile file;
  final VoidCallback onDownload;
  final VoidCallback? onSaveAs;
  final VoidCallback onDelete;
  final VoidCallback onShare;

  const ExportActionsSheet({
    super.key,
    required this.file,
    required this.onDownload,
    this.onSaveAs,
    required this.onDelete,
    required this.onShare,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // File info header
          ListTile(
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
            subtitle: Text(
              '${file.formattedFileSize} • ${file.template}',
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ),
          const Divider(),

          // Actions
          ListTile(
            leading: const Icon(Icons.download),
            title: const Text('Download'),
            onTap: () {
              Navigator.of(context).pop();
              onDownload();
            },
          ),

          if (onSaveAs != null) ...[
            ListTile(
              leading: const Icon(Icons.save_alt),
              title: const Text('Save As...'),
              onTap: () {
                Navigator.of(context).pop();
                onSaveAs!();
              },
            ),
          ],

          if (!file.isExpired) ...[
            ListTile(
              leading: const Icon(Icons.share),
              title: const Text('Share'),
              onTap: () {
                Navigator.of(context).pop();
                onShare();
              },
            ),
          ],

          ListTile(
            leading: const Icon(Icons.delete, color: Colors.red),
            title: const Text('Delete', style: TextStyle(color: Colors.red)),
            onTap: () {
              Navigator.of(context).pop();
              onDelete();
            },
          ),

          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Cancel'),
            ),
          ),
        ],
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

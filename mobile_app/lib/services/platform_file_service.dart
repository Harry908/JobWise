import 'package:flutter/foundation.dart';
import 'package:universal_html/html.dart' as html;

/// Platform-aware file service for handling downloads and file operations
class PlatformFileService {
  /// Download file bytes and trigger browser download on web
  static void downloadOnWeb({
    required Uint8List bytes,
    required String filename,
    String? mimeType,
  }) {
    if (!kIsWeb) return;

    final blob = html.Blob([bytes], mimeType ?? 'application/octet-stream');
    final url = html.Url.createObjectUrlFromBlob(blob);
    
    final anchor = html.AnchorElement()
      ..href = url
      ..download = filename
      ..style.display = 'none';
    
    html.document.body?.append(anchor);
    anchor.click();
    anchor.remove();
    
    // Clean up the URL after a short delay
    Future.delayed(const Duration(seconds: 1), () {
      html.Url.revokeObjectUrl(url);
    });
  }

  /// Get MIME type from file extension
  static String getMimeType(String filename) {
    final ext = filename.split('.').last.toLowerCase();
    switch (ext) {
      case 'pdf':
        return 'application/pdf';
      case 'docx':
        return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
      case 'doc':
        return 'application/msword';
      case 'zip':
        return 'application/zip';
      case 'txt':
        return 'text/plain';
      default:
        return 'application/octet-stream';
    }
  }

  /// Check if running on web
  static bool get isWeb => kIsWeb;
}

import 'dart:io';

class ExportedFile {
  final String exportId;
  final String? generationId;
  final String? jobId; // Denormalized for efficient filtering
  final String format; // 'pdf', 'docx', 'zip'
  final String template;
  final String filename;
  final int fileSizeBytes;
  final String downloadUrl;
  final DateTime createdAt;
  final DateTime expiresAt;
  final String? localCachePath; // Local cache file path (platform-specific)
  final DateTime? cacheExpiresAt; // Cache expiration (7 days default)
  final Map<String, dynamic>? metadata; // Job title, company, etc.

  ExportedFile({
    required this.exportId,
    this.generationId,
    this.jobId,
    required this.format,
    required this.template,
    required this.filename,
    required this.fileSizeBytes,
    required this.downloadUrl,
    required this.createdAt,
    required this.expiresAt,
    this.localCachePath,
    this.cacheExpiresAt,
    this.metadata,
  });

  factory ExportedFile.fromJson(Map<String, dynamic> json) {
    return ExportedFile(
      exportId: json['export_id'] ?? json['id'],
      generationId: json['generation_id'],
      jobId: json['job_id'],
      format: json['format'],
      template: json['template'],
      filename: json['filename'],
      fileSizeBytes: json['file_size_bytes'],
      downloadUrl: json['download_url'],
      createdAt: DateTime.parse(json['created_at']),
      expiresAt: DateTime.parse(json['expires_at']),
      localCachePath: json['local_cache_path'],
      cacheExpiresAt: json['cache_expires_at'] != null
          ? DateTime.parse(json['cache_expires_at'])
          : null,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'export_id': exportId,
      'generation_id': generationId,
      'job_id': jobId,
      'format': format,
      'template': template,
      'filename': filename,
      'file_size_bytes': fileSizeBytes,
      'download_url': downloadUrl,
      'created_at': createdAt.toIso8601String(),
      'expires_at': expiresAt.toIso8601String(),
      'local_cache_path': localCachePath,
      'cache_expires_at': cacheExpiresAt?.toIso8601String(),
      'metadata': metadata,
    };
  }

  String get formattedFileSize {
    final kb = fileSizeBytes / 1024;
    if (kb < 1024) {
      return '${kb.toStringAsFixed(1)} KB';
    }
    final mb = kb / 1024;
    return '${mb.toStringAsFixed(1)} MB';
  }

  bool get isExpired => DateTime.now().isAfter(expiresAt);

  /// Check if local cache is valid (exists and not expired)
  Future<bool> isCacheValid() async {
    if (localCachePath == null || cacheExpiresAt == null) {
      return false;
    }

    // Check expiration
    if (DateTime.now().isAfter(cacheExpiresAt!)) {
      return false;
    }

    // Check file exists
    final file = File(localCachePath!);
    return await file.exists();
  }

  /// Create a copy with updated cache information
  ExportedFile copyWithCache({
    required String localCachePath,
    required DateTime cacheExpiresAt,
  }) {
    return ExportedFile(
      exportId: exportId,
      generationId: generationId,
      jobId: jobId,
      format: format,
      template: template,
      filename: filename,
      fileSizeBytes: fileSizeBytes,
      downloadUrl: downloadUrl,
      createdAt: createdAt,
      expiresAt: expiresAt,
      localCachePath: localCachePath,
      cacheExpiresAt: cacheExpiresAt,
      metadata: metadata,
    );
  }

  /// Get job title from metadata (if available)
  String? get jobTitle => metadata?['job_title'] as String?;

  /// Get company name from metadata (if available)
  String? get companyName => metadata?['company_name'] as String?;

  String get formatIcon {
    switch (format.toLowerCase()) {
      case 'pdf':
        return '📄';
      case 'docx':
        return '📝';
      case 'zip':
        return '📦';
      default:
        return '📄';
    }
  }

  String get templateDisplayName {
    switch (template.toLowerCase()) {
      case 'modern':
        return 'Modern';
      case 'classic':
        return 'Classic';
      case 'creative':
        return 'Creative';
      case 'ats_optimized':
        return 'ATS-Optimized';
      default:
        return template;
    }
  }
}

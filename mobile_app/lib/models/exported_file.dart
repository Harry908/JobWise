class ExportedFile {
  final String exportId;
  final String? generationId;
  final String format; // 'pdf', 'docx', 'zip'
  final String template;
  final String filename;
  final int fileSizeBytes;
  final String downloadUrl;
  final DateTime createdAt;
  final DateTime expiresAt;
  final String? jobId; // Added to tie to specific job

  ExportedFile({
    required this.exportId,
    this.generationId,
    required this.format,
    required this.template,
    required this.filename,
    required this.fileSizeBytes,
    required this.downloadUrl,
    required this.createdAt,
    required this.expiresAt,
    this.jobId,
  });

  factory ExportedFile.fromJson(Map<String, dynamic> json) {
    return ExportedFile(
      exportId: json['export_id'] ?? json['id'],
      generationId: json['generation_id'],
      format: json['format'],
      template: json['template'],
      filename: json['filename'],
      fileSizeBytes: json['file_size_bytes'],
      downloadUrl: json['download_url'],
      createdAt: DateTime.parse(json['created_at']),
      expiresAt: DateTime.parse(json['expires_at']),
      jobId: json['job_id'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'export_id': exportId,
      'generation_id': generationId,
      'format': format,
      'template': template,
      'filename': filename,
      'file_size_bytes': fileSizeBytes,
      'download_url': downloadUrl,
      'created_at': createdAt.toIso8601String(),
      'expires_at': expiresAt.toIso8601String(),
      'job_id': jobId,
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

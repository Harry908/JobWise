import 'dart:convert';
import 'dart:io';
import 'package:path_provider/path_provider.dart';

/// Service to persist export cache metadata locally
class ExportCacheService {
  static const String _cacheFileName = 'export_cache_metadata.json';
  
  /// Get the cache metadata file path
  Future<File> _getCacheFile() async {
    final directory = await getApplicationDocumentsDirectory();
    return File('${directory.path}/$_cacheFileName');
  }
  
  /// Load all cached export metadata
  Future<Map<String, CachedExportInfo>> loadCacheMetadata() async {
    try {
      final file = await _getCacheFile();
      if (!await file.exists()) {
        return {};
      }
      
      final contents = await file.readAsString();
      final json = jsonDecode(contents) as Map<String, dynamic>;
      
      final result = <String, CachedExportInfo>{};
      json.forEach((exportId, data) {
        result[exportId] = CachedExportInfo.fromJson(data);
      });
      
      return result;
    } catch (e) {
      return {};
    }
  }
  
  /// Save cache metadata for an export
  Future<void> saveCacheInfo(String exportId, CachedExportInfo info) async {
    final metadata = await loadCacheMetadata();
    metadata[exportId] = info;
    await _saveMetadata(metadata);
  }
  
  /// Remove cache metadata for an export
  Future<void> removeCacheInfo(String exportId) async {
    final metadata = await loadCacheMetadata();
    metadata.remove(exportId);
    await _saveMetadata(metadata);
  }
  
  /// Get cache info for a specific export
  Future<CachedExportInfo?> getCacheInfo(String exportId) async {
    final metadata = await loadCacheMetadata();
    return metadata[exportId];
  }
  
  /// Check if a cached file is valid (exists and not expired)
  Future<bool> isCacheValid(String exportId) async {
    final info = await getCacheInfo(exportId);
    if (info == null) return false;
    
    // Check expiration
    if (DateTime.now().isAfter(info.expiresAt)) {
      await removeCacheInfo(exportId);
      return false;
    }
    
    // Check file exists
    final file = File(info.localPath);
    if (!await file.exists()) {
      await removeCacheInfo(exportId);
      return false;
    }
    
    return true;
  }
  
  Future<void> _saveMetadata(Map<String, CachedExportInfo> metadata) async {
    final file = await _getCacheFile();
    final json = <String, dynamic>{};
    metadata.forEach((exportId, info) {
      json[exportId] = info.toJson();
    });
    await file.writeAsString(jsonEncode(json));
  }
  
  /// Clean up expired cache entries and orphaned files
  Future<void> cleanupExpiredCache() async {
    final metadata = await loadCacheMetadata();
    final now = DateTime.now();
    final expiredIds = <String>[];
    
    for (final entry in metadata.entries) {
      if (now.isAfter(entry.value.expiresAt)) {
        expiredIds.add(entry.key);
        // Try to delete the file
        try {
          final file = File(entry.value.localPath);
          if (await file.exists()) {
            await file.delete();
          }
        } catch (_) {}
      }
    }
    
    for (final id in expiredIds) {
      metadata.remove(id);
    }
    
    await _saveMetadata(metadata);
  }
}

/// Information about a cached export file
class CachedExportInfo {
  final String localPath;
  final DateTime downloadedAt;
  final DateTime expiresAt;
  final String? userSavePath; // If user saved to custom location
  
  CachedExportInfo({
    required this.localPath,
    required this.downloadedAt,
    required this.expiresAt,
    this.userSavePath,
  });
  
  factory CachedExportInfo.fromJson(Map<String, dynamic> json) {
    return CachedExportInfo(
      localPath: json['local_path'],
      downloadedAt: DateTime.parse(json['downloaded_at']),
      expiresAt: DateTime.parse(json['expires_at']),
      userSavePath: json['user_save_path'],
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'local_path': localPath,
      'downloaded_at': downloadedAt.toIso8601String(),
      'expires_at': expiresAt.toIso8601String(),
      'user_save_path': userSavePath,
    };
  }
}

import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

// Conditional import for dart:io
import 'export_cache_service_io.dart' if (dart.library.html) 'export_cache_service_web.dart' as platform;

/// Service to persist export cache metadata locally
/// On mobile: Uses file system
/// On web: Uses localStorage via flutter_secure_storage
class ExportCacheService {
  static const String _cacheKey = 'export_cache_metadata';
  
  // Web storage
  final FlutterSecureStorage _webStorage = const FlutterSecureStorage();
  
  /// Load all cached export metadata
  Future<Map<String, CachedExportInfo>> loadCacheMetadata() async {
    try {
      String? contents;
      
      if (kIsWeb) {
        contents = await _webStorage.read(key: _cacheKey);
      } else {
        contents = await platform.readCacheFile();
      }
      
      if (contents == null || contents.isEmpty) {
        return {};
      }
      
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
  /// On web: Only checks expiration (no file system access)
  Future<bool> isCacheValid(String exportId) async {
    final info = await getCacheInfo(exportId);
    if (info == null) return false;
    
    // Check expiration
    if (DateTime.now().isAfter(info.expiresAt)) {
      await removeCacheInfo(exportId);
      return false;
    }
    
    // On web, we can't check file existence - just trust the metadata
    if (kIsWeb) {
      return true;
    }
    
    // On mobile, check file exists
    final exists = await platform.fileExists(info.localPath);
    if (!exists) {
      await removeCacheInfo(exportId);
      return false;
    }
    
    return true;
  }
  
  Future<void> _saveMetadata(Map<String, CachedExportInfo> metadata) async {
    final json = <String, dynamic>{};
    metadata.forEach((exportId, info) {
      json[exportId] = info.toJson();
    });
    final contents = jsonEncode(json);
    
    if (kIsWeb) {
      await _webStorage.write(key: _cacheKey, value: contents);
    } else {
      await platform.writeCacheFile(contents);
    }
  }
  
  /// Clean up expired cache entries and orphaned files
  Future<void> cleanupExpiredCache() async {
    final metadata = await loadCacheMetadata();
    final now = DateTime.now();
    final expiredIds = <String>[];
    
    for (final entry in metadata.entries) {
      if (now.isAfter(entry.value.expiresAt)) {
        expiredIds.add(entry.key);
        // Try to delete the file (mobile only)
        if (!kIsWeb) {
          await platform.deleteFile(entry.value.localPath);
        }
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

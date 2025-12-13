/// Stub implementations for web platform
/// These functions are not called on web because kIsWeb checks prevent them
library;

/// Read cache file contents - not used on web
Future<String?> readCacheFile() async {
  return null;
}

/// Write cache file contents - not used on web
Future<void> writeCacheFile(String contents) async {
  // No-op on web
}

/// Check if a file exists - not used on web
Future<bool> fileExists(String path) async {
  return false;
}

/// Delete a file - not used on web
Future<void> deleteFile(String path) async {
  // No-op on web
}

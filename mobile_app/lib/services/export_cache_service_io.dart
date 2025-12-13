import 'dart:io';
import 'package:path_provider/path_provider.dart';

const String _cacheFileName = 'export_cache_metadata.json';

/// Read cache file contents (mobile/desktop only)
Future<String?> readCacheFile() async {
  try {
    final directory = await getApplicationDocumentsDirectory();
    final file = File('${directory.path}/$_cacheFileName');
    if (await file.exists()) {
      return await file.readAsString();
    }
    return null;
  } catch (e) {
    return null;
  }
}

/// Write cache file contents (mobile/desktop only)
Future<void> writeCacheFile(String contents) async {
  final directory = await getApplicationDocumentsDirectory();
  final file = File('${directory.path}/$_cacheFileName');
  await file.writeAsString(contents);
}

/// Check if a file exists (mobile/desktop only)
Future<bool> fileExists(String path) async {
  final file = File(path);
  return await file.exists();
}

/// Delete a file (mobile/desktop only)
Future<void> deleteFile(String path) async {
  try {
    final file = File(path);
    if (await file.exists()) {
      await file.delete();
    }
  } catch (_) {}
}

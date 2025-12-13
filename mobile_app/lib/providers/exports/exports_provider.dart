import 'dart:typed_data';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/exported_file.dart';
import '../../models/template.dart';
import '../../services/api/exports_api_client.dart';
import '../../services/export_cache_service.dart';
import '../auth_provider.dart';

class ExportsState {
  final List<ExportedFile> files;
  final List<Template> templates;
  final bool isLoading;
  final String? error;
  final String? selectedJobId;

  const ExportsState({
    this.files = const [],
    this.templates = const [],
    this.isLoading = false,
    this.error,
    this.selectedJobId,
  });

  ExportsState copyWith({
    List<ExportedFile>? files,
    List<Template>? templates,
    bool? isLoading,
    String? error,
    String? selectedJobId,
  }) {
    return ExportsState(
      files: files ?? this.files,
      templates: templates ?? this.templates,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
      selectedJobId: selectedJobId ?? this.selectedJobId,
    );
  }

  List<ExportedFile> get filesForSelectedJob {
    if (selectedJobId == null) return files;
    return files.where((file) => file.jobId == selectedJobId).toList();
  }

  Map<String, int> get fileCountByFormat {
    final jobFiles = filesForSelectedJob;
    final counts = <String, int>{};
    for (final file in jobFiles) {
      counts[file.format] = (counts[file.format] ?? 0) + 1;
    }
    return counts;
  }

  int get totalFileSize {
    return filesForSelectedJob.fold(0, (sum, file) => sum + file.fileSizeBytes);
  }

  String get formattedTotalSize {
    final bytes = totalFileSize;
    if (bytes < 1024) return '$bytes B';
    if (bytes < 1024 * 1024) return '${(bytes / 1024).round()} KB';
    if (bytes < 1024 * 1024 * 1024) return '${(bytes / (1024 * 1024)).round()} MB';
    return '${(bytes / (1024 * 1024 * 1024)).round()} GB';
  }
}

class ExportsNotifier extends StateNotifier<ExportsState> {
  final ExportsApiClient _apiClient;

  ExportsNotifier(this._apiClient) : super(const ExportsState());

  Future<void> loadTemplates() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final templates = await _apiClient.getTemplates();
      state = state.copyWith(templates: templates, isLoading: false);
    } catch (e) {
      state = state.copyWith(error: e.toString(), isLoading: false);
    }
  }

  Future<void> loadExportedFiles({String? jobId}) async {
    state = state.copyWith(isLoading: true, error: null, selectedJobId: jobId);
    try {
      // Load persisted cache metadata from local storage
      final cacheService = ExportCacheService();
      final persistedCache = await cacheService.loadCacheMetadata();
      
      final response = await _apiClient.getExportedFiles(jobId: jobId);
      final files = (response['exports'] as List? ?? [])
          .map((json) {
            final file = ExportedFile.fromJson(json);
            
            // Check persisted cache metadata
            if (persistedCache.containsKey(file.exportId)) {
              final cached = persistedCache[file.exportId]!;
              // Only use if not expired
              if (DateTime.now().isBefore(cached.expiresAt)) {
                return file.copyWithCache(
                  localCachePath: cached.localPath,
                  cacheExpiresAt: cached.expiresAt,
                );
              }
            }
            
            return file;
          })
          .toList();
      state = state.copyWith(files: files, isLoading: false);
    } catch (e) {
      state = state.copyWith(error: e.toString(), isLoading: false);
    }
  }

  Future<void> exportToPDF({
    required String generationId,
    required String templateId,
    Map<String, dynamic>? options,
  }) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final exportedFile = await _apiClient.exportToPDF(
        generationId: generationId,
        templateId: templateId,
        options: options,
      );
      final updatedFiles = [exportedFile, ...state.files];
      state = state.copyWith(files: updatedFiles, isLoading: false);
    } catch (e) {
      state = state.copyWith(error: e.toString(), isLoading: false);
    }
  }

  Future<void> exportToDOCX({
    required String generationId,
    required String templateId,
    Map<String, dynamic>? options,
  }) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final exportedFile = await _apiClient.exportToDOCX(
        generationId: generationId,
        templateId: templateId,
        options: options,
      );
      final updatedFiles = [exportedFile, ...state.files];
      state = state.copyWith(files: updatedFiles, isLoading: false);
    } catch (e) {
      state = state.copyWith(error: e.toString(), isLoading: false);
    }
  }

  Future<void> batchExport({
    required List<String> generationIds,
    required String templateId,
    required String format,
    Map<String, dynamic>? options,
  }) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final exportedFile = await _apiClient.batchExport(
        generationIds: generationIds,
        templateId: templateId,
        format: format,
        options: options,
      );
      final updatedFiles = [exportedFile, ...state.files];
      state = state.copyWith(files: updatedFiles, isLoading: false);
    } catch (e) {
      state = state.copyWith(error: e.toString(), isLoading: false);
    }
  }

  Future<void> deleteFile(String exportId) async {
    try {
      await _apiClient.deleteFile(exportId);
      final updatedFiles = state.files.where((file) => file.exportId != exportId).toList();
      state = state.copyWith(files: updatedFiles);
    } catch (e) {
      state = state.copyWith(error: e.toString());
    }
  }

  /// Load exports for a specific job (optimized query, pre-grouped by date)
  Future<Map<String, List<ExportedFile>>> loadJobExports(String jobId) async {
    try {
      final response = await _apiClient.getJobExports(jobId: jobId);
      
      // Load persisted cache metadata from local storage
      final cacheService = ExportCacheService();
      final persistedCache = await cacheService.loadCacheMetadata();
      
      // Build a map of cached exports from current state (in-memory)
      final cachedExports = <String, ExportedFile>{};
      for (final file in state.files) {
        if (file.localCachePath != null) {
          cachedExports[file.exportId] = file;
        }
      }
      
      // Parse exports_by_date from response
      final exportsByDateJson = response['exports_by_date'] as Map<String, dynamic>? ?? {};
      final exportsByDate = <String, List<ExportedFile>>{};
      
      exportsByDateJson.forEach((date, exportsJson) {
        final exports = (exportsJson as List? ?? [])
            .map((json) {
              final file = ExportedFile.fromJson(json);
              
              // First check in-memory state
              if (cachedExports.containsKey(file.exportId)) {
                final cached = cachedExports[file.exportId]!;
                return file.copyWithCache(
                  localCachePath: cached.localCachePath!,
                  cacheExpiresAt: cached.cacheExpiresAt!,
                );
              }
              
              // Then check persisted cache metadata
              if (persistedCache.containsKey(file.exportId)) {
                final cached = persistedCache[file.exportId]!;
                // Only use if not expired
                if (DateTime.now().isBefore(cached.expiresAt)) {
                  return file.copyWithCache(
                    localCachePath: cached.localPath,
                    cacheExpiresAt: cached.expiresAt,
                  );
                }
              }
              
              return file;
            })
            .toList();
        exportsByDate[date] = exports;
      });
      
      return exportsByDate;
    } catch (e) {
      rethrow;
    }
  }

  /// Download an export and save to local cache
  Future<void> downloadExport(String exportId, String savePath, {Function(double)? onProgress, String? userSavePath}) async {
    try {
      await _apiClient.downloadFile(
        exportId: exportId,
        savePath: savePath,
        onProgress: onProgress,
      );

      final expiresAt = DateTime.now().add(const Duration(days: 7));
      
      // Persist cache metadata locally
      final cacheService = ExportCacheService();
      await cacheService.saveCacheInfo(
        exportId,
        CachedExportInfo(
          localPath: savePath,
          downloadedAt: DateTime.now(),
          expiresAt: expiresAt,
          userSavePath: userSavePath,
        ),
      );

      // Update cached path in state and set cache expiry (7 days)
      final updatedFiles = state.files.map((f) {
        if (f.exportId == exportId) {
          return f.copyWithCache(
            localCachePath: savePath,
            cacheExpiresAt: expiresAt,
          );
        }
        return f;
      }).toList();

      state = state.copyWith(files: updatedFiles);
    } catch (e) {
      rethrow;
    }
  }

  /// Download export and return bytes (for web browser downloads)
  Future<Uint8List> downloadExportBytes(String exportId) async {
    try {
      return await _apiClient.downloadFileBytes(exportId: exportId);
    } catch (e) {
      rethrow;
    }
  }

  /// Delete an export
  Future<void> deleteExport(String exportId) async {
    try {
      await _apiClient.deleteFile(exportId);
    } catch (e) {
      rethrow;
    }
  }

  void clearError() {
    state = state.copyWith(error: null);
  }

  void setSelectedJob(String? jobId) {
    state = state.copyWith(selectedJobId: jobId);
  }
}

// Providers
final exportsApiClientProvider = Provider<ExportsApiClient>((ref) {
  final httpClient = ref.watch(baseHttpClientProvider);
  return ExportsApiClient(httpClient.dio);
});

final exportsNotifierProvider = StateNotifierProvider<ExportsNotifier, ExportsState>((ref) {
  final apiClient = ref.watch(exportsApiClientProvider);
  return ExportsNotifier(apiClient);
});

// Helper providers for filtered data
final selectedJobExportedFilesProvider = Provider<List<ExportedFile>>((ref) {
  final state = ref.watch(exportsNotifierProvider);
  return state.filesForSelectedJob;
});

final exportedFilesByFormatProvider = Provider<Map<String, int>>((ref) {
  final state = ref.watch(exportsNotifierProvider);
  return state.fileCountByFormat;
});

final totalExportSizeProvider = Provider<String>((ref) {
  final state = ref.watch(exportsNotifierProvider);
  return state.formattedTotalSize;
});

import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Platform-aware storage service that uses:
/// - FlutterSecureStorage on mobile (encrypted)
/// - Web storage on web (localStorage with optional encryption key)
class PlatformStorageService {
  static const String _accessTokenKey = 'access_token';
  static const String _refreshTokenKey = 'refresh_token';

  // In-memory cache for faster access
  String? _accessToken;

  // Mobile: secure storage
  FlutterSecureStorage? _secureStorage;

  PlatformStorageService() {
    if (!kIsWeb) {
      _secureStorage = const FlutterSecureStorage(
        aOptions: AndroidOptions(
          encryptedSharedPreferences: true,
        ),
      );
    }
  }

  Future<void> saveTokens(String accessToken, String refreshToken) async {
    _accessToken = accessToken;

    if (kIsWeb) {
      await _webWrite(_accessTokenKey, accessToken);
      await _webWrite(_refreshTokenKey, refreshToken);
    } else {
      await _secureStorage!.write(key: _accessTokenKey, value: accessToken);
      await _secureStorage!.write(key: _refreshTokenKey, value: refreshToken);
    }
  }

  Future<String?> getToken() async {
    // Return cached token if available
    if (_accessToken != null) {
      return _accessToken;
    }

    if (kIsWeb) {
      _accessToken = await _webRead(_accessTokenKey);
    } else {
      _accessToken = await _secureStorage!.read(key: _accessTokenKey);
    }
    return _accessToken;
  }

  Future<String?> getRefreshToken() async {
    if (kIsWeb) {
      return await _webRead(_refreshTokenKey);
    } else {
      return await _secureStorage!.read(key: _refreshTokenKey);
    }
  }

  Future<void> clearTokens() async {
    _accessToken = null;

    if (kIsWeb) {
      await _webDelete(_accessTokenKey);
      await _webDelete(_refreshTokenKey);
    } else {
      await _secureStorage!.delete(key: _accessTokenKey);
      await _secureStorage!.delete(key: _refreshTokenKey);
    }
  }

  Future<bool> hasTokens() async {
    final token = await getToken();
    final refreshToken = await getRefreshToken();
    return token != null && refreshToken != null;
  }

  // Web storage methods using conditional import pattern
  Future<void> _webWrite(String key, String value) async {
    // This will be implemented via web-specific code
    // For now, using a simple approach that works with flutter_secure_storage's web support
    if (kIsWeb) {
      // flutter_secure_storage v9+ supports web via localStorage
      _secureStorage ??= const FlutterSecureStorage();
      await _secureStorage!.write(key: key, value: value);
    }
  }

  Future<String?> _webRead(String key) async {
    if (kIsWeb) {
      _secureStorage ??= const FlutterSecureStorage();
      return await _secureStorage!.read(key: key);
    }
    return null;
  }

  Future<void> _webDelete(String key) async {
    if (kIsWeb) {
      _secureStorage ??= const FlutterSecureStorage();
      await _secureStorage!.delete(key: key);
    }
  }
}

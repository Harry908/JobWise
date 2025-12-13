import 'package:flutter/foundation.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

class AppConfig {
  static String get apiBaseUrl {
    // Check for environment variable first
    final envUrl = dotenv.env['API_BASE_URL'];
    if (envUrl != null && envUrl.isNotEmpty) {
      return envUrl;
    }
    
    // Platform-specific defaults
    if (kIsWeb) {
      // Web: Use relative path (same origin) or configure for your deployed backend
      // For local development, you may need to run backend with CORS enabled
      return dotenv.env['WEB_API_BASE_URL'] ?? 'http://localhost:8000/api/v1';
    } else {
      // Android emulator uses 10.0.2.2 to reach host machine's localhost
      // iOS simulator uses localhost directly
      return 'http://10.0.2.2:8000/api/v1';
    }
  }

  /// Check if running on web platform
  static bool get isWeb => kIsWeb;

  /// Check if running on mobile platform
  static bool get isMobile => !kIsWeb;

  static Future<void> load() async {
    try {
      await dotenv.load(fileName: '.env');
    } catch (e) {
      // .env file not found, using default values
      debugPrint('Warning: .env file not found, using default configuration');
    }
  }
}
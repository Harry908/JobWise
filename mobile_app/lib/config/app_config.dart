import 'package:flutter_dotenv/flutter_dotenv.dart';

class AppConfig {
  static String get apiBaseUrl {
    return dotenv.env['API_BASE_URL'] ?? 'http://localhost:8000/api/v1';
  }

  static Future<void> load() async {
    await dotenv.load(fileName: '.env');
  }
}
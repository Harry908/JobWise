import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Service for managing app settings and preferences
class SettingsService {
  static final SettingsService _instance = SettingsService._internal();
  factory SettingsService() => _instance;
  SettingsService._internal();

  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  // Date format options
  static const String dateFormatUS = 'MM/dd/yyyy';
  static const String dateFormatISO = 'yyyy-MM-dd';
  static const String dateFormatEU = 'dd/MM/yyyy';

  static const String _dateFormatKey = 'date_format_preference';
  static const String _defaultDateFormat = dateFormatUS;

  /// Get the current date format preference
  Future<String> getDateFormat() async {
    final format = await _storage.read(key: _dateFormatKey);
    return format ?? _defaultDateFormat;
  }

  /// Set the date format preference
  Future<void> setDateFormat(String format) async {
    await _storage.write(key: _dateFormatKey, value: format);
  }

  /// Convert date string from display format to API format (YYYY-MM-DD)
  String toApiFormat(String displayDate, String currentFormat) {
    if (displayDate.isEmpty) return displayDate;
    
    try {
      DateTime date;
      if (currentFormat == dateFormatUS) {
        // Parse MM/dd/yyyy
        final parts = displayDate.split('/');
        if (parts.length == 3) {
          date = DateTime(
            int.parse(parts[2]), // year
            int.parse(parts[0]), // month
            int.parse(parts[1]), // day
          );
        } else {
          return displayDate;
        }
      } else if (currentFormat == dateFormatEU) {
        // Parse dd/MM/yyyy
        final parts = displayDate.split('/');
        if (parts.length == 3) {
          date = DateTime(
            int.parse(parts[2]), // year
            int.parse(parts[1]), // month
            int.parse(parts[0]), // day
          );
        } else {
          return displayDate;
        }
      } else {
        // Already in ISO format
        return displayDate;
      }
      
      // Return in API format (YYYY-MM-DD)
      return date.toIso8601String().split('T')[0];
    } catch (e) {
      return displayDate;
    }
  }

  /// Convert date string from API format (YYYY-MM-DD) to display format
  String toDisplayFormat(String apiDate, String targetFormat) {
    if (apiDate.isEmpty) return apiDate;
    
    try {
      // Parse API format (YYYY-MM-DD)
      final date = DateTime.parse(apiDate);
      
      if (targetFormat == dateFormatUS) {
        // Format as MM/dd/yyyy
        return '${date.month.toString().padLeft(2, '0')}/${date.day.toString().padLeft(2, '0')}/${date.year}';
      } else if (targetFormat == dateFormatEU) {
        // Format as dd/MM/yyyy
        return '${date.day.toString().padLeft(2, '0')}/${date.month.toString().padLeft(2, '0')}/${date.year}';
      } else {
        // Return in ISO format
        return date.toIso8601String().split('T')[0];
      }
    } catch (e) {
      return apiDate;
    }
  }

  /// Format a DateTime to display format
  String formatDateToDisplay(DateTime date, String format) {
    if (format == dateFormatUS) {
      return '${date.month.toString().padLeft(2, '0')}/${date.day.toString().padLeft(2, '0')}/${date.year}';
    } else if (format == dateFormatEU) {
      return '${date.day.toString().padLeft(2, '0')}/${date.month.toString().padLeft(2, '0')}/${date.year}';
    } else {
      return date.toIso8601String().split('T')[0];
    }
  }

  /// Get date format hint text
  String getDateFormatHint(String format) {
    if (format == dateFormatUS) {
      return '01/15/2020';
    } else if (format == dateFormatEU) {
      return '15/01/2020';
    } else {
      return '2020-01-15';
    }
  }

  /// Get date format label
  String getDateFormatLabel(String format) {
    if (format == dateFormatUS) {
      return 'Date (MM/dd/yyyy)';
    } else if (format == dateFormatEU) {
      return 'Date (dd/MM/yyyy)';
    } else {
      return 'Date (yyyy-MM-dd)';
    }
  }

  /// Get regex pattern for validation
  RegExp getDateFormatRegex(String format) {
    if (format == dateFormatUS || format == dateFormatEU) {
      return RegExp(r'^\d{2}/\d{2}/\d{4}$');
    } else {
      return RegExp(r'^\d{4}-\d{2}-\d{2}$');
    }
  }
}

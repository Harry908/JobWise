import 'package:flutter/material.dart';
import '../services/settings_service.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final _settingsService = SettingsService();
  String _selectedDateFormat = SettingsService.dateFormatUS;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final format = await _settingsService.getDateFormat();
    setState(() {
      _selectedDateFormat = format;
      _isLoading = false;
    });
  }

  Future<void> _saveDateFormat(String format) async {
    await _settingsService.setDateFormat(format);
    setState(() {
      _selectedDateFormat = format;
    });
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Date format preference saved'),
          duration: Duration(seconds: 2),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              children: [
                const Padding(
                  padding: EdgeInsets.all(16.0),
                  child: Text(
                    'Date Format',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const Padding(
                  padding: EdgeInsets.symmetric(horizontal: 16.0),
                  child: Text(
                    'Choose how dates are displayed throughout the app',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey,
                    ),
                  ),
                ),
                const SizedBox(height: 8),
                // ignore: deprecated_member_use
                RadioListTile<String>(
                  title: const Text('US Format'),
                  subtitle: Text(
                    'MM/dd/yyyy - Example: ${_settingsService.getDateFormatHint(SettingsService.dateFormatUS)}',
                  ),
                  value: SettingsService.dateFormatUS,
                  // ignore: deprecated_member_use
                  groupValue: _selectedDateFormat,
                  // ignore: deprecated_member_use
                  onChanged: (value) {
                    if (value != null) {
                      _saveDateFormat(value);
                    }
                  },
                ),
                // ignore: deprecated_member_use
                RadioListTile<String>(
                  title: const Text('European Format'),
                  subtitle: Text(
                    'dd/MM/yyyy - Example: ${_settingsService.getDateFormatHint(SettingsService.dateFormatEU)}',
                  ),
                  value: SettingsService.dateFormatEU,
                  // ignore: deprecated_member_use
                  groupValue: _selectedDateFormat,
                  // ignore: deprecated_member_use
                  onChanged: (value) {
                    if (value != null) {
                      _saveDateFormat(value);
                    }
                  },
                ),
                // ignore: deprecated_member_use
                RadioListTile<String>(
                  title: const Text('ISO Format'),
                  subtitle: Text(
                    'yyyy-MM-dd - Example: ${_settingsService.getDateFormatHint(SettingsService.dateFormatISO)}',
                  ),
                  value: SettingsService.dateFormatISO,
                  // ignore: deprecated_member_use
                  groupValue: _selectedDateFormat,
                  // ignore: deprecated_member_use
                  onChanged: (value) {
                    if (value != null) {
                      _saveDateFormat(value);
                    }
                  },
                ),
                const Divider(height: 32),
                const Padding(
                  padding: EdgeInsets.all(16.0),
                  child: Text(
                    'About',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const ListTile(
                  title: Text('App Version'),
                  trailing: Text('1.0.0'),
                ),
                const ListTile(
                  title: Text('JobWise'),
                  subtitle: Text('AI-powered job application assistant'),
                ),
              ],
            ),
    );
  }
}

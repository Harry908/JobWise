import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/settings_provider.dart';
import '../services/settings_service.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dateFormatState = ref.watch(dateFormatSettingProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
      ),
      body: dateFormatState.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, stack) => Center(child: Text('Error: $err')),
        data: (selectedDateFormat) {
          return ListView(
            children: const [
              Padding(
                padding: EdgeInsets.all(16.0),
                child: Text(
                  'Date Format',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              Padding(
                padding: EdgeInsets.symmetric(horizontal: 16.0),
                child: Text(
                  'Choose how dates are displayed throughout the app',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey,
                  ),
                ),
              ),
              SizedBox(height: 8),
              _DateFormatRadioList(),
              Divider(height: 32),
              Padding(
                padding: EdgeInsets.all(16.0),
                child: Text(
                  'About',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              ListTile(
                title: Text('App Version'),
                trailing: Text('1.0.0'),
              ),
              ListTile(
                title: Text('JobWise'),
                subtitle: Text('AI-powered job application assistant'),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _DateFormatRadioList extends ConsumerWidget {
  const _DateFormatRadioList();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selectedDateFormat = ref.watch(dateFormatSettingProvider).value;
    final settingsService = ref.watch(settingsServiceProvider);

    if (selectedDateFormat == null) {
      return const SizedBox.shrink();
    }

    return Column(
      children: [
        ListTile(
          title: const Text('US Format'),
          subtitle: Text(
            'MM/dd/yyyy - Example: ${settingsService.getDateFormatHint(SettingsService.dateFormatUS)}',
          ),
          leading: Radio<String>(
            value: SettingsService.dateFormatUS,
            groupValue: selectedDateFormat,
            onChanged: (value) => _updateDateFormat(ref, context, value),
          ),
          onTap: () => _updateDateFormat(ref, context, SettingsService.dateFormatUS),
        ),
        ListTile(
          title: const Text('European Format'),
          subtitle: Text(
            'dd/MM/yyyy - Example: ${settingsService.getDateFormatHint(SettingsService.dateFormatEU)}',
          ),
          leading: Radio<String>(
            value: SettingsService.dateFormatEU,
            groupValue: selectedDateFormat,
            onChanged: (value) => _updateDateFormat(ref, context, value),
          ),
          onTap: () => _updateDateFormat(ref, context, SettingsService.dateFormatEU),
        ),
        ListTile(
          title: const Text('ISO Format'),
          subtitle: Text(
            'yyyy-MM-dd - Example: ${settingsService.getDateFormatHint(SettingsService.dateFormatISO)}',
          ),
          leading: Radio<String>(
            value: SettingsService.dateFormatISO,
            groupValue: selectedDateFormat,
            onChanged: (value) => _updateDateFormat(ref, context, value),
          ),
          onTap: () => _updateDateFormat(ref, context, SettingsService.dateFormatISO),
        ),
      ],
    );
  }

  Future<void> _updateDateFormat(
      WidgetRef ref, BuildContext context, String? value) async {
    if (value != null) {
      await ref.read(dateFormatSettingProvider.notifier).setDateFormat(value);
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Date format preference saved'),
            duration: Duration(seconds: 2),
          ),
        );
      }
    }
  }
}

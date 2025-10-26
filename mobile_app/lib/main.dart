import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'app.dart';
import 'config/app_config.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  print('Main: Loading AppConfig...');
  await AppConfig.load();
  print('Main: AppConfig loaded, API URL: ${AppConfig.apiBaseUrl}');
  runApp(const ProviderScope(child: App()));
}

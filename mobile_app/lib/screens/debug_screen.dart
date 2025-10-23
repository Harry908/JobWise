import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/storage_service.dart';

class DebugScreen extends ConsumerStatefulWidget {
  const DebugScreen({super.key});

  @override
  ConsumerState<DebugScreen> createState() => _DebugScreenState();
}

class _DebugScreenState extends ConsumerState<DebugScreen> {
  final _storage = StorageService();

  Future<void> _clearTokens() async {
    await _storage.clearTokens();
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Tokens cleared! Restart the app to see login screen.')),
      );
    }
  }

  Future<void> _checkTokens() async {
    final hasTokens = await _storage.hasTokens();
    final token = await _storage.getToken();
    final refreshToken = await _storage.getRefreshToken();

    if (mounted) {
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('Token Status'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Has tokens: $hasTokens'),
              Text('Access token: ${token != null ? "Present (${token.length} chars)" : "None"}'),
              Text('Refresh token: ${refreshToken != null ? "Present (${refreshToken.length} chars)" : "None"}'),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('OK'),
            ),
          ],
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Debug Tools'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              'Authentication Debug',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _checkTokens,
              child: const Text('Check Stored Tokens'),
            ),
            const SizedBox(height: 10),
            ElevatedButton(
              onPressed: _clearTokens,
              style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
              child: const Text('Clear All Tokens'),
            ),
            const SizedBox(height: 20),
            const Text(
              'After clearing tokens, restart the app to see the login screen.',
              style: TextStyle(color: Colors.grey),
            ),
          ],
        ),
      ),
    );
  }
}
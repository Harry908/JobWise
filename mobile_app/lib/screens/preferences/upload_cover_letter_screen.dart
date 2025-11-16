// lib/screens/preferences/upload_cover_letter_screen.dart

import 'dart:io';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/preference_provider.dart';

class UploadCoverLetterScreen extends ConsumerWidget {
  const UploadCoverLetterScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selectedFile = ValueNotifier<File?>(null);

    ref.listen<AsyncValue<void>>(sampleCoverLettersProvider, (_, state) {
      if (state is AsyncError) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(state.error.toString()),
            backgroundColor: Colors.red,
          ),
        );
      }
      if (state is AsyncData) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Cover letter uploaded successfully!'),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.of(context).pop();
      }
    });

    Future<void> pickFile() async {
      try {
        final result = await FilePicker.platform.pickFiles(
          type: FileType.custom,
          allowedExtensions: ['pdf', 'docx', 'txt'],
        );

        if (result != null && result.files.single.path != null) {
          selectedFile.value = File(result.files.single.path!);
        }
      } catch (e) {
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Failed to pick file: $e'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    }

    Future<void> uploadFile() async {
      if (selectedFile.value == null) return;
      await ref
          .read(sampleCoverLettersProvider.notifier)
          .upload(selectedFile.value!.path);
    }

    final uploadState = ref.watch(sampleCoverLettersProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Upload Sample Cover Letter'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Card(
              child: Padding(
                padding: EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Upload Your Best Cover Letter',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    SizedBox(height: 8),
                    Text(
                      'Our AI will analyze your writing style, tone, and formality to match your preferred communication style in future cover letters.',
                      style: TextStyle(
                        color: Colors.grey,
                      ),
                    ),
                    SizedBox(height: 16),
                    Text(
                      'Supported formats: PDF, DOCX, TXT',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey,
                      ),
                    ),
                    Text(
                      'Maximum file size: 5 MB',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            ValueListenableBuilder<File?>(
              valueListenable: selectedFile,
              builder: (context, file, child) {
                if (file == null) {
                  return const SizedBox.shrink();
                }
                return Card(
                  color: Colors.blue.shade50,
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Row(
                      children: [
                        const Icon(Icons.description, color: Colors.blue),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                file.path.split(Platform.pathSeparator).last,
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                ),
                                overflow: TextOverflow.ellipsis,
                              ),
                              const SizedBox(height: 4),
                              FutureBuilder<int>(
                                future: file.length(),
                                builder: (context, snapshot) {
                                  if (snapshot.hasData) {
                                    final kb = snapshot.data! / 1024;
                                    final mb = kb / 1024;
                                    final size = mb >= 1
                                        ? '${mb.toStringAsFixed(1)} MB'
                                        : '${kb.toStringAsFixed(1)} KB';
                                    return Text(
                                      size,
                                      style: const TextStyle(
                                        fontSize: 12,
                                        color: Colors.grey,
                                      ),
                                    );
                                  }
                                  return const SizedBox.shrink();
                                },
                              ),
                            ],
                          ),
                        ),
                        IconButton(
                          icon: const Icon(Icons.close, color: Colors.red),
                          onPressed: () {
                            selectedFile.value = null;
                          },
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
            const SizedBox(height: 16),
            ValueListenableBuilder<File?>(
              valueListenable: selectedFile,
              builder: (context, file, child) {
                return ElevatedButton.icon(
                  onPressed: uploadState.isLoading ? null : pickFile,
                  icon: const Icon(Icons.upload_file),
                  label: Text(file == null ? 'Choose File' : 'Choose Different File'),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.all(16),
                  ),
                );
              }
            ),
            const Spacer(),
            if (uploadState.isLoading) const LinearProgressIndicator(),
            const SizedBox(height: 16),
            ValueListenableBuilder<File?>(
              valueListenable: selectedFile,
              builder: (context, file, child) {
                return ElevatedButton(
                  onPressed: file == null || uploadState.isLoading
                      ? null
                      : uploadFile,
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.all(16),
                    backgroundColor: Theme.of(context).primaryColor,
                    foregroundColor: Colors.white,
                  ),
                  child: uploadState.isLoading
                      ? const Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                              ),
                            ),
                            SizedBox(width: 12),
                            Text('Uploading and analyzing...'),
                          ],
                        )
                      : const Text(
                          'Upload Cover Letter',
                          style: TextStyle(fontSize: 16),
                        ),
                );
              }
            ),
          ],
        ),
      ),
    );
  }
}

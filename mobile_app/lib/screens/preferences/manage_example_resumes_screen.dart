// lib/screens/preferences/manage_example_resumes_screen.dart

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../models/preferences/example_resume.dart';
import '../../providers/preference_provider.dart';
import 'upload_sample_resume_screen.dart';

class ManageExampleResumesScreen extends ConsumerWidget {
  const ManageExampleResumesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final exampleResumesAsync = ref.watch(exampleResumesProvider);

    ref.listen<AsyncValue<List<ExampleResume>>>(exampleResumesProvider,
        (_, state) {
      if (state.hasError && !state.isLoading) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(state.error.toString()),
            backgroundColor: Colors.red,
          ),
        );
      }
    });

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Example Resumes'),
      ),
      body: exampleResumesAsync.when(
        data: (resumes) {
          if (resumes.isEmpty) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(32.0),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(
                      Icons.description_outlined,
                      size: 80,
                      color: Colors.grey,
                    ),
                    const SizedBox(height: 24),
                    const Text(
                      'No example resumes uploaded yet',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'Upload sample resumes to help our AI learn your preferred layout and formatting style.',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: Colors.grey,
                      ),
                    ),
                    const SizedBox(height: 24),
                    ElevatedButton.icon(
                      onPressed: () {
                        Navigator.of(context).push(
                          MaterialPageRoute(
                            builder: (context) =>
                                const UploadSampleResumeScreen(),
                          ),
                        );
                      },
                      icon: const Icon(Icons.upload_file),
                      label: const Text('Upload Resume'),
                    ),
                  ],
                ),
              ),
            );
          }

          return ListView.builder(
            padding: const EdgeInsets.all(16.0),
            itemCount: resumes.length + 1,
            itemBuilder: (context, index) {
              if (index == 0) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 16.0),
                  child: ElevatedButton.icon(
                    onPressed: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (context) =>
                              const UploadSampleResumeScreen(),
                        ),
                      );
                    },
                    icon: const Icon(Icons.upload_file),
                    label: const Text('Upload New Resume'),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.all(16),
                    ),
                  ),
                );
              }

              final resume = resumes[index - 1];
              return Card(
                margin: const EdgeInsets.only(bottom: 12.0),
                child: ListTile(
                  leading: CircleAvatar(
                    backgroundColor:
                        resume.isPrimary ? Colors.blue : Colors.grey.shade300,
                    child: Icon(
                      resume.isPrimary ? Icons.star : Icons.description,
                      color: resume.isPrimary ? Colors.white : Colors.grey,
                    ),
                  ),
                  title: Text(
                    resume.originalFilename,
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  subtitle: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const SizedBox(height: 4),
                      Text(resume.fileSizeFormatted),
                      Text(resume.fileTypeDisplay),
                      Text(
                        'Uploaded: ${DateFormat.yMMMd().format(resume.uploadedAt)}',
                        style: const TextStyle(fontSize: 12),
                      ),
                      if (resume.isPrimary)
                        const Padding(
                          padding: EdgeInsets.only(top: 4.0),
                          child: Text(
                            'PRIMARY',
                            style: TextStyle(
                              color: Colors.blue,
                              fontWeight: FontWeight.bold,
                              fontSize: 12,
                            ),
                          ),
                        ),
                    ],
                  ),
                  trailing: PopupMenuButton(
                    itemBuilder: (context) => [
                      if (!resume.isPrimary)
                        const PopupMenuItem(
                          value: 'set_primary',
                          child: Row(
                            children: [
                              Icon(Icons.star, size: 20),
                              SizedBox(width: 8),
                              Text('Set as Primary'),
                            ],
                          ),
                        ),
                      const PopupMenuItem(
                        value: 'delete',
                        child: Row(
                          children: [
                            Icon(Icons.delete, size: 20, color: Colors.red),
                            SizedBox(width: 8),
                            Text('Delete', style: TextStyle(color: Colors.red)),
                          ],
                        ),
                      ),
                    ],
                    onSelected: (value) async {
                      if (value == 'set_primary') {
                        await ref
                            .read(exampleResumesProvider.notifier)
                            .setPrimary(resume.id);
                      } else if (value == 'delete') {
                        final confirmed = await showDialog<bool>(
                          context: context,
                          builder: (context) => AlertDialog(
                            title: const Text('Delete Resume'),
                            content: Text(
                              'Are you sure you want to delete "${resume.originalFilename}"?',
                            ),
                            actions: [
                              TextButton(
                                onPressed: () =>
                                    Navigator.of(context).pop(false),
                                child: const Text('Cancel'),
                              ),
                              TextButton(
                                onPressed: () =>
                                    Navigator.of(context).pop(true),
                                child: const Text(
                                  'Delete',
                                  style: TextStyle(color: Colors.red),
                                ),
                              ),
                            ],
                          ),
                        );

                        if (confirmed == true) {
                          await ref
                              .read(exampleResumesProvider.notifier)
                              .delete(resume.id);
                        }
                      }
                    },
                  ),
                ),
              );
            },
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => Center(
          child: Padding(
            padding: const EdgeInsets.all(32.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(
                  Icons.error_outline,
                  size: 64,
                  color: Colors.red,
                ),
                const SizedBox(height: 16),
                Text(
                  'Failed to load resumes',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 8),
                Text(
                  error.toString(),
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: Colors.grey),
                ),
                const SizedBox(height: 24),
                ElevatedButton.icon(
                  onPressed: () {
                    ref.invalidate(exampleResumesProvider);
                  },
                  icon: const Icon(Icons.refresh),
                  label: const Text('Retry'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
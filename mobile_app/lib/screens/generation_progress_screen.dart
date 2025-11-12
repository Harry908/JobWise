import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../models/generation.dart';
import '../providers/generation_provider.dart';

/// Screen for displaying real-time generation progress with stage tracking
class GenerationProgressScreen extends ConsumerStatefulWidget {
  final String generationId;

  const GenerationProgressScreen({
    super.key,
    required this.generationId,
  });

  @override
  ConsumerState<GenerationProgressScreen> createState() =>
      _GenerationProgressScreenState();
}

class _GenerationProgressScreenState
    extends ConsumerState<GenerationProgressScreen> {
  bool _navigatedToResult = false;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final generationStream =
        ref.watch(generationStreamProvider(widget.generationId));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Generating Document'),
        automaticallyImplyLeading: false,
      ),
      body: generationStream.when(
        data: (generation) {
          // Auto-navigate to result on completion (only once)
          if (generation.isComplete && !_navigatedToResult) {
            _navigatedToResult = true;
            WidgetsBinding.instance.addPostFrameCallback((_) {
              if (mounted) {
                context.go('/generations/${generation.id}/result');
              }
            });
          }

          // Show error state
          if (generation.isFailed) {
            return _buildErrorState(theme, generation);
          }

          // Show cancelled state
          if (generation.status == GenerationStatus.cancelled) {
            return _buildCancelledState(theme);
          }

          // Show progress
          return _buildProgressView(theme, generation);
        },
        loading: () => _buildLoadingState(theme),
        error: (error, stackTrace) => _buildErrorView(theme, error),
      ),
    );
  }

  Widget _buildProgressView(ThemeData theme, Generation generation) {
    return Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Animated progress indicator
            _buildProgressIndicator(theme, generation),
            const SizedBox(height: 48),

            // Stage indicators
            _buildStageIndicators(theme, generation),
            const SizedBox(height: 32),

            // Current stage info
            _buildCurrentStageInfo(theme, generation),
            const SizedBox(height: 48),

            // Estimated time remaining
            if (generation.estimatedCompletion != null)
              _buildEstimatedTime(theme, generation),

            const SizedBox(height: 32),

            // Cancel button (only if still processing)
            if (generation.isProcessing) _buildCancelButton(theme),
          ],
        ),
      ),
    );
  }

  Widget _buildProgressIndicator(ThemeData theme, Generation generation) {
    final percentage = generation.progress.percentage / 100;

    return SizedBox(
      width: 200,
      height: 200,
      child: Stack(
        alignment: Alignment.center,
        children: [
          SizedBox(
            width: 200,
            height: 200,
            child: CircularProgressIndicator(
              value: percentage,
              strokeWidth: 12,
              backgroundColor: theme.colorScheme.surfaceContainerHighest,
              valueColor: AlwaysStoppedAnimation<Color>(
                theme.colorScheme.primary,
              ),
            ),
          ),
          Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                '${generation.progress.percentage}%',
                style: theme.textTheme.displaySmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: theme.colorScheme.primary,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                'Complete',
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStageIndicators(ThemeData theme, Generation generation) {
    return Column(
      children: List.generate(
        generation.progress.totalStages,
        (index) {
          final stageNumber = index + 1;
          final isComplete = generation.progress.currentStage > stageNumber;
          final isCurrent = generation.progress.currentStage == stageNumber;

          return Padding(
            padding: const EdgeInsets.symmetric(vertical: 8.0),
            child: Row(
              children: [
                // Stage indicator icon
                Container(
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: isComplete
                        ? theme.colorScheme.primary
                        : isCurrent
                            ? theme.colorScheme.primaryContainer
                            : theme.colorScheme.surfaceContainerHighest,
                  ),
                  child: Center(
                    child: isComplete
                        ? Icon(
                            Icons.check,
                            color: theme.colorScheme.onPrimary,
                            size: 20,
                          )
                        : isCurrent
                            ? SizedBox(
                                width: 20,
                                height: 20,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  valueColor: AlwaysStoppedAnimation<Color>(
                                    theme.colorScheme.primary,
                                  ),
                                ),
                              )
                            : Text(
                                '$stageNumber',
                                style: theme.textTheme.bodyMedium?.copyWith(
                                  color: theme.colorScheme.onSurfaceVariant,
                                ),
                              ),
                  ),
                ),
                const SizedBox(width: 16),

                // Stage info
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        _getStageName(stageNumber),
                        style: theme.textTheme.titleSmall?.copyWith(
                          fontWeight: isCurrent ? FontWeight.bold : FontWeight.normal,
                          color: isCurrent
                              ? theme.colorScheme.primary
                              : isComplete
                                  ? theme.colorScheme.onSurface
                                  : theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                      Text(
                        _getStageDescription(stageNumber),
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  String _getStageName(int stage) {
    switch (stage) {
      case 1:
        return 'Analysis & Matching';
      case 2:
        return 'Generation & Validation';
      default:
        return 'Stage $stage';
    }
  }

  String _getStageDescription(int stage) {
    switch (stage) {
      case 1:
        return 'Analyzing job and matching with your profile content';
      case 2:
        return 'Generating tailored resume and validating quality';
      default:
        return 'Processing...';
    }
  }

  Widget _buildCurrentStageInfo(ThemeData theme, Generation generation) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.info_outline,
                  color: theme.colorScheme.primary,
                  size: 20,
                ),
                const SizedBox(width: 8),
                Text(
                  'Current Status',
                  style: theme.textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              generation.progress.stageDescription ?? 'Processing...',
              style: theme.textTheme.bodyMedium,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEstimatedTime(ThemeData theme, Generation generation) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(
          Icons.schedule,
          size: 16,
          color: theme.colorScheme.onSurfaceVariant,
        ),
        const SizedBox(width: 4),
        Text(
          'Estimated: ${generation.estimatedCompletion}',
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
      ],
    );
  }

  Widget _buildCancelButton(ThemeData theme) {
    return OutlinedButton.icon(
      onPressed: () => _showCancelDialog(),
      icon: const Icon(Icons.cancel),
      label: const Text('Cancel Generation'),
      style: OutlinedButton.styleFrom(
        foregroundColor: theme.colorScheme.error,
        side: BorderSide(color: theme.colorScheme.error),
      ),
    );
  }

  Widget _buildLoadingState(ThemeData theme) {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          CircularProgressIndicator(),
          SizedBox(height: 16),
          Text('Loading generation status...'),
        ],
      ),
    );
  }

  Widget _buildErrorState(ThemeData theme, Generation generation) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 64,
              color: theme.colorScheme.error,
            ),
            const SizedBox(height: 16),
            Text(
              'Generation Failed',
              style: theme.textTheme.headlineSmall?.copyWith(
                color: theme.colorScheme.error,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              generation.errorMessage ?? 'An unexpected error occurred',
              textAlign: TextAlign.center,
              style: theme.textTheme.bodyMedium,
            ),
            const SizedBox(height: 32),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                OutlinedButton(
                  onPressed: () => context.pop(),
                  child: const Text('Go Back'),
                ),
                const SizedBox(width: 16),
                FilledButton.icon(
                  onPressed: () {
                    // TODO: Implement retry with same options
                    context.pop();
                  },
                  icon: const Icon(Icons.refresh),
                  label: const Text('Retry'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCancelledState(ThemeData theme) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.cancel_outlined,
              size: 64,
              color: theme.colorScheme.onSurfaceVariant,
            ),
            const SizedBox(height: 16),
            Text(
              'Generation Cancelled',
              style: theme.textTheme.headlineSmall,
            ),
            const SizedBox(height: 8),
            Text(
              'The generation was cancelled',
              textAlign: TextAlign.center,
              style: theme.textTheme.bodyMedium,
            ),
            const SizedBox(height: 32),
            FilledButton(
              onPressed: () => context.pop(),
              child: const Text('Go Back'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorView(ThemeData theme, Object error) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 64,
              color: theme.colorScheme.error,
            ),
            const SizedBox(height: 16),
            Text(
              'Error Loading Status',
              style: theme.textTheme.headlineSmall?.copyWith(
                color: theme.colorScheme.error,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              error.toString(),
              textAlign: TextAlign.center,
              style: theme.textTheme.bodyMedium,
            ),
            const SizedBox(height: 32),
            FilledButton.icon(
              onPressed: () => context.pop(),
              icon: const Icon(Icons.arrow_back),
              label: const Text('Go Back'),
            ),
          ],
        ),
      ),
    );
  }

  void _showCancelDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Cancel Generation?'),
        content: const Text(
          'Are you sure you want to cancel this generation? This action cannot be undone.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('No, Continue'),
          ),
          FilledButton(
            onPressed: () async {
              final navigator = Navigator.of(context);
              final scaffoldMessenger = ScaffoldMessenger.of(context);
              navigator.pop();
              try {
                await ref
                    .read(generationProvider.notifier)
                    .cancelGeneration(widget.generationId);
                if (mounted) {
                  navigator.pop();
                }
              } catch (e) {
                if (mounted) {
                  scaffoldMessenger.showSnackBar(
                    SnackBar(
                      content: Text('Failed to cancel: ${e.toString()}'),
                      backgroundColor: Colors.red,
                    ),
                  );
                }
              }
            },
            style: FilledButton.styleFrom(
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
            child: const Text('Yes, Cancel'),
          ),
        ],
      ),
    );
  }
}

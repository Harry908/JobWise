import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../models/generation.dart';
import '../providers/generation_provider.dart';
// TODO: Add share_plus and url_launcher packages to pubspec.yaml
// import 'package:share_plus/share_plus.dart';
// import 'package:url_launcher/url_launcher.dart';

/// Screen for displaying generation results with ATS score and recommendations
class GenerationResultScreen extends ConsumerWidget {
  final String generationId;

  const GenerationResultScreen({
    super.key,
    required this.generationId,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final generationAsync = ref.watch(activeGenerationProvider(generationId));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Generation Result'),
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            tooltip: 'View History',
            onPressed: () => context.push('/generations'),
          ),
        ],
      ),
      body: generationAsync.when(
        data: (generation) {
          if (generation.status != GenerationStatus.completed) {
            return _buildNotCompleteView(theme, generation);
          }

          if (generation.result == null) {
            return _buildNoResultView(theme);
          }

          return _buildResultView(
            context,
            theme,
            generation,
            ref.watch(activeGenerationProvider(generationId).notifier).getRawResult(),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stackTrace) => _buildErrorView(theme, error),
      ),
    );
  }

  Widget _buildResultView(
    BuildContext context,
    ThemeData theme,
    Generation generation,
    Future<Map<String, dynamic>> fullResultFuture,
  ) {
    final result = generation.result!;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Success header
          _buildSuccessHeader(theme),
          const SizedBox(height: 24),

          // ATS Score Card
          _buildATSScoreCard(theme, result),
          const SizedBox(height: 16),

          // Metrics Cards
          Row(
            children: [
              Expanded(
                child: _buildMetricCard(
                  theme,
                  'Match',
                  '${result.matchPercentage}%',
                  Icons.verified,
                  Colors.green,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildMetricCard(
                  theme,
                  'Keywords',
                  '${result.keywordsMatched}/${result.keywordsTotal}',
                  Icons.key,
                  Colors.blue,
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),

          // Recommendations
          if (result.recommendations.isNotEmpty) ...[
            _buildRecommendationsCard(theme, result.recommendations),
            const SizedBox(height: 24),
          ],

          // Generation Info
          _buildGenerationInfo(theme, generation),
          const SizedBox(height: 24),

          // Resume Content
          FutureBuilder<Map<String, dynamic>>(
            future: fullResultFuture,
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Card(
                  child: Padding(
                    padding: EdgeInsets.all(32.0),
                    child: Center(
                      child: CircularProgressIndicator(),
                    ),
                  ),
                );
              } else if (snapshot.hasError) {
                return Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Text(
                      'Error loading content: ${snapshot.error}',
                      style: TextStyle(color: theme.colorScheme.error),
                    ),
                  ),
                );
              } else if (snapshot.hasData) {
                return _buildResumeContent(context, theme, snapshot.data!);
              } else {
                return const SizedBox.shrink();
              }
            },
          ),
          const SizedBox(height: 24),

          // Action Buttons (simplified)
          _buildActionButtons(context, theme, result),
          const SizedBox(height: 16),
        ],
      ),
    );
  }

  Widget _buildSuccessHeader(ThemeData theme) {
    return Card(
      color: theme.colorScheme.primaryContainer,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Row(
          children: [
            Icon(
              Icons.check_circle,
              color: theme.colorScheme.primary,
              size: 48,
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Generation Complete!',
                    style: theme.textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: theme.colorScheme.onPrimaryContainer,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Your tailored resume is ready',
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onPrimaryContainer,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildATSScoreCard(ThemeData theme, GenerationResult result) {
    final score = result.atsScore;
    final scoreColor = _getScoreColor(score);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          children: [
            Text(
              'ATS Score',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Stack(
              alignment: Alignment.center,
              children: [
                SizedBox(
                  width: 150,
                  height: 150,
                  child: CircularProgressIndicator(
                    value: score / 100,
                    strokeWidth: 16,
                    backgroundColor: theme.colorScheme.surfaceContainerHighest,
                    valueColor: AlwaysStoppedAnimation<Color>(scoreColor),
                  ),
                ),
                Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      '${score.toInt()}',
                      style: theme.textTheme.displayLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: scoreColor,
                      ),
                    ),
                    Text(
                      _getScoreLabel(score),
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 16),
            Text(
              _getScoreDescription(score),
              textAlign: TextAlign.center,
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Color _getScoreColor(double score) {
    if (score >= 80) return Colors.green;
    if (score >= 60) return Colors.orange;
    return Colors.red;
  }

  String _getScoreLabel(double score) {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Needs Work';
  }

  String _getScoreDescription(double score) {
    if (score >= 80) {
      return 'Your resume is highly optimized for ATS systems and should pass most screenings.';
    } else if (score >= 60) {
      return 'Your resume has good ATS compatibility. Consider implementing the recommendations below.';
    } else if (score >= 40) {
      return 'Your resume needs improvement for better ATS performance. Review recommendations carefully.';
    } else {
      return 'Your resume may have difficulty passing ATS screenings. Please review all recommendations.';
    }
  }

  Widget _buildMetricCard(
    ThemeData theme,
    String label,
    String value,
    IconData icon,
    Color color,
  ) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Icon(icon, size: 32, color: color),
            const SizedBox(height: 8),
            Text(
              value,
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecommendationsCard(
    ThemeData theme,
    List<String> recommendations,
  ) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.lightbulb_outline,
                  color: theme.colorScheme.primary,
                  size: 20,
                ),
                const SizedBox(width: 8),
                Text(
                  'Recommendations',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ...recommendations.map(
              (recommendation) => Padding(
                padding: const EdgeInsets.only(bottom: 12.0),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(
                      Icons.arrow_right,
                      color: theme.colorScheme.primary,
                      size: 20,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        recommendation,
                        style: theme.textTheme.bodyMedium,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildGenerationInfo(ThemeData theme, Generation generation) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Generation Details',
              style: theme.textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            _buildInfoRow(
              theme,
              'Document Type',
              generation.documentType == DocumentType.resume
                  ? 'Resume'
                  : 'Cover Letter',
            ),
            _buildInfoRow(
              theme,
              'Generated',
              _formatDate(generation.completedAt ?? generation.createdAt),
            ),
            if (generation.generationTime != null)
              _buildInfoRow(
                theme,
                'Generation Time',
                '${generation.generationTime!.toStringAsFixed(1)}s',
              ),
            if (generation.tokensUsed > 0)
              _buildInfoRow(
                theme,
                'Tokens Used',
                '${generation.tokensUsed}',
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(ThemeData theme, String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
          Text(
            value,
            style: theme.textTheme.bodyMedium?.copyWith(
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildResumeContent(
      BuildContext context, ThemeData theme, Map<String, dynamic> fullResult) {
    // Extract content from the result
    // The backend returns content as a Map with formats: text, html, markdown
    final contentMap = fullResult['content'] as Map<String, dynamic>?;
    final textContent = contentMap?['text'] as String? ?? 'No content available';

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Resume Content',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.copy),
                  tooltip: 'Copy to clipboard',
                  onPressed: () {
                    Clipboard.setData(ClipboardData(text: textContent));
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('Copied to clipboard'),
                        duration: Duration(seconds: 2),
                      ),
                    );
                  },
                ),
              ],
            ),
            const Divider(),
            const SizedBox(height: 8),
            Container(
              constraints: const BoxConstraints(maxHeight: 400),
              decoration: BoxDecoration(
                color: theme.colorScheme.surfaceContainerHighest
                    .withAlpha(100),
                borderRadius: BorderRadius.circular(8),
              ),
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(12.0),
                child: SelectableText(
                  textContent,
                  style: theme.textTheme.bodyMedium?.copyWith(
                    fontFamily: 'monospace',
                    fontSize: 12,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year} ${date.hour}:${date.minute.toString().padLeft(2, '0')}';
  }

  Widget _buildActionButtons(
    BuildContext context,
    ThemeData theme,
    GenerationResult result,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        FilledButton.icon(
          onPressed: () => _handleViewPDF(context, result.pdfUrl),
          icon: const Icon(Icons.picture_as_pdf),
          label: const Text('View PDF'),
          style: FilledButton.styleFrom(
            padding: const EdgeInsets.all(16),
          ),
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: OutlinedButton.icon(
                onPressed: () => _handleDownload(context, result.pdfUrl),
                icon: const Icon(Icons.download),
                label: const Text('Download'),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: OutlinedButton.icon(
                onPressed: () => _handleShare(context, result.pdfUrl),
                icon: const Icon(Icons.share),
                label: const Text('Share'),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        TextButton.icon(
          onPressed: () {
            // TODO: Implement regenerate with new options
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Regeneration feature coming soon'),
              ),
            );
          },
          icon: const Icon(Icons.refresh),
          label: const Text('Regenerate with Different Options'),
        ),
      ],
    );
  }

  Future<void> _handleViewPDF(BuildContext context, String? pdfUrl) async {
    if (pdfUrl == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('PDF not available'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    // TODO: Implement with url_launcher package
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('View PDF feature coming soon - add url_launcher package'),
      ),
    );
  }

  Future<void> _handleDownload(BuildContext context, String? pdfUrl) async {
    if (pdfUrl == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('PDF not available'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    // TODO: Implement actual download logic
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Download feature coming soon'),
      ),
    );
  }

  Future<void> _handleShare(BuildContext context, String? pdfUrl) async {
    if (pdfUrl == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('PDF not available'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    // TODO: Implement with share_plus package
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Share feature coming soon - add share_plus package'),
      ),
    );
  }

  Widget _buildNotCompleteView(ThemeData theme, Generation generation) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.hourglass_empty,
              size: 64,
              color: theme.colorScheme.primary,
            ),
            const SizedBox(height: 16),
            Text(
              'Generation Not Complete',
              style: theme.textTheme.headlineSmall,
            ),
            const SizedBox(height: 8),
            Text(
              'Status: ${generation.status.name}',
              textAlign: TextAlign.center,
              style: theme.textTheme.bodyMedium,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNoResultView(ThemeData theme) {
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
              'No Result Available',
              style: theme.textTheme.headlineSmall?.copyWith(
                color: theme.colorScheme.error,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'The generation result is not available',
              textAlign: TextAlign.center,
              style: theme.textTheme.bodyMedium,
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
              'Error Loading Result',
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
          ],
        ),
      ),
    );
  }
}

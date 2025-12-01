import 'dart:io' show File;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:file_picker/file_picker.dart';
import '../models/profile.dart' as model;
import '../providers/profile_provider.dart';
import '../providers/samples_provider.dart';
import '../providers/generations_provider.dart';
import '../widgets/error_display.dart';

class ProfileViewScreen extends ConsumerStatefulWidget {
  const ProfileViewScreen({super.key});

  @override
  ConsumerState<ProfileViewScreen> createState() => _ProfileViewScreenState();
}

class _ProfileViewScreenState extends ConsumerState<ProfileViewScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    // Load samples once when screen initializes
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(samplesProvider.notifier).loadSamples();
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _enhanceProfile(BuildContext context, model.Profile profile) async {
    final generationsState = ref.read(generationsProvider);
    
    if (generationsState.isEnhancing) {
      return; // Already enhancing
    }

    // Show confirmation dialog
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('AI Profile Enhancement'),
        content: const Text(
          'This will use AI to enhance your profile descriptions based on your writing style from uploaded samples.\n\n'
          'Make sure you have uploaded a cover letter sample for best results.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Enhance'),
          ),
        ],
      ),
    );

    if (confirmed != true || !context.mounted) return;

    // Show progress dialog
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const AlertDialog(
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('Enhancing profile with AI...'),
          ],
        ),
      ),
    );

    // Call enhancement API
    final success = await ref.read(generationsProvider.notifier).enhanceProfile(
      profileId: profile.id,
    );

    if (!context.mounted) return;
    
    // Close progress dialog
    Navigator.pop(context);

    if (success) {
      // Refresh profile to show enhanced descriptions
      ref.invalidate(profileProvider);
      
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('✨ Profile enhanced successfully!'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } else {
      final error = ref.read(generationsProvider).errorMessage;
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(error ?? 'Failed to enhance profile'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final profileAsync = ref.watch(profileProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Profile'),
        actions: profileAsync.maybeWhen(
          data: (profile) => profile != null
              ? [
                  IconButton(
                    icon: const Icon(Icons.edit),
                    tooltip: 'Edit Profile',
                    onPressed: () => context.push('/profile/edit'),
                  )
                ]
              : [],
          orElse: () => [],
        ),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(icon: Icon(Icons.person), text: 'Profile'),
            Tab(icon: Icon(Icons.auto_awesome), text: 'AI Preferences'),
          ],
        ),
      ),
      body: profileAsync.when(
        data: (profile) {
          if (profile == null) {
            return ErrorDisplay(
              message: 'No profile found. Please create one first.',
              onRetry: () => context.push('/profile/edit'),
              retryText: 'Create Profile',
            );
          }
          return TabBarView(
            controller: _tabController,
            children: [
              // Profile Tab
              RefreshIndicator(
                onRefresh: () => ref.refresh(profileProvider.future),
                child: SingleChildScrollView(
                  physics: const AlwaysScrollableScrollPhysics(),
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // AI Enhancement Button
                      Center(
                        child: ElevatedButton.icon(
                          onPressed: () => _enhanceProfile(context, profile),
                          icon: const Icon(Icons.auto_awesome),
                          label: const Text('AI Enhance Profile'),
                          style: ElevatedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 24,
                              vertical: 12,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 24),
                      _buildPersonalInfoSection(context, profile),
                      const SizedBox(height: 24),
                      if (profile.professionalSummary != null &&
                          profile.professionalSummary!.isNotEmpty)
                        _buildProfessionalSummarySection(context, profile),
                      if (profile.professionalSummary != null &&
                          profile.professionalSummary!.isNotEmpty)
                        const SizedBox(height: 24),
                      _buildExperiencesSection(context, profile.experiences),
                      const SizedBox(height: 24),
                      _buildEducationSection(context, profile.education),
                      const SizedBox(height: 24),
                      _buildSkillsSection(context, profile.skills),
                      const SizedBox(height: 24),
                      _buildProjectsSection(context, profile.projects),
                      const SizedBox(height: 32),
                    ],
                  ),
                ),
              ),
              // AI Preferences Tab
              RefreshIndicator(
                onRefresh: () async {
                  await ref.read(samplesProvider.notifier).loadSamples();
                },
                child: SingleChildScrollView(
                  physics: const AlwaysScrollableScrollPhysics(),
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _buildAIGenerationPreferencesSection(context),
                      const SizedBox(height: 32),
                    ],
                  ),
                ),
              ),
            ],
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, stack) => ErrorDisplay(
          message: 'Failed to load profile: ${err.toString()}',
          onRetry: () => ref.invalidate(profileProvider),
        ),
      ),
    );
  }

  Widget _buildPersonalInfoSection(BuildContext context, model.Profile profile) {
    final theme = Theme.of(context);
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                IconButton(
                  icon: const Icon(Icons.edit, size: 20),
                  onPressed: () => context.push('/profile/edit'),
                  tooltip: 'Edit Contact Info',
                  padding: EdgeInsets.zero,
                  constraints: const BoxConstraints(),
                ),
              ],
            ),
            Row(
              children: [
                CircleAvatar(
                  radius: 40,
                  backgroundColor: theme.colorScheme.primary,
                  child: Text(
                    profile.personalInfo.fullName.isNotEmpty
                        ? profile.personalInfo.fullName.substring(0, 1).toUpperCase()
                        : '?',
                    style: const TextStyle(
                      fontSize: 32,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        profile.personalInfo.fullName,
                        style: theme.textTheme.headlineMedium
                            ?.copyWith(fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 4),
                      if (profile.personalInfo.location != null)
                        Row(
                          children: [
                            Icon(
                              Icons.location_on,
                              size: 16,
                              color: theme.colorScheme.onSurfaceVariant,
                            ),
                            const SizedBox(width: 4),
                            Flexible(
                              child: Text(
                                profile.personalInfo.location!,
                                style: theme.textTheme.bodyMedium?.copyWith(
                                  color: theme.colorScheme.onSurfaceVariant,
                                ),
                              ),
                            ),
                          ],
                        ),
                    ],
                  ),
                ),
              ],
            ),
            const Divider(height: 24),
            _buildContactInfo(
                Icons.email, profile.personalInfo.email, theme),
            if (profile.personalInfo.phone != null)
              _buildContactInfo(
                  Icons.phone, profile.personalInfo.phone!, theme),
            if (profile.personalInfo.linkedin != null)
              _buildContactInfo(
                  Icons.link, profile.personalInfo.linkedin!, theme),
            if (profile.personalInfo.github != null)
              _buildContactInfo(
                  Icons.code, profile.personalInfo.github!, theme),
            if (profile.personalInfo.website != null)
              _buildContactInfo(
                  Icons.web, profile.personalInfo.website!, theme),
          ],
        ),
      ),
    );
  }

  Widget _buildContactInfo(IconData icon, String text, ThemeData theme) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        children: [
          Icon(icon, size: 20, color: theme.colorScheme.primary),
          const SizedBox(width: 12),
          Expanded(
            child: Text(text, style: theme.textTheme.bodyMedium),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(BuildContext context, String title, {VoidCallback? onAdd}) {
    return Row(
      children: [
        Expanded(
          child: Text(
            title,
            style: Theme.of(context)
                .textTheme
                .headlineSmall
                ?.copyWith(fontWeight: FontWeight.bold),
          ),
        ),
        if (onAdd != null)
          IconButton(
            icon: const Icon(Icons.add_circle_outline),
            onPressed: onAdd,
            tooltip: 'Add $title',
            color: Theme.of(context).colorScheme.primary,
          ),
      ],
    );
  }

  Widget _buildProfessionalSummarySection(
      BuildContext context, model.Profile profile) {
    final theme = Theme.of(context);
    final hasEnhanced = profile.enhancedSummary != null && 
                       profile.enhancedSummary!.isNotEmpty;
    final displaySummary = profile.professionalSummary ?? '';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSectionHeader(context, 'Professional Summary'),
        const SizedBox(height: 8),
        Card(
          elevation: 1,
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    IconButton(
                      icon: const Icon(Icons.edit, size: 20),
                      onPressed: () => context.push('/profile/edit'),
                      tooltip: 'Edit Summary',
                      padding: EdgeInsets.zero,
                      constraints: const BoxConstraints(),
                    ),
                  ],
                ),
                if (hasEnhanced) ...[
                  Text(
                    'AI Enhanced Summary',
                    style: theme.textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: Colors.green[700],
                    ),
                  ),
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.green.withAlpha(26),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.green.withAlpha(51)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(Icons.auto_awesome, size: 16, color: Colors.green[700]),
                            const SizedBox(width: 4),
                            Text(
                              'AI Enhanced',
                              style: theme.textTheme.labelSmall?.copyWith(
                                color: Colors.green[700],
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(
                          profile.enhancedSummary!,
                          style: theme.textTheme.bodyMedium?.copyWith(height: 1.4),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'Original Summary',
                    style: theme.textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                  const SizedBox(height: 8),
                  ExpansionTile(
                    tilePadding: EdgeInsets.zero,
                    title: Text(
                      'View Original',
                      style: theme.textTheme.labelSmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                    children: [
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: theme.colorScheme.surfaceContainerHighest,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          displaySummary,
                          style: theme.textTheme.bodyMedium?.copyWith(
                            height: 1.4,
                            color: theme.colorScheme.onSurfaceVariant,
                          ),
                        ),
                      ),
                    ],
                  ),
                ] else ...[
                  Text(
                    displaySummary,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(height: 1.5),
                  ),
                ],
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildExperiencesSection(
      BuildContext context, List<model.Experience> experiences) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSectionHeader(
          context,
          'Work Experience',
          onAdd: () => context.push('/profile/edit'),
        ),
        const SizedBox(height: 8),
        if (experiences.isEmpty)
          _buildEmptySectionCard(context, 'No work experience added yet.')
        else
          ...experiences.map((exp) => _buildExperienceCard(context, exp)),
      ],
    );
  }

  Widget _buildExperienceCard(BuildContext context, model.Experience experience) {
    final theme = Theme.of(context);
    final hasEnhanced = experience.enhancedDescription != null && 
                        experience.enhancedDescription!.isNotEmpty;
    
    return Card(
      elevation: 1,
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    experience.title,
                    style: theme.textTheme.titleMedium
                        ?.copyWith(fontWeight: FontWeight.bold),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.edit, size: 20),
                  onPressed: () => context.push('/profile/edit'),
                  tooltip: 'Edit Experience',
                  padding: EdgeInsets.zero,
                  constraints: const BoxConstraints(),
                ),
              ],
            ),
            const SizedBox(height: 4),
            Text(
              experience.company,
              style: theme.textTheme.bodyLarge
                  ?.copyWith(color: theme.colorScheme.primary),
            ),
            if (experience.location != null) ...[
              const SizedBox(height: 4),
              _buildDetailRow(theme, Icons.location_on, experience.location!),
            ],
            const SizedBox(height: 4),
            _buildDetailRow(
                theme,
                Icons.calendar_today,
                _formatStringDateRange(
                    experience.startDate, experience.endDate)),
            if (experience.description != null &&
                experience.description!.isNotEmpty) ...[
              const SizedBox(height: 12),
              if (hasEnhanced) ...[
                Text(
                  'AI Enhanced Description',
                  style: theme.textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: Colors.green[700],
                  ),
                ),
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.green.withAlpha(26),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.green.withAlpha(51)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.auto_awesome, size: 16, color: Colors.green[700]),
                          const SizedBox(width: 4),
                          Text(
                            'AI Enhanced',
                            style: theme.textTheme.labelSmall?.copyWith(
                              color: Colors.green[700],
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        experience.enhancedDescription!,
                        style: theme.textTheme.bodyMedium?.copyWith(height: 1.4),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  'Original Description',
                  style: theme.textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
                const SizedBox(height: 8),
                ExpansionTile(
                  tilePadding: EdgeInsets.zero,
                  title: Text(
                    'View Original',
                    style: theme.textTheme.labelSmall?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                  children: [
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: theme.colorScheme.surfaceContainerHighest,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        experience.description!,
                        style: theme.textTheme.bodyMedium?.copyWith(
                          height: 1.4,
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                    ),
                  ],
                ),
              ] else ...[
                Text(
                  experience.description!,
                  style: theme.textTheme.bodyMedium?.copyWith(height: 1.4),
                ),
              ],
            ],
            if (experience.achievements.isNotEmpty) ...[
              const SizedBox(height: 12),
              ...experience.achievements
                  .map((a) => _buildBulletPoint(theme, a)),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildEducationSection(
      BuildContext context, List<model.Education> education) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSectionHeader(
          context,
          'Education',
          onAdd: () => context.push('/profile/edit'),
        ),
        const SizedBox(height: 8),
        if (education.isEmpty)
          _buildEmptySectionCard(context, 'No education added yet.')
        else
          ...education.map((edu) => _buildEducationCard(context, edu)),
      ],
    );
  }

  Widget _buildEducationCard(BuildContext context, model.Education education) {
    final theme = Theme.of(context);
    return Card(
      elevation: 1,
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              education.degree,
              style: theme.textTheme.titleMedium
                  ?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 4),
            Text(
              education.institution,
              style: theme.textTheme.bodyLarge
                  ?.copyWith(color: theme.colorScheme.primary),
            ),
            const SizedBox(height: 4),
            _buildDetailRow(
                theme,
                Icons.calendar_today,
                _formatStringDateRange(
                    education.startDate, education.endDate)),
            if (education.gpa != null) ...[
              const SizedBox(height: 4),
              Text(
                'GPA: ${education.gpa}',
                style: theme.textTheme.bodyMedium
                    ?.copyWith(fontWeight: FontWeight.w500),
              ),
            ],
            if (education.honors.isNotEmpty) ...[
              const SizedBox(height: 12),
              ...education.honors.map((h) => _buildBulletPoint(theme, h)),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildSkillsSection(BuildContext context, model.Skills skills) {
    final theme = Theme.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSectionHeader(
          context,
          'Skills',
          onAdd: () => context.push('/profile/edit'),
        ),
        const SizedBox(height: 8),
        Card(
          elevation: 1,
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (skills.technical.isNotEmpty) ...[
                  Text(
                    'Technical Skills',
                    style: theme.textTheme.titleMedium
                        ?.copyWith(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: skills.technical.map((skill) {
                      return Chip(
                        label: Text(skill),
                        backgroundColor:
                            theme.colorScheme.primary.withAlpha(26),
                        labelStyle: TextStyle(
                          color: theme.colorScheme.primary,
                          fontWeight: FontWeight.w500,
                        ),
                      );
                    }).toList(),
                  ),
                ],
                if (skills.technical.isNotEmpty && skills.soft.isNotEmpty)
                  const SizedBox(height: 16),
                if (skills.soft.isNotEmpty) ...[
                  Text(
                    'Soft Skills',
                    style: theme.textTheme.titleMedium
                        ?.copyWith(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: skills.soft.map((skill) {
                      return Chip(
                        label: Text(skill),
                        backgroundColor: Colors.green.withAlpha(26),
                        labelStyle: const TextStyle(
                          color: Colors.green,
                          fontWeight: FontWeight.w500,
                        ),
                      );
                    }).toList(),
                  ),
                ],
                if (skills.technical.isEmpty && skills.soft.isEmpty)
                  Text(
                    'No skills added yet.',
                    style: theme.textTheme.bodyMedium
                        ?.copyWith(color: theme.colorScheme.onSurfaceVariant),
                  ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildProjectsSection(BuildContext context, List<model.Project> projects) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSectionHeader(
          context,
          'Projects',
          onAdd: () => context.push('/profile/edit'),
        ),
        const SizedBox(height: 8),
        if (projects.isEmpty)
          _buildEmptySectionCard(context, 'No projects added yet.')
        else
          ...projects.map((project) => _buildProjectCard(context, project)),
      ],
    );
  }

  Widget _buildProjectCard(BuildContext context, model.Project project) {
    final theme = Theme.of(context);
    final hasEnhanced = project.enhancedDescription != null && 
                        project.enhancedDescription!.isNotEmpty;
    
    return Card(
      elevation: 1,
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    project.name,
                    style: theme.textTheme.titleMedium
                        ?.copyWith(fontWeight: FontWeight.bold),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.edit, size: 20),
                  onPressed: () => context.push('/profile/edit'),
                  tooltip: 'Edit Project',
                  padding: EdgeInsets.zero,
                  constraints: const BoxConstraints(),
                ),
              ],
            ),
            if (project.url != null) ...[
              const SizedBox(height: 4),
              Row(
                children: [
                  Icon(Icons.link, size: 16, color: theme.colorScheme.primary),
                  const SizedBox(width: 4),
                  Expanded(
                    child: Text(
                      project.url!,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: theme.colorScheme.primary,
                        decoration: TextDecoration.underline,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
            ],
            if (project.startDate != null) ...[
              const SizedBox(height: 4),
              _buildDetailRow(
                  theme,
                  Icons.calendar_today,
                  _formatStringDateRange(project.startDate, project.endDate)),
            ],
            const SizedBox(height: 12),
            if (hasEnhanced) ...[
              Text(
                'AI Enhanced Description',
                style: theme.textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: Colors.green[700],
                ),
              ),
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.green.withAlpha(26),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.green.withAlpha(51)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.auto_awesome, size: 16, color: Colors.green[700]),
                        const SizedBox(width: 4),
                        Text(
                          'AI Enhanced',
                          style: theme.textTheme.labelSmall?.copyWith(
                            color: Colors.green[700],
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      project.enhancedDescription!,
                      style: theme.textTheme.bodyMedium?.copyWith(height: 1.4),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 12),
              Text(
                'Original Description',
                style: theme.textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
              const SizedBox(height: 8),
              ExpansionTile(
                tilePadding: EdgeInsets.zero,
                title: Text(
                  'View Original',
                  style: theme.textTheme.labelSmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
                children: [
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: theme.colorScheme.surfaceContainerHighest,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      project.description,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        height: 1.4,
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ),
                ],
              ),
            ] else ...[
              Text(
                project.description,
                style: theme.textTheme.bodyMedium?.copyWith(height: 1.4),
              ),
            ],
            if (project.technologies.isNotEmpty) ...[
              const SizedBox(height: 12),
              Wrap(
                spacing: 6,
                runSpacing: 6,
                children: project.technologies.map((tech) {
                  return Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.blue.withAlpha(26),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      tech,
                      style: theme.textTheme.bodySmall
                          ?.copyWith(color: Colors.blue[700]),
                    ),
                  );
                }).toList(),
              ),
            ],
            if (project.highlights.isNotEmpty) ...[
              const SizedBox(height: 12),
              ...project.highlights.map((h) => _buildBulletPoint(theme, h)),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildEmptySectionCard(BuildContext context, String message) {
    final theme = Theme.of(context);
    return Card(
      elevation: 1,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Text(
          message,
          style: theme.textTheme.bodyMedium
              ?.copyWith(color: theme.colorScheme.onSurfaceVariant),
        ),
      ),
    );
  }

  Widget _buildDetailRow(ThemeData theme, IconData icon, String text) {
    return Row(
      children: [
        Icon(icon, size: 16, color: theme.colorScheme.onSurfaceVariant),
        const SizedBox(width: 4),
        Expanded(
          child: Text(
            text,
            style: theme.textTheme.bodyMedium
                ?.copyWith(color: theme.colorScheme.onSurfaceVariant),
          ),
        ),
      ],
    );
  }

  Widget _buildBulletPoint(ThemeData theme, String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('• ', style: TextStyle(fontSize: 16)),
          Expanded(
            child: Text(text, style: theme.textTheme.bodyMedium),
          ),
        ],
      ),
    );
  }

  String _formatStringDateRange(String? startDate, String? endDate) {
    if (startDate == null || startDate.isEmpty) return 'Date not specified';

    final start = _formatStringDate(startDate);
    final end = (endDate == null || endDate.isEmpty)
        ? 'Present'
        : _formatStringDate(endDate);

    return '$start - $end';
  }

  String _formatStringDate(String date) {
    try {
      final parsedDate = DateTime.parse(date);
      const months = [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
      ];
      return '${months[parsedDate.month - 1]} ${parsedDate.year}';
    } catch (e) {
      return date; // If parsing fails, return the date string as is
    }
  }

  Widget _buildAIGenerationPreferencesSection(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSectionHeader(context, 'AI Generation Preferences'),
        const SizedBox(height: 8),
        const Text(
          'Upload sample documents to teach the AI your preferred formatting and writing style for tailored resume and cover letter generation.',
          style: TextStyle(
            fontSize: 14,
            color: Colors.grey,
          ),
        ),
        const SizedBox(height: 16),
        const _SampleResumeUploadCard(),
        const SizedBox(height: 16),
        const _SampleCoverLetterUploadCard(),
      ],
    );
  }
}

/// View sample document text in a dialog
Future<void> _viewSampleText(WidgetRef ref, BuildContext context, String sampleId, String fileName) async {
  try {
    // Show loading dialog
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const Center(
        child: CircularProgressIndicator(),
      ),
    );

    // Fetch sample details
    final apiClient = ref.read(samplesApiClientProvider);
    final sample = await apiClient.getSample(sampleId);

    // Close loading dialog
    if (context.mounted) {
      Navigator.of(context).pop();
    }

    // Show text dialog
    if (context.mounted) {
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('Sample Content'),
          content: SizedBox(
            width: double.maxFinite,
            child: SingleChildScrollView(
              child: Text(
                sample.fullText ?? 'No text available',
                style: const TextStyle(fontFamily: 'monospace'),
              ),
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Close'),
            ),
          ],
        ),
      );
    }
  } catch (e) {
    // Close loading dialog if still open
    if (context.mounted) {
      Navigator.of(context).pop();
    }
    
    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to load sample: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }
}

class _SampleResumeUploadCard extends ConsumerWidget {
  const _SampleResumeUploadCard();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final samplesState = ref.watch(samplesProvider);
    final resumeSamples = samplesState.resumeSamples;
    final theme = Theme.of(context);

    return Card(
      elevation: 1,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.description, color: theme.colorScheme.primary),
                const SizedBox(width: 8),
                Text(
                  'Sample Resume',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              'Upload a well-formatted resume to teach the AI your preferred layout and structure.',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 16),
            samplesState.isLoading
                ? const Center(
                    child: Padding(
                      padding: EdgeInsets.all(16.0),
                      child: CircularProgressIndicator(),
                    ),
                  )
                : samplesState.errorMessage != null
                ? Column(
                children: [
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(12.0),
                    margin: const EdgeInsets.only(bottom: 16.0),
                    decoration: BoxDecoration(
                      color: Colors.red[50],
                      border: Border.all(color: Colors.red[300]!),
                      borderRadius: BorderRadius.circular(8.0),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(Icons.error, color: Colors.red[700], size: 20),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                samplesState.errorMessage ?? 'Unknown error',
                                style: TextStyle(
                                  color: Colors.red[700],
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton.icon(
                            onPressed: () {
                              ref.read(samplesProvider.notifier).loadSamples();
                            },
                            icon: const Icon(Icons.refresh, size: 18),
                            label: const Text('Retry'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.red[700],
                              foregroundColor: Colors.white,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              )
                : Column(
                children: [
                  if (resumeSamples.isNotEmpty) ...[
                    ...resumeSamples.map((resume) => ListTile(
                          contentPadding: EdgeInsets.zero,
                          leading: Icon(
                            Icons.file_copy,
                            color: theme.colorScheme.primary,
                          ),
                          title: Text(
                            'Uploaded: ${resume.createdAt.toLocal().toString().split(' ')[0]} • ${resume.wordCount} words${resume.isActive ? ' (Active)' : ''}',
                            style: theme.textTheme.bodyMedium,
                          ),
                          trailing: IconButton(
                            icon: const Icon(Icons.delete),
                            onPressed: () async {
                              try {
                                await ref
                                    .read(samplesProvider.notifier)
                                    .deleteSample(resume.id);
                                if (context.mounted) {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(
                                      content: Text('Resume deleted successfully'),
                                    ),
                                  );
                                }
                              } catch (e) {
                                if (context.mounted) {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    SnackBar(
                                      content: Text('Delete failed: $e'),
                                      backgroundColor: Colors.red,
                                    ),
                                  );
                                }
                              }
                            },
                          ),
                          onTap: () => _viewSampleText(ref, context, resume.id, resume.fileName),
                        )),
                    const SizedBox(height: 16),
                  ],
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: () => _uploadSampleResume(ref, context),
                      icon: const Icon(Icons.upload_file),
                      label: Text(
                        resumeSamples.isEmpty ? 'Upload Resume' : 'Upload Another Resume',
                      ),
                    ),
                  ),
                ],
              ),
          ],
        ),
      ),
    );
  }

  Future<void> _uploadSampleResume(WidgetRef ref, BuildContext context) async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['txt'], // Only .txt per Generation API spec
        allowMultiple: false,
      );

      if (result != null && result.files.isNotEmpty) {
        final file = result.files.first;
        
        // Validate file size (1MB limit for Generation API)
        if (file.size > 1 * 1024 * 1024) {
          if (context.mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('File size too large. Maximum allowed size is 1 MB.'),
                backgroundColor: Colors.red,
              ),
            );
          }
          return;
        }

        // Read file bytes - use bytes if available, otherwise read from path
        List<int> fileBytes;
        if (file.bytes != null) {
          fileBytes = file.bytes!;
        } else if (file.path != null) {
          fileBytes = await File(file.path!).readAsBytes();
        } else {
          if (context.mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Unable to read file. Please try again.'),
                backgroundColor: Colors.red,
              ),
            );
          }
          return;
        }

        try {
          await ref.read(samplesProvider.notifier).uploadSample(
            documentType: 'resume',
            fileName: file.name,
            fileBytes: fileBytes,
          );
          
          if (context.mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text(
                  'Resume uploaded successfully! AI can now learn from your formatting.',
                ),
                backgroundColor: Colors.green,
                duration: Duration(seconds: 3),
              ),
            );
          }
        } catch (e) {
          if (context.mounted) {
            String errorMessage = 'Upload failed: Unknown error';
            
            // Handle specific error types
            final errorStr = e.toString();
            if (errorStr.contains('413')) {
              errorMessage = 'File size too large. Maximum allowed size is 1 MB.';
            } else if (errorStr.contains('Only .txt files are supported')) {
              errorMessage = 'Only .txt files are supported for sample uploads.';
            } else if (errorStr.contains('404')) {
              errorMessage = 'Upload service not available. Please try again later.';
            } else if (errorStr.contains('401')) {
              errorMessage = 'Please log in again to upload files.';
            } else {
              errorMessage = 'Upload failed: $errorStr';
            }
            
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(errorMessage),
                backgroundColor: Colors.red,
                duration: const Duration(seconds: 5),
              ),
            );
          }
        }
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('File selection failed: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }
}

class _SampleCoverLetterUploadCard extends ConsumerWidget {
  const _SampleCoverLetterUploadCard();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final samplesState = ref.watch(samplesProvider);
    final coverLetterSample = samplesState.activeCoverLetterSample;
    final theme = Theme.of(context);

    return Card(
      elevation: 1,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.edit_document, color: Colors.green[700]),
                const SizedBox(width: 8),
                Text(
                  'Sample Cover Letter',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              'Upload a cover letter to teach the AI your preferred writing style and tone.',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 16),
            if (samplesState.isLoading)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(16.0),
                  child: CircularProgressIndicator(),
                ),
              )
            else if (samplesState.errorMessage != null)
              Column(
                children: [
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(12.0),
                    margin: const EdgeInsets.only(bottom: 16.0),
                    decoration: BoxDecoration(
                      color: Colors.red[50],
                      border: Border.all(color: Colors.red[300]!),
                      borderRadius: BorderRadius.circular(8.0),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(Icons.error, color: Colors.red[700], size: 20),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                samplesState.errorMessage!,
                                style: TextStyle(
                                  color: Colors.red[700],
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton.icon(
                            onPressed: () {
                              ref.read(samplesProvider.notifier).loadSamples();
                            },
                            icon: const Icon(Icons.refresh, size: 18),
                            label: const Text('Retry'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.red[700],
                              foregroundColor: Colors.white,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              )
            else
              Column(
                children: [
                  if (coverLetterSample != null) ...[
                    ListTile(
                      contentPadding: EdgeInsets.zero,
                      leading: Icon(
                        Icons.article,
                        color: Colors.green[700],
                      ),
                      title: Text(
                        'Uploaded: ${coverLetterSample.createdAt.toLocal().toString().split(' ')[0]} • ${coverLetterSample.wordCount} words${coverLetterSample.isActive ? ' (Active)' : ''}',
                        style: theme.textTheme.bodyMedium,
                      ),
                      trailing: IconButton(
                        icon: const Icon(Icons.delete),
                        onPressed: () async {
                          try {
                            await ref
                                .read(samplesProvider.notifier)
                                .deleteSample(coverLetterSample.id);
                            if (context.mounted) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(
                                  content: Text('Cover letter sample deleted'),
                                ),
                              );
                            }
                          } catch (e) {
                            if (context.mounted) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(
                                  content: Text('Failed to delete: $e'),
                                  backgroundColor: Colors.red,
                                ),
                              );
                            }
                          }
                        },
                      ),
                      onTap: () => _viewSampleText(ref, context, coverLetterSample.id, coverLetterSample.fileName),
                    ),
                    const SizedBox(height: 16),
                  ],
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: () => _uploadCoverLetter(ref, context),
                      icon: const Icon(Icons.upload_file),
                      label: Text(
                        coverLetterSample == null
                            ? 'Upload Cover Letter'
                            : 'Upload Another Sample',
                      ),
                    ),
                  ),
                ],
              ),
          ],
        ),
      ),
    );
  }

  Future<void> _uploadCoverLetter(WidgetRef ref, BuildContext context) async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['txt'],
        allowMultiple: false,
      );

      if (result != null && result.files.isNotEmpty) {
        final file = result.files.first;
        
        // Validate file size (1MB limit for V3 API)
        if (file.size > 1 * 1024 * 1024) {
          if (context.mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('File size too large. Maximum allowed size is 1 MB.'),
                backgroundColor: Colors.red,
              ),
            );
          }
          return;
        }

        // Read file bytes - use bytes if available, otherwise read from path
        List<int> fileBytes;
        if (file.bytes != null) {
          fileBytes = file.bytes!;
        } else if (file.path != null) {
          fileBytes = await File(file.path!).readAsBytes();
        } else {
          if (context.mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Unable to read file. Please try again.'),
                backgroundColor: Colors.red,
              ),
            );
          }
          return;
        }

        try {
          await ref.read(samplesProvider.notifier).uploadSample(
            documentType: 'cover_letter',
            fileName: file.name,
            fileBytes: fileBytes,
          );
          
          if (context.mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text(
                  'Cover letter uploaded successfully! AI writing style has been updated.',
                ),
                backgroundColor: Colors.green,
                duration: Duration(seconds: 3),
              ),
            );
          }
        } catch (e) {
          if (context.mounted) {
            String errorMessage = 'Upload failed: Unknown error';
            
            // Handle specific error types
            final errorStr = e.toString();
            if (errorStr.contains('413')) {
              errorMessage = 'File size too large. Maximum allowed size is 1 MB.';
            } else if (errorStr.contains('Only .txt files are supported')) {
              errorMessage = 'Only .txt files are supported for sample uploads.';
            } else if (errorStr.contains('404')) {
              errorMessage = 'Upload service not available. Please try again later.';
            } else if (errorStr.contains('401')) {
              errorMessage = 'Please log in again to upload files.';
            } else {
              errorMessage = 'Upload failed: $errorStr';
            }
            
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(errorMessage),
                backgroundColor: Colors.red,
                duration: const Duration(seconds: 5),
              ),
            );
          }
        }
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('File selection failed: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }
}

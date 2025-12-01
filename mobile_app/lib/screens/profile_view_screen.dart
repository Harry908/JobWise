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
import '../widgets/tag_input.dart';

class ProfileViewScreen extends ConsumerStatefulWidget {
  const ProfileViewScreen({super.key});

  @override
  ConsumerState<ProfileViewScreen> createState() => _ProfileViewScreenState();
}

class _ProfileViewScreenState extends ConsumerState<ProfileViewScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  model.Profile? _pendingProfile;
  bool _hasUnsavedChanges = false;

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
    final displayProfile = _pendingProfile ?? profileAsync.value;

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Profile'),
        actions: const [],
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
          final currentProfile = displayProfile ?? profile;
          return TabBarView(
            controller: _tabController,
            children: [
              // Profile Tab
              RefreshIndicator(
                onRefresh: () async {
                  setState(() {
                    _pendingProfile = null;
                    _hasUnsavedChanges = false;
                  });
                  ref.invalidate(profileProvider);
                },
                child: SingleChildScrollView(
                  physics: const AlwaysScrollableScrollPhysics(),
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // AI Enhancement Button
                      Center(
                        child: ElevatedButton.icon(
                          onPressed: () => _enhanceProfile(context, currentProfile),
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
                      _buildPersonalInfoSection(context, currentProfile),
                      const SizedBox(height: 24),
                      if (currentProfile.professionalSummary != null &&
                          currentProfile.professionalSummary!.isNotEmpty)
                        _buildProfessionalSummarySection(context, currentProfile),
                      if (currentProfile.professionalSummary != null &&
                          currentProfile.professionalSummary!.isNotEmpty)
                        const SizedBox(height: 24),
                      _buildExperiencesSection(context, currentProfile.experiences),
                      const SizedBox(height: 24),
                      _buildEducationSection(context, currentProfile.education),
                      const SizedBox(height: 24),
                      _buildSkillsSection(context, currentProfile.skills),
                      const SizedBox(height: 24),
                      _buildProjectsSection(context, currentProfile.projects),
                      const SizedBox(height: 80), // Extra space for floating button
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
      floatingActionButton: _hasUnsavedChanges
          ? FloatingActionButton.extended(
              onPressed: () => _saveAllChanges(context),
              icon: const Icon(Icons.save),
              label: const Text('Save Changes'),
              backgroundColor: Colors.green,
            )
          : null,
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
                  onPressed: () => _showEditPersonalInfoModal(context, profile),
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
                      onPressed: () => _showEditSummaryModal(context, profile),
                      tooltip: 'Edit Summary',
                      padding: EdgeInsets.zero,
                      constraints: const BoxConstraints(),
                    ),
                  ],
                ),
                if (hasEnhanced) ...[
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'AI Enhanced Summary',
                        style: theme.textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: Colors.green[700],
                        ),
                      ),
                      IconButton(
                        icon: Icon(Icons.delete, size: 20, color: Colors.red[700]),
                        onPressed: () => _removeEnhancedSummary(context, profile),
                        tooltip: 'Remove Enhanced Summary',
                        padding: EdgeInsets.zero,
                        constraints: const BoxConstraints(),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.green.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.green.withValues(alpha: 0.2)),
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
          onAdd: () => _showEditExperienceModal(context, null),
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
                  onPressed: () => _showEditExperienceModal(context, experience),
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
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'AI Enhanced Description',
                      style: theme.textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Colors.green[700],
                      ),
                    ),
                    IconButton(
                      icon: Icon(Icons.delete, size: 20, color: Colors.red[700]),
                      onPressed: () => _removeEnhancedDescription(context, experience, 'experience'),
                      tooltip: 'Remove Enhanced Description',
                      padding: EdgeInsets.zero,
                      constraints: const BoxConstraints(),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.green.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.green.withValues(alpha: 0.2)),
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
              Text(
                'Key Achievements:',
                style: theme.textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 8),
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
          onAdd: () => _showEditEducationModal(context, null),
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
            Row(
              children: [
                Expanded(
                  child: Text(
                    education.degree,
                    style: theme.textTheme.titleMedium
                        ?.copyWith(fontWeight: FontWeight.bold),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.edit, size: 20),
                  onPressed: () => _showEditEducationModal(context, education),
                  tooltip: 'Edit Education',
                  padding: EdgeInsets.zero,
                  constraints: const BoxConstraints(),
                ),
              ],
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
          onAdd: () => _showEditSkillsModal(context, skills),
        ),
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
                      onPressed: () => _showEditSkillsModal(context, skills),
                      tooltip: 'Edit Skills',
                      padding: EdgeInsets.zero,
                      constraints: const BoxConstraints(),
                    ),
                  ],
                ),
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
                            theme.colorScheme.primary.withValues(alpha: 0.1),
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
                        backgroundColor: Colors.green.withValues(alpha: 0.1),
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
          onAdd: () => _showEditProjectModal(context, null),
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
                  onPressed: () => _showEditProjectModal(context, project),
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
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'AI Enhanced Description',
                    style: theme.textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: Colors.green[700],
                    ),
                  ),
                  IconButton(
                    icon: Icon(Icons.delete, size: 20, color: Colors.red[700]),
                    onPressed: () => _removeEnhancedDescription(context, project, 'project'),
                    tooltip: 'Remove Enhanced Description',
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.green.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.green.withValues(alpha: 0.2)),
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
                      color: Colors.blue.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      tech,
                      style: theme.textTheme.bodyMedium
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

  Future<void> _showEditPersonalInfoModal(BuildContext context, model.Profile profile) async {
    final updatedPersonalInfo = await showDialog<model.PersonalInfo>(
      context: context,
      builder: (context) => _EditPersonalInfoDialog(personalInfo: profile.personalInfo),
    );

    if (updatedPersonalInfo != null && context.mounted) {
      if (updatedPersonalInfo == profile.personalInfo) return;

      final updatedProfile = profile.copyWith(personalInfo: updatedPersonalInfo);
      
      setState(() {
        _pendingProfile = updatedProfile;
        _hasUnsavedChanges = true;
      });
      
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Personal info updated. Click "Save Changes" to apply.'),
          duration: Duration(seconds: 2),
        ),
      );
    }
  }

  Future<void> _showEditEducationModal(BuildContext context, model.Education? education) async {
    final isNew = education == null;
    final initialEducation = education ?? const model.Education(
      institution: '',
      degree: '',
      fieldOfStudy: '',
      startDate: '',
    );

    final updatedEducation = await showDialog<model.Education>(
      context: context,
      builder: (context) => _EditEducationDialog(education: initialEducation),
    );

    if (updatedEducation != null && context.mounted) {
      if (!isNew && updatedEducation == education) return;

      final currentProfile = _pendingProfile ?? ref.read(profileProvider).value;
      
      if (currentProfile != null) {
        List<model.Education> updatedList;
        if (isNew) {
          updatedList = [...currentProfile.education, updatedEducation];
        } else {
          updatedList = currentProfile.education.map((edu) {
            return (edu.id != null && edu.id == education.id) || edu == education
                ? updatedEducation 
                : edu;
          }).toList();
        }
        
        setState(() {
          _pendingProfile = currentProfile.copyWith(education: updatedList);
          _hasUnsavedChanges = true;
        });
        
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Education updated. Click "Save Changes" to apply.'),
            duration: Duration(seconds: 2),
          ),
        );
      }
    }
  }

  Future<void> _showEditSkillsModal(BuildContext context, model.Skills skills) async {
    final updatedSkills = await showDialog<model.Skills>(
      context: context,
      builder: (context) => _EditSkillsDialog(skills: skills),
    );

    if (updatedSkills != null && context.mounted) {
      if (updatedSkills == skills) return;

      final currentProfile = _pendingProfile ?? ref.read(profileProvider).value;
      
      if (currentProfile != null) {
        setState(() {
          _pendingProfile = currentProfile.copyWith(skills: updatedSkills);
          _hasUnsavedChanges = true;
        });
        
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Skills updated. Click "Save Changes" to apply.'),
            duration: Duration(seconds: 2),
          ),
        );
      }
    }
  }

  Future<void> _showEditSummaryModal(BuildContext context, model.Profile profile) async {
    final result = await showDialog<Map<String, String>>(
      context: context,
      builder: (context) => _EditSummaryDialog(
        initialSummary: profile.professionalSummary,
        initialEnhancedSummary: profile.enhancedSummary,
      ),
    );

    if (result != null && context.mounted) {
      final summaryText = result['summary']!;
      final enhancedText = result['enhanced']!;
      
      if (summaryText == (profile.professionalSummary ?? '') && 
          enhancedText == (profile.enhancedSummary ?? '')) {
        return;
      }

      final updatedProfile = profile.copyWith(
        professionalSummary: summaryText.isEmpty ? null : summaryText,
        enhancedSummary: enhancedText.isEmpty ? null : enhancedText,
      );
      
      setState(() {
        _pendingProfile = updatedProfile;
        _hasUnsavedChanges = true;
      });
      
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Summary updated. Click "Save Changes" to apply.'),
          duration: Duration(seconds: 2),
        ),
      );
    }
  }

  Future<void> _showEditExperienceModal(BuildContext context, model.Experience? experience) async {
    final isNew = experience == null;
    final initialExperience = experience ?? const model.Experience(
      id: null,
      title: '',
      company: '',
      startDate: '',
      achievements: [],
    );

    final updatedExperience = await showDialog<model.Experience>(
      context: context,
      builder: (context) => _EditExperienceDialog(experience: initialExperience),
    );

    if (updatedExperience != null && context.mounted) {
      if (!isNew && updatedExperience == experience) return;

      final currentProfile = _pendingProfile ?? ref.read(profileProvider).value;
      
      if (currentProfile != null) {
        List<model.Experience> updatedList;
        if (isNew) {
          updatedList = [...currentProfile.experiences, updatedExperience];
        } else {
          updatedList = currentProfile.experiences.map((exp) {
            return (exp.id != null && exp.id == experience.id) || exp == experience
                ? updatedExperience 
                : exp;
          }).toList();
        }
        
        setState(() {
          _pendingProfile = currentProfile.copyWith(experiences: updatedList);
          _hasUnsavedChanges = true;
        });
        
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Experience updated. Click "Save Changes" to apply.'),
            duration: Duration(seconds: 2),
          ),
        );
      }
    }
  }

  Future<void> _showEditProjectModal(BuildContext context, model.Project? project) async {
    final isNew = project == null;
    final initialProject = project ?? const model.Project(
      id: null,
      name: '',
      description: '',
      technologies: [],
      highlights: [],
    );

    final updatedProject = await showDialog<model.Project>(
      context: context,
      builder: (context) => _EditProjectDialog(project: initialProject),
    );

    if (updatedProject != null && context.mounted) {
      if (!isNew && updatedProject == project) return;

      final currentProfile = _pendingProfile ?? ref.read(profileProvider).value;
      
      if (currentProfile != null) {
        List<model.Project> updatedList;
        if (isNew) {
          updatedList = [...currentProfile.projects, updatedProject];
        } else {
          updatedList = currentProfile.projects.map((proj) {
            return (proj.id != null && proj.id == project.id) || proj == project
                ? updatedProject 
                : proj;
          }).toList();
        }
        
        setState(() {
          _pendingProfile = currentProfile.copyWith(projects: updatedList);
          _hasUnsavedChanges = true;
        });
        
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Project updated. Click "Save Changes" to apply.'),
            duration: Duration(seconds: 2),
          ),
        );
      }
    }
  }

  Future<void> _removeEnhancedSummary(BuildContext context, model.Profile profile) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Remove Enhanced Summary'),
        content: const Text('Are you sure you want to remove the AI-enhanced summary?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Remove'),
          ),
        ],
      ),
    );

    if (confirmed == true && context.mounted) {
      final updatedProfile = profile.copyWith(enhancedSummary: '');
      setState(() {
        _pendingProfile = updatedProfile;
        _hasUnsavedChanges = true;
      });
      
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Enhanced summary removed. Click "Save Changes" to apply.'),
          duration: Duration(seconds: 2),
        ),
      );
    }
  }

  Future<void> _removeEnhancedDescription(BuildContext context, dynamic item, String type) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Remove Enhanced Description'),
        content: const Text('Are you sure you want to remove the AI-enhanced description?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Remove'),
          ),
        ],
      ),
    );

    if (confirmed == true && context.mounted) {
      final currentProfile = _pendingProfile ?? ref.read(profileProvider).value;
      
      if (currentProfile == null) return;

      if (type == 'experience') {
        final experience = item as model.Experience;
        final updatedExperience = experience.copyWith(enhancedDescription: '');
        final updatedExperiences = currentProfile.experiences.map((exp) {
          return exp.id == experience.id ? updatedExperience : exp;
        }).toList();
        
        setState(() {
          _pendingProfile = currentProfile.copyWith(experiences: updatedExperiences);
          _hasUnsavedChanges = true;
        });
      } else if (type == 'project') {
        final project = item as model.Project;
        final updatedProject = model.Project(
          id: project.id,
          name: project.name,
          description: project.description,
          enhancedDescription: null,
          technologies: project.technologies,
          url: project.url,
          repositoryUrl: project.repositoryUrl,
          startDate: project.startDate,
          endDate: project.endDate,
          isOngoing: project.isOngoing,
          highlights: project.highlights,
        );
        
        final updatedProjects = currentProfile.projects.map((proj) {
          return proj.id == project.id ? updatedProject : proj;
        }).toList();
        
        setState(() {
          _pendingProfile = currentProfile.copyWith(projects: updatedProjects);
          _hasUnsavedChanges = true;
        });
      }
      
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Enhanced description removed. Click "Save Changes" to apply.'),
          duration: Duration(seconds: 2),
        ),
      );
    }
  }

  Future<void> _saveAllChanges(BuildContext context) async {
    if (_pendingProfile == null) return;

    try {
      // Show loading indicator
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (context) => const Center(
          child: CircularProgressIndicator(),
        ),
      );

      // Save the profile
      await ref.read(profileProvider.notifier).updateProfile(_pendingProfile!);

      if (!context.mounted) return;

      // Close loading dialog
      Navigator.of(context).pop();

      // Reset state
      setState(() {
        _pendingProfile = null;
        _hasUnsavedChanges = false;
      });

      // Show success message
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('✓ All changes saved successfully!'),
          backgroundColor: Colors.green,
          duration: Duration(seconds: 2),
        ),
      );

      // Refresh profile
      ref.invalidate(profileProvider);
    } catch (e) {
      if (!context.mounted) return;

      // Close loading dialog
      Navigator.of(context).pop();

      // Show error message
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to save changes: $e'),
          backgroundColor: Colors.red,
          duration: const Duration(seconds: 3),
        ),
      );
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


class _EditSummaryDialog extends StatefulWidget {
  final String? initialSummary;
  final String? initialEnhancedSummary;

  const _EditSummaryDialog({
    this.initialSummary,
    this.initialEnhancedSummary,
  });

  @override
  State<_EditSummaryDialog> createState() => _EditSummaryDialogState();
}

class _EditSummaryDialogState extends State<_EditSummaryDialog> {
  late TextEditingController _summaryController;
  late TextEditingController _enhancedController;

  @override
  void initState() {
    super.initState();
    _summaryController = TextEditingController(text: widget.initialSummary ?? '');
    _enhancedController = TextEditingController(text: widget.initialEnhancedSummary ?? '');
  }

  @override
  void dispose() {
    _summaryController.dispose();
    _enhancedController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Edit Professional Summary'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: _summaryController,
              decoration: const InputDecoration(
                labelText: 'Professional Summary',
                border: OutlineInputBorder(),
              ),
              minLines: 3,
              maxLines: 10,
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _enhancedController,
              decoration: const InputDecoration(
                labelText: 'Enhanced Summary (Optional)',
                border: OutlineInputBorder(),
                helperText: 'AI-enhanced version',
              ),
              minLines: 3,
              maxLines: 10,
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: () {
            Navigator.of(context).pop({
              'summary': _summaryController.text,
              'enhanced': _enhancedController.text,
            });
          },
          child: const Text('Save'),
        ),
      ],
    );
  }
}

class _EditExperienceDialog extends StatefulWidget {
  final model.Experience experience;

  const _EditExperienceDialog({required this.experience});

  @override
  State<_EditExperienceDialog> createState() => _EditExperienceDialogState();
}

class _EditExperienceDialogState extends State<_EditExperienceDialog> {
  late TextEditingController _titleController;
  late TextEditingController _companyController;
  late TextEditingController _locationController;
  late TextEditingController _descriptionController;
  late TextEditingController _enhancedDescriptionController;
  late TextEditingController _achievementsController;
  late TextEditingController _startDateController;
  late TextEditingController _endDateController;

  Future<void> _pickDate(TextEditingController controller) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: DateTime.now(),
      firstDate: DateTime(1950),
      lastDate: DateTime(2100),
    );
    if (picked != null) {
      setState(() {
        controller.text = '${picked.year}-${picked.month.toString().padLeft(2, '0')}-${picked.day.toString().padLeft(2, '0')}';
      });
    }
  }

  @override
  void initState() {
    super.initState();
    _titleController = TextEditingController(text: widget.experience.title);
    _companyController = TextEditingController(text: widget.experience.company);
    _locationController = TextEditingController(text: widget.experience.location);
    _descriptionController = TextEditingController(text: widget.experience.description);
    _enhancedDescriptionController = TextEditingController(text: widget.experience.enhancedDescription ?? '');
    _achievementsController = TextEditingController(text: widget.experience.achievements.join('\n'));
    _startDateController = TextEditingController(text: widget.experience.startDate);
    _endDateController = TextEditingController(text: widget.experience.endDate);
  }

  @override
  void dispose() {
    _titleController.dispose();
    _companyController.dispose();
    _locationController.dispose();
    _descriptionController.dispose();
    _enhancedDescriptionController.dispose();
    _achievementsController.dispose();
    _startDateController.dispose();
    _endDateController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Edit Experience'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: _titleController,
              decoration: const InputDecoration(labelText: 'Job Title'),
            ),
            TextField(
              controller: _companyController,
              decoration: const InputDecoration(labelText: 'Company'),
            ),
            TextField(
              controller: _locationController,
              decoration: const InputDecoration(labelText: 'Location'),
            ),
            GestureDetector(
              onTap: () => _pickDate(_startDateController),
              child: AbsorbPointer(
                child: TextField(
                  controller: _startDateController,
                  decoration: const InputDecoration(
                    labelText: 'Start Date',
                    suffixIcon: Icon(Icons.calendar_today),
                  ),
                ),
              ),
            ),
            GestureDetector(
              onTap: () => _pickDate(_endDateController),
              child: AbsorbPointer(
                child: TextField(
                  controller: _endDateController,
                  decoration: const InputDecoration(
                    labelText: 'End Date',
                    suffixIcon: Icon(Icons.calendar_today),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _descriptionController,
              decoration: const InputDecoration(
                labelText: 'Description',
                border: OutlineInputBorder(),
              ),
              minLines: 3,
              maxLines: 10,
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _enhancedDescriptionController,
              decoration: const InputDecoration(
                labelText: 'Enhanced Description (Optional)',
                border: OutlineInputBorder(),
                helperText: 'AI-enhanced version',
              ),
              minLines: 3,
              maxLines: 10,
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _achievementsController,
              decoration: const InputDecoration(
                labelText: 'Key Achievements',
                border: OutlineInputBorder(),
                helperText: 'One achievement per line',
              ),
              minLines: 3,
              maxLines: 10,
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: () {
            Navigator.of(context).pop(widget.experience.copyWith(
              title: _titleController.text,
              company: _companyController.text,
              location: _locationController.text,
              description: _descriptionController.text,
              enhancedDescription: _enhancedDescriptionController.text.isEmpty ? null : _enhancedDescriptionController.text,
              achievements: _achievementsController.text.isEmpty 
                  ? [] 
                  : _achievementsController.text.split('\n').where((line) => line.trim().isNotEmpty).toList(),
              startDate: _startDateController.text,
              endDate: _endDateController.text,
            ));
          },
          child: const Text('Save'),
        ),
      ],
    );
  }
}

class _EditProjectDialog extends StatefulWidget {
  final model.Project project;

  const _EditProjectDialog({required this.project});

  @override
  State<_EditProjectDialog> createState() => _EditProjectDialogState();
}

class _EditProjectDialogState extends State<_EditProjectDialog> {
  late TextEditingController _nameController;
  late TextEditingController _descriptionController;
  late TextEditingController _enhancedDescriptionController;
  late TextEditingController _technologiesController;
  late TextEditingController _urlController;
  late TextEditingController _startDateController;
  late TextEditingController _endDateController;

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: widget.project.name);
    _descriptionController = TextEditingController(text: widget.project.description);
    _enhancedDescriptionController = TextEditingController(text: widget.project.enhancedDescription ?? '');
    _technologiesController = TextEditingController(text: widget.project.technologies.join(', '));
    _urlController = TextEditingController(text: widget.project.url ?? '');
    _startDateController = TextEditingController(text: widget.project.startDate ?? '');
    _endDateController = TextEditingController(text: widget.project.endDate ?? '');
  }

  @override
  void dispose() {
    _nameController.dispose();
    _descriptionController.dispose();
    _enhancedDescriptionController.dispose();
    _technologiesController.dispose();
    _urlController.dispose();
    _startDateController.dispose();
    _endDateController.dispose();
    super.dispose();
  }

  Future<void> _pickDate(TextEditingController controller) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: DateTime.now(),
      firstDate: DateTime(1950),
      lastDate: DateTime(2100),
    );
    if (picked != null) {
      setState(() {
        controller.text = '${picked.year}-${picked.month.toString().padLeft(2, '0')}-${picked.day.toString().padLeft(2, '0')}';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Edit Project'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: _nameController,
              decoration: const InputDecoration(labelText: 'Project Name'),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _descriptionController,
              decoration: const InputDecoration(
                labelText: 'Description',
                border: OutlineInputBorder(),
              ),
              minLines: 3,
              maxLines: 10,
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _enhancedDescriptionController,
              decoration: const InputDecoration(
                labelText: 'Enhanced Description (Optional)',
                border: OutlineInputBorder(),
                helperText: 'AI-enhanced version',
              ),
              minLines: 3,
              maxLines: 10,
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _technologiesController,
              decoration: const InputDecoration(
                labelText: 'Technologies (comma separated)',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 8),
            GestureDetector(
              onTap: () => _pickDate(_startDateController),
              child: AbsorbPointer(
                child: TextField(
                  controller: _startDateController,
                  decoration: const InputDecoration(
                    labelText: 'Start Date',
                    suffixIcon: Icon(Icons.calendar_today),
                  ),
                ),
              ),
            ),
            GestureDetector(
              onTap: () => _pickDate(_endDateController),
              child: AbsorbPointer(
                child: TextField(
                  controller: _endDateController,
                  decoration: const InputDecoration(
                    labelText: 'End Date',
                    suffixIcon: Icon(Icons.calendar_today),
                  ),
                ),
              ),
            ),
            TextField(
              controller: _urlController,
              decoration: const InputDecoration(labelText: 'URL (Optional)'),
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: () {
            final techs = _technologiesController.text
                .split(',')
                .map((e) => e.trim())
                .where((e) => e.isNotEmpty)
                .toList();
                
            // Manual copyWith since Project doesn't have it
            final updatedProject = model.Project(
              id: widget.project.id,
              name: _nameController.text,
              description: _descriptionController.text,
              enhancedDescription: _enhancedDescriptionController.text.isEmpty ? null : _enhancedDescriptionController.text,
              technologies: techs,
              url: _urlController.text.isEmpty ? null : _urlController.text,
              repositoryUrl: widget.project.repositoryUrl,
              startDate: _startDateController.text.isEmpty ? null : _startDateController.text,
              endDate: _endDateController.text.isEmpty ? null : _endDateController.text,
              isOngoing: widget.project.isOngoing,
              highlights: widget.project.highlights,
            );
                
            Navigator.of(context).pop(updatedProject);
          },
          child: const Text('Save'),
        ),
      ],
    );
  }
}

class _EditPersonalInfoDialog extends StatefulWidget {
  final model.PersonalInfo personalInfo;

  const _EditPersonalInfoDialog({required this.personalInfo});

  @override
  State<_EditPersonalInfoDialog> createState() => _EditPersonalInfoDialogState();
}

class _EditPersonalInfoDialogState extends State<_EditPersonalInfoDialog> {
  late TextEditingController _fullNameController;
  late TextEditingController _emailController;
  late TextEditingController _phoneController;
  late TextEditingController _locationController;
  late TextEditingController _linkedinController;
  late TextEditingController _githubController;
  late TextEditingController _websiteController;

  @override
  void initState() {
    super.initState();
    _fullNameController = TextEditingController(text: widget.personalInfo.fullName);
    _emailController = TextEditingController(text: widget.personalInfo.email);
    _phoneController = TextEditingController(text: widget.personalInfo.phone ?? '');
    _locationController = TextEditingController(text: widget.personalInfo.location ?? '');
    _linkedinController = TextEditingController(text: widget.personalInfo.linkedin ?? '');
    _githubController = TextEditingController(text: widget.personalInfo.github ?? '');
    _websiteController = TextEditingController(text: widget.personalInfo.website ?? '');
  }

  @override
  void dispose() {
    _fullNameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    _locationController.dispose();
    _linkedinController.dispose();
    _githubController.dispose();
    _websiteController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Edit Personal Info'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: _fullNameController,
              decoration: const InputDecoration(labelText: 'Full Name'),
            ),
            TextField(
              controller: _emailController,
              decoration: const InputDecoration(labelText: 'Email'),
            ),
            TextField(
              controller: _phoneController,
              decoration: const InputDecoration(labelText: 'Phone'),
            ),
            TextField(
              controller: _locationController,
              decoration: const InputDecoration(labelText: 'Location'),
            ),
            TextField(
              controller: _linkedinController,
              decoration: const InputDecoration(labelText: 'LinkedIn URL'),
            ),
            TextField(
              controller: _githubController,
              decoration: const InputDecoration(labelText: 'GitHub URL'),
            ),
            TextField(
              controller: _websiteController,
              decoration: const InputDecoration(labelText: 'Website URL'),
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: () {
            Navigator.of(context).pop(widget.personalInfo.copyWith(
              fullName: _fullNameController.text,
              email: _emailController.text,
              phone: _phoneController.text.isEmpty ? null : _phoneController.text,
              location: _locationController.text.isEmpty ? null : _locationController.text,
              linkedin: _linkedinController.text.isEmpty ? null : _linkedinController.text,
              github: _githubController.text.isEmpty ? null : _githubController.text,
              website: _websiteController.text.isEmpty ? null : _websiteController.text,
            ));
          },
          child: const Text('Save'),
        ),
      ],
    );
  }
}

class _EditEducationDialog extends StatefulWidget {
  final model.Education education;

  const _EditEducationDialog({required this.education});

  @override
  State<_EditEducationDialog> createState() => _EditEducationDialogState();
}

class _EditEducationDialogState extends State<_EditEducationDialog> {
  late TextEditingController _institutionController;
  late TextEditingController _degreeController;
  late TextEditingController _fieldOfStudyController;
  late TextEditingController _startDateController;
  late TextEditingController _endDateController;
  late TextEditingController _gpaController;

  Future<void> _pickDate(TextEditingController controller) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: DateTime.now(),
      firstDate: DateTime(1950),
      lastDate: DateTime(2100),
    );
    if (picked != null) {
      setState(() {
        controller.text = '${picked.year}-${picked.month.toString().padLeft(2, '0')}-${picked.day.toString().padLeft(2, '0')}';
      });
    }
  }

  @override
  void initState() {
    super.initState();
    _institutionController = TextEditingController(text: widget.education.institution);
    _degreeController = TextEditingController(text: widget.education.degree);
    _fieldOfStudyController = TextEditingController(text: widget.education.fieldOfStudy);
    _startDateController = TextEditingController(text: widget.education.startDate);
    _endDateController = TextEditingController(text: widget.education.endDate ?? '');
    _gpaController = TextEditingController(text: widget.education.gpa?.toString() ?? '');
  }

  @override
  void dispose() {
    _institutionController.dispose();
    _degreeController.dispose();
    _fieldOfStudyController.dispose();
    _startDateController.dispose();
    _endDateController.dispose();
    _gpaController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Edit Education'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: _institutionController,
              decoration: const InputDecoration(labelText: 'Institution'),
            ),
            TextField(
              controller: _degreeController,
              decoration: const InputDecoration(labelText: 'Degree'),
            ),
            TextField(
              controller: _fieldOfStudyController,
              decoration: const InputDecoration(labelText: 'Field of Study'),
            ),
            GestureDetector(
              onTap: () => _pickDate(_startDateController),
              child: AbsorbPointer(
                child: TextField(
                  controller: _startDateController,
                  decoration: const InputDecoration(
                    labelText: 'Start Date',
                    suffixIcon: Icon(Icons.calendar_today),
                  ),
                ),
              ),
            ),
            GestureDetector(
              onTap: () => _pickDate(_endDateController),
              child: AbsorbPointer(
                child: TextField(
                  controller: _endDateController,
                  decoration: const InputDecoration(
                    labelText: 'End Date',
                    suffixIcon: Icon(Icons.calendar_today),
                  ),
                ),
              ),
            ),
            TextField(
              controller: _gpaController,
              decoration: const InputDecoration(labelText: 'GPA'),
              keyboardType: TextInputType.number,
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: () {
            // Manual copyWith/constructor since Education might not have copyWith or it might be incomplete
            final updatedEducation = model.Education(
              id: widget.education.id,
              institution: _institutionController.text,
              degree: _degreeController.text,
              fieldOfStudy: _fieldOfStudyController.text,
              startDate: _startDateController.text,
              endDate: _endDateController.text.isEmpty ? null : _endDateController.text,
              gpa: double.tryParse(_gpaController.text),
              honors: widget.education.honors,
              description: widget.education.description,
              isCurrent: widget.education.isCurrent,
            );
            Navigator.of(context).pop(updatedEducation);
          },
          child: const Text('Save'),
        ),
      ],
    );
  }
}

class _EditSkillsDialog extends StatefulWidget {
  final model.Skills skills;

  const _EditSkillsDialog({required this.skills});

  @override
  State<_EditSkillsDialog> createState() => _EditSkillsDialogState();
}

class _EditSkillsDialogState extends State<_EditSkillsDialog> {
  late List<String> _technicalSkills;
  late List<String> _softSkills;

  @override
  void initState() {
    super.initState();
    _technicalSkills = List.from(widget.skills.technical);
    _softSkills = List.from(widget.skills.soft);
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Edit Skills'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TagInput(
              initialTags: _technicalSkills,
              onTagsChanged: (tags) {
                setState(() {
                  _technicalSkills = tags;
                });
              },
              labelText: 'Technical Skills',
              hintText: 'Add a skill...',
            ),
            const SizedBox(height: 16),
            TagInput(
              initialTags: _softSkills,
              onTagsChanged: (tags) {
                setState(() {
                  _softSkills = tags;
                });
              },
              labelText: 'Soft Skills',
              hintText: 'Add a skill...',
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: () {
            Navigator.of(context).pop(widget.skills.copyWith(
              technical: _technicalSkills,
              soft: _softSkills,
            ));
          },
          child: const Text('Save'),
        ),
      ],
    );
  }
}

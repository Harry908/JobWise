import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../models/profile.dart' as model;
import '../providers/profile_provider.dart';
import '../widgets/error_display.dart';

class ProfileViewScreen extends ConsumerWidget {
  const ProfileViewScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
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
          return RefreshIndicator(
            onRefresh: () => ref.refresh(profileProvider.future),
            child: SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildPersonalInfoSection(context, profile),
                  const SizedBox(height: 24),
                  if (profile.professionalSummary != null &&
                      profile.professionalSummary!.isNotEmpty)
                    _buildProfessionalSummarySection(
                        context, profile.professionalSummary!),
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

  Widget _buildSectionHeader(BuildContext context, String title) {
    return Text(
      title,
      style: Theme.of(context)
          .textTheme
          .headlineSmall
          ?.copyWith(fontWeight: FontWeight.bold),
    );
  }

  Widget _buildProfessionalSummarySection(
      BuildContext context, String summary) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSectionHeader(context, 'Professional Summary'),
        const SizedBox(height: 8),
        Card(
          elevation: 1,
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Text(
              summary,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(height: 1.5),
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
        _buildSectionHeader(context, 'Work Experience'),
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
    return Card(
      elevation: 1,
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              experience.title,
              style: theme.textTheme.titleMedium
                  ?.copyWith(fontWeight: FontWeight.bold),
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
              Text(
                experience.description!,
                style: theme.textTheme.bodyMedium?.copyWith(height: 1.4),
              ),
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
        _buildSectionHeader(context, 'Education'),
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
        _buildSectionHeader(context, 'Skills'),
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
        _buildSectionHeader(context, 'Projects'),
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
    return Card(
      elevation: 1,
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              project.name,
              style: theme.textTheme.titleMedium
                  ?.copyWith(fontWeight: FontWeight.bold),
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
            Text(
              project.description,
              style: theme.textTheme.bodyMedium?.copyWith(height: 1.4),
            ),
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
}

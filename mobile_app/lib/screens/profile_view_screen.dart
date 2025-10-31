import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../constants/colors.dart';
import '../constants/text_styles.dart';
import '../models/profile.dart';
import '../providers/profile_provider.dart';
import '../widgets/error_display.dart';
import 'profile_edit_screen.dart';

class ProfileViewScreen extends ConsumerWidget {
  const ProfileViewScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profileState = ref.watch(profileProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Profile'),
        backgroundColor: AppColors.primary,
        actions: [
          if (profileState.profile != null)
            IconButton(
              icon: const Icon(Icons.edit),
              tooltip: 'Edit Profile',
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => const ProfileEditScreen(),
                  ),
                );
              },
            ),
        ],
      ),
      body: _buildBody(context, profileState),
    );
  }

  Widget _buildBody(BuildContext context, ProfileState profileState) {
    if (profileState.isLoading) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    if (profileState.profile == null) {
      return ErrorDisplay(
        message: 'No profile found. Please create your profile first.',
        onRetry: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => const ProfileEditScreen(),
            ),
          );
        },
        retryText: 'Create Profile',
      );
    }

    return RefreshIndicator(
      onRefresh: () async {
        // Reload profile by recreating the provider
        // This is a simple approach, you could also add a refresh method to the provider
      },
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildPersonalInfoSection(context, profileState.profile!),
            const SizedBox(height: 24),
            if (profileState.profile!.professionalSummary != null)
              _buildProfessionalSummarySection(
                context,
                profileState.profile!.professionalSummary!,
              ),
            if (profileState.profile!.professionalSummary != null)
              const SizedBox(height: 24),
            _buildExperiencesSection(context, profileState.profile!.experiences),
            const SizedBox(height: 24),
            _buildEducationSection(context, profileState.profile!.education),
            const SizedBox(height: 24),
            _buildSkillsSection(context, profileState.profile!.skills),
            const SizedBox(height: 24),
            _buildProjectsSection(context, profileState.profile!.projects),
            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }

  Widget _buildPersonalInfoSection(BuildContext context, Profile profile) {
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
                  backgroundColor: AppColors.primary,
                  child: Text(
                    profile.personalInfo.fullName.substring(0, 1).toUpperCase(),
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
                        style: AppTextStyles.headlineMedium.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      if (profile.personalInfo.location != null)
                        Row(
                          children: [
                            Icon(
                              Icons.location_on,
                              size: 16,
                              color: Colors.grey[600],
                            ),
                            const SizedBox(width: 4),
                            Flexible(
                              child: Text(
                                profile.personalInfo.location!,
                                style: AppTextStyles.bodyMedium.copyWith(
                                  color: Colors.grey[600],
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
            _buildContactInfo(Icons.email, profile.personalInfo.email),
            if (profile.personalInfo.phone != null)
              _buildContactInfo(Icons.phone, profile.personalInfo.phone!),
            if (profile.personalInfo.linkedin != null)
              _buildContactInfo(Icons.business, profile.personalInfo.linkedin!),
            if (profile.personalInfo.github != null)
              _buildContactInfo(Icons.code, profile.personalInfo.github!),
            if (profile.personalInfo.website != null)
              _buildContactInfo(Icons.web, profile.personalInfo.website!),
          ],
        ),
      ),
    );
  }

  Widget _buildContactInfo(IconData icon, String text) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        children: [
          Icon(icon, size: 20, color: AppColors.primary),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              text,
              style: AppTextStyles.bodyMedium,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProfessionalSummarySection(BuildContext context, String summary) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Professional Summary',
          style: AppTextStyles.headlineSmall.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        Card(
          elevation: 1,
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Text(
              summary,
              style: AppTextStyles.bodyMedium.copyWith(
                height: 1.5,
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildExperiencesSection(BuildContext context, List<Experience> experiences) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Work Experience',
          style: AppTextStyles.headlineSmall.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        if (experiences.isEmpty)
          Card(
            elevation: 1,
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Text(
                'No work experience added yet.',
                style: AppTextStyles.bodyMedium.copyWith(
                  color: Colors.grey[600],
                ),
              ),
            ),
          )
        else
          ...experiences.map((exp) => _buildExperienceCard(exp)),
      ],
    );
  }

  Widget _buildExperienceCard(Experience experience) {
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
              style: AppTextStyles.titleMedium.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              experience.company,
              style: AppTextStyles.bodyLarge.copyWith(
                color: AppColors.primary,
              ),
            ),
            if (experience.location != null) ...[
              const SizedBox(height: 4),
              Row(
                children: [
                  Icon(Icons.location_on, size: 16, color: Colors.grey[600]),
                  const SizedBox(width: 4),
                  Text(
                    experience.location!,
                    style: AppTextStyles.bodyMedium.copyWith(
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
            ],
            const SizedBox(height: 4),
            Row(
              children: [
                Icon(Icons.calendar_today, size: 16, color: Colors.grey[600]),
                const SizedBox(width: 4),
                Text(
                  _formatDateRange(experience.startDate, experience.endDate),
                  style: AppTextStyles.bodyMedium.copyWith(
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
            if (experience.description != null) ...[
              const SizedBox(height: 12),
              Text(
                experience.description!,
                style: AppTextStyles.bodyMedium.copyWith(
                  height: 1.4,
                ),
              ),
            ],
            if (experience.achievements.isNotEmpty) ...[
              const SizedBox(height: 12),
              ...experience.achievements.map(
                (achievement) => Padding(
                  padding: const EdgeInsets.only(bottom: 4.0),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('• ', style: TextStyle(fontSize: 16)),
                      Expanded(
                        child: Text(
                          achievement,
                          style: AppTextStyles.bodyMedium,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildEducationSection(BuildContext context, List<Education> education) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Education',
          style: AppTextStyles.headlineSmall.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        if (education.isEmpty)
          Card(
            elevation: 1,
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Text(
                'No education added yet.',
                style: AppTextStyles.bodyMedium.copyWith(
                  color: Colors.grey[600],
                ),
              ),
            ),
          )
        else
          ...education.map((edu) => _buildEducationCard(edu)),
      ],
    );
  }

  Widget _buildEducationCard(Education education) {
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
              style: AppTextStyles.titleMedium.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              education.institution,
              style: AppTextStyles.bodyLarge.copyWith(
                color: AppColors.primary,
              ),
            ),
            const SizedBox(height: 4),
            Row(
              children: [
                Icon(Icons.calendar_today, size: 16, color: Colors.grey[600]),
                const SizedBox(width: 4),
                Text(
                  _formatStringDateRange(education.startDate, education.endDate),
                  style: AppTextStyles.bodyMedium.copyWith(
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
            if (education.gpa != null) ...[
              const SizedBox(height: 4),
              Text(
                'GPA: ${education.gpa}',
                style: AppTextStyles.bodyMedium.copyWith(
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
            if (education.honors.isNotEmpty) ...[
              const SizedBox(height: 12),
              ...education.honors.map(
                (honor) => Padding(
                  padding: const EdgeInsets.only(bottom: 4.0),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('• ', style: TextStyle(fontSize: 16)),
                      Expanded(
                        child: Text(
                          honor,
                          style: AppTextStyles.bodyMedium,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildSkillsSection(BuildContext context, Skills skills) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Skills',
          style: AppTextStyles.headlineSmall.copyWith(
            fontWeight: FontWeight.bold,
          ),
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
                    style: AppTextStyles.titleMedium.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: skills.technical.map((skill) {
                      return Chip(
                        label: Text(skill),
                        backgroundColor: AppColors.primary.withOpacity(0.1),
                        labelStyle: TextStyle(
                          color: AppColors.primary,
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
                    style: AppTextStyles.titleMedium.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: skills.soft.map((skill) {
                      return Chip(
                        label: Text(skill),
                        backgroundColor: Colors.green.withOpacity(0.1),
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
                    style: AppTextStyles.bodyMedium.copyWith(
                      color: Colors.grey[600],
                    ),
                  ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildProjectsSection(BuildContext context, List<Project> projects) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Projects',
          style: AppTextStyles.headlineSmall.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        if (projects.isEmpty)
          Card(
            elevation: 1,
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Text(
                'No projects added yet.',
                style: AppTextStyles.bodyMedium.copyWith(
                  color: Colors.grey[600],
                ),
              ),
            ),
          )
        else
          ...projects.map((project) => _buildProjectCard(project)),
      ],
    );
  }

  Widget _buildProjectCard(Project project) {
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
              style: AppTextStyles.titleMedium.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            if (project.url != null) ...[
              const SizedBox(height: 4),
              Row(
                children: [
                  Icon(Icons.link, size: 16, color: AppColors.primary),
                  const SizedBox(width: 4),
                  Expanded(
                    child: Text(
                      project.url!,
                      style: AppTextStyles.bodyMedium.copyWith(
                        color: AppColors.primary,
                        decoration: TextDecoration.underline,
                      ),
                    ),
                  ),
                ],
              ),
            ],
            if (project.startDate != null) ...[
              const SizedBox(height: 4),
              Row(
                children: [
                  Icon(Icons.calendar_today, size: 16, color: Colors.grey[600]),
                  const SizedBox(width: 4),
                  Text(
                    _formatStringDateRange(project.startDate, project.endDate),
                    style: AppTextStyles.bodyMedium.copyWith(
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
            ],
            const SizedBox(height: 12),
            Text(
              project.description,
              style: AppTextStyles.bodyMedium.copyWith(
                height: 1.4,
              ),
            ),
            if (project.technologies.isNotEmpty) ...[
              const SizedBox(height: 12),
              Wrap(
                spacing: 6,
                runSpacing: 6,
                children: project.technologies.map((tech) {
                  return Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.blue.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      tech,
                      style: AppTextStyles.bodySmall.copyWith(
                        color: Colors.blue[700],
                      ),
                    ),
                  );
                }).toList(),
              ),
            ],
            if (project.highlights.isNotEmpty) ...[
              const SizedBox(height: 12),
              ...project.highlights.map(
                (highlight) => Padding(
                  padding: const EdgeInsets.only(bottom: 4.0),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('• ', style: TextStyle(fontSize: 16)),
                      Expanded(
                        child: Text(
                          highlight,
                          style: AppTextStyles.bodyMedium,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  String _formatStringDateRange(String? startDate, String? endDate) {
    if (startDate == null || startDate.isEmpty) return 'Date not specified';
    
    final start = _formatStringDate(startDate);
    final end = (endDate == null || endDate.isEmpty) ? 'Present' : _formatStringDate(endDate);

    return '$start - $end';
  }

  String _formatStringDate(String date) {
    try {
      final parsedDate = DateTime.parse(date);
      final months = [
        'Jan',
        'Feb',
        'Mar',
        'Apr',
        'May',
        'Jun',
        'Jul',
        'Aug',
        'Sep',
        'Oct',
        'Nov',
        'Dec'
      ];
      return '${months[parsedDate.month - 1]} ${parsedDate.year}';
    } catch (e) {
      // If parsing fails, return the date string as is
      return date;
    }
  }
}

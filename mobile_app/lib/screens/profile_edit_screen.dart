import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../models/profile.dart' as model;
import '../providers/profile_provider.dart';
import '../utils/validators.dart';
import '../widgets/loading_overlay.dart';
import '../widgets/profile_cards.dart';
import '../widgets/profile_dialogs.dart';
import '../widgets/tag_input.dart';

class ProfileEditScreen extends ConsumerStatefulWidget {
  const ProfileEditScreen({super.key});

  @override
  ConsumerState<ProfileEditScreen> createState() => _ProfileEditScreenState();
}

class _ProfileEditScreenState extends ConsumerState<ProfileEditScreen> {
  final _formKey = GlobalKey<FormState>();

  // Controllers
  late TextEditingController _fullNameController;
  late TextEditingController _emailController;
  late TextEditingController _phoneController;
  late TextEditingController _locationController;
  late TextEditingController _linkedinController;
  late TextEditingController _githubController;
  late TextEditingController _websiteController;
  late TextEditingController _summaryController;

  // Local state for dynamic lists
  List<model.Experience> _experiences = [];
  List<model.Education> _education = [];
  List<String> _technicalSkills = [];
  List<String> _softSkills = [];
  List<model.Project> _projects = [];

  @override
  void initState() {
    super.initState();
    _initializeControllers();
    _loadExistingProfile();
  }

  void _initializeControllers() {
    _fullNameController = TextEditingController();
    _emailController = TextEditingController();
    _phoneController = TextEditingController();
    _locationController = TextEditingController();
    _linkedinController = TextEditingController();
    _githubController = TextEditingController();
    _websiteController = TextEditingController();
    _summaryController = TextEditingController();
  }

  void _loadExistingProfile() {
    // Use `ref.read` to get the initial state without listening
    final profile = ref.read(profileProvider).value;
    if (profile != null) {
      setState(() {
        _fullNameController.text = profile.personalInfo.fullName;
        _emailController.text = profile.personalInfo.email;
        _phoneController.text = profile.personalInfo.phone ?? '';
        _locationController.text = profile.personalInfo.location ?? '';
        _linkedinController.text = profile.personalInfo.linkedin ?? '';
        _githubController.text = profile.personalInfo.github ?? '';
        _websiteController.text = profile.personalInfo.website ?? '';
        _summaryController.text = profile.professionalSummary ?? '';
        _experiences = List.from(profile.experiences);
        _education = List.from(profile.education);
        _technicalSkills = List.from(profile.skills.technical);
        _softSkills = List.from(profile.skills.soft);
        _projects = List.from(profile.projects);
      });
    }
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
    _summaryController.dispose();
    super.dispose();
  }

  Future<void> _saveProfile() async {
    if (!_formKey.currentState!.validate()) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please fill in all required fields.'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    final existingProfile = ref.read(profileProvider).value;
    final isCreating = existingProfile == null;

    final profileData = model.Profile(
      id: existingProfile?.id ?? '',
      userId: existingProfile?.userId ?? 0,
      personalInfo: model.PersonalInfo(
        fullName: _fullNameController.text.trim(),
        email: _emailController.text.trim(),
        phone: _phoneController.text.trim().nullIfEmpty(),
        location: _locationController.text.trim().nullIfEmpty(),
        linkedin: _linkedinController.text.trim().nullIfEmpty(),
        github: _githubController.text.trim().nullIfEmpty(),
        website: _websiteController.text.trim().nullIfEmpty(),
      ),
      professionalSummary: _summaryController.text.trim().nullIfEmpty(),
      experiences: _experiences,
      education: _education,
      skills: model.Skills(
        technical: _technicalSkills,
        soft: _softSkills,
        certifications: existingProfile?.skills.certifications ?? [],
      ),
      projects: _projects,
      customFields: existingProfile?.customFields ?? {},
      createdAt: existingProfile?.createdAt ?? DateTime.now(),
      updatedAt: DateTime.now(),
    );

    try {
      if (isCreating) {
        await ref.read(profileProvider.notifier).createProfile(profileData);
      } else {
        await ref.read(profileProvider.notifier).updateProfile(profileData);
      }

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Profile saved successfully')),
        );
        context.pop();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error saving profile: ${e.toString()}'),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final profileState = ref.watch(profileProvider);
    final isSaving = profileState.isLoading && profileState.value != null;

    return Scaffold(
      appBar: AppBar(
        title: Text(ref.read(profileProvider).value == null
            ? 'Create Profile'
            : 'Edit Profile'),
        actions: [
          IconButton(
            onPressed: isSaving ? null : _saveProfile,
            icon: isSaving
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Icon(Icons.save),
            tooltip: 'Save Profile',
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: Stack(
        children: [
          Form(
            key: _formKey,
            child: ListView(
              padding: const EdgeInsets.all(16),
              children: [
                _buildSectionHeader('Personal Information'),
                _buildPersonalInfoForm(),
                const SizedBox(height: 24),
                _buildSectionHeader('Work Experience'),
                _buildExperiencesForm(),
                const SizedBox(height: 24),
                _buildSectionHeader('Education'),
                _buildEducationForm(),
                const SizedBox(height: 24),
                _buildSectionHeader('Skills'),
                _buildSkillsForm(),
                const SizedBox(height: 24),
                _buildSectionHeader('Projects'),
                _buildProjectsForm(),
                const SizedBox(height: 24),
                SizedBox(
                  width: double.infinity,
                  child: FilledButton.icon(
                    onPressed: isSaving ? null : _saveProfile,
                    icon: const Icon(Icons.save),
                    label: const Text('Save Profile'),
                    style: FilledButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                  ),
                ),
              ],
            ),
          ),
          if (isSaving) const LoadingOverlay(message: 'Saving profile...'),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16.0),
      child: Text(
        title,
        style: Theme.of(context)
            .textTheme
            .titleLarge
            ?.copyWith(fontWeight: FontWeight.bold),
      ),
    );
  }

  Widget _buildPersonalInfoForm() {
    return Column(
      children: [
        TextFormField(
          controller: _fullNameController,
          decoration: const InputDecoration(labelText: 'Full Name*'),
          validator: (value) =>
              (value == null || value.isEmpty) ? 'Full name is required' : null,
        ),
        const SizedBox(height: 16),
        TextFormField(
          controller: _emailController,
          keyboardType: TextInputType.emailAddress,
          decoration: const InputDecoration(labelText: 'Email*'),
          validator: Validators.validateEmail,
        ),
        const SizedBox(height: 16),
        TextFormField(
          controller: _phoneController,
          keyboardType: TextInputType.phone,
          decoration: const InputDecoration(labelText: 'Phone'),
        ),
        const SizedBox(height: 16),
        TextFormField(
          controller: _locationController,
          decoration: const InputDecoration(labelText: 'Location'),
        ),
        const SizedBox(height: 16),
        TextFormField(
          controller: _linkedinController,
          decoration: const InputDecoration(labelText: 'LinkedIn URL'),
          validator: Validators.validateUrl,
        ),
        const SizedBox(height: 16),
        TextFormField(
          controller: _githubController,
          decoration: const InputDecoration(labelText: 'GitHub URL'),
          validator: Validators.validateUrl,
        ),
        const SizedBox(height: 16),
        TextFormField(
          controller: _websiteController,
          decoration: const InputDecoration(labelText: 'Personal Website'),
          validator: Validators.validateUrl,
        ),
        const SizedBox(height: 16),
        TextFormField(
          controller: _summaryController,
          maxLines: 4,
          decoration: const InputDecoration(
            labelText: 'Professional Summary',
            alignLabelWithHint: true,
          ),
        ),
      ],
    );
  }

  Widget _buildExperiencesForm() {
    return Column(
      children: [
        ..._experiences.asMap().entries.map((entry) {
          return ExperienceCard(
            experience: entry.value,
            onEdit: () => _editExperience(entry.key),
            onDelete: () => setState(() => _experiences.removeAt(entry.key)),
          );
        }),
        const SizedBox(height: 16),
        Center(
          child: OutlinedButton.icon(
            onPressed: _addExperience,
            icon: const Icon(Icons.add),
            label: const Text('Add Experience'),
          ),
        ),
      ],
    );
  }

  Widget _buildEducationForm() {
    return Column(
      children: [
        ..._education.asMap().entries.map((entry) {
          return EducationCard(
            education: entry.value,
            onEdit: () => _editEducation(entry.key),
            onDelete: () => setState(() => _education.removeAt(entry.key)),
          );
        }),
        const SizedBox(height: 16),
        Center(
          child: OutlinedButton.icon(
            onPressed: _addEducation,
            icon: const Icon(Icons.add),
            label: const Text('Add Education'),
          ),
        ),
      ],
    );
  }

  Widget _buildSkillsForm() {
    return Column(
      children: [
        TagInput(
          initialTags: _technicalSkills,
          onTagsChanged: (tags) => setState(() => _technicalSkills = tags),
          labelText: 'Technical Skills',
        ),
        const SizedBox(height: 24),
        TagInput(
          initialTags: _softSkills,
          onTagsChanged: (tags) => setState(() => _softSkills = tags),
          labelText: 'Soft Skills',
        ),
      ],
    );
  }

  Widget _buildProjectsForm() {
    return Column(
      children: [
        ..._projects.asMap().entries.map((entry) {
          return ProjectCard(
            project: entry.value,
            onEdit: () => _editProject(entry.key),
            onDelete: () => setState(() => _projects.removeAt(entry.key)),
          );
        }),
        const SizedBox(height: 16),
        Center(
          child: OutlinedButton.icon(
            onPressed: _addProject,
            icon: const Icon(Icons.add),
            label: const Text('Add Project'),
          ),
        ),
      ],
    );
  }

  void _addExperience() => _showExperienceDialog();
  void _editExperience(int index) =>
      _showExperienceDialog(experience: _experiences[index], index: index);

  void _addEducation() => _showEducationDialog();
  void _editEducation(int index) =>
      _showEducationDialog(education: _education[index], index: index);

  void _addProject() => _showProjectDialog();
  void _editProject(int index) =>
      _showProjectDialog(project: _projects[index], index: index);

  void _showExperienceDialog({model.Experience? experience, int? index}) {
    showDialog(
      context: context,
      builder: (_) => ExperienceDialog(
        experience: experience,
        onSave: (exp) => setState(() {
          if (index != null) {
            _experiences[index] = exp;
          } else {
            _experiences.add(exp);
          }
        }),
      ),
    );
  }

  void _showEducationDialog({model.Education? education, int? index}) {
    showDialog(
      context: context,
      builder: (_) => EducationDialog(
        education: education,
        onSave: (edu) => setState(() {
          if (index != null) {
            _education[index] = edu;
          } else {
            _education.add(edu);
          }
        }),
      ),
    );
  }

  void _showProjectDialog({model.Project? project, int? index}) {
    showDialog(
      context: context,
      builder: (_) => ProjectDialog(
        project: project,
        onSave: (proj) => setState(() {
          if (index != null) {
            _projects[index] = proj;
          } else {
            _projects.add(proj);
          }
        }),
      ),
    );
  }
}

extension on String {
  String? nullIfEmpty() => isEmpty ? null : this;
}
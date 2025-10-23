import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/profile.dart';
import '../../providers/profile_provider.dart';
import '../../utils/validators.dart';
import '../../widgets/loading_overlay.dart';
import '../../widgets/profile_cards.dart';
import '../../widgets/profile_dialogs.dart';

class ProfileEditScreen extends ConsumerStatefulWidget {
  const ProfileEditScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<ProfileEditScreen> createState() => _ProfileEditScreenState();
}

class _ProfileEditScreenState extends ConsumerState<ProfileEditScreen> {
  int _currentStep = 0;
  final _formKeys = List.generate(4, (_) => GlobalKey<FormState>());

  // Personal Info Controllers
  late TextEditingController _fullNameController;
  late TextEditingController _emailController;
  late TextEditingController _phoneController;
  late TextEditingController _locationController;
  late TextEditingController _linkedinController;
  late TextEditingController _githubController;
  late TextEditingController _websiteController;
  late TextEditingController _summaryController;

  // Dynamic lists
  final List<Experience> _experiences = [];
  final List<Education> _education = [];
  final List<String> _technicalSkills = [];
  final List<String> _softSkills = [];
  final List<Project> _projects = [];

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
    final profile = ref.read(profileProvider).profile;
    if (profile != null) {
      _fullNameController.text = profile.personalInfo.fullName;
      _emailController.text = profile.personalInfo.email;
      _phoneController.text = profile.personalInfo.phone ?? '';
      _locationController.text = profile.personalInfo.location ?? '';
      _linkedinController.text = profile.personalInfo.linkedin ?? '';
      _githubController.text = profile.personalInfo.github ?? '';
      _websiteController.text = profile.personalInfo.website ?? '';
      _summaryController.text = profile.professionalSummary ?? '';
      _experiences.addAll(profile.experiences);
      _education.addAll(profile.education);
      _technicalSkills.addAll(profile.skills.technical);
      _softSkills.addAll(profile.skills.soft);
      _projects.addAll(profile.projects);
    }
  }

  @override
  Widget build(BuildContext context) {
    final profileState = ref.watch(profileProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text(profileState.profile == null ? 'Create Profile' : 'Edit Profile'),
      ),
      body: Stack(
        children: [
          SafeArea(
            child: Stepper(
              currentStep: _currentStep,
              onStepContinue: _onStepContinue,
              onStepCancel: _onStepCancel,
              onStepTapped: (step) => setState(() => _currentStep = step),
              controlsBuilder: (context, details) {
                return Row(
                  children: [
                    if (_currentStep < 3)
                      ElevatedButton(
                        onPressed: details.onStepContinue,
                        child: const Text('Continue'),
                      ),
                    if (_currentStep == 3)
                      ElevatedButton(
                        onPressed: profileState.isSaving ? null : _saveProfile,
                        child: const Text('Save Profile'),
                      ),
                    const SizedBox(width: 8),
                    if (_currentStep > 0)
                      TextButton(
                        onPressed: details.onStepCancel,
                        child: const Text('Back'),
                      ),
                  ],
                );
              },
              steps: [
                Step(
                  title: const Text('Personal Information'),
                  subtitle: const Text('Basic contact details'),
                  content: _buildPersonalInfoForm(),
                  isActive: _currentStep >= 0,
                  state: _getStepState(0),
                ),
                Step(
                  title: const Text('Work Experience'),
                  subtitle: const Text('Professional background'),
                  content: _buildExperiencesForm(),
                  isActive: _currentStep >= 1,
                  state: _getStepState(1),
                ),
                Step(
                  title: const Text('Education & Skills'),
                  subtitle: const Text('Academic background and abilities'),
                  content: _buildEducationSkillsForm(),
                  isActive: _currentStep >= 2,
                  state: _getStepState(2),
                ),
                Step(
                  title: const Text('Projects'),
                  subtitle: const Text('Portfolio and achievements'),
                  content: _buildProjectsForm(),
                  isActive: _currentStep >= 3,
                  state: _getStepState(3),
                ),
              ],
            ),
          ),
          if (profileState.isSaving) const LoadingOverlay(message: 'Saving profile...'),
        ],
      ),
    );
  }

  StepState _getStepState(int stepIndex) {
    if (_currentStep > stepIndex) return StepState.complete;
    if (_currentStep == stepIndex) return StepState.editing;
    return StepState.indexed;
  }

  Widget _buildPersonalInfoForm() {
    return Form(
      key: _formKeys[0],
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          TextFormField(
            controller: _fullNameController,
            decoration: const InputDecoration(
              labelText: 'Full Name*',
              prefixIcon: Icon(Icons.person),
              border: OutlineInputBorder(),
            ),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Full name is required';
              }
              return null;
            },
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _emailController,
            keyboardType: TextInputType.emailAddress,
            decoration: const InputDecoration(
              labelText: 'Email*',
              prefixIcon: Icon(Icons.email),
              border: OutlineInputBorder(),
            ),
            validator: Validators.validateEmail,
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _phoneController,
            keyboardType: TextInputType.phone,
            decoration: const InputDecoration(
              labelText: 'Phone',
              prefixIcon: Icon(Icons.phone),
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _locationController,
            decoration: const InputDecoration(
              labelText: 'Location',
              prefixIcon: Icon(Icons.location_on),
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _linkedinController,
            decoration: const InputDecoration(
              labelText: 'LinkedIn URL',
              prefixIcon: Icon(Icons.business),
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _githubController,
            decoration: const InputDecoration(
              labelText: 'GitHub URL',
              prefixIcon: Icon(Icons.code),
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _websiteController,
            decoration: const InputDecoration(
              labelText: 'Personal Website',
              prefixIcon: Icon(Icons.web),
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _summaryController,
            maxLines: 4,
            decoration: const InputDecoration(
              labelText: 'Professional Summary',
              border: OutlineInputBorder(),
              hintText: 'Brief overview of your professional background and goals...',
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildExperiencesForm() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        ..._experiences.asMap().entries.map((entry) {
          return ExperienceCard(
            experience: entry.value,
            onEdit: () => _editExperience(entry.key),
            onDelete: () => _deleteExperience(entry.key),
          );
        }).toList(),
        const SizedBox(height: 16),
        Center(
          child: ElevatedButton.icon(
            onPressed: _addExperience,
            icon: const Icon(Icons.add),
            label: const Text('Add Experience'),
          ),
        ),
      ],
    );
  }

  Widget _buildEducationSkillsForm() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Education',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        ..._education.asMap().entries.map((entry) {
          return EducationCard(
            education: entry.value,
            onEdit: () => _editEducation(entry.key),
            onDelete: () => _deleteEducation(entry.key),
          );
        }).toList(),
        const SizedBox(height: 16),
        Center(
          child: ElevatedButton.icon(
            onPressed: _addEducation,
            icon: const Icon(Icons.add),
            label: const Text('Add Education'),
          ),
        ),
        const SizedBox(height: 24),
        const Text(
          'Technical Skills',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          children: _technicalSkills
              .map((skill) => Chip(
                    label: Text(skill),
                    onDeleted: () {
                      setState(() {
                        _technicalSkills.remove(skill);
                      });
                    },
                  ))
              .toList(),
        ),
        const SizedBox(height: 8),
        TextField(
          decoration: const InputDecoration(
            labelText: 'Add Technical Skill',
            suffixIcon: Icon(Icons.add),
            border: OutlineInputBorder(),
          ),
          onSubmitted: (value) {
            if (value.isNotEmpty && !_technicalSkills.contains(value)) {
              setState(() {
                _technicalSkills.add(value);
              });
            }
          },
        ),
        const SizedBox(height: 24),
        const Text(
          'Soft Skills',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          children: _softSkills
              .map((skill) => Chip(
                    label: Text(skill),
                    onDeleted: () {
                      setState(() {
                        _softSkills.remove(skill);
                      });
                    },
                  ))
              .toList(),
        ),
        const SizedBox(height: 8),
        TextField(
          decoration: const InputDecoration(
            labelText: 'Add Soft Skill',
            suffixIcon: Icon(Icons.add),
            border: OutlineInputBorder(),
          ),
          onSubmitted: (value) {
            if (value.isNotEmpty && !_softSkills.contains(value)) {
              setState(() {
                _softSkills.add(value);
              });
            }
          },
        ),
      ],
    );
  }

  Widget _buildProjectsForm() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        ..._projects.asMap().entries.map((entry) {
          return ProjectCard(
            project: entry.value,
            onEdit: () => _editProject(entry.key),
            onDelete: () => _deleteProject(entry.key),
          );
        }).toList(),
        const SizedBox(height: 16),
        Center(
          child: ElevatedButton.icon(
            onPressed: _addProject,
            icon: const Icon(Icons.add),
            label: const Text('Add Project'),
          ),
        ),
      ],
    );
  }

  void _onStepContinue() {
    if (_currentStep < 3) {
      if (_formKeys[_currentStep].currentState?.validate() ?? false) {
        setState(() {
          _currentStep++;
        });
      }
    }
  }

  void _onStepCancel() {
    if (_currentStep > 0) {
      setState(() {
        _currentStep--;
      });
    }
  }

  Future<void> _saveProfile() async {
    if (!_formKeys[0].currentState!.validate()) {
      setState(() => _currentStep = 0);
      return;
    }

    final profile = Profile(
      id: ref.read(profileProvider).profile?.id ?? '',
      userId: ref.read(profileProvider).profile?.userId ?? '',
      personalInfo: PersonalInfo(
        fullName: _fullNameController.text.trim(),
        email: _emailController.text.trim(),
        phone: _phoneController.text.isEmpty ? null : _phoneController.text.trim(),
        location: _locationController.text.isEmpty ? null : _locationController.text.trim(),
        linkedin: _linkedinController.text.isEmpty ? null : _linkedinController.text.trim(),
        github: _githubController.text.isEmpty ? null : _githubController.text.trim(),
        website: _websiteController.text.isEmpty ? null : _websiteController.text.trim(),
      ),
      professionalSummary: _summaryController.text.isEmpty ? null : _summaryController.text.trim(),
      experiences: _experiences,
      education: _education,
      skills: Skills(
        technical: _technicalSkills,
        soft: _softSkills,
      ),
      projects: _projects,
      customFields: {},
      version: ref.read(profileProvider).profile?.version ?? 1,
      createdAt: ref.read(profileProvider).profile?.createdAt ?? DateTime.now(),
      updatedAt: DateTime.now(),
    );

    try {
      if (ref.read(profileProvider).profile == null) {
        await ref.read(profileProvider.notifier).createProfile(profile);
      } else {
        await ref.read(profileProvider.notifier).updateProfile(profile);
      }

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Profile saved successfully')),
        );
        Navigator.pop(context);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: ${e.toString()}')),
        );
      }
    }
  }

  void _addExperience() {
    _showExperienceDialog();
  }

  void _editExperience(int index) {
    _showExperienceDialog(experience: _experiences[index], index: index);
  }

  void _deleteExperience(int index) {
    setState(() {
      _experiences.removeAt(index);
    });
  }

  void _addEducation() {
    _showEducationDialog();
  }

  void _editEducation(int index) {
    _showEducationDialog(education: _education[index], index: index);
  }

  void _deleteEducation(int index) {
    setState(() {
      _education.removeAt(index);
    });
  }

  void _addProject() {
    _showProjectDialog();
  }

  void _editProject(int index) {
    _showProjectDialog(project: _projects[index], index: index);
  }

  void _deleteProject(int index) {
    setState(() {
      _projects.removeAt(index);
    });
  }

  void _showExperienceDialog({Experience? experience, int? index}) {
    showDialog(
      context: context,
      builder: (context) => ExperienceDialog(
        experience: experience,
        onSave: (exp) {
          setState(() {
            if (index != null) {
              _experiences[index] = exp;
            } else {
              _experiences.add(exp);
            }
          });
        },
      ),
    );
  }

  void _showEducationDialog({Education? education, int? index}) {
    showDialog(
      context: context,
      builder: (context) => EducationDialog(
        education: education,
        onSave: (edu) {
          setState(() {
            if (index != null) {
              _education[index] = edu;
            } else {
              _education.add(edu);
            }
          });
        },
      ),
    );
  }

  void _showProjectDialog({Project? project, int? index}) {
    showDialog(
      context: context,
      builder: (context) => ProjectDialog(
        project: project,
        onSave: (proj) {
          setState(() {
            if (index != null) {
              _projects[index] = proj;
            } else {
              _projects.add(proj);
            }
          });
        },
      ),
    );
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
}
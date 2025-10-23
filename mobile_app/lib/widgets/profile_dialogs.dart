import 'package:flutter/material.dart';
import '../../models/profile.dart';

class ExperienceDialog extends StatefulWidget {
  final Experience? experience;
  final Function(Experience) onSave;

  const ExperienceDialog({
    super.key,
    this.experience,
    required this.onSave,
  });

  @override
  State<ExperienceDialog> createState() => _ExperienceDialogState();
}

class _ExperienceDialogState extends State<ExperienceDialog> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _titleController;
  late TextEditingController _companyController;
  late TextEditingController _locationController;
  late TextEditingController _startDateController;
  late TextEditingController _endDateController;
  late TextEditingController _descriptionController;
  late TextEditingController _achievementsController;
  bool _isCurrent = false;

  @override
  void initState() {
    super.initState();
    _titleController = TextEditingController(text: widget.experience?.title ?? '');
    _companyController = TextEditingController(text: widget.experience?.company ?? '');
    _locationController = TextEditingController(text: widget.experience?.location ?? '');
    _startDateController = TextEditingController(text: widget.experience?.startDate ?? '');
    _endDateController = TextEditingController(text: widget.experience?.endDate ?? '');
    _descriptionController = TextEditingController(text: widget.experience?.description ?? '');
    _achievementsController = TextEditingController(
      text: widget.experience?.achievements.join('\n') ?? '',
    );
    _isCurrent = widget.experience?.isCurrent ?? false;
  }

  @override
  void dispose() {
    _titleController.dispose();
    _companyController.dispose();
    _locationController.dispose();
    _startDateController.dispose();
    _endDateController.dispose();
    _descriptionController.dispose();
    _achievementsController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(widget.experience == null ? 'Add Experience' : 'Edit Experience'),
      content: SingleChildScrollView(
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                controller: _titleController,
                decoration: const InputDecoration(labelText: 'Job Title'),
                validator: (value) => value?.isEmpty ?? true ? 'Required' : null,
              ),
              TextFormField(
                controller: _companyController,
                decoration: const InputDecoration(labelText: 'Company'),
                validator: (value) => value?.isEmpty ?? true ? 'Required' : null,
              ),
              TextFormField(
                controller: _locationController,
                decoration: const InputDecoration(labelText: 'Location'),
              ),
              TextFormField(
                controller: _startDateController,
                decoration: const InputDecoration(labelText: 'Start Date (MM/YYYY)'),
                validator: (value) => value?.isEmpty ?? true ? 'Required' : null,
              ),
              TextFormField(
                controller: _endDateController,
                decoration: const InputDecoration(labelText: 'End Date (MM/YYYY)'),
                enabled: !_isCurrent,
              ),
              CheckboxListTile(
                title: const Text('Current Position'),
                value: _isCurrent,
                onChanged: (value) {
                  setState(() {
                    _isCurrent = value ?? false;
                  });
                },
              ),
              TextFormField(
                controller: _descriptionController,
                decoration: const InputDecoration(labelText: 'Description'),
                maxLines: 3,
              ),
              TextFormField(
                controller: _achievementsController,
                decoration: const InputDecoration(
                  labelText: 'Key Achievements (one per line)',
                ),
                maxLines: 4,
              ),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: _save,
          child: const Text('Save'),
        ),
      ],
    );
  }

  void _save() {
    if (_formKey.currentState?.validate() ?? false) {
      final experience = Experience(
        id: widget.experience?.id ?? '',
        title: _titleController.text,
        company: _companyController.text,
        location: _locationController.text.isEmpty ? null : _locationController.text,
        startDate: _startDateController.text,
        endDate: _isCurrent ? null : (_endDateController.text.isEmpty ? null : _endDateController.text),
        isCurrent: _isCurrent,
        description: _descriptionController.text.isEmpty ? null : _descriptionController.text,
        achievements: _achievementsController.text
            .split('\n')
            .where((achievement) => achievement.trim().isNotEmpty)
            .toList(),
      );
      widget.onSave(experience);
      Navigator.of(context).pop();
    }
  }
}

class EducationDialog extends StatefulWidget {
  final Education? education;
  final Function(Education) onSave;

  const EducationDialog({
    super.key,
    this.education,
    required this.onSave,
  });

  @override
  State<EducationDialog> createState() => _EducationDialogState();
}

class _EducationDialogState extends State<EducationDialog> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _degreeController;
  late TextEditingController _institutionController;
  late TextEditingController _fieldOfStudyController;
  late TextEditingController _startDateController;
  late TextEditingController _endDateController;
  late TextEditingController _gpaController;
  late TextEditingController _honorsController;

  @override
  void initState() {
    super.initState();
    _degreeController = TextEditingController(text: widget.education?.degree ?? '');
    _institutionController = TextEditingController(text: widget.education?.institution ?? '');
    _fieldOfStudyController = TextEditingController(text: widget.education?.fieldOfStudy ?? '');
    _startDateController = TextEditingController(text: widget.education?.startDate ?? '');
    _endDateController = TextEditingController(text: widget.education?.endDate ?? '');
    _gpaController = TextEditingController(text: widget.education?.gpa?.toString() ?? '');
    _honorsController = TextEditingController(
      text: widget.education?.honors.join('\n') ?? '',
    );
  }

  @override
  void dispose() {
    _degreeController.dispose();
    _institutionController.dispose();
    _fieldOfStudyController.dispose();
    _startDateController.dispose();
    _endDateController.dispose();
    _gpaController.dispose();
    _honorsController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(widget.education == null ? 'Add Education' : 'Edit Education'),
      content: SingleChildScrollView(
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                controller: _degreeController,
                decoration: const InputDecoration(labelText: 'Degree'),
                validator: (value) => value?.isEmpty ?? true ? 'Required' : null,
              ),
              TextFormField(
                controller: _institutionController,
                decoration: const InputDecoration(labelText: 'Institution'),
                validator: (value) => value?.isEmpty ?? true ? 'Required' : null,
              ),
              TextFormField(
                controller: _fieldOfStudyController,
                decoration: const InputDecoration(labelText: 'Field of Study'),
                validator: (value) => value?.isEmpty ?? true ? 'Required' : null,
              ),
              TextFormField(
                controller: _startDateController,
                decoration: const InputDecoration(labelText: 'Start Date (MM/YYYY)'),
                validator: (value) => value?.isEmpty ?? true ? 'Required' : null,
              ),
              TextFormField(
                controller: _endDateController,
                decoration: const InputDecoration(labelText: 'End Date (MM/YYYY)'),
              ),
              TextFormField(
                controller: _gpaController,
                decoration: const InputDecoration(labelText: 'GPA (optional)'),
                keyboardType: TextInputType.number,
              ),
              TextFormField(
                controller: _honorsController,
                decoration: const InputDecoration(
                  labelText: 'Honors & Awards (one per line)',
                ),
                maxLines: 4,
              ),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: _save,
          child: const Text('Save'),
        ),
      ],
    );
  }

  void _save() {
    if (_formKey.currentState?.validate() ?? false) {
      final education = Education(
        id: widget.education?.id ?? '',
        degree: _degreeController.text,
        institution: _institutionController.text,
        fieldOfStudy: _fieldOfStudyController.text,
        startDate: _startDateController.text,
        endDate: _endDateController.text.isEmpty ? null : _endDateController.text,
        gpa: _gpaController.text.isEmpty ? null : double.tryParse(_gpaController.text),
        honors: _honorsController.text
            .split('\n')
            .where((honor) => honor.trim().isNotEmpty)
            .toList(),
      );
      widget.onSave(education);
      Navigator.of(context).pop();
    }
  }
}

class ProjectDialog extends StatefulWidget {
  final Project? project;
  final Function(Project) onSave;

  const ProjectDialog({
    super.key,
    this.project,
    required this.onSave,
  });

  @override
  State<ProjectDialog> createState() => _ProjectDialogState();
}

class _ProjectDialogState extends State<ProjectDialog> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _nameController;
  late TextEditingController _descriptionController;
  late TextEditingController _technologiesController;
  late TextEditingController _urlController;
  late TextEditingController _startDateController;
  late TextEditingController _endDateController;

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: widget.project?.name ?? '');
    _descriptionController = TextEditingController(text: widget.project?.description ?? '');
    _technologiesController = TextEditingController(
      text: widget.project?.technologies.join(', ') ?? '',
    );
    _urlController = TextEditingController(text: widget.project?.url ?? '');
    _startDateController = TextEditingController(text: widget.project?.startDate ?? '');
    _endDateController = TextEditingController(text: widget.project?.endDate ?? '');
  }

  @override
  void dispose() {
    _nameController.dispose();
    _descriptionController.dispose();
    _technologiesController.dispose();
    _urlController.dispose();
    _startDateController.dispose();
    _endDateController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(widget.project == null ? 'Add Project' : 'Edit Project'),
      content: SingleChildScrollView(
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(labelText: 'Project Name'),
                validator: (value) => value?.isEmpty ?? true ? 'Required' : null,
              ),
              TextFormField(
                controller: _descriptionController,
                decoration: const InputDecoration(labelText: 'Description'),
                maxLines: 3,
                validator: (value) => value?.isEmpty ?? true ? 'Required' : null,
              ),
              TextFormField(
                controller: _technologiesController,
                decoration: const InputDecoration(
                  labelText: 'Technologies (comma-separated)',
                ),
              ),
              TextFormField(
                controller: _urlController,
                decoration: const InputDecoration(labelText: 'Project URL (optional)'),
              ),
              TextFormField(
                controller: _startDateController,
                decoration: const InputDecoration(labelText: 'Start Date (MM/YYYY)'),
              ),
              TextFormField(
                controller: _endDateController,
                decoration: const InputDecoration(labelText: 'End Date (MM/YYYY)'),
              ),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: _save,
          child: const Text('Save'),
        ),
      ],
    );
  }

  void _save() {
    if (_formKey.currentState?.validate() ?? false) {
      final project = Project(
        id: widget.project?.id ?? '',
        name: _nameController.text,
        description: _descriptionController.text,
        technologies: _technologiesController.text
            .split(',')
            .map((tech) => tech.trim())
            .where((tech) => tech.isNotEmpty)
            .toList(),
        url: _urlController.text.isEmpty ? null : _urlController.text,
        startDate: _startDateController.text.isEmpty ? null : _startDateController.text,
        endDate: _endDateController.text.isEmpty ? null : _endDateController.text,
      );
      widget.onSave(project);
      Navigator.of(context).pop();
    }
  }
}
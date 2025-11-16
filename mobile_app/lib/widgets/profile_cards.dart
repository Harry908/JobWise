import 'package:flutter/material.dart';
import '../../models/profile.dart';

class ExperienceCard extends StatelessWidget {
  final Experience experience;
  final VoidCallback onEdit;
  final VoidCallback onDelete;

  const ExperienceCard({
    super.key,
    required this.experience,
    required this.onEdit,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    experience.title,
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.edit),
                  onPressed: onEdit,
                ),
                IconButton(
                  icon: const Icon(Icons.delete),
                  onPressed: onDelete,
                ),
              ],
            ),
            const SizedBox(height: 4),
            Text(
              experience.company,
              style: const TextStyle(
                fontSize: 16,
                color: Colors.grey,
              ),
            ),
            if (experience.location != null) ...[
              const SizedBox(height: 4),
              Text(
                experience.location!,
                style: const TextStyle(color: Colors.grey),
              ),
            ],
            const SizedBox(height: 8),
            Text(
              '${experience.startDate} - ${experience.isCurrent ? 'Present' : (experience.endDate ?? 'Present')}',
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
            if (experience.description != null) ...[
              const SizedBox(height: 8),
              Text(experience.description!),
            ],
            if (experience.achievements.isNotEmpty) ...[
              const SizedBox(height: 8),
              const Text(
                'Key Achievements:',
                style: TextStyle(fontWeight: FontWeight.w500),
              ),
              ...experience.achievements.map((achievement) => Padding(
                    padding: const EdgeInsets.only(left: 8, top: 4),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('• ', style: TextStyle(color: Colors.grey)),
                        Expanded(child: Text(achievement)),
                      ],
                    ),
                  )),
            ],
          ],
        ),
      ),
    );
  }
}

class EducationCard extends StatelessWidget {
  final Education education;
  final VoidCallback onEdit;
  final VoidCallback onDelete;

  const EducationCard({
    super.key,
    required this.education,
    required this.onEdit,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    education.degree,
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.edit),
                  onPressed: onEdit,
                ),
                IconButton(
                  icon: const Icon(Icons.delete),
                  onPressed: onDelete,
                ),
              ],
            ),
            const SizedBox(height: 4),
            Text(
              education.institution,
              style: const TextStyle(
                fontSize: 16,
                color: Colors.grey,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              'Field of Study: ${education.fieldOfStudy}',
              style: const TextStyle(color: Colors.grey),
            ),
            const SizedBox(height: 8),
            Text(
              '${education.startDate} - ${education.endDate ?? 'Present'}',
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
            if (education.gpa != null) ...[
              const SizedBox(height: 4),
              Text('GPA: ${education.gpa}'),
            ],
            if (education.honors.isNotEmpty) ...[
              const SizedBox(height: 8),
              const Text(
                'Honors & Awards:',
                style: TextStyle(fontWeight: FontWeight.w500),
              ),
              ...education.honors.map((honor) => Padding(
                    padding: const EdgeInsets.only(left: 8, top: 4),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('• ', style: TextStyle(color: Colors.grey)),
                        Expanded(child: Text(honor)),
                      ],
                    ),
                  )),
            ],
          ],
        ),
      ),
    );
  }
}

class ProjectCard extends StatelessWidget {
  final Project project;
  final VoidCallback onEdit;
  final VoidCallback onDelete;

  const ProjectCard({
    super.key,
    required this.project,
    required this.onEdit,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    project.name,
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.edit),
                  onPressed: onEdit,
                ),
                IconButton(
                  icon: const Icon(Icons.delete),
                  onPressed: onDelete,
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(project.description),
            if (project.technologies.isNotEmpty) ...[
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                children: project.technologies
                    .map((tech) => Chip(
                          label: Text(tech),
                          backgroundColor: const Color.fromRGBO(33, 150, 243, 0.1),
                        ))
                    .toList(),
              ),
            ],
            if (project.url != null) ...[
              const SizedBox(height: 8),
              Row(
                children: [
                  const Icon(Icons.link, size: 16, color: Colors.grey),
                  const SizedBox(width: 4),
                  Expanded(
                    child: Text(
                      project.url!,
                      style: const TextStyle(color: Colors.blue),
                    ),
                  ),
                ],
              ),
            ],
            if (project.startDate != null || project.endDate != null) ...[
              const SizedBox(height: 8),
              Text(
                '${project.startDate ?? 'Start'} - ${project.endDate ?? 'Present'}',
                style: const TextStyle(fontWeight: FontWeight.w500),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
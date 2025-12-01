import 'package:flutter_test/flutter_test.dart';
import 'package:mobile_app/models/profile.dart';

void main() {
  group('Profile Equality', () {
    test('Profile objects with same properties should be equal', () {
      final now = DateTime.now();
      final profile1 = Profile(
        id: '1',
        userId: 1,
        personalInfo: const PersonalInfo(
          fullName: 'John Doe',
          email: 'john@example.com',
          phone: '1234567890',
          location: 'New York',
          linkedin: 'linkedin.com/in/johndoe',
          website: 'johndoe.com',
        ),
        education: const [
          Education(
            institution: 'University A',
            degree: 'Bachelor',
            fieldOfStudy: 'CS',
            startDate: '2020',
          ),
        ],
        experiences: [],
        projects: [],
        skills: const Skills(technical: ['Dart'], soft: [], certifications: [], languages: []),
        createdAt: now,
        updatedAt: now,
      );

      final profile2 = Profile(
        id: '1',
        userId: 1,
        personalInfo: const PersonalInfo(
          fullName: 'John Doe',
          email: 'john@example.com',
          phone: '1234567890',
          location: 'New York',
          linkedin: 'linkedin.com/in/johndoe',
          website: 'johndoe.com',
        ),
        education: const [
          Education(
            institution: 'University A',
            degree: 'Bachelor',
            fieldOfStudy: 'CS',
            startDate: '2020',
          ),
        ],
        experiences: [],
        projects: [],
        skills: const Skills(technical: ['Dart'], soft: [], certifications: [], languages: []),
        createdAt: now,
        updatedAt: now,
      );

      expect(profile1.id, equals(profile2.id), reason: 'id');
      expect(profile1.userId, equals(profile2.userId), reason: 'userId');
      expect(profile1.personalInfo, equals(profile2.personalInfo), reason: 'personalInfo');
      expect(profile1.professionalSummary, equals(profile2.professionalSummary), reason: 'professionalSummary');
      expect(profile1.enhancedSummary, equals(profile2.enhancedSummary), reason: 'enhancedSummary');
      expect(profile1.experiences, equals(profile2.experiences), reason: 'experiences');
      expect(profile1.education, equals(profile2.education), reason: 'education');
      expect(profile1.skills, equals(profile2.skills), reason: 'skills');
      expect(profile1.projects, equals(profile2.projects), reason: 'projects');
      expect(profile1.customFields, equals(profile2.customFields), reason: 'customFields');
      expect(profile1.createdAt, equals(profile2.createdAt), reason: 'createdAt');
      expect(profile1.updatedAt, equals(profile2.updatedAt), reason: 'updatedAt');

      expect(profile1, equals(profile2));
      expect(profile1.hashCode, equals(profile2.hashCode));
    });

    test('Profile objects with different properties should not be equal', () {
      final now = DateTime.now();
      final profile1 = Profile(
        id: '1',
        userId: 1,
        personalInfo: const PersonalInfo(
          fullName: 'John Doe',
          email: 'john@example.com',
        ),
        education: [],
        experiences: [],
        projects: [],
        skills: const Skills(technical: [], soft: [], certifications: [], languages: []),
        createdAt: now,
        updatedAt: now,
      );

      final profile2 = profile1.copyWith(
        personalInfo: profile1.personalInfo.copyWith(fullName: 'Jane Doe'),
      );

      expect(profile1, isNot(equals(profile2)));
    });
  });

  group('Education Equality', () {
    test('Education objects with same properties should be equal', () {
      const edu1 = Education(
        institution: 'University A',
        degree: 'Bachelor',
        fieldOfStudy: 'CS',
        startDate: '2020',
      );

      const edu2 = Education(
        institution: 'University A',
        degree: 'Bachelor',
        fieldOfStudy: 'CS',
        startDate: '2020',
      );

      expect(edu1, equals(edu2));
      expect(edu1.hashCode, equals(edu2.hashCode));
    });
  });

  group('Skills Equality', () {
    test('Skills objects with same lists should be equal', () {
      const skills1 = Skills(
        technical: ['Dart', 'Flutter'],
        soft: ['Communication'],
        certifications: [],
        languages: [],
      );

      const skills2 = Skills(
        technical: ['Dart', 'Flutter'],
        soft: ['Communication'],
        certifications: [],
        languages: [],
      );

      expect(skills1, equals(skills2));
      expect(skills1.hashCode, equals(skills2.hashCode));
    });

    test('Skills objects with different lists should not be equal', () {
      const skills1 = Skills(technical: ['Dart']);
      const skills2 = Skills(technical: ['Flutter']);

      expect(skills1, isNot(equals(skills2)));
    });
  });
}

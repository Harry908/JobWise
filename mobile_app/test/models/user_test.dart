import 'package:flutter_test/flutter_test.dart';
import 'package:mobile_app/models/user.dart';

void main() {
  group('User Model', () {
    const testUserJson = {
      'id': '123',
      'email': 'test@example.com',
      'full_name': 'John Doe',
      'is_active': true,
      'is_verified': false,
      'created_at': '2025-10-22T10:00:00Z',
      'updated_at': '2025-10-22T10:00:00Z',
    };

    const testUser = User(
      id: '123',
      email: 'test@example.com',
      fullName: 'John Doe',
      isActive: true,
      isVerified: false,
      createdAt: null, // DateTime parsing not tested here
      updatedAt: null,
    );

    test('fromJson creates User from valid JSON', () {
      final user = User.fromJson(testUserJson);

      expect(user.id, '123');
      expect(user.email, 'test@example.com');
      expect(user.fullName, 'John Doe');
      expect(user.isActive, true);
      expect(user.isVerified, false);
    });

    test('fromJson handles integer id conversion', () {
      final jsonWithIntId = {
        ...testUserJson,
        'id': 123,
      };

      final user = User.fromJson(jsonWithIntId);
      expect(user.id, '123');
    });

    test('toJson converts User to JSON', () {
      final json = testUser.toJson();

      expect(json['id'], '123');
      expect(json['email'], 'test@example.com');
      expect(json['full_name'], 'John Doe');
      expect(json['isActive'], true);
      expect(json['isVerified'], false);
    });

    test('copyWith creates new instance with updated fields', () {
      final updatedUser = testUser.copyWith(
        email: 'new@example.com',
        fullName: 'Jane Doe',
      );

      expect(updatedUser.id, testUser.id);
      expect(updatedUser.email, 'new@example.com');
      expect(updatedUser.fullName, 'Jane Doe');
      expect(updatedUser.isActive, testUser.isActive);
    });

    test('equality works correctly', () {
      const user1 = User(
        id: '123',
        email: 'test@example.com',
        fullName: 'John Doe',
      );

      const user2 = User(
        id: '123',
        email: 'test@example.com',
        fullName: 'John Doe',
      );

      const user3 = User(
        id: '456',
        email: 'test@example.com',
        fullName: 'John Doe',
      );

      expect(user1, user2);
      expect(user1 == user3, false);
    });

    test('hashCode is consistent', () {
      const user1 = User(
        id: '123',
        email: 'test@example.com',
        fullName: 'John Doe',
      );

      const user2 = User(
        id: '123',
        email: 'test@example.com',
        fullName: 'John Doe',
      );

      expect(user1.hashCode, user2.hashCode);
    });

    test('default values are applied', () {
      const user = User(
        id: '123',
        email: 'test@example.com',
        fullName: 'John Doe',
      );

      expect(user.isActive, true);
      expect(user.isVerified, false);
      expect(user.createdAt, null);
      expect(user.updatedAt, null);
    });
  });
}
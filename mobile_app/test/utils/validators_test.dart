import 'package:flutter_test/flutter_test.dart';
import 'package:mobile_app/utils/validators.dart';

void main() {
  group('Validators', () {
    group('validateEmail', () {
      test('returns null for valid email', () {
        expect(Validators.validateEmail('test@example.com'), null);
        expect(Validators.validateEmail('user.name+tag@domain.co.uk'), null);
        expect(Validators.validateEmail('123@test-domain.com'), null);
      });

      test('returns error for null or empty email', () {
        expect(Validators.validateEmail(null), 'Email is required');
        expect(Validators.validateEmail(''), 'Email is required');
        expect(Validators.validateEmail('   '), 'Email is required');
      });

      test('returns error for invalid email format', () {
        expect(Validators.validateEmail('invalid'), 'Please enter a valid email address');
        expect(Validators.validateEmail('test@'), 'Please enter a valid email address');
        expect(Validators.validateEmail('@example.com'), 'Please enter a valid email address');
        expect(Validators.validateEmail('test.example.com'), 'Please enter a valid email address');
        expect(Validators.validateEmail('test@.com'), 'Please enter a valid email address');
      });
    });

    group('validatePassword', () {
      test('returns null for valid password', () {
        expect(Validators.validatePassword('Password123!'), null);
        expect(Validators.validatePassword('MySecurePass1'), null);
        expect(Validators.validatePassword('Complex@2025'), null);
      });

      test('returns error for null or empty password', () {
        expect(Validators.validatePassword(null), 'Password is required');
        expect(Validators.validatePassword(''), 'Password is required');
      });

      test('returns error for password too short', () {
        expect(Validators.validatePassword('Pass1'), 'Password must be at least 8 characters long');
        expect(Validators.validatePassword('1234567'), 'Password must be at least 8 characters long');
      });

      test('returns error for password without uppercase letter', () {
        expect(Validators.validatePassword('password123'), 'Password must contain at least one uppercase letter');
        expect(Validators.validatePassword('password!@#'), 'Password must contain at least one uppercase letter');
      });

      test('returns error for password without lowercase letter', () {
        expect(Validators.validatePassword('PASSWORD123'), 'Password must contain at least one lowercase letter');
        expect(Validators.validatePassword('PASSWORD!@#'), 'Password must contain at least one lowercase letter');
      });

      test('returns error for password without number', () {
        expect(Validators.validatePassword('Password!'), 'Password must contain at least one number');
        expect(Validators.validatePassword('PasswordABC'), 'Password must contain at least one number');
      });
    });

    group('validateFullName', () {
      test('returns null for valid full name', () {
        expect(Validators.validateFullName('John Doe'), null);
        expect(Validators.validateFullName('Mary Jane Smith'), null);
        expect(Validators.validateFullName('José María González'), null);
      });

      test('returns error for null or empty full name', () {
        expect(Validators.validateFullName(null), 'Full name is required');
        expect(Validators.validateFullName(''), 'Full name is required');
        expect(Validators.validateFullName('   '), 'Full name is required');
      });

      test('returns error for full name too short', () {
        expect(Validators.validateFullName('A'), 'Full name must be at least 2 characters long');
        expect(Validators.validateFullName('AB'), null); // Exactly 2 characters should be valid
      });
    });

    group('validateConfirmPassword', () {
      test('returns null when passwords match', () {
        expect(Validators.validateConfirmPassword('Password123', 'Password123'), null);
        expect(Validators.validateConfirmPassword('Complex@2025!', 'Complex@2025!'), null);
      });

      test('returns error for null or empty confirm password', () {
        expect(Validators.validateConfirmPassword(null, 'Password123'), 'Please confirm your password');
        expect(Validators.validateConfirmPassword('', 'Password123'), 'Please confirm your password');
      });

      test('returns error when passwords do not match', () {
        expect(Validators.validateConfirmPassword('Password123', 'Password456'), 'Passwords do not match');
        expect(Validators.validateConfirmPassword('password', 'PASSWORD'), 'Passwords do not match');
        expect(Validators.validateConfirmPassword('Password123', 'Password1234'), 'Passwords do not match');
      });
    });

    group('Integration tests', () {
      test('complete password validation scenarios', () {
        // Valid password
        expect(Validators.validatePassword('ValidPass123!'), null);

        // Missing uppercase
        expect(Validators.validatePassword('validpass123!'), isNotNull);

        // Missing lowercase
        expect(Validators.validatePassword('VALIDPASS123!'), isNotNull);

        // Missing number
        expect(Validators.validatePassword('ValidPass!'), isNotNull);

        // Too short
        expect(Validators.validatePassword('Va1!'), isNotNull);
      });

      test('email validation edge cases', () {
        // Valid emails with special characters
        expect(Validators.validateEmail('test.email+tag@example.com'), null);
        expect(Validators.validateEmail('user_name@domain.co.uk'), null);

        // Invalid emails
        expect(Validators.validateEmail('test@.com'), isNotNull);
        expect(Validators.validateEmail('test..email@example.com'), isNotNull);
      });
    });
  });
}
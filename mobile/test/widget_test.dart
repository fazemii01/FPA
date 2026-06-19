import 'package:flutter_test/flutter_test.dart';
import 'package:fingerprint_scanner/models/user_model.dart';

void main() {
  group('User Model Tests', () {
    test('User fromJson parses correctly', () {
      final json = {
        'id': 1,
        'email': 'test@example.com',
        'full_name': 'Test User',
        'role': 'admin',
        'is_active': true,
        'created_at': '2026-06-05T12:00:00.000Z',
      };

      final user = User.fromJson(json);

      expect(user.id, 1);
      expect(user.email, 'test@example.com');
      expect(user.fullName, 'Test User');
      expect(user.role, 'admin');
      expect(user.isActive, true);
      expect(user.createdAt, DateTime.parse('2026-06-05T12:00:00.000Z'));
    });

    test('User toJson works correctly', () {
      final user = User(
        id: 1,
        email: 'test@example.com',
        fullName: 'Test User',
        role: 'admin',
        permissions: const [],
        isActive: true,
        createdAt: DateTime.parse('2026-06-05T12:00:00.000Z'),
      );

      final json = user.toJson();

      expect(json['id'], 1);
      expect(json['email'], 'test@example.com');
      expect(json['full_name'], 'Test User');
      expect(json['role'], 'admin');
      expect(json['is_active'], true);
      expect(json['created_at'], '2026-06-05T12:00:00.000Z');
    });
  });

  group('AuthResponse Model Tests', () {
    test('AuthResponse fromJson parses correctly', () {
      final json = {
        'access_token': 'mock_token_123',
        'token_type': 'bearer',
        'role': 'staff',
      };

      final authResponse = AuthResponse.fromJson(json);

      expect(authResponse.accessToken, 'mock_token_123');
      expect(authResponse.tokenType, 'bearer');
      expect(authResponse.role, 'staff');
    });
  });
}

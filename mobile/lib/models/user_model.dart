class User {
  final int id;
  final String email;
  final String? fullName;
  final String role;
  final List<String> permissions;
  final int? lembagaId;
  final String? lembagaName;
  final int? lembagaCredits;
  final String? lembagaType;
  final bool isActive;
  final DateTime createdAt;

  User({
    required this.id,
    required this.email,
    this.fullName,
    required this.role,
    required this.permissions,
    this.lembagaId,
    this.lembagaName,
    this.lembagaCredits,
    this.lembagaType,
    required this.isActive,
    required this.createdAt,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] is int ? json['id'] : int.parse(json['id'].toString()),
      email: json['email'] as String,
      fullName: json['full_name'] as String?,
      role: json['role'] as String? ?? 'staff',
      permissions: (json['permissions'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      lembagaId: json['lembaga_id'] as int?,
      lembagaName: json['lembaga_name'] as String?,
      lembagaCredits: json['lembaga_credits'] as int?,
      lembagaType: json['lembaga_type'] as String?,
      isActive: json['is_active'] as bool? ?? true,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'full_name': fullName,
      'role': role,
      'permissions': permissions,
      'lembaga_id': lembagaId,
      'lembaga_name': lembagaName,
      'lembaga_credits': lembagaCredits,
      'lembaga_type': lembagaType,
      'is_active': isActive,
      'created_at': createdAt.toIso8601String(),
    };
  }

  // Helper method to check if user has a permission
  bool hasPermission(String permission) {
    // Super admin bypasses all permission checks
    if (role == 'super_admin') return true;
    return permissions.contains(permission);
  }
}

class AuthResponse {
  final String accessToken;
  final String tokenType;
  final String role;
  final List<String> permissions;

  AuthResponse({
    required this.accessToken,
    required this.tokenType,
    required this.role,
    required this.permissions,
  });

  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    return AuthResponse(
      accessToken: json['access_token'] as String,
      tokenType: json['token_type'] as String? ?? 'bearer',
      role: json['role'] as String? ?? 'staff',
      permissions: (json['permissions'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
    );
  }
}

class User {
  final String id;
  final String email;
  final String fullName;
  final bool isActive;
  final bool isVerified;
  final DateTime? createdAt;
  final DateTime? updatedAt;

  const User({
    required this.id,
    required this.email,
    required this.fullName,
    this.isActive = true,
    this.isVerified = false,
    this.createdAt,
    this.updatedAt,
  });

  User copyWith({
    String? id,
    String? email,
    String? fullName,
    bool? isActive,
    bool? isVerified,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return User(
      id: id ?? this.id,
      email: email ?? this.email,
      fullName: fullName ?? this.fullName,
      isActive: isActive ?? this.isActive,
      isVerified: isVerified ?? this.isVerified,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  factory User.fromJson(Map<String, dynamic> json) {
    // Convert id to string if it's an integer
    if (json['id'] is int) {
      json = Map<String, dynamic>.from(json)..['id'] = json['id'].toString();
    }

    // Parse DateTime fields manually
    DateTime? createdAt;
    DateTime? updatedAt;

    if (json['created_at'] is String) {
      try {
        createdAt = DateTime.parse(json['created_at']);
      } catch (e) {
        // Silent fail for date parsing
      }
    }

    if (json['updated_at'] is String) {
      try {
        updatedAt = DateTime.parse(json['updated_at']);
      } catch (e) {
        // Silent fail for date parsing
      }
    }

    try {
      final user = User(
        id: json['id'] as String,
        email: json['email'] as String,
        fullName: json['full_name'] as String,
        isActive: json['is_active'] as bool? ?? true,
        isVerified: json['is_verified'] as bool? ?? false,
        createdAt: createdAt,
        updatedAt: updatedAt,
      );
      return user;
    } catch (e) {
      rethrow;
    }
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'full_name': fullName,
      'is_active': isActive,
      'is_verified': isVerified,
      'created_at': createdAt?.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
    };
  }

  @override
  String toString() {
    return 'User(id: $id, email: $email, fullName: $fullName, isActive: $isActive, isVerified: $isVerified, createdAt: $createdAt, updatedAt: $updatedAt)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;

    return other is User &&
        other.id == id &&
        other.email == email &&
        other.fullName == fullName &&
        other.isActive == isActive &&
        other.isVerified == isVerified &&
        other.createdAt == createdAt &&
        other.updatedAt == updatedAt;
  }

  @override
  int get hashCode {
    return id.hashCode ^
        email.hashCode ^
        fullName.hashCode ^
        isActive.hashCode ^
        isVerified.hashCode ^
        createdAt.hashCode ^
        updatedAt.hashCode;
  }
}
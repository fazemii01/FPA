class ScanSession {
  final int id;
  final int userId;
  final String participantName;
  final int participantAge;
  final String? participantGender;
  final String? notes;
  final String status;
  final DateTime? submittedAt;
  final int? reviewedById;
  final DateTime? reviewedAt;
  final DateTime? approvedAt;
  final String? rejectionReason;
  final DateTime createdAt;
  final DateTime updatedAt;
  final DateTime? completedAt;
  final List<Fingerprint> fingerprints;

  ScanSession({
    required this.id,
    required this.userId,
    required this.participantName,
    required this.participantAge,
    this.participantGender,
    this.notes,
    required this.status,
    this.submittedAt,
    this.reviewedById,
    this.reviewedAt,
    this.approvedAt,
    this.rejectionReason,
    required this.createdAt,
    required this.updatedAt,
    this.completedAt,
    this.fingerprints = const [],
  });

  factory ScanSession.fromJson(Map<String, dynamic> json) {
    return ScanSession(
      id: json['id'] as int,
      userId: json['user_id'] as int,
      participantName: json['participant_name'] as String? ?? '',
      participantAge: json['participant_age'] as int? ?? 0,
      participantGender: json['participant_gender'] as String?,
      notes: json['notes'] as String?,
      status: json['status'] as String,
      submittedAt: json['submitted_at'] != null ? DateTime.parse(json['submitted_at'] as String) : null,
      reviewedById: json['reviewed_by_id'] as int?,
      reviewedAt: json['reviewed_at'] != null ? DateTime.parse(json['reviewed_at'] as String) : null,
      approvedAt: json['approved_at'] != null ? DateTime.parse(json['approved_at'] as String) : null,
      rejectionReason: json['rejection_reason'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
      completedAt: json['completed_at'] != null 
          ? DateTime.parse(json['completed_at'] as String)
          : null,
      fingerprints: (json['fingerprints'] as List<dynamic>?)
          ?.map((e) => Fingerprint.fromJson(e as Map<String, dynamic>))
          .toList() ?? [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'participant_name': participantName,
      'participant_age': participantAge,
      'participant_gender': participantGender,
      'notes': notes,
      'status': status,
      'submitted_at': submittedAt?.toIso8601String(),
      'reviewed_by_id': reviewedById,
      'reviewed_at': reviewedAt?.toIso8601String(),
      'approved_at': approvedAt?.toIso8601String(),
      'rejection_reason': rejectionReason,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'completed_at': completedAt?.toIso8601String(),
      'fingerprints': fingerprints.map((e) => e.toJson()).toList(),
    };
  }

  ScanSession copyWith({
    int? id,
    int? userId,
    String? participantName,
    int? participantAge,
    String? participantGender,
    String? notes,
    String? status,
    DateTime? submittedAt,
    int? reviewedById,
    DateTime? reviewedAt,
    DateTime? approvedAt,
    String? rejectionReason,
    DateTime? createdAt,
    DateTime? updatedAt,
    DateTime? completedAt,
    List<Fingerprint>? fingerprints,
  }) {
    return ScanSession(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      participantName: participantName ?? this.participantName,
      participantAge: participantAge ?? this.participantAge,
      participantGender: participantGender ?? this.participantGender,
      notes: notes ?? this.notes,
      status: status ?? this.status,
      submittedAt: submittedAt ?? this.submittedAt,
      reviewedById: reviewedById ?? this.reviewedById,
      reviewedAt: reviewedAt ?? this.reviewedAt,
      approvedAt: approvedAt ?? this.approvedAt,
      rejectionReason: rejectionReason ?? this.rejectionReason,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      completedAt: completedAt ?? this.completedAt,
      fingerprints: fingerprints ?? this.fingerprints,
    );
  }

  int get completedCount => fingerprints.length;
  int get remainingCount => 10 - completedCount;
  bool get isComplete => completedCount == 10;
}

class Fingerprint {
  final int id;
  final int scanSessionId;
  final String fingerPosition;
  final String imagePath;
  final double? qualityScore;
  final String? patternType;
  final int? ridgeCount;
  final DateTime createdAt;

  Fingerprint({
    required this.id,
    required this.scanSessionId,
    required this.fingerPosition,
    required this.imagePath,
    this.qualityScore,
    this.patternType,
    this.ridgeCount,
    required this.createdAt,
  });

  factory Fingerprint.fromJson(Map<String, dynamic> json) {
    return Fingerprint(
      id: json['id'] as int,
      scanSessionId: json['scan_session_id'] as int,
      fingerPosition: json['finger_position'] as String,
      imagePath: json['image_path'] as String,
      qualityScore: (json['quality_score'] as num?)?.toDouble(),
      patternType: json['pattern_type'] as String?,
      ridgeCount: json['ridge_count'] as int?,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'scan_session_id': scanSessionId,
      'finger_position': fingerPosition,
      'image_path': imagePath,
      'quality_score': qualityScore,
      'pattern_type': patternType,
      'ridge_count': ridgeCount,
      'created_at': createdAt.toIso8601String(),
    };
  }

  Fingerprint copyWith({
    int? id,
    int? scanSessionId,
    String? fingerPosition,
    String? imagePath,
    double? qualityScore,
    String? patternType,
    int? ridgeCount,
    DateTime? createdAt,
  }) {
    return Fingerprint(
      id: id ?? this.id,
      scanSessionId: scanSessionId ?? this.scanSessionId,
      fingerPosition: fingerPosition ?? this.fingerPosition,
      imagePath: imagePath ?? this.imagePath,
      qualityScore: qualityScore ?? this.qualityScore,
      patternType: patternType ?? this.patternType,
      ridgeCount: ridgeCount ?? this.ridgeCount,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  bool get isGoodQuality => qualityScore != null && qualityScore! >= 70;
  bool get isFairQuality => qualityScore != null && qualityScore! >= 50;
}

class Report {
  final int id;
  final int scanSessionId;
  final double overallScore;
  final String? pdfPath;
  final String? pdfUrl;
  final Map<String, dynamic>? metrics;
  final DateTime createdAt;

  Report({
    required this.id,
    required this.scanSessionId,
    required this.overallScore,
    this.pdfPath,
    this.pdfUrl,
    this.metrics,
    required this.createdAt,
  });

  factory Report.fromJson(Map<String, dynamic> json) {
    return Report(
      id: json['id'] as int,
      scanSessionId: json['scan_session_id'] as int,
      overallScore: (json['overall_score'] as num).toDouble(),
      pdfPath: json['pdf_path'] as String?,
      pdfUrl: json['pdf_url'] as String?,
      metrics: json['metrics'] as Map<String, dynamic>?,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'scan_session_id': scanSessionId,
      'overall_score': overallScore,
      'pdf_path': pdfPath,
      'pdf_url': pdfUrl,
      'metrics': metrics,
      'created_at': createdAt.toIso8601String(),
    };
  }
}

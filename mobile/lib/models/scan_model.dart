class ScanSession {
  final int id;
  final int userId;
  final String status;
  final DateTime createdAt;
  final DateTime updatedAt;
  final DateTime? completedAt;
  final List<Fingerprint> fingerprints;

  ScanSession({
    required this.id,
    required this.userId,
    required this.status,
    required this.createdAt,
    required this.updatedAt,
    this.completedAt,
    this.fingerprints = const [],
  });

  factory ScanSession.fromJson(Map<String, dynamic> json) {
    return ScanSession(
      id: json['id'] as int,
      userId: json['user_id'] as int,
      status: json['status'] as String,
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
      'status': status,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
      'completed_at': completedAt?.toIso8601String(),
      'fingerprints': fingerprints.map((e) => e.toJson()).toList(),
    };
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
  final DateTime createdAt;

  Fingerprint({
    required this.id,
    required this.scanSessionId,
    required this.fingerPosition,
    required this.imagePath,
    this.qualityScore,
    required this.createdAt,
  });

  factory Fingerprint.fromJson(Map<String, dynamic> json) {
    return Fingerprint(
      id: json['id'] as int,
      scanSessionId: json['scan_session_id'] as int,
      fingerPosition: json['finger_position'] as String,
      imagePath: json['image_path'] as String,
      qualityScore: (json['quality_score'] as num?)?.toDouble(),
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
      'created_at': createdAt.toIso8601String(),
    };
  }

  bool get isGoodQuality => qualityScore != null && qualityScore! >= 70;
  bool get isFairQuality => qualityScore != null && qualityScore! >= 50;
}

class Report {
  final int id;
  final int scanSessionId;
  final double overallScore;
  final String? pdfPath;
  final Map<String, dynamic>? metrics;
  final DateTime createdAt;

  Report({
    required this.id,
    required this.scanSessionId,
    required this.overallScore,
    this.pdfPath,
    this.metrics,
    required this.createdAt,
  });

  factory Report.fromJson(Map<String, dynamic> json) {
    return Report(
      id: json['id'] as int,
      scanSessionId: json['scan_session_id'] as int,
      overallScore: (json['overall_score'] as num).toDouble(),
      pdfPath: json['pdf_path'] as String?,
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
      'metrics': metrics,
      'created_at': createdAt.toIso8601String(),
    };
  }
}

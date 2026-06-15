import 'package:flutter/material.dart';
import '../models/scan_model.dart';
import '../services/api_service.dart';

class ScanProvider extends ChangeNotifier {
  final ApiService _apiService = ApiService();

  ScanSession? _currentSession;
  List<ScanSession> _sessions = [];
  List<ScanSession> _reviewQueue = [];
  Report? _currentReport;
  bool _isLoading = false;
  String? _error;
  Map<String, dynamic>? _lastDebugImages;

  ScanSession? get currentSession => _currentSession;
  List<ScanSession> get sessions => _sessions;
  List<ScanSession> get reviewQueue => _reviewQueue;
  Map<String, dynamic>? get lastDebugImages => _lastDebugImages;
  /// Sessions that have been approved and are ready for report generation (Admin only).
  List<ScanSession> get approvedQueue =>
      _sessions.where((s) => s.status == 'approved').toList();
  Report? get currentReport => _currentReport;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<bool> createSession({
    required String participantName,
    required int participantAge,
    String? participantGender,
    String? notes,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _apiService.post(
        '/scans/sessions',
        data: {
          'participant_name': participantName,
          'participant_age': participantAge,
          'participant_gender': participantGender,
          'notes': notes,
        },
      );
      _currentSession = ScanSession.fromJson(response);
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> loadSession(int sessionId) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _apiService.get('/scans/sessions/$sessionId');
      _currentSession = ScanSession.fromJson(response);
      
      // Update in local sessions list if present
      final index = _sessions.indexWhere((s) => s.id == sessionId);
      if (index != -1) {
        _sessions[index] = _currentSession!;
      }

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> uploadFingerprint({
    required int sessionId,
    required String fingerPosition,
    required String imagePath,
    String? enhancedImagePath,
  }) async {
    _isLoading = true;
    _error = null;
    _lastDebugImages = null;
    notifyListeners();

    try {
      final response = await _apiService.uploadFile(
        '/scans/sessions/$sessionId/fingerprints',
        imagePath: imagePath,
        enhancedImagePath: enhancedImagePath,
        fingerPosition: fingerPosition,
      );

      final fingerprint = Fingerprint.fromJson(response);
      
      if (_currentSession != null) {
        final List<Fingerprint> updatedFingerprints = List.from(_currentSession!.fingerprints);
        final existingIndex = updatedFingerprints.indexWhere(
          (f) => f.fingerPosition == fingerprint.fingerPosition,
        );
        if (existingIndex != -1) {
          updatedFingerprints[existingIndex] = fingerprint;
        } else {
          updatedFingerprints.add(fingerprint);
        }

        String newStatus = _currentSession!.status;
        if (updatedFingerprints.length >= 10) {
          newStatus = 'scan_completed';
        } else if (newStatus == 'draft' || newStatus == 'registered' || newStatus == 'need_rescan') {
          newStatus = 'scanning';
        }

        _currentSession = _currentSession!.copyWith(
          fingerprints: updatedFingerprints,
          status: newStatus,
        );

        // Update session in local sessions list in-place
        final index = _sessions.indexWhere((s) => s.id == sessionId);
        if (index != -1) {
          _sessions[index] = _currentSession!;
        } else {
          _sessions.add(_currentSession!);
        }
      }

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      if (e is ScanValidationException) {
        _error = e.message;
        _lastDebugImages = e.debugImages;
      } else {
        _error = e.toString();
      }
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> updateFingerprintFeatures({
    required int fingerprintId,
    required String patternType,
    required int ridgeCount,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _apiService.put(
        '/scans/fingerprints/$fingerprintId/features',
        data: {
          'pattern_type': patternType,
          'ridge_count': ridgeCount,
        },
      );

      final updatedFp = Fingerprint.fromJson(response);

      if (_currentSession != null) {
        final List<Fingerprint> updatedFingerprints = List.from(_currentSession!.fingerprints);
        final index = updatedFingerprints.indexWhere((f) => f.id == fingerprintId);
        if (index != -1) {
          updatedFingerprints[index] = updatedFp;
          _currentSession = _currentSession!.copyWith(fingerprints: updatedFingerprints);
        }
      }

      // Update in local sessions list if present
      for (int i = 0; i < _sessions.length; i++) {
        if (_sessions[i].id == _currentSession?.id) {
          final List<Fingerprint> fps = List.from(_sessions[i].fingerprints);
          final idx = fps.indexWhere((f) => f.id == fingerprintId);
          if (idx != -1) {
            fps[idx] = updatedFp;
            _sessions[i] = _sessions[i].copyWith(fingerprints: fps);
          }
          break;
        }
      }

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> submitForReview(int sessionId) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _apiService.post('/scans/sessions/$sessionId/submit');
      final updatedSession = ScanSession.fromJson(response);
      if (_currentSession != null && _currentSession!.id == sessionId) {
        _currentSession = updatedSession;
      }
      final index = _sessions.indexWhere((s) => s.id == sessionId);
      if (index != -1) {
        _sessions[index] = updatedSession;
      }
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> approveSession(int sessionId) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _apiService.post('/scans/sessions/$sessionId/approve');
      final updatedSession = ScanSession.fromJson(response);
      if (_currentSession != null && _currentSession!.id == sessionId) {
        _currentSession = updatedSession;
      }
      final index = _sessions.indexWhere((s) => s.id == sessionId);
      if (index != -1) {
        _sessions[index] = updatedSession;
      }
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> rejectSession(int sessionId, String reason) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _apiService.post(
        '/scans/sessions/$sessionId/reject',
        data: {'reason': reason},
      );
      final updatedSession = ScanSession.fromJson(response);
      if (_currentSession != null && _currentSession!.id == sessionId) {
        _currentSession = updatedSession;
      }
      final index = _sessions.indexWhere((s) => s.id == sessionId);
      if (index != -1) {
        _sessions[index] = updatedSession;
      }
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> requestRescan(int sessionId, List<String> fingerPositions, String reason) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _apiService.post(
        '/scans/sessions/$sessionId/request-rescan',
        data: {
          'finger_positions': fingerPositions,
          'reason': reason,
        },
      );
      final updatedSession = ScanSession.fromJson(response);
      if (_currentSession != null && _currentSession!.id == sessionId) {
        _currentSession = updatedSession;
      }
      final index = _sessions.indexWhere((s) => s.id == sessionId);
      if (index != -1) {
        _sessions[index] = updatedSession;
      }
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> generateReport(int sessionId) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _apiService.post(
        '/reports/sessions/$sessionId/generate',
      );

      _currentReport = Report.fromJson(response);
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> loadSessions() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _apiService.get('/scans/sessions');
      _sessions = (response as List)
          .map((e) => ScanSession.fromJson(e as Map<String, dynamic>))
          .toList();
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> loadReviewQueue() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _apiService.get('/scans/review-queue');
      _reviewQueue = (response as List)
          .map((e) => ScanSession.fromJson(e as Map<String, dynamic>))
          .toList();
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> deleteSession(int sessionId) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      await _apiService.delete('/scans/sessions/$sessionId');
      _sessions.removeWhere((s) => s.id == sessionId);
      if (_currentSession?.id == sessionId) {
        _currentSession = null;
      }
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> loadReport(int sessionId) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _apiService.get('/reports/sessions/$sessionId');
      _currentReport = Report.fromJson(response);
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
}

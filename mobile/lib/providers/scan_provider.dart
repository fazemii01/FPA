import 'package:flutter/material.dart';
import '../models/scan_model.dart';
import '../services/api_service.dart';

class ScanProvider extends ChangeNotifier {
  final ApiService _apiService = ApiService();

  ScanSession? _currentSession;
  List<ScanSession> _sessions = [];
  Report? _currentReport;
  bool _isLoading = false;
  String? _error;

  ScanSession? get currentSession => _currentSession;
  List<ScanSession> get sessions => _sessions;
  Report? get currentReport => _currentReport;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<bool> createSession() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _apiService.post('/scans/sessions');
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

  Future<bool> uploadFingerprint({
    required int sessionId,
    required String fingerPosition,
    required String imagePath,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _apiService.uploadFile(
        '/scans/sessions/$sessionId/fingerprints',
        imagePath: imagePath,
        fingerPosition: fingerPosition,
      );

      final fingerprint = Fingerprint.fromJson(response);
      
      if (_currentSession != null) {
        _currentSession = ScanSession(
          id: _currentSession!.id,
          userId: _currentSession!.userId,
          status: _currentSession!.status,
          createdAt: _currentSession!.createdAt,
          updatedAt: _currentSession!.updatedAt,
          completedAt: _currentSession!.completedAt,
          fingerprints: [..._currentSession!.fingerprints, fingerprint],
        );
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

  void clearError() {
    _error = null;
    notifyListeners();
  }
}

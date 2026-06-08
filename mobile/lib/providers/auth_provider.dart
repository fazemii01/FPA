import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:go_router/go_router.dart';
import '../models/user_model.dart';
import '../services/api_service.dart';
import '../routes/navigator_key.dart';

class AuthProvider extends ChangeNotifier {
  final ApiService _apiService = ApiService();
  
  User? _user;
  String? _token;
  bool _isLoading = false;
  String? _error;

  User? get user => _user;
  String? get token => _token;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get isAuthenticated => _token != null && _user != null;

  AuthProvider() {
    _loadStoredToken();
    ApiService.onUnauthorized = () {
      if (_token != null) {
        logout();
        navigatorKey.currentContext?.go('/login');
      }
    };
  }

  Future<void> _loadStoredToken() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('auth_token');
    if (_token != null) {
      try {
        final response = await _apiService.get('/auth/me');
        _user = User.fromJson(response);
      } catch (e) {
        _token = null;
        await prefs.remove('auth_token');
      }
    }
    notifyListeners();
  }

  Future<bool> checkToken() async {
    await _loadStoredToken();
    return _token != null && _user != null;
  }

  Future<bool> register({
    required String email,
    required String password,
    String? fullName,
    String role = 'staff',
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _apiService.post(
        '/auth/register',
        data: {
          'email': email,
          'password': password,
          'full_name': fullName,
          'role': role,
        },
      );

      if (!isAuthenticated) {
        _user = User.fromJson(response);
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

  Future<bool> login({
    required String email,
    required String password,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _apiService.post(
        '/auth/login',
        data: {
          'email': email,
          'password': password,
        },
      );

      final authResponse = AuthResponse.fromJson(response);
      _token = authResponse.accessToken;

      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('auth_token', _token!);

      // Fetch user details immediately after login
      final userResponse = await _apiService.get('/auth/me');
      _user = User.fromJson(userResponse);

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _token = null;
      _user = null;
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove('auth_token');
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<void> logout() async {
    _user = null;
    _token = null;
    _error = null;

    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');

    notifyListeners();
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
}

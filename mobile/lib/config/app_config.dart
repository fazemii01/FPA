class ApiConfig {
  static const String baseUrl = 'http://192.168.100.145:8000';
  static const String apiVersion = '/api/v1';

  static const Duration connectTimeout = Duration(seconds: 90);
  static const Duration receiveTimeout = Duration(seconds: 90);

  // Endpoints
  static const String authRegister = '$baseUrl/auth/register';
  static const String authLogin = '$baseUrl/auth/login';

  static const String scanSessions = '$baseUrl/scans/sessions';
  static const String scanFingerprints = '$baseUrl/scans/sessions';

  static const String reports = '$baseUrl/reports';

  static const String health = '$baseUrl/health';
}

class StorageKeys {
  static const String authToken = 'auth_token';
  static const String userId = 'user_id';
  static const String userEmail = 'user_email';
  static const String userName = 'user_name';
  static const String lastSyncTime = 'last_sync_time';
}

class AppConstants {
  static const int maxFingerprints = 10;
  static const double minQualityScore = 50.0;
  static const double goodQualityScore = 70.0;

  static const List<String> fingerPositions = [
    'left_thumb',
    'left_index',
    'left_middle',
    'left_ring',
    'left_pinky',
    'right_thumb',
    'right_index',
    'right_middle',
    'right_ring',
    'right_pinky',
  ];

  static const Map<String, String> fingerLabels = {
    'left_thumb': 'Ibu Jari Kiri',
    'left_index': 'Telunjuk Kiri',
    'left_middle': 'Jari Tengah Kiri',
    'left_ring': 'Jari Manis Kiri',
    'left_pinky': 'Jari Kelingking Kiri',
    'right_thumb': 'Ibu Jari Kanan',
    'right_index': 'Telunjuk Kanan',
    'right_middle': 'Jari Tengah Kanan',
    'right_ring': 'Jari Manis Kanan',
    'right_pinky': 'Jari Kelingking Kanan',
  };
}

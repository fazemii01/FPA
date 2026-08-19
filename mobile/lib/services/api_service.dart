import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../config/app_config.dart';

class ScanValidationException implements Exception {
  final String message;
  final Map<String, dynamic>? debugImages;

  ScanValidationException(this.message, this.debugImages);

  @override
  String toString() => message;
}

class ApiException implements Exception {
  final String message;
  ApiException(this.message);
  @override
  String toString() => message;
}

class ApiService {
  late Dio _dio;

  static void Function()? onUnauthorized;

  ApiService() {
    _dio = Dio(
      BaseOptions(
        baseUrl: ApiConfig.baseUrl,
        connectTimeout: ApiConfig.connectTimeout,
        receiveTimeout: ApiConfig.receiveTimeout,
        contentType: 'application/json',
      ),
    );

    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final prefs = await SharedPreferences.getInstance();
          final token = prefs.getString('auth_token');
          
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          
          return handler.next(options);
        },
        onError: (error, handler) {
          if (error.response?.statusCode == 401) {
            onUnauthorized?.call();
          }
          return handler.next(error);
        },
      ),
    );
  }

  Future<dynamic> get(String endpoint) async {
    try {
      final response = await _dio.get(endpoint);
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<dynamic> post(String endpoint, {Map<String, dynamic>? data}) async {
    try {
      final response = await _dio.post(endpoint, data: data);
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<dynamic> put(String endpoint, {Map<String, dynamic>? data}) async {
    try {
      final response = await _dio.put(endpoint, data: data);
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<dynamic> delete(String endpoint) async {
    try {
      final response = await _dio.delete(endpoint);
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Fetches raw bytes from an endpoint (e.g. image proxy).
  Future<List<int>> getBytes(String endpoint) async {
    try {
      final response = await _dio.get<List<int>>(
        endpoint,
        options: Options(responseType: ResponseType.bytes),
      );
      return response.data ?? [];
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<dynamic> uploadFile(
    String endpoint, {
    required String imagePath,
    String? enhancedImagePath,
    required String fingerPosition,
  }) async {
    try {
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(imagePath, filename: 'raw.jpg'),
        if (enhancedImagePath != null)
          'enhanced_file': await MultipartFile.fromFile(enhancedImagePath, filename: 'enhanced.png'),
      });

      final response = await _dio.post(
        endpoint,
        data: formData,
        queryParameters: {'finger_position': fingerPosition},
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Exception _handleError(DioException error) {
    if (error.response != null) {
      final data = error.response?.data;
      if (data is Map<String, dynamic>) {
        final detail = data['detail'];
        if (detail is Map<String, dynamic> && detail.containsKey('message')) {
          return ScanValidationException(
            detail['message'].toString(),
            detail['debug_images'] as Map<String, dynamic>?,
          );
        } else if (detail is String && detail.isNotEmpty) {
          return ApiException(detail);
        } else if (detail is List && detail.isNotEmpty) {
          final messages = detail.map((item) {
            if (item is Map && item.containsKey('msg')) {
              final loc = item['loc'] is List ? (item['loc'] as List).join('.') : '';
              return loc.isNotEmpty ? '$loc: ${item['msg']}' : item['msg'].toString();
            }
            return item.toString();
          }).join(', ');
          return ApiException(messages.isNotEmpty ? messages : 'Validation error');
        } else if (detail != null) {
          return ApiException(detail.toString());
        } else if (data.containsKey('message') && data['message'] != null) {
          return ApiException(data['message'].toString());
        }
      } else if (data is String && data.isNotEmpty) {
        if (data.contains('<html') || data.contains('<!DOCTYPE')) {
          final code = error.response?.statusCode;
          return ApiException(
            code == 502 || code == 504
                ? 'Server sedang tidak dapat dijangkau (Gateway Error $code). Harap hubungi admin.'
                : 'Server error ($code). Silakan coba beberapa saat lagi.',
          );
        }
        return ApiException(data);
      }

      final statusCode = error.response?.statusCode;
      if (statusCode == 502 || statusCode == 503 || statusCode == 504) {
        return ApiException('Server sedang tidak dapat dijangkau (Gateway Error $statusCode). Harap hubungi admin.');
      } else if (statusCode == 500) {
        return ApiException('Terjadi kesalahan internal pada server (500).');
      } else if (statusCode == 401) {
        return ApiException('Email atau password salah / sesi berakhir.');
      } else if (statusCode == 403) {
        return ApiException('Akses ditolak.');
      } else if (statusCode == 404) {
        return ApiException('Data tidak ditemukan.');
      }
      return ApiException('Terjadi kesalahan ($statusCode)');
    } else if (error.type == DioExceptionType.connectionTimeout) {
      return ApiException('Koneksi timeout. Periksa jaringan internet Anda.');
    } else if (error.type == DioExceptionType.receiveTimeout) {
      return ApiException('Server tidak merespons (Receive timeout).');
    } else if (error.type == DioExceptionType.connectionError) {
      return ApiException('Tidak dapat terhubung ke server. Periksa koneksi internet Anda.');
    } else {
      return ApiException(error.message ?? 'Terjadi kesalahan jaringan');
    }
  }
}

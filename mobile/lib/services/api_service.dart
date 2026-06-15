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
      final detail = error.response?.data['detail'];
      if (detail is Map<String, dynamic> && detail.containsKey('message')) {
        return ScanValidationException(
          detail['message'].toString(),
          detail['debug_images'] as Map<String, dynamic>?,
        );
      } else if (detail is String) {
        return ApiException(detail);
      } else if (detail != null) {
        return ApiException(detail.toString());
      } else {
        return ApiException('An error occurred');
      }
    } else if (error.type == DioExceptionType.connectionTimeout) {
      return ApiException('Connection timeout');
    } else if (error.type == DioExceptionType.receiveTimeout) {
      return ApiException('Receive timeout');
    } else {
      return ApiException(error.message ?? 'An error occurred');
    }
  }
}

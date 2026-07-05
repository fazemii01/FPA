import 'dart:io';
import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import '../config/app_config.dart';
import 'notification_service.dart';

class NtfySubscriptionService {
  static final NtfySubscriptionService _instance = NtfySubscriptionService._internal();
  factory NtfySubscriptionService() => _instance;
  NtfySubscriptionService._internal();

  WebSocket? _webSocket;
  bool _isConnecting = false;
  Timer? _reconnectTimer;

  String get _wsUrl {
    final uri = Uri.parse(ApiConfig.baseUrl);
    final host = uri.host;
    // Connect to websocket stream of topic "fpa-updates" on port 8080
    return "ws://$host:8080/fpa-updates/ws";
  }

  void start() {
    if (_webSocket != null || _isConnecting) return;
    _connect();
  }

  void stop() {
    _reconnectTimer?.cancel();
    _webSocket?.close();
    _webSocket = null;
  }

  Future<void> _connect() async {
    _isConnecting = true;
    debugPrint("Ntfy: Connecting to $_wsUrl...");

    try {
      _webSocket = await WebSocket.connect(_wsUrl).timeout(const Duration(seconds: 10));
      _isConnecting = false;
      debugPrint("Ntfy: Connected to websocket stream.");

      _webSocket!.listen(
        (data) {
          _handleMessage(data);
        },
        onDone: () {
          debugPrint("Ntfy: Connection closed. Retrying...");
          _handleDisconnect();
        },
        onError: (err) {
          debugPrint("Ntfy: Error: $err. Retrying...");
          _handleDisconnect();
        },
        cancelOnError: true,
      );
    } catch (e) {
      _isConnecting = false;
      debugPrint("Ntfy: Connection failed: $e. Retrying in 10s...");
      _handleDisconnect();
    }
  }

  void _handleDisconnect() {
    _webSocket = null;
    _reconnectTimer?.cancel();
    _reconnectTimer = Timer(const Duration(seconds: 10), () {
      _connect();
    });
  }

  void _handleMessage(dynamic data) {
    try {
      final Map<String, dynamic> json = jsonDecode(data.toString());
      
      // ntfy sends a "message" type event when a notification is posted
      if (json['event'] == 'message') {
        final String title = json['title'] ?? 'Pembaruan Aplikasi';
        final String body = json['message'] ?? 'Versi baru tersedia!';
        
        NotificationService.showUpdateNotification(
          title: title,
          body: body,
        );
      }
    } catch (e) {
      debugPrint("Ntfy: Error parsing message: $e");
    }
  }
}

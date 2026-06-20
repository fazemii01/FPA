import 'dart:io';
import 'dart:async';
import 'package:flutter/material.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:ota_update/ota_update.dart';
import 'package:url_launcher/url_launcher.dart';
import 'api_service.dart';

class UpdateService {
  static Future<void> checkForUpdates(BuildContext context) async {
    try {
      final data = await ApiService().get('/app/version');
      if (data == null) return;

      final String latestVersion = data['latest_version'] ?? '';
      final String apkUrl = data['apk_url'] ?? '';
      final String iosUrl = data['ios_url'] ?? '';
      final bool forceUpdate = data['force_update'] ?? false;

      if (latestVersion.isEmpty) return;

      final packageInfo = await PackageInfo.fromPlatform();
      final currentVersion = packageInfo.version;

      if (_isVersionOlder(currentVersion, latestVersion)) {
        if (!context.mounted) return;
        await _showUpdateDialog(context, latestVersion, apkUrl, iosUrl, forceUpdate);
      }
    } catch (e) {
      debugPrint('Failed to check for updates: $e');
    }
  }

  static bool _isVersionOlder(String current, String latest) {
    try {
      List<int> currentParts = current.split('.').map((x) => int.tryParse(x) ?? 0).toList();
      List<int> latestParts = latest.split('.').map((x) => int.tryParse(x) ?? 0).toList();

      int maxLength = currentParts.length > latestParts.length ? currentParts.length : latestParts.length;
      for (int i = 0; i < maxLength; i++) {
        int currentPart = i < currentParts.length ? currentParts[i] : 0;
        int latestPart = i < latestParts.length ? latestParts[i] : 0;

        if (latestPart > currentPart) return true;
        if (latestPart < currentPart) return false;
      }
    } catch (e) {
      debugPrint('Error parsing version: $e');
    }
    return false;
  }

  static Future<void> _showUpdateDialog(
    BuildContext context,
    String latestVersion,
    String apkUrl,
    String iosUrl,
    bool forceUpdate,
  ) async {
    return showDialog<void>(
      context: context,
      barrierDismissible: !forceUpdate,
      builder: (BuildContext dialogContext) {
        return WillPopScope(
          onWillPop: () async => !forceUpdate,
          child: AlertDialog(
            title: const Text('Update Aplikasi Tersedia'),
            content: Text('Versi terbaru ($latestVersion) telah dirilis. Silakan unduh pembaruan untuk melanjutkan.'),
            actions: <Widget>[
              if (!forceUpdate)
                TextButton(
                  child: const Text('Nanti'),
                  onPressed: () {
                    Navigator.of(dialogContext).pop();
                  },
                ),
              TextButton(
                child: const Text('Update Sekarang'),
                onPressed: () async {
                  Navigator.of(dialogContext).pop(); // Close dialog
                  if (Platform.isAndroid) {
                    await _runAndroidOta(context, apkUrl);
                  } else if (Platform.isIOS) {
                    await launchUrl(Uri.parse(iosUrl), mode: LaunchMode.externalApplication);
                  }
                },
              ),
            ],
          ),
        );
      },
    );
  }

  static Future<void> _runAndroidOta(BuildContext context, String apkUrl) async {
    showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext progressContext) {
        return OtaProgressDialog(apkUrl: apkUrl);
      },
    );
  }
}

class OtaProgressDialog extends StatefulWidget {
  final String apkUrl;
  const OtaProgressDialog({Key? key, required this.apkUrl}) : super(key: key);

  @override
  State<OtaProgressDialog> createState() => _OtaProgressDialogState();
}

class _OtaProgressDialogState extends State<OtaProgressDialog> {
  double _progress = 0;
  String _status = "Mengunduh...";
  StreamSubscription<OtaEvent>? _subscription;

  @override
  void initState() {
    super.initState();
    _startDownload();
  }

  void _startDownload() {
    try {
      _subscription = OtaUpdate().execute(
        widget.apkUrl,
        destinationFilename: 'fpa-latest.apk',
      ).listen(
        (OtaEvent event) {
          if (event.status == OtaStatus.DOWNLOADING) {
            setState(() {
              _progress = double.tryParse(event.value ?? '0') ?? 0;
              _status = "Mengunduh...";
            });
          } else if (event.status == OtaStatus.INSTALLING) {
            setState(() {
              _status = "Memasang...";
            });
            // Auto close progress dialog when installing starts
            Navigator.of(context).pop();
          } else if (event.status == OtaStatus.ALREADY_RUNNING_ERROR ||
                     event.status == OtaStatus.PERMISSION_NOT_GRANTED_ERROR ||
                     event.status == OtaStatus.INTERNAL_ERROR ||
                     event.status == OtaStatus.DOWNLOAD_ERROR ||
                     event.status == OtaStatus.INSTALLATION_ERROR ||
                     event.status == OtaStatus.CHECKSUM_ERROR) {
            setState(() {
              _status = "Gagal mengunduh: ${event.status}";
            });
            Future.delayed(const Duration(seconds: 3), () {
              if (mounted) Navigator.of(context).pop();
            });
          }
        },
        onError: (error) {
          setState(() {
            _status = "Gagal mengunduh: $error";
          });
          Future.delayed(const Duration(seconds: 3), () {
            if (mounted) Navigator.of(context).pop();
          });
        },
      );
    } catch (e) {
      setState(() {
        _status = "Gagal menginisiasi update: $e";
      });
      Future.delayed(const Duration(seconds: 3), () {
        if (mounted) Navigator.of(context).pop();
      });
    }
  }

  @override
  void dispose() {
    _subscription?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(_status),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          LinearProgressIndicator(value: _progress / 100),
          const SizedBox(height: 16),
          Text('${_progress.toStringAsFixed(0)}%'),
        ],
      ),
    );
  }
}

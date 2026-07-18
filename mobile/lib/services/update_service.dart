import 'dart:io';
import 'dart:async';
import 'package:flutter/material.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:url_launcher/url_launcher.dart';
import 'api_service.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../providers/auth_provider.dart';
import '../routes/navigator_key.dart';
import '../theme/app_theme.dart';
import 'notification_service.dart';

class UpdateService {
  static Future<void> checkSilentUpdate() async {
    try {
      final data = await ApiService().get('/app/version');
      if (data == null) return;

      final String latestVersion = data['latest_version'] ?? '';
      if (latestVersion.isEmpty) return;

      final packageInfo = await PackageInfo.fromPlatform();
      final currentVersion = packageInfo.version;

      if (_isVersionOlder(currentVersion, latestVersion)) {
        await NotificationService.showUpdateNotification(
          title: 'Pembaruan Aplikasi Tersedia',
          body: 'Versi terbaru ($latestVersion) telah dirilis. Ketuk untuk melihat atau perbarui dari menu Profil.',
        );
      }
    } catch (e) {
      debugPrint('Failed to check for updates silently: $e');
    }
  }

  static Future<void> checkManualUpdate(BuildContext context) async {
    // Show spinner dialog
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const Center(child: CircularProgressIndicator()),
    );

    try {
      final data = await ApiService().get('/app/version');
      if (context.mounted) {
        Navigator.pop(context); // Close the progress indicator
      }

      if (data == null) {
        if (context.mounted) {
          _showInfoDialog(context, 'Kesalahan', 'Gagal terhubung ke server pembaruan.');
        }
        return;
      }

      final String latestVersion = data['latest_version'] ?? '';
      final String apkUrl = data['apk_url'] ?? '';
      final String iosUrl = data['ios_url'] ?? '';

      if (latestVersion.isEmpty) {
        if (context.mounted) {
          _showInfoDialog(context, 'Kesalahan', 'Data pembaruan tidak valid.');
        }
        return;
      }

      final packageInfo = await PackageInfo.fromPlatform();
      final currentVersion = packageInfo.version;

      if (_isVersionOlder(currentVersion, latestVersion)) {
        if (context.mounted) {
          // Show alert dialog allowing selection (freely choose update or not)
          await showDialog<void>(
            context: context,
            barrierDismissible: true,
            builder: (BuildContext dialogContext) {
              return AlertDialog(
                backgroundColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                title: const Text(
                  'Update Aplikasi Tersedia',
                  style: TextStyle(color: AppTheme.primaryColor, fontWeight: FontWeight.bold),
                ),
                content: Text(
                  'Versi terbaru ($latestVersion) telah dirilis. Silakan unduh pembaruan untuk melanjutkan.',
                  style: const TextStyle(color: Colors.black87),
                ),
                actions: <Widget>[
                  TextButton(
                    child: const Text('Nanti', style: TextStyle(color: Colors.grey)),
                    onPressed: () {
                      Navigator.of(dialogContext).pop();
                    },
                  ),
                  TextButton(
                    child: const Text('Update Sekarang', style: TextStyle(color: AppTheme.primaryColor, fontWeight: FontWeight.bold)),
                    onPressed: () async {
                      Navigator.of(dialogContext).pop(); // Close dialog
                      
                      // Log out the user first for a clean state
                      final authProvider = Provider.of<AuthProvider>(context, listen: false);
                      if (authProvider.isAuthenticated) {
                        await authProvider.logout();
                        final currentCtx = navigatorKey.currentContext;
                        if (currentCtx != null && currentCtx.mounted) {
                          currentCtx.go('/login');
                        }
                        await Future.delayed(const Duration(milliseconds: 500));
                      }
                      
                      final updateContext = navigatorKey.currentContext ?? context;
                      if (updateContext.mounted) {
                        if (Platform.isAndroid) {
                          await _redirectToPlayStore();
                        } else if (Platform.isIOS) {
                          await launchUrl(Uri.parse(iosUrl), mode: LaunchMode.externalApplication);
                        }
                      }
                    },
                  ),
                ],
              );
            },
          );
        }
      } else {
        if (context.mounted) {
          _showInfoDialog(
            context,
            'Aplikasi Up-to-Date',
            'Aplikasi Anda berada di versi terbaru (v$currentVersion).',
          );
        }
      }
    } catch (e) {
      if (context.mounted) {
        Navigator.pop(context); // Close the progress indicator
        _showInfoDialog(context, 'Kesalahan', 'Gagal memeriksa pembaruan: $e');
      }
    }
  }

  static void _showInfoDialog(BuildContext context, String title, String message) {
    showDialog<void>(
      context: context,
      builder: (BuildContext dialogContext) {
        return AlertDialog(
          backgroundColor: Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
          title: Text(
            title,
            style: const TextStyle(color: AppTheme.primaryColor, fontWeight: FontWeight.bold),
          ),
          content: Text(
            message,
            style: const TextStyle(color: Colors.black87),
          ),
          actions: <Widget>[
            TextButton(
              child: const Text('Tutup', style: TextStyle(color: AppTheme.primaryColor, fontWeight: FontWeight.bold)),
              onPressed: () {
                Navigator.of(dialogContext).pop();
              },
            ),
          ],
        );
      },
    );
  }

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

        final authProvider = Provider.of<AuthProvider>(context, listen: false);
        if (authProvider.isAuthenticated) {
          // Show alert to user explaining they will be logged out for the update
          await showDialog<void>(
            context: context,
            barrierDismissible: false,
            builder: (BuildContext alertContext) {
              return AlertDialog(
                backgroundColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                title: const Text(
                  'Pembaruan Tersedia',
                  style: TextStyle(color: AppTheme.primaryColor, fontWeight: FontWeight.bold),
                ),
                content: const Text(
                  'Pembaruan aplikasi baru tersedia. Anda akan dikeluarkan dari akun terlebih dahulu untuk melanjutkan proses pembaruan.',
                  style: TextStyle(color: Colors.black87),
                ),
                actions: <Widget>[
                  TextButton(
                    child: const Text('OK', style: TextStyle(color: AppTheme.primaryColor, fontWeight: FontWeight.bold)),
                    onPressed: () {
                      Navigator.of(alertContext).pop();
                    },
                  ),
                ],
              );
            },
          );

          // Log out the user
          await authProvider.logout();

          // Navigate to login page using the navigatorKey context to ensure safety
          final currentCtx = navigatorKey.currentContext;
          if (currentCtx != null && currentCtx.mounted) {
            currentCtx.go('/login');
          }

          // Allow transition to finish
          await Future.delayed(const Duration(milliseconds: 500));
        }

        // Get the latest mounted context, preferably the login page context
        final updateContext = navigatorKey.currentContext ?? context;
        if (updateContext.mounted) {
          await _showUpdateDialog(updateContext, latestVersion, apkUrl, iosUrl, forceUpdate);
        }
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
        return PopScope(
          canPop: !forceUpdate,
          child: AlertDialog(
            backgroundColor: Colors.white,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            title: const Text(
              'Update Aplikasi Tersedia',
              style: TextStyle(color: AppTheme.primaryColor, fontWeight: FontWeight.bold),
            ),
            content: Text(
              'Versi terbaru ($latestVersion) telah dirilis. Silakan unduh pembaruan untuk melanjutkan.',
              style: const TextStyle(color: Colors.black87),
            ),
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
                    await _redirectToPlayStore();
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

  static Future<void> _redirectToPlayStore() async {
    try {
      final packageInfo = await PackageInfo.fromPlatform();
      final packageName = packageInfo.packageName;
      final playStoreUri = Uri.parse('market://details?id=$packageName');
      if (await canLaunchUrl(playStoreUri)) {
        await launchUrl(playStoreUri, mode: LaunchMode.externalApplication);
      } else {
        final webUri = Uri.parse('https://play.google.com/store/apps/details?id=$packageName');
        await launchUrl(webUri, mode: LaunchMode.externalApplication);
      }
    } catch (e) {
      debugPrint('Failed to redirect to Play Store: $e');
    }
  }
}

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../providers/scan_provider.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/app_toast.dart';
import '../../theme/app_theme.dart';
import '../../widgets/fingerprint_image.dart';
import '../../models/scan_model.dart';
import '../../config/app_config.dart';

class ReportScreen extends StatefulWidget {
  final int sessionId;

  const ReportScreen({
    super.key,
    required this.sessionId,
  });

  @override
  State<ReportScreen> createState() => _ReportScreenState();
}

class _ReportScreenState extends State<ReportScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ScanProvider>().loadReport(widget.sessionId);
      context.read<ScanProvider>().loadSession(widget.sessionId);
    });
  }

  void _showFingerDetail(BuildContext context, Fingerprint fp, String label) {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          backgroundColor: Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
          title: Text(
            label,
            style: const TextStyle(
              color: AppTheme.primaryColor,
              fontWeight: FontWeight.bold,
            ),
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: Container(
                  color: Colors.grey[100],
                  width: double.infinity,
                  height: 200,
                  child: FingerprintImage(
                    fingerprintId: fp.id,
                    height: 200,
                    fit: BoxFit.cover,
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Text(
                'Kualitas: ${fp.qualityScore?.toStringAsFixed(1) ?? "N/A"}%',
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
              ),
              const SizedBox(height: 8),
              Text('Tipe Pola: ${fp.patternType ?? "-"}'),
              const SizedBox(height: 4),
              Text('Jumlah Garis (Ridge): ${fp.ridgeCount ?? "-"}'),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Tutup', style: TextStyle(color: Colors.grey)),
            ),
          ],
        );
      },
    );
  }

  void _showFingerprintsBottomSheet(BuildContext context, ScanSession session) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.only(
          topLeft: Radius.circular(16),
          topRight: Radius.circular(16),
        ),
      ),
      builder: (context) {
        return SafeArea(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                margin: const EdgeInsets.symmetric(vertical: 12),
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: Colors.grey[300],
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              const Text(
                'Detail Sidik Jari',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: AppTheme.primaryColor,
                ),
              ),
              const SizedBox(height: 12),
              Expanded(
                child: ListView.builder(
                  itemCount: session.fingerprints.length,
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  itemBuilder: (context, index) {
                    final fp = session.fingerprints[index];
                    final label = AppConstants.fingerLabels[fp.fingerPosition] ?? fp.fingerPosition;
                    final Color qualityColor = fp.isGoodQuality
                        ? AppTheme.successColor
                        : fp.isFairQuality
                            ? AppTheme.warningColor
                            : AppTheme.errorColor;

                    return Container(
                      margin: const EdgeInsets.only(bottom: 10),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: const Color(0xFFE0E0E0)),
                      ),
                      child: ListTile(
                        leading: CircleAvatar(
                          backgroundColor: qualityColor.withOpacity(0.15),
                          child: Text(
                            '${index + 1}',
                            style: TextStyle(
                              color: qualityColor,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                        title: Text(
                          label,
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                        subtitle: Text(
                          'Kualitas: ${fp.qualityScore?.toStringAsFixed(1) ?? "N/A"}%',
                          style: TextStyle(color: qualityColor, fontSize: 12),
                        ),
                        trailing: const Icon(Icons.chevron_right_rounded, color: Colors.grey),
                        onTap: () {
                          Navigator.pop(context);
                          _showFingerDetail(context, fp, label);
                        },
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      backgroundColor: const Color(0xFFFAFAFA),
      appBar: AppBar(
        backgroundColor: const Color(0xFFFAFAFA),
        elevation: 0,
        scrolledUnderElevation: 0,
        title: Text(
          'Laporan Pemindaian',
          style: theme.textTheme.titleLarge?.copyWith(
            color: AppTheme.primaryColor,
            fontWeight: FontWeight.bold,
          ),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, color: AppTheme.primaryColor, size: 20),
          onPressed: () => context.go('/home'),
        ),
      ),
      body: Consumer<ScanProvider>(
        builder: (context, scanProvider, _) {
          final report = scanProvider.currentReport;

          if (scanProvider.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          if (report == null) {
            return const Center(
              child: Text('Laporan tidak ditemukan'),
            );
          }

          final metrics = report.metrics;
          final totalFingerprints = metrics?['total_fingerprints'] ?? 0;
          final averageQuality = metrics?['average_quality'] ?? 0.0;
          final qualityScores = metrics?['quality_scores'] as Map<String, dynamic>? ?? {};

          return SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Container(
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: const Color(0xFFE0E0E0)),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.01),
                        blurRadius: 10,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Skor Keseluruhan',
                          style: theme.textTheme.titleMedium?.copyWith(
                            color: AppTheme.primaryColor,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 16),
                        Center(
                          child: Column(
                            children: [
                              Text(
                                '${report.overallScore.toStringAsFixed(1)}%',
                                style: theme.textTheme.displayLarge?.copyWith(
                                  color: _getScoreColor(report.overallScore),
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(height: 8),
                              Text(
                                _getScoreLabel(report.overallScore),
                                style: theme.textTheme.titleMedium?.copyWith(
                                  color: _getScoreColor(report.overallScore),
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Container(
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: const Color(0xFFE0E0E0)),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.01),
                        blurRadius: 10,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Ringkasan',
                          style: theme.textTheme.titleMedium?.copyWith(
                            color: AppTheme.primaryColor,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 16),
                        _buildInfoRow('Total Sidik Jari', '$totalFingerprints'),
                        const Divider(height: 20),
                        _buildInfoRow(
                          'Rata-rata Kualitas',
                          '${averageQuality.toStringAsFixed(1)}%',
                        ),
                        const Divider(height: 20),
                        _buildInfoRow(
                          'Dibuat Pada',
                          _formatDate(report.createdAt),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Container(
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: const Color(0xFFE0E0E0)),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.01),
                        blurRadius: 10,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Detail Kualitas Jari',
                          style: theme.textTheme.titleMedium?.copyWith(
                            color: AppTheme.primaryColor,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 16),
                        ...qualityScores.entries.map((entry) {
                          final position = entry.key;
                          final score = (entry.value as num).toDouble();
                          return Padding(
                            padding: const EdgeInsets.only(bottom: 12),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    Text(
                                      _formatFingerPosition(position),
                                      style: theme.textTheme.bodyMedium?.copyWith(
                                        fontWeight: FontWeight.w500,
                                      ),
                                    ),
                                    Text(
                                      '${score.toStringAsFixed(1)}%',
                                      style: theme.textTheme.bodyMedium?.copyWith(
                                        fontWeight: FontWeight.bold,
                                        color: _getScoreColor(score),
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 4),
                                ClipRRect(
                                  borderRadius: BorderRadius.circular(4),
                                  child: LinearProgressIndicator(
                                    value: score / 100,
                                    minHeight: 8,
                                    backgroundColor: const Color(0xFFF1F5F9),
                                    valueColor: AlwaysStoppedAnimation<Color>(
                                      _getScoreColor(score),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          );
                        }),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                ElevatedButton.icon(
                  onPressed: () => _handleDownloadPDF(context),
                  icon: const Icon(Icons.download),
                  label: const Text('Unduh Laporan PDF'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppTheme.primaryColor,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                ElevatedButton.icon(
                  onPressed: () => _handlePreviewPDF(context),
                  icon: const Icon(Icons.remove_red_eye_rounded),
                  label: const Text('Lihat Laporan'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppTheme.successColor,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                if (scanProvider.currentSession != null) ...[
                  OutlinedButton.icon(
                    onPressed: () => _showFingerprintsBottomSheet(context, scanProvider.currentSession!),
                    icon: const Icon(Icons.fingerprint_rounded, color: AppTheme.primaryColor),
                    label: const Text('Lihat Detail Sidik Jari', style: TextStyle(color: AppTheme.primaryColor)),
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      side: const BorderSide(color: AppTheme.primaryColor),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                ],
                OutlinedButton.icon(
                  onPressed: () => context.go('/home'),
                  icon: const Icon(Icons.home_rounded, color: AppTheme.primaryColor),
                  label: const Text('Kembali ke Beranda', style: TextStyle(color: AppTheme.primaryColor)),
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    side: const BorderSide(color: AppTheme.primaryColor),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
  String _formatFingerPosition(String position) {
    return position
        .split('_')
        .map((word) => word[0].toUpperCase() + word.substring(1))
        .join(' ');
  }

  String _formatDate(DateTime date) {
    return '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')} ${date.hour.toString().padLeft(2, '0')}:${date.minute.toString().padLeft(2, '0')}';
  }

  Future<void> _handleDownloadPDF(BuildContext context) async {
    final authProvider = context.read<AuthProvider>();
    final token = authProvider.token;
    if (token != null) {
      final url = Uri.parse('${ApiConfig.reports}/sessions/${widget.sessionId}/download?token=$token');
      try {
        final launched = await launchUrl(url, mode: LaunchMode.externalApplication);
        if (!launched) {
          final launchedDefault = await launchUrl(url, mode: LaunchMode.platformDefault);
          if (!launchedDefault && context.mounted) {
            AppToast.showError(context, 'Tidak dapat mengunduh laporan PDF');
          }
        }
      } catch (e) {
        try {
          final launchedDefault = await launchUrl(url, mode: LaunchMode.platformDefault);
          if (!launchedDefault && context.mounted) {
            AppToast.showError(context, 'Gagal mengunduh: $e');
          }
        } catch (err) {
          if (context.mounted) {
            AppToast.showError(context, 'Error: $err');
          }
        }
      }
    } else {
      AppToast.showError(context, 'Token autentikasi tidak ditemukan');
    }
  }

  Future<void> _handlePreviewPDF(BuildContext context) async {
    final report = context.read<ScanProvider>().currentReport;
    if (report?.pdfUrl != null) {
      final url = Uri.parse(report!.pdfUrl!);
      try {
        final launched = await launchUrl(url, mode: LaunchMode.externalApplication);
        if (!launched) {
          final launchedDefault = await launchUrl(url, mode: LaunchMode.platformDefault);
          if (!launchedDefault && context.mounted) {
            AppToast.showError(context, 'Tidak dapat membuka preview laporan');
          }
        }
      } catch (e) {
        try {
          final launchedDefault = await launchUrl(url, mode: LaunchMode.platformDefault);
          if (!launchedDefault && context.mounted) {
            AppToast.showError(context, 'Gagal membuka preview: $e');
          }
        } catch (err) {
          if (context.mounted) {
            AppToast.showError(context, 'Error: $err');
          }
        }
      }
    } else {
      AppToast.showError(context, 'URL preview tidak ditemukan');
    }
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: const TextStyle(color: Colors.grey),
          ),
          Text(
            value,
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }

  Color _getScoreColor(double score) {
    if (score >= 80) return AppTheme.successColor;
    if (score >= 60) return AppTheme.warningColor;
    return AppTheme.errorColor;
  }

  String _getScoreLabel(double score) {
    if (score >= 80) return 'Kualitas Sangat Baik';
    if (score >= 60) return 'Kualitas Baik';
    if (score >= 40) return 'Kualitas Cukup';
    return 'Kualitas Rendah';
  }
}

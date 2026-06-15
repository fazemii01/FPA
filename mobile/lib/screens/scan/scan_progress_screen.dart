import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../../config/app_config.dart';
import '../../providers/scan_provider.dart';
import '../../widgets/fingerprint_image.dart';

class ScanProgressScreen extends StatelessWidget {
  final int sessionId;
  final int currentFingerIndex;

  const ScanProgressScreen({
    Key? key,
    required this.sessionId,
    required this.currentFingerIndex,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Progres Pemindaian'),
        automaticallyImplyLeading: false,
      ),
      body: Consumer<ScanProvider>(
        builder: (context, scanProvider, _) {
          final session = scanProvider.currentSession;
          
          if (session == null) {
            return const Center(child: Text('Sesi tidak ditemukan'));
          }

          final progress = session.completedCount / 10;
          final nextFingerIndex = currentFingerIndex < 10 ? currentFingerIndex : 10;

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Progres Pemindaian',
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                        const SizedBox(height: 16),
                        ClipRRect(
                          borderRadius: BorderRadius.circular(8),
                          child: LinearProgressIndicator(
                            value: progress,
                            minHeight: 12,
                          ),
                        ),
                        const SizedBox(height: 12),
                        Text(
                          '${session.completedCount}/10 jari berhasil dipindai',
                          style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                Text(
                  'Jari yang Sudah Dipindai',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const SizedBox(height: 12),
                _buildScannedFingersList(context, session),
                const SizedBox(height: 24),
                if (nextFingerIndex < 10) ...[
                  Text(
                    'Jari Berikutnya',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 12),
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        children: [
                          Icon(
                            Icons.fingerprint,
                            size: 48,
                            color: Theme.of(context).primaryColor,
                          ),
                          const SizedBox(height: 12),
                          Text(
                            AppConstants.fingerLabels[
                              AppConstants.fingerPositions[nextFingerIndex]
                            ]!,
                            style: Theme.of(context).textTheme.titleMedium,
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),
                  ElevatedButton(
                    onPressed: () {
                      final nextPosition = AppConstants.fingerPositions[nextFingerIndex];
                      context.go(
                        '/scan/camera/$sessionId/$nextPosition/$nextFingerIndex',
                      );
                    },
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                    child: const Text('Lanjut ke Jari Berikutnya'),
                  ),
                ] else ...[
                  Card(
                    color: Colors.green[50],
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        children: [
                          Icon(
                            Icons.check_circle,
                            size: 48,
                            color: Colors.green,
                          ),
                          const SizedBox(height: 12),
                          Text(
                            'Semua Jari Berhasil Dipindai!',
                            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              color: Colors.green,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),
                  ElevatedButton(
                    onPressed: () => context.go('/scan/review/$sessionId'),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                    child: const Text('Lanjut ke Review'),
                  ),
                ],
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildScannedFingersList(BuildContext context, dynamic session) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: List.generate(
        session.fingerprints.length,
        (index) {
          final fp = session.fingerprints[index];
          final label = AppConstants.fingerLabels[fp.fingerPosition]!;
          return ActionChip(
            label: Text(label),
            avatar: const CircleAvatar(
              child: Icon(Icons.check, size: 16, color: Colors.green),
            ),
            backgroundColor: Colors.green[100],
            onPressed: () => _showFingerDetail(context, fp, label),
          );
        },
      ),
    );
  }

  void _showFingerDetail(BuildContext context, dynamic fp, String label) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(label),
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
            Text('Tanggal Pengambilan: ${_formatDate(fp.createdAt)}'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Tutup'),
          ),
        ],
      ),
    );
  }

  String _formatDate(DateTime dateTime) {
    return '${dateTime.day}/${dateTime.month}/${dateTime.year} ${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
  }
}

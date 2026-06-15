import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../../config/app_config.dart';
import '../../providers/scan_provider.dart';
import '../../models/scan_model.dart';
import '../../widgets/fingerprint_image.dart';

class ScanScreen extends StatefulWidget {
  const ScanScreen({Key? key}) : super(key: key);

  @override
  State<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends State<ScanScreen> {
  void _showFingerDetail(BuildContext context, int sessionId, Fingerprint fp, String label) {
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
          ElevatedButton.icon(
            onPressed: () {
              Navigator.pop(context); // Close the dialog
              context.go('/scan/capture/$sessionId/${fp.fingerPosition}');
            },
            icon: const Icon(Icons.refresh_rounded),
            label: const Text('Scan Ulang'),
          ),
        ],
      ),
    );
  }

  String _formatDate(DateTime dateTime) {
    return '${dateTime.day}/${dateTime.month}/${dateTime.year} ${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Sesi Pemindaian'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go('/home'),
        ),
      ),
      body: Consumer<ScanProvider>(
        builder: (context, scanProvider, _) {
          final session = scanProvider.currentSession;
          
          if (session == null) {
            return const Center(
              child: Text('Tidak ada sesi aktif'),
            );
          }

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
                          'Kemajuan Pemindaian',
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                        const SizedBox(height: 16),
                        ClipRRect(
                          borderRadius: BorderRadius.circular(8),
                          child: LinearProgressIndicator(
                            value: session.completedCount / 10,
                            minHeight: 8,
                          ),
                        ),
                        const SizedBox(height: 12),
                        Text(
                          '${session.completedCount}/10 sidik jari terpindai',
                          style: Theme.of(context).textTheme.bodyMedium,
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                Text(
                  'Ambil Sidik Jari',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 12),
                GridView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 2,
                    crossAxisSpacing: 12,
                    mainAxisSpacing: 12,
                  ),
                  itemCount: AppConstants.fingerPositions.length,
                  itemBuilder: (context, index) {
                    final position = AppConstants.fingerPositions[index];
                    final label = AppConstants.fingerLabels[position]!;
                    
                    Fingerprint? fingerprint;
                    for (final fp in session.fingerprints) {
                      if (fp.fingerPosition == position) {
                        fingerprint = fp;
                        break;
                      }
                    }
                    final isScanned = fingerprint != null;

                    return GestureDetector(
                      onTap: () {
                        if (fingerprint != null) {
                          _showFingerDetail(context, session.id, fingerprint, label);
                        } else {
                          context.go(
                            '/scan/capture/${session.id}/$position',
                          );
                        }
                      },
                      child: Card(
                        child: Stack(
                          children: [
                            Center(
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Icon(
                                    isScanned ? Icons.check_circle : Icons.fingerprint,
                                    size: 40,
                                    color: isScanned
                                        ? Colors.green
                                        : Colors.grey[400],
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    label,
                                    textAlign: TextAlign.center,
                                    style: Theme.of(context).textTheme.bodySmall,
                                  ),
                                ],
                              ),
                            ),
                            if (isScanned)
                              Positioned(
                                top: 8,
                                right: 8,
                                child: Container(
                                  padding: const EdgeInsets.all(4),
                                  decoration: BoxDecoration(
                                    color: Colors.green,
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  child: const Icon(
                                    Icons.check,
                                    color: Colors.white,
                                    size: 16,
                                  ),
                                ),
                              ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
                const SizedBox(height: 24),
                if (session.isComplete)
                  ElevatedButton.icon(
                    onPressed: () => context.go('/scan/review/${session.id}'),
                    icon: const Icon(Icons.rate_review),
                    label: const Text('Tinjau Hasil Pemindaian'),
                  ),
              ],
            ),
          );
        },
      ),
    );
  }
}

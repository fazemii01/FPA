import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import 'dart:io';
import '../../config/app_config.dart';
import '../../providers/scan_provider.dart';

class ReviewCapturedFingersScreen extends StatelessWidget {
  final int sessionId;

  const ReviewCapturedFingersScreen({
    Key? key,
    required this.sessionId,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Review Sidik Jari'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
      ),
      body: Consumer<ScanProvider>(
        builder: (context, scanProvider, _) {
          final session = scanProvider.currentSession;
          
          if (session == null || session.fingerprints.isEmpty) {
            return const Center(child: Text('Tidak ada sidik jari yang dipindai'));
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
                          'Ringkasan Pemindaian',
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                        const SizedBox(height: 16),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'Total Jari',
                                  style: Theme.of(context).textTheme.bodySmall,
                                ),
                                Text(
                                  '${session.completedCount}/10',
                                  style: Theme.of(context).textTheme.headlineSmall,
                                ),
                              ],
                            ),
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'Kualitas Rata-rata',
                                  style: Theme.of(context).textTheme.bodySmall,
                                ),
                                Text(
                                  '${_calculateAverageQuality(session).toStringAsFixed(1)}%',
                                  style: Theme.of(context).textTheme.headlineSmall,
                                ),
                              ],
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                Text(
                  'Detail Sidik Jari',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const SizedBox(height: 12),
                ListView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: session.fingerprints.length,
                  itemBuilder: (context, index) {
                    final fp = session.fingerprints[index];
                    final label = AppConstants.fingerLabels[fp.fingerPosition]!;
                    
                    return Card(
                      margin: const EdgeInsets.only(bottom: 12),
                      child: ListTile(
                        leading: CircleAvatar(
                          child: Text('${index + 1}'),
                        ),
                        title: Text(label),
                        subtitle: Text(
                          'Kualitas: ${fp.qualityScore?.toStringAsFixed(1) ?? "N/A"}%',
                        ),
                        trailing: Icon(
                          fp.isGoodQuality ? Icons.check_circle : Icons.info,
                          color: fp.isGoodQuality ? Colors.green : Colors.orange,
                        ),
                        onTap: () => _showFingerDetail(context, fp, label),
                      ),
                    );
                  },
                ),
                const SizedBox(height: 24),
                ElevatedButton(
                  onPressed: () => context.go('/scan/processing/$sessionId'),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                  child: const Text('Lanjut ke Pemrosesan'),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  double _calculateAverageQuality(dynamic session) {
    if (session.fingerprints.isEmpty) return 0;
    final total = session.fingerprints
        .fold<double>(0, (sum, fp) => sum + (fp.qualityScore ?? 0));
    return total / session.fingerprints.length;
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
            if (File(fp.imagePath).existsSync())
              ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: Image.file(
                  File(fp.imagePath),
                  height: 200,
                  fit: BoxFit.cover,
                ),
              ),
            const SizedBox(height: 16),
            Text('Kualitas: ${fp.qualityScore?.toStringAsFixed(1) ?? "N/A"}%'),
            const SizedBox(height: 8),
            Text('Tanggal: ${fp.createdAt.toString().split('.')[0]}'),
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
}

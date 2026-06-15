import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../../providers/scan_provider.dart';

class ReportViewScreen extends StatefulWidget {
  final int sessionId;

  const ReportViewScreen({
    Key? key,
    required this.sessionId,
  }) : super(key: key);

  @override
  State<ReportViewScreen> createState() => _ReportViewScreenState();
}

class _ReportViewScreenState extends State<ReportViewScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ScanProvider>().loadReport(widget.sessionId);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Laporan PDF'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.download),
            onPressed: () => _downloadReport(context),
          ),
        ],
      ),
      body: Consumer<ScanProvider>(
        builder: (context, scanProvider, _) {
          final report = scanProvider.currentReport;
          
          if (scanProvider.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          if (report == null) {
            return const Center(child: Text('Laporan tidak ditemukan'));
          }

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      children: [
                        const Icon(
                          Icons.picture_as_pdf,
                          size: 64,
                          color: Colors.red,
                        ),
                        const SizedBox(height: 16),
                        Text(
                          'Laporan Sidik Jari',
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'ID: ${report.id}',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Informasi Laporan',
                          style: Theme.of(context).textTheme.titleMedium,
                        ),
                        const SizedBox(height: 16),
                        _buildDetailRow(
                          'Skor Keseluruhan',
                          '${report.overallScore.toStringAsFixed(1)}%',
                        ),
                        const Divider(),
                        _buildDetailRow(
                          'Status',
                          'Selesai',
                        ),
                        const Divider(),
                        _buildDetailRow(
                          'Tanggal Dibuat',
                          report.createdAt.toString().split('.')[0],
                        ),
                        const Divider(),
                        _buildDetailRow(
                          'Lokasi File',
                          report.pdfPath ?? 'Tidak tersedia',
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                Text(
                  'Catatan',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const SizedBox(height: 12),
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Text(
                      _getReportNotes(report.overallScore),
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                ElevatedButton.icon(
                  onPressed: () => _downloadReport(context),
                  icon: const Icon(Icons.download),
                  label: const Text('Unduh Laporan'),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                ),
                const SizedBox(height: 12),
                OutlinedButton.icon(
                  onPressed: () => context.go('/home'),
                  icon: const Icon(Icons.home),
                  label: const Text('Kembali ke Beranda'),
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label),
          Expanded(
            child: Text(
              value,
              textAlign: TextAlign.right,
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
          ),
        ],
      ),
    );
  }

  String _getReportNotes(double score) {
    if (score >= 80) {
      return 'Laporan menunjukkan kualitas sidik jari yang sangat baik. Semua jari berhasil dipindai dengan standar kualitas tinggi.';
    } else if (score >= 60) {
      return 'Laporan menunjukkan kualitas sidik jari yang baik. Sebagian besar jari memenuhi standar kualitas yang diterima.';
    } else if (score >= 40) {
      return 'Laporan menunjukkan kualitas sidik jari yang cukup. Beberapa jari mungkin perlu dipindai ulang untuk hasil yang lebih baik.';
    } else {
      return 'Laporan menunjukkan kualitas sidik jari yang rendah. Disarankan untuk melakukan pemindaian ulang dengan kondisi yang lebih baik.';
    }
  }

  void _downloadReport(BuildContext context) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Laporan sedang diunduh...')),
    );
  }
}

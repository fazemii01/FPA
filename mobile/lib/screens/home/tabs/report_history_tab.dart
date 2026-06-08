import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../../../providers/scan_provider.dart';
import '../../../models/scan_model.dart';

class ReportHistoryTab extends StatelessWidget {
  const ReportHistoryTab({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final scanProvider = context.watch<ScanProvider>();
    final reportSessions = scanProvider.sessions.where((s) => 
      s.status == 'report_generated' || s.status == 'generating_report'
    ).toList();

    return RefreshIndicator(
      onRefresh: scanProvider.loadSessions,
      child: reportSessions.isEmpty
          ? const Center(child: Text('Belum ada laporan yang selesai.'))
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: reportSessions.length,
              itemBuilder: (context, index) {
                final session = reportSessions[index];
                return _buildReportCard(context, session, scanProvider);
              },
            ),
    );
  }

  Widget _buildReportCard(BuildContext context, ScanSession session, ScanProvider scanProvider) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      elevation: 1,
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: CircleAvatar(
          backgroundColor: Colors.purple.withOpacity(0.1),
          child: const Icon(Icons.description, color: Colors.purple),
        ),
        title: Text(
          session.participantName.isNotEmpty ? session.participantName : 'Sesi #${session.id}',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 4),
            Text('Status: ${session.status == 'report_generated' ? 'Laporan Selesai' : 'Sedang Diproses'}'),
          ],
        ),
        trailing: const Icon(Icons.remove_red_eye, color: Colors.blue),
        onTap: () async {
          showDialog(
            context: context,
            barrierDismissible: false,
            builder: (context) => const Center(child: CircularProgressIndicator()),
          );
          final success = await scanProvider.loadSession(session.id);
          if (context.mounted) {
            Navigator.pop(context);
            if (success) {
              context.push('/report/${session.id}');
            }
          }
        },
      ),
    );
  }
}

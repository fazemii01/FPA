import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../../../providers/auth_provider.dart';
import '../../../providers/scan_provider.dart';
import '../../../models/scan_model.dart';

class SessionTab extends StatefulWidget {
  const SessionTab({Key? key}) : super(key: key);

  @override
  State<SessionTab> createState() => _SessionTabState();
}

class _SessionTabState extends State<SessionTab> {
  String _searchQuery = '';

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();
    final scanProvider = context.watch<ScanProvider>();
    final isAdmin = authProvider.user?.role == 'admin';

    final filteredSessions = scanProvider.sessions.where((s) {
      final query = _searchQuery.toLowerCase();
      return s.participantName.toLowerCase().contains(query) ||
             'sesi #${s.id}'.contains(query);
    }).toList();

    return Scaffold(
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: TextField(
              decoration: InputDecoration(
                hintText: 'Cari nama peserta...',
                prefixIcon: const Icon(Icons.search),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                contentPadding: const EdgeInsets.symmetric(horizontal: 16),
              ),
              onChanged: (value) {
                setState(() {
                  _searchQuery = value;
                });
              },
            ),
          ),
          Expanded(
            child: RefreshIndicator(
              onRefresh: scanProvider.loadSessions,
              child: filteredSessions.isEmpty
                  ? const Center(child: Text('Tidak ada sesi yang ditemukan.'))
                  : ListView.builder(
                      itemCount: filteredSessions.length,
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      itemBuilder: (context, index) {
                        final session = filteredSessions[index];
                        return _buildSessionCard(
                            context, session, scanProvider, isAdmin);
                      },
                    ),
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => context.push('/clients/create'),
        icon: const Icon(Icons.add),
        label: const Text('Registrasi Sesi'),
      ),
    );
  }

  // ── Status helper ──────────────────────────────────────────────────────────

  Map<String, dynamic> _statusMeta(String status) {
    switch (status) {
      case 'scan_completed':
        return {'label': 'Siap Kirim', 'color': Colors.teal};
      case 'scanning':
        return {'label': 'Memindai', 'color': Colors.orange};
      case 'waiting_for_review':
        return {'label': 'Menunggu Tinjauan', 'color': Colors.amber};
      case 'approved':
        return {'label': 'Disetujui', 'color': Colors.green};
      case 'rejected':
        return {'label': 'Ditolak', 'color': Colors.red};
      case 'need_rescan':
        return {'label': 'Perlu Scan Ulang', 'color': Colors.deepOrange};
      case 'generating_report':
        return {'label': 'Membuat Laporan', 'color': Colors.purple};
      case 'report_generated':
        return {'label': 'Laporan Selesai', 'color': Colors.indigo};
      case 'registered':
        return {'label': 'Terdaftar', 'color': Colors.blue};
      default:
        return {'label': status, 'color': Colors.grey};
    }
  }

  // ── Session Card ───────────────────────────────────────────────────────────

  Widget _buildSessionCard(
    BuildContext context,
    ScanSession session,
    ScanProvider scanProvider,
    bool isAdmin,
  ) {
    final meta = _statusMeta(session.status);
    final Color statusColor = meta['color'] as Color;
    final String statusLabel = meta['label'] as String;
    final bool isScanCompleted = session.status == 'scan_completed';

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      elevation: 1,
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => _onCardTap(context, session, scanProvider, isAdmin),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // ── Top row: avatar + info + actions ──
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Avatar
                  CircleAvatar(
                    backgroundColor:
                        Theme.of(context).primaryColor.withOpacity(0.1),
                    child: Icon(Icons.fingerprint,
                        color: Theme.of(context).primaryColor),
                  ),
                  const SizedBox(width: 12),
                  // Name + details
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          session.participantName.isNotEmpty
                              ? session.participantName
                              : 'Sesi #${session.id}',
                          style: const TextStyle(
                              fontWeight: FontWeight.bold, fontSize: 15),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Umur: ${session.participantAge} th  ·  ${session.completedCount}/10 Jari',
                          style: TextStyle(
                              color: Colors.grey[600], fontSize: 12),
                        ),
                        const SizedBox(height: 6),
                        // Status badge
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 8, vertical: 3),
                          decoration: BoxDecoration(
                            color: statusColor.withOpacity(0.12),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(
                            statusLabel,
                            style: TextStyle(
                              color: statusColor,
                              fontSize: 11,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  // Admin delete button
                  if (isAdmin)
                    IconButton(
                      icon:
                          const Icon(Icons.delete_outline, color: Colors.red),
                      tooltip: 'Hapus Sesi',
                      onPressed: () =>
                          _confirmDelete(context, session, scanProvider),
                    ),
                ],
              ),

              // ── "Kirim Scan" button — visible when scan_completed ──
              if (isScanCompleted) ...[
                const SizedBox(height: 10),
                const Divider(height: 1),
                const SizedBox(height: 10),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: () =>
                        _confirmSubmit(context, session, scanProvider),
                    icon: const Icon(Icons.send_rounded, size: 18),
                    label: const Text('Kirim Scan'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.teal,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 10),
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8)),
                      textStyle: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  // ── Card tap → navigate ────────────────────────────────────────────────────

  Future<void> _onCardTap(
    BuildContext context,
    ScanSession session,
    ScanProvider scanProvider,
    bool isAdmin,
  ) async {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => const Center(child: CircularProgressIndicator()),
    );
    final success = await scanProvider.loadSession(session.id);
    if (mounted) {
      Navigator.pop(context);
      if (success) {
        final s = session.status;
        if (s == 'report_generated' || s == 'generating_report') {
          context.push('/report/${session.id}');
        } else {
          context.push('/scan/review/${session.id}');
        }
      }
    }
  }

  // ── Confirm & submit for review ────────────────────────────────────────────

  Future<void> _confirmSubmit(
    BuildContext context,
    ScanSession session,
    ScanProvider scanProvider,
  ) async {
    final name = session.participantName.isNotEmpty
        ? session.participantName
        : 'Sesi #${session.id}';

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Kirim untuk Ditinjau?'),
        content: Text(
          'Semua 10 jari peserta "$name" telah dipindai.\n\n'
          'Kirim sesi ini ke antrian tinjauan admin?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Batal'),
          ),
          ElevatedButton.icon(
            onPressed: () => Navigator.pop(ctx, true),
            icon: const Icon(Icons.send_rounded, size: 16),
            label: const Text('Kirim Scan'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.teal,
              foregroundColor: Colors.white,
            ),
          ),
        ],
      ),
    );

    if (confirmed == true && mounted) {
      final success = await scanProvider.submitForReview(session.id);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(success
                ? 'Sesi "$name" berhasil dikirim untuk ditinjau!'
                : scanProvider.error ?? 'Gagal mengirim sesi'),
            backgroundColor: success ? Colors.green : Colors.red,
          ),
        );
        if (success) {
          scanProvider.loadSessions(); // refresh list
        }
      }
    }
  }

  // ── Confirm delete ─────────────────────────────────────────────────────────

  Future<void> _confirmDelete(
    BuildContext context,
    ScanSession session,
    ScanProvider scanProvider,
  ) async {
    final bool isApproved =
        session.status == 'approved' || session.status == 'report_generated';
    final name = session.participantName.isNotEmpty
        ? session.participantName
        : 'Sesi #${session.id}';

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Hapus Sesi Ini?'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Sesi peserta "$name" beserta semua data sidik jari akan dihapus '
              'secara permanen. Tindakan ini tidak dapat dibatalkan.',
            ),
            if (isApproved) ...[
              const SizedBox(height: 12),
              const Text(
                '⚠️ Laporan untuk sesi ini mungkin sudah dibuat.',
                style: TextStyle(
                    color: Colors.red, fontWeight: FontWeight.bold),
              ),
            ],
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Batal'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('Hapus'),
          ),
        ],
      ),
    );

    if (confirmed == true && mounted) {
      final success = await scanProvider.deleteSession(session.id);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(success
                ? 'Sesi berhasil dihapus'
                : scanProvider.error ?? 'Gagal menghapus sesi'),
            backgroundColor: success ? Colors.green : Colors.red,
          ),
        );
      }
    }
  }
}

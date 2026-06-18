import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../../../providers/auth_provider.dart';
import '../../../providers/scan_provider.dart';
import '../../../models/scan_model.dart';
import '../../../theme/app_theme.dart';
import '../../../widgets/app_toast.dart';

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
    final canDelete = authProvider.user?.hasPermission('DELETE_SESSION') ?? false;

    final filteredSessions = scanProvider.sessions.where((s) {
      final query = _searchQuery.toLowerCase();
      return s.participantName.toLowerCase().contains(query) ||
             'sesi #${s.id}'.contains(query);
    }).toList();

    return Scaffold(
      backgroundColor: const Color(0xFFFAFAFA),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
            child: TextField(
              decoration: const InputDecoration(
                hintText: 'Cari nama peserta...',
                prefixIcon: Icon(Icons.search_rounded, color: Colors.grey),
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
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                      itemBuilder: (context, index) {
                        final session = filteredSessions[index];
                        return _buildSessionCard(
                            context, session, scanProvider, canDelete);
                      },
                    ),
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => context.push('/clients/create'),
        backgroundColor: AppTheme.primaryColor,
        foregroundColor: Colors.white,
        elevation: 2,
        icon: const Icon(Icons.add_rounded),
        label: const Text(
          'Registrasi Sesi',
          style: TextStyle(fontWeight: FontWeight.bold, letterSpacing: 0.5),
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
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
        return {'label': 'Menunggu Tinjauan', 'color': AppTheme.warningColor};
      case 'approved':
        return {'label': 'Disetujui', 'color': AppTheme.successColor};
      case 'rejected':
        return {'label': 'Ditolak', 'color': AppTheme.errorColor};
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
    bool canDelete,
  ) {
    final meta = _statusMeta(session.status);
    final Color statusColor = meta['color'] as Color;
    final String statusLabel = meta['label'] as String;
    final bool isScanCompleted = session.status == 'scan_completed';

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFFE0E0E0)),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(8),
        onTap: () => _onCardTap(context, session, scanProvider, canDelete),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: AppTheme.primaryColor.withOpacity(0.05),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Icons.fingerprint_rounded,
                        color: AppTheme.primaryColor, size: 24),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          session.participantName.isNotEmpty
                              ? session.participantName
                              : 'Sesi #${session.id}',
                          style: const TextStyle(
                              fontWeight: FontWeight.bold, fontSize: 15, color: AppTheme.primaryColor),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Umur: ${session.participantAge} th  ·  ${session.completedCount}/10 Jari',
                          style: TextStyle(
                              color: Colors.grey[600], fontSize: 12),
                        ),
                        const SizedBox(height: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: statusColor.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            statusLabel,
                            style: TextStyle(
                              color: statusColor,
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  if (canDelete)
                    IconButton(
                      icon:
                          const Icon(Icons.delete_outline_rounded, color: AppTheme.errorColor),
                      tooltip: 'Hapus Sesi',
                      onPressed: () =>
                          _confirmDelete(context, session, scanProvider),
                    ),
                ],
              ),
              if (isScanCompleted) ...[
                const SizedBox(height: 12),
                const Divider(height: 1, color: Color(0xFFF0F0F0)),
                const SizedBox(height: 12),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: () =>
                        _confirmSubmit(context, session, scanProvider),
                    icon: const Icon(Icons.send_rounded, size: 16),
                    label: const Text('Kirim Scan'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.primaryColor,
                      foregroundColor: Colors.white,
                      elevation: 0,
                      shadowColor: Colors.transparent,
                      padding: const EdgeInsets.symmetric(vertical: 12),
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
    bool canDelete,
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
        if (success) {
          AppToast.showSuccess(context, 'Sesi "$name" berhasil dikirim untuk ditinjau!');
        } else {
          AppToast.showError(context, scanProvider.error ?? 'Gagal mengirim sesi');
        }
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
        if (success) {
          AppToast.showSuccess(context, 'Sesi berhasil dihapus');
        } else {
          AppToast.showError(context, scanProvider.error ?? 'Gagal menghapus sesi');
        }
      }
    }
  }
}

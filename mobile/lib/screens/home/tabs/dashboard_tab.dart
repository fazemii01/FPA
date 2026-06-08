import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../../../providers/auth_provider.dart';
import '../../../providers/scan_provider.dart';
import '../../../models/scan_model.dart';

class DashboardTab extends StatefulWidget {
  const DashboardTab({Key? key}) : super(key: key);

  @override
  State<DashboardTab> createState() => _DashboardTabState();
}

class _DashboardTabState extends State<DashboardTab> {
  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();
    final scanProvider = context.watch<ScanProvider>();
    final user = authProvider.user;
    final isAdmin = user?.role == 'admin';

    return RefreshIndicator(
      onRefresh: () async {
        await scanProvider.loadSessions();
        if (isAdmin) {
          await scanProvider.loadReviewQueue();
        }
      },
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Welcome Card
            Card(
              elevation: 2,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
              child: Container(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      Theme.of(context).primaryColor,
                      Theme.of(context).primaryColor.withBlue(200),
                    ],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(16),
                ),
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Selamat Datang, ${user?.fullName ?? user?.email ?? "User"}',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      'Peran: ${isAdmin ? "Administrator" : "Staf Pemindaian"}',
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.85),
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),

            // Summary Grid
            Text(
              'Ringkasan',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 10),
            _buildSummaryGrid(context, scanProvider, isAdmin),
            const SizedBox(height: 24),

            // Quick Actions
            if (!isAdmin) ...[
              ElevatedButton.icon(
                onPressed: () => context.push('/clients/create'),
                icon: const Icon(Icons.person_add_alt_1),
                label: const Text('Registrasi Peserta Baru'),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
              const SizedBox(height: 24),
            ],

            // Recent Sessions
            Text(
              'Sesi Terbaru',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 10),
            if (scanProvider.sessions.isEmpty && scanProvider.isLoading)
              const Center(child: CircularProgressIndicator())
            else if (scanProvider.sessions.isEmpty)
              const Center(child: Text('Belum ada sesi terbaru'))
            else
              ...scanProvider.sessions.take(5).map((session) => _buildRecentSessionCard(context, session, scanProvider, isAdmin)).toList(),
          ],
        ),
      ),
    );
  }

  Widget _buildSummaryGrid(BuildContext context, ScanProvider scanProvider, bool isAdmin) {
    int total = scanProvider.sessions.length;
    int waiting = scanProvider.sessions.where((s) => s.status == 'waiting_for_review').length;
    int needRescan = scanProvider.sessions.where((s) => s.status == 'need_rescan').length;
    int approved = scanProvider.sessions.where((s) => s.status == 'approved').length;
    int rejected = scanProvider.sessions.where((s) => s.status == 'rejected').length;
    int reportGenerated = scanProvider.sessions.where((s) => s.status == 'report_generated' || s.status == 'generating_report').length;

    List<Widget> cards = [];
    
    cards.add(_buildStatCard(context, 'Total Sesi', total.toString(), Colors.blue));
    cards.add(_buildStatCard(context, 'Menunggu Tinjauan', waiting.toString(), Colors.amber));
    
    if (isAdmin) {
      cards.add(_buildStatCard(context, 'Disetujui', approved.toString(), Colors.green));
      cards.add(_buildStatCard(context, 'Ditolak', rejected.toString(), Colors.red));
    } else {
      cards.add(_buildStatCard(context, 'Perlu Pindai Ulang', needRescan.toString(), Colors.deepOrange));
    }
    cards.add(_buildStatCard(context, 'Laporan Selesai', reportGenerated.toString(), Colors.purple));

    return GridView.count(
      crossAxisCount: 2,
      crossAxisSpacing: 10,
      mainAxisSpacing: 10,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      childAspectRatio: 1.5,
      children: cards,
    );
  }

  Widget _buildStatCard(BuildContext context, String title, String value, Color color) {
    return Card(
      elevation: 1,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          border: Border(left: BorderSide(color: color, width: 4)),
        ),
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(title, style: TextStyle(color: Colors.grey[600], fontSize: 12, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Text(value, style: TextStyle(color: color, fontSize: 24, fontWeight: FontWeight.bold)),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentSessionCard(BuildContext context, ScanSession session, ScanProvider scanProvider, bool isAdmin) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: Theme.of(context).primaryColor.withOpacity(0.1),
          child: Icon(Icons.fingerprint, color: Theme.of(context).primaryColor),
        ),
        title: Text(session.participantName.isNotEmpty ? session.participantName : 'Sesi #${session.id}'),
        subtitle: Text('${session.completedCount}/10 Jari | ${session.status}'),
        onTap: () async {
          showDialog(
            context: context,
            barrierDismissible: false,
            builder: (context) => const Center(child: CircularProgressIndicator()),
          );
          final success = await scanProvider.loadSession(session.id);
          if (mounted) {
            Navigator.pop(context);
            if (success) {
              if (isAdmin || session.status == 'waiting_for_review' || session.status == 'approved' || session.status == 'rejected') {
                if (session.status == 'report_generated' || session.status == 'generating_report') {
                  context.push('/report/${session.id}');
                } else {
                  context.push('/scan/review/${session.id}');
                }
              } else {
                context.push('/scan');
              }
            }
          }
        },
      ),
    );
  }
}

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../../../providers/auth_provider.dart';
import '../../../providers/scan_provider.dart';
import '../../../models/scan_model.dart';
import '../../../theme/app_theme.dart';

class DashboardTab extends StatefulWidget {
  const DashboardTab({Key? key}) : super(key: key);

  @override
  State<DashboardTab> createState() => _DashboardTabState();
}

class _DashboardTabState extends State<DashboardTab> {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final authProvider = context.watch<AuthProvider>();
    final scanProvider = context.watch<ScanProvider>();
    final user = authProvider.user;
    final isAdmin = user?.role == 'admin';

    int total = scanProvider.sessions.length;
    int waiting = scanProvider.sessions.where((s) => s.status == 'waiting_for_review').length;
    int reportGenerated = scanProvider.sessions.where((s) => s.status == 'report_generated' || s.status == 'generating_report').length;

    return Scaffold(
      backgroundColor: const Color(0xFFFAFAFA),
      body: RefreshIndicator(
        onRefresh: () async {
          await scanProvider.loadSessions();
          if (isAdmin) {
            await scanProvider.loadReviewQueue();
          }
        },
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(24),
          child: TweenAnimationBuilder<double>(
            tween: Tween<double>(begin: 0.0, end: 1.0),
            duration: const Duration(milliseconds: 600),
            curve: Curves.easeOutCubic,
            builder: (context, value, child) {
              return Transform.translate(
                offset: Offset(0, 30 * (1 - value)),
                child: Opacity(
                  opacity: value,
                  child: child,
                ),
              );
            },
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const SizedBox(height: 12),
                // Welcome Panel
                _buildWelcomePanel(context, user, isAdmin),
                const SizedBox(height: 32),

                // Bento Grid Section Header
                Text(
                  'Ringkasan Analisis',
                  style: theme.textTheme.titleMedium?.copyWith(
                    color: AppTheme.primaryColor,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 16),

                // Bento Grid Layout
                // Card 1: Wide Hero Card
                _buildHeroBentoCard(context, total, waiting, theme),
                const SizedBox(height: 12),

                // Row 2: Two cards side by side
                Row(
                  children: [
                    Expanded(
                      child: _buildBentoCard(
                        context: context,
                        title: 'Tinjauan',
                        value: waiting.toString(),
                        subtitle: 'Perlu verifikasi',
                        icon: Icons.pending_actions_rounded,
                        accentColor: AppTheme.warningColor,
                        theme: theme,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: _buildBentoCard(
                        context: context,
                        title: 'Laporan',
                        value: reportGenerated.toString(),
                        subtitle: 'Telah terbit',
                        icon: Icons.check_circle_outline_rounded,
                        accentColor: AppTheme.secondaryColor,
                        theme: theme,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),

                // Card 4: System Health status card (100% width)
                _buildSystemHealthCard(context, theme),
                const SizedBox(height: 24),

                // Quick Actions
                if (!isAdmin) ...[
                  _buildQuickActionBtn(context, theme),
                  const SizedBox(height: 24),
                ],

                // Recent Sessions
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Aktivitas Terbaru',
                      style: theme.textTheme.titleMedium?.copyWith(
                        color: AppTheme.primaryColor,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                if (scanProvider.sessions.isEmpty && scanProvider.isLoading)
                  const Center(child: CircularProgressIndicator())
                else if (scanProvider.sessions.isEmpty)
                  const Center(child: Text('Belum ada sesi terbaru'))
                else
                  ...scanProvider.sessions
                      .take(5)
                      .map((session) => _buildRecentSessionCard(context, session, scanProvider, isAdmin)),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildWelcomePanel(BuildContext context, dynamic user, bool isAdmin) {
    return Row(
      children: [
        CircleAvatar(
          radius: 24,
          backgroundColor: AppTheme.primaryColor.withOpacity(0.1),
          child: Text(
            (user?.fullName ?? user?.email ?? 'U').substring(0, 1).toUpperCase(),
            style: const TextStyle(
              color: AppTheme.primaryColor,
              fontWeight: FontWeight.bold,
              fontSize: 18,
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Selamat Datang,',
                style: TextStyle(
                  color: Colors.grey[500],
                  fontSize: 12,
                ),
              ),
              Text(
                user?.fullName ?? user?.email ?? 'User',
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                  color: AppTheme.primaryColor,
                ),
              ),
            ],
          ),
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
          decoration: BoxDecoration(
            color: AppTheme.primaryColor.withOpacity(0.05),
            borderRadius: BorderRadius.circular(6),
          ),
          child: Text(
            isAdmin ? 'Admin' : 'Operator',
            style: const TextStyle(
              color: AppTheme.primaryColor,
              fontSize: 11,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildHeroBentoCard(BuildContext context, int total, int waiting, ThemeData theme) {
    return Container(
      decoration: BoxDecoration(
        color: AppTheme.primaryColor,
        borderRadius: BorderRadius.circular(8),
        boxShadow: [
          BoxShadow(
            color: AppTheme.primaryColor.withOpacity(0.15),
            blurRadius: 15,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      padding: const EdgeInsets.all(20),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'AKTIVITAS UTAMA',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.7),
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 1.5,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  '$total Total Sesi',
                  style: theme.textTheme.headlineLarge?.copyWith(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Semua sesi pemindaian terdaftar',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.8),
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.15),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Row(
              children: [
                const Icon(Icons.sync, color: Colors.white, size: 16),
                const SizedBox(width: 4),
                Text(
                  '$waiting Pending',
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBentoCard({
    required BuildContext context,
    required String title,
    required String value,
    required String subtitle,
    required IconData icon,
    required Color accentColor,
    required ThemeData theme,
  }) {
    return Container(
      height: 120,
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
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Icon(icon, color: accentColor, size: 20),
              Container(
                width: 8,
                height: 8,
                decoration: BoxDecoration(
                  color: accentColor,
                  shape: BoxShape.circle,
                ),
              ),
            ],
          ),
          const Spacer(),
          Text(
            value,
            style: theme.textTheme.headlineMedium?.copyWith(
              color: AppTheme.primaryColor,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            title,
            style: TextStyle(
              color: Colors.grey[800],
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSystemHealthCard(BuildContext context, ThemeData theme) {
    return Container(
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
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.analytics_outlined, color: AppTheme.primaryColor, size: 20),
              const SizedBox(width: 8),
              Text(
                'Status Sistem Biometrik',
                style: theme.textTheme.titleMedium?.copyWith(
                  color: AppTheme.primaryColor,
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: AppTheme.successColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Row(
                  children: [
                    CircleAvatar(radius: 4, backgroundColor: AppTheme.successColor),
                    SizedBox(width: 4),
                    Text(
                      'Optimal',
                      style: TextStyle(color: AppTheme.successColor, fontSize: 10, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildHealthDial('Engine API', 0.98, '98%', AppTheme.primaryColor),
              _buildHealthDial('Clarity Rate', 0.92, '92%', AppTheme.secondaryColor),
              _buildHealthDial('DB Sync', 1.0, 'Ready', AppTheme.successColor),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildHealthDial(String label, double value, String status, Color color) {
    return Column(
      children: [
        SizedBox(
          height: 54,
          width: 54,
          child: Stack(
            alignment: Alignment.center,
            children: [
              CircularProgressIndicator(
                value: value,
                strokeWidth: 4,
                backgroundColor: const Color(0xFFF0F0F0),
                valueColor: AlwaysStoppedAnimation<Color>(color),
              ),
              Text(
                status,
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                  color: Colors.grey[800],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 8),
        Text(
          label,
          style: TextStyle(
            fontSize: 11,
            color: Colors.grey[600],
          ),
        ),
      ],
    );
  }

  Widget _buildQuickActionBtn(BuildContext context, ThemeData theme) {
    return ElevatedButton.icon(
      onPressed: () => context.push('/clients/create'),
      icon: const Icon(Icons.person_add_alt_1_rounded, size: 20),
      label: const Text('Registrasi Peserta Baru'),
      style: ElevatedButton.styleFrom(
        backgroundColor: AppTheme.primaryColor,
        foregroundColor: Colors.white,
        elevation: 0,
        shadowColor: Colors.transparent,
        padding: const EdgeInsets.symmetric(vertical: 16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
    );
  }

  Widget _buildRecentSessionCard(BuildContext context, ScanSession session, ScanProvider scanProvider, bool isAdmin) {
    Color badgeColor;
    String statusText;

    switch (session.status) {
      case 'approved':
        badgeColor = AppTheme.successColor;
        statusText = 'Disetujui';
        break;
      case 'rejected':
        badgeColor = AppTheme.errorColor;
        statusText = 'Ditolak';
        break;
      case 'waiting_for_review':
        badgeColor = AppTheme.warningColor;
        statusText = 'Tinjauan';
        break;
      case 'need_rescan':
        badgeColor = Colors.deepOrange;
        statusText = 'Rescan';
        break;
      case 'report_generated':
        badgeColor = Colors.purple;
        statusText = 'Selesai';
        break;
      default:
        badgeColor = Colors.grey;
        statusText = session.status;
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFFE0E0E0)),
      ),
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: AppTheme.primaryColor.withOpacity(0.05),
            shape: BoxShape.circle,
          ),
          child: const Icon(Icons.fingerprint_rounded, color: AppTheme.primaryColor, size: 24),
        ),
        title: Text(
          session.participantName.isNotEmpty ? session.participantName : 'Sesi #${session.id}',
          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: AppTheme.primaryColor),
        ),
        subtitle: Padding(
          padding: const EdgeInsets.only(top: 4),
          child: Text(
            '${session.completedCount}/10 Jari terindeks',
            style: TextStyle(color: Colors.grey[600], fontSize: 12),
          ),
        ),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: badgeColor.withOpacity(0.1),
            borderRadius: BorderRadius.circular(6),
          ),
          child: Text(
            statusText,
            style: TextStyle(
              color: badgeColor,
              fontWeight: FontWeight.bold,
              fontSize: 10,
            ),
          ),
        ),
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

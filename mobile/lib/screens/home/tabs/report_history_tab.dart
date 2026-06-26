import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../../providers/scan_provider.dart';
import '../../../providers/auth_provider.dart';
import '../../../models/scan_model.dart';
import '../../../theme/app_theme.dart';
import '../../../widgets/app_toast.dart';

class ReportHistoryTab extends StatelessWidget {
  const ReportHistoryTab({super.key});

  @override
  Widget build(BuildContext context) {
    final scanProvider = context.watch<ScanProvider>();
    final authProvider = context.watch<AuthProvider>();
    final reportSessions = scanProvider.sessions.where((s) => 
      s.status == 'report_generated' || s.status == 'generating_report'
    ).toList();

    return Scaffold(
      backgroundColor: const Color(0xFFFAFAFA),
      body: RefreshIndicator(
        onRefresh: scanProvider.loadSessions,
        child: reportSessions.isEmpty
            ? const Center(
                child: Padding(
                  padding: EdgeInsets.all(32),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.history_toggle_off_rounded, size: 64, color: Colors.grey),
                      SizedBox(height: 16),
                      Text(
                        'Belum ada laporan yang selesai.',
                        style: TextStyle(color: Colors.grey, fontSize: 16),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ),
              )
            : ListView.builder(
                padding: const EdgeInsets.all(24),
                itemCount: reportSessions.length,
                itemBuilder: (context, index) {
                  final session = reportSessions[index];
                  return _buildReportCard(context, session, scanProvider, authProvider);
                },
              ),
      ),
    );
  }

  Widget _buildReportCard(
    BuildContext context,
    ScanSession session,
    ScanProvider scanProvider,
    AuthProvider authProvider,
  ) {
    final isDone = session.status == 'report_generated';
    final canGenerateReport = authProvider.user?.hasPermission('GENERATE_REPORT') ?? false;
    
    final Color badgeColor = isDone ? AppTheme.successColor : AppTheme.warningColor;
    final String badgeLabel = isDone ? 'Laporan Selesai' : 'Sedang Diproses';
 
    return BouncingWidget(
      onTap: () => _onCardTap(context, session, scanProvider),
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
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
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: AppTheme.primaryColor.withOpacity(0.08),
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.description_outlined, color: AppTheme.primaryColor, size: 24),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      session.participantName.isNotEmpty ? session.participantName : 'Sesi #${session.id}',
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: AppTheme.primaryColor),
                    ),
                    const SizedBox(height: 6),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: badgeColor.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(
                        badgeLabel,
                        style: TextStyle(
                          color: badgeColor,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              if (canGenerateReport && isDone) ...[
                _RegenerateButton(
                  sessionId: session.id,
                  participantName: session.participantName.isNotEmpty ? session.participantName : 'Sesi #${session.id}',
                  scanProvider: scanProvider,
                ),
                const SizedBox(width: 12),
              ],
              const Icon(Icons.remove_red_eye_rounded, color: AppTheme.primaryColor, size: 20),
              const SizedBox(width: 8),
              const Icon(Icons.download_rounded, color: AppTheme.primaryColor, size: 20),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _onCardTap(BuildContext context, ScanSession session, ScanProvider scanProvider) async {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const Center(child: CircularProgressIndicator()),
    );
    final success = await scanProvider.loadReport(session.id);
    if (context.mounted) {
      Navigator.pop(context);
      if (success && scanProvider.currentReport?.pdfUrl != null) {
        final url = Uri.parse(scanProvider.currentReport!.pdfUrl!);
        try {
          final launched = await launchUrl(url, mode: LaunchMode.externalApplication);
          if (!launched) {
            final launchedDefault = await launchUrl(url, mode: LaunchMode.platformDefault);
            if (!launchedDefault && context.mounted) {
              AppToast.showError(context, 'Tidak dapat membuka link laporan');
            }
          }
        } catch (e) {
          try {
            final launchedDefault = await launchUrl(url, mode: LaunchMode.platformDefault);
            if (!launchedDefault && context.mounted) {
              AppToast.showError(context, 'Gagal membuka link: $e');
            }
          } catch (err) {
            if (context.mounted) {
              AppToast.showError(context, 'Error: $err');
            }
          }
        }
      } else {
        if (context.mounted) {
          AppToast.showWarning(context, 'Laporan tidak ditemukan atau belum selesai');
        }
      }
    }
  }
}

// ── Regenerate Report Button Widget (Admin only) ──────────────────────────────

class _RegenerateButton extends StatefulWidget {
  final int sessionId;
  final String participantName;
  final ScanProvider scanProvider;

  const _RegenerateButton({
    required this.sessionId,
    required this.participantName,
    required this.scanProvider,
  });

  @override
  State<_RegenerateButton> createState() => _RegenerateButtonState();
}

class _RegenerateButtonState extends State<_RegenerateButton> {
  bool _isLoading = false;

  Future<void> _regenerateReport(BuildContext context) async {
    if (_isLoading) return;
    
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Regenerasi Laporan?'),
        content: Text(
          'Apakah Anda yakin ingin melakukan regenerasi laporan analisis sidik jari untuk peserta "${widget.participantName}"?'
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Batal'),
          ),
          ElevatedButton.icon(
            onPressed: () => Navigator.pop(ctx, true),
            icon: const Icon(Icons.refresh_rounded, size: 16),
            label: const Text('Regenerasi'),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.primaryColor,
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
          ),
        ],
      ),
    );

    if (confirmed == true && context.mounted) {
      setState(() => _isLoading = true);
      
      final success = await widget.scanProvider.generateReport(widget.sessionId);
      await widget.scanProvider.loadSession(widget.sessionId);
      
      if (context.mounted) {
        setState(() => _isLoading = false);
        if (success) {
          AppToast.showSuccess(context, 'Laporan berhasil diregenerasi!');
        } else {
          AppToast.showError(
            context,
            widget.scanProvider.error ?? 'Gagal meregenerasi laporan',
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const SizedBox(
        width: 20,
        height: 20,
        child: CircularProgressIndicator(
          strokeWidth: 2,
          valueColor: AlwaysStoppedAnimation<Color>(AppTheme.primaryColor),
        ),
      );
    }

    return BouncingWidget(
      onTap: () => _regenerateReport(context),
      child: Container(
        padding: const EdgeInsets.all(6),
        decoration: BoxDecoration(
          color: AppTheme.primaryColor.withOpacity(0.08),
          borderRadius: BorderRadius.circular(6),
        ),
        child: const Icon(
          Icons.refresh_rounded,
          color: AppTheme.primaryColor,
          size: 20,
        ),
      ),
    );
  }
}

// ── Bouncing Click Scale Animation Widget ──────────────────────────────────────

class BouncingWidget extends StatefulWidget {
  final Widget child;
  final VoidCallback onTap;

  const BouncingWidget({
    super.key,
    required this.child,
    required this.onTap,
  });

  @override
  State<BouncingWidget> createState() => _BouncingWidgetState();
}

class _BouncingWidgetState extends State<BouncingWidget> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 100),
      lowerBound: 0.0,
      upperBound: 0.05,
    );
    _scaleAnimation = Tween<double>(begin: 1.0, end: 0.95).animate(_controller);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTapDown: (_) => _controller.forward(),
      onTapUp: (_) {
        _controller.reverse();
        widget.onTap();
      },
      onTapCancel: () => _controller.reverse(),
      child: ScaleTransition(
        scale: _scaleAnimation,
        child: widget.child,
      ),
    );
  }
}

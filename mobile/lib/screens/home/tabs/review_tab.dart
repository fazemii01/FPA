import 'dart:io';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../../../providers/scan_provider.dart';
import '../../../models/scan_model.dart';
import '../../../theme/app_theme.dart';
import '../../../widgets/app_toast.dart';

class ReviewTab extends StatelessWidget {
  const ReviewTab({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final scanProvider = context.watch<ScanProvider>();
    final reviewQueue = scanProvider.reviewQueue;       // waiting_for_review
    final approvedQueue = scanProvider.approvedQueue;   // approved → ready for report

    final isEmpty = reviewQueue.isEmpty && approvedQueue.isEmpty;

    return Scaffold(
      backgroundColor: const Color(0xFFFAFAFA),
      body: RefreshIndicator(
        onRefresh: () async {
          await Future.wait([
            scanProvider.loadReviewQueue(),
            scanProvider.loadSessions(),
          ]);
        },
        child: isEmpty
            ? const Center(
                child: Padding(
                  padding: EdgeInsets.all(32),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.inbox_outlined, size: 64, color: Colors.grey),
                      SizedBox(height: 16),
                      Text(
                        'Tidak ada sesi dalam antrian tinjauan.',
                        style: TextStyle(color: Colors.grey, fontSize: 16),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ),
              )
            : ListView(
                padding: const EdgeInsets.all(24),
                children: [
                  // ── Section 1: Perlu Ditinjau ──────────────────────────────
                  if (reviewQueue.isNotEmpty) ...[
                    _SectionHeader(
                      icon: Icons.rate_review_outlined,
                      label: 'Perlu Ditinjau',
                      count: reviewQueue.length,
                      color: AppTheme.warningColor,
                    ),
                    const SizedBox(height: 12),
                    ...reviewQueue.map(
                      (session) => _ReviewCard(
                        session: session,
                        mode: _CardMode.review,
                      ),
                    ),
                    const SizedBox(height: 24),
                  ],

                  // ── Section 2: Siap Buat Laporan ───────────────────────────
                  if (approvedQueue.isNotEmpty) ...[
                    _SectionHeader(
                      icon: Icons.picture_as_pdf_outlined,
                      label: 'Siap Buat Laporan',
                      count: approvedQueue.length,
                      color: AppTheme.successColor,
                    ),
                    const SizedBox(height: 12),
                    ...approvedQueue.map(
                      (session) => _ReviewCard(
                        session: session,
                        mode: _CardMode.generateReport,
                      ),
                    ),
                  ],
                ],
              ),
      ),
    );
  }
}

// ── Section header ─────────────────────────────────────────────────────────────

class _SectionHeader extends StatelessWidget {
  const _SectionHeader({
    required this.icon,
    required this.label,
    required this.count,
    required this.color,
  });

  final IconData icon;
  final String label;
  final int count;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, color: color, size: 18),
        const SizedBox(width: 8),
        Text(
          label,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 14,
            color: color,
            letterSpacing: 0.5,
          ),
        ),
        const SizedBox(width: 8),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Text(
            '$count',
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.bold,
              fontSize: 11,
            ),
          ),
        ),
      ],
    );
  }
}

// ── Card mode ─────────────────────────────────────────────────────────────────

enum _CardMode { review, generateReport }

// ── Bouncing Click Scale Animation Widget ──────────────────────────────────────

class BouncingWidget extends StatefulWidget {
  final Widget child;
  final VoidCallback onTap;

  const BouncingWidget({
    Key? key,
    required this.child,
    required this.onTap,
  }) : super(key: key);

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

// ── Review / Approved card ────────────────────────────────────────────────────

class _ReviewCard extends StatefulWidget {
  const _ReviewCard({required this.session, required this.mode});

  final ScanSession session;
  final _CardMode mode;

  @override
  State<_ReviewCard> createState() => _ReviewCardState();
}

class _ReviewCardState extends State<_ReviewCard> {
  bool _isLoading = false;

  double _calculateAverageQuality(ScanSession session) {
    if (session.fingerprints.isEmpty) return 0.0;
    double total = 0.0;
    int count = 0;
    for (var f in session.fingerprints) {
      if (f.qualityScore != null) {
        total += f.qualityScore!;
        count++;
      }
    }
    return count > 0 ? (total / count) : 0.0;
  }

  Widget _buildBiometricThumbnail(ScanSession session) {
    final hasFingerprint = session.fingerprints.isNotEmpty;
    final firstFingerprint = hasFingerprint ? session.fingerprints.first : null;
    
    Widget imageWidget;
    if (firstFingerprint != null && firstFingerprint.imagePath.isNotEmpty) {
      final path = firstFingerprint.imagePath;
      if (path.startsWith('http')) {
        imageWidget = Image.network(
          path,
          fit: BoxFit.cover,
          errorBuilder: (_, __, ___) => const Icon(Icons.broken_image_outlined, size: 20, color: Colors.grey),
        );
      } else {
        imageWidget = Image.file(
          File(path),
          fit: BoxFit.cover,
          errorBuilder: (_, __, ___) => const Icon(Icons.fingerprint_rounded, size: 24, color: AppTheme.primaryColor),
        );
      }
    } else {
      imageWidget = const Icon(Icons.fingerprint_rounded, size: 24, color: AppTheme.primaryColor);
    }

    return Container(
      width: 48,
      height: 48,
      decoration: BoxDecoration(
        color: AppTheme.primaryColor.withOpacity(0.05),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: const Color(0xFFE0E0E0)),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(5),
        child: imageWidget,
      ),
    );
  }

  Widget _buildClarityProgressBar(double avgQuality) {
    final displayScore = avgQuality.toStringAsFixed(0);
    Color barColor;
    if (avgQuality >= 70) {
      barColor = AppTheme.successColor;
    } else if (avgQuality >= 50) {
      barColor = AppTheme.warningColor;
    } else {
      barColor = AppTheme.errorColor;
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Indeks Kejelasan',
              style: TextStyle(color: Colors.grey[600], fontSize: 10, fontWeight: FontWeight.bold),
            ),
            Text(
              '$displayScore%',
              style: TextStyle(color: barColor, fontSize: 10, fontWeight: FontWeight.bold),
            ),
          ],
        ),
        const SizedBox(height: 4),
        ClipRRect(
          borderRadius: BorderRadius.circular(2),
          child: LinearProgressIndicator(
            value: avgQuality / 100,
            minHeight: 4,
            backgroundColor: const Color(0xFFF0F0F0),
            valueColor: AlwaysStoppedAnimation<Color>(barColor),
          ),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final scanProvider = context.read<ScanProvider>();
    final isReview = widget.mode == _CardMode.review;
    final avgQuality = _calculateAverageQuality(widget.session);

    return BouncingWidget(
      onTap: () => _navigate(context, scanProvider),
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
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                children: [
                  _buildBiometricThumbnail(widget.session),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          widget.session.participantName.isNotEmpty
                              ? widget.session.participantName
                              : 'Sesi #${widget.session.id}',
                          style: const TextStyle(
                              fontWeight: FontWeight.bold, fontSize: 15, color: AppTheme.primaryColor),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Umur: ${widget.session.participantAge} th  ·  ${widget.session.completedCount}/10 Jari',
                          style: TextStyle(color: Colors.grey[600], fontSize: 12),
                        ),
                      ],
                    ),
                  ),
                  if (_isLoading)
                    const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  else if (!isReview)
                    BouncingWidget(
                      onTap: () => _quickGenerateReport(context, scanProvider),
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                        decoration: BoxDecoration(
                          color: AppTheme.primaryColor,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(Icons.picture_as_pdf_rounded, size: 14, color: Colors.white),
                            SizedBox(width: 4),
                            Text(
                              'Buat Laporan',
                              style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold),
                            ),
                          ],
                        ),
                      ),
                    )
                  else
                    const Icon(Icons.chevron_right_rounded, color: Colors.grey),
                ],
              ),
              if (widget.session.fingerprints.isNotEmpty) ...[
                const SizedBox(height: 12),
                _buildClarityProgressBar(avgQuality),
              ],
            ],
          ),
        ),
      ),
    );
  }

  // Navigate to the review screen (loads session first)
  Future<void> _navigate(
      BuildContext context, ScanProvider scanProvider) async {
    if (_isLoading) return;
    setState(() => _isLoading = true);
    final success = await scanProvider.loadSession(widget.session.id);
    if (mounted) {
      setState(() => _isLoading = false);
      if (success) {
        context.push('/scan/review/${widget.session.id}');
      }
    }
  }

  // Quick "Buat Laporan" directly from the card (approved sessions)
  Future<void> _quickGenerateReport(
      BuildContext context, ScanProvider scanProvider) async {
    if (_isLoading) return;
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Buat Laporan?'),
        content: Text(
          'Buat laporan analisis sidik jari untuk peserta '
          '"${widget.session.participantName.isNotEmpty ? widget.session.participantName : "Sesi #${widget.session.id}"}"?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Batal'),
          ),
          ElevatedButton.icon(
            onPressed: () => Navigator.pop(ctx, true),
            icon: const Icon(Icons.picture_as_pdf_rounded, size: 16),
            label: const Text('Buat Laporan'),
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

    if (confirmed == true && mounted) {
      setState(() => _isLoading = true);
      final success =
          await scanProvider.generateReport(widget.session.id);
      if (mounted) {
        setState(() => _isLoading = false);
        if (success) {
          AppToast.showSuccess(context, 'Laporan berhasil dibuat!');
          context.push('/report/${widget.session.id}');
        } else {
          AppToast.showError(context, scanProvider.error ?? 'Gagal membuat laporan');
        }
      }
    }
  }
}

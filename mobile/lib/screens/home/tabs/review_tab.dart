import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../../../providers/scan_provider.dart';
import '../../../models/scan_model.dart';

class ReviewTab extends StatelessWidget {
  const ReviewTab({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final scanProvider = context.watch<ScanProvider>();
    final reviewQueue = scanProvider.reviewQueue;       // waiting_for_review
    final approvedQueue = scanProvider.approvedQueue;   // approved → ready for report

    final isEmpty = reviewQueue.isEmpty && approvedQueue.isEmpty;

    return RefreshIndicator(
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
              padding: const EdgeInsets.all(16),
              children: [
                // ── Section 1: Perlu Ditinjau ──────────────────────────────
                if (reviewQueue.isNotEmpty) ...[
                  _SectionHeader(
                    icon: Icons.rate_review_outlined,
                    label: 'Perlu Ditinjau',
                    count: reviewQueue.length,
                    color: Colors.amber,
                  ),
                  const SizedBox(height: 8),
                  ...reviewQueue.map(
                    (session) => _ReviewCard(
                      session: session,
                      mode: _CardMode.review,
                    ),
                  ),
                  const SizedBox(height: 20),
                ],

                // ── Section 2: Siap Buat Laporan ───────────────────────────
                if (approvedQueue.isNotEmpty) ...[
                  _SectionHeader(
                    icon: Icons.picture_as_pdf_outlined,
                    label: 'Siap Buat Laporan',
                    count: approvedQueue.length,
                    color: const Color(0xFF6C63FF),
                  ),
                  const SizedBox(height: 8),
                  ...approvedQueue.map(
                    (session) => _ReviewCard(
                      session: session,
                      mode: _CardMode.generateReport,
                    ),
                  ),
                ],
              ],
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
        Icon(icon, color: color, size: 20),
        const SizedBox(width: 8),
        Text(
          label,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 15,
            color: color,
          ),
        ),
        const SizedBox(width: 8),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
          decoration: BoxDecoration(
            color: color.withOpacity(0.12),
            borderRadius: BorderRadius.circular(20),
          ),
          child: Text(
            '$count',
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.bold,
              fontSize: 12,
            ),
          ),
        ),
      ],
    );
  }
}

// ── Card mode ─────────────────────────────────────────────────────────────────

enum _CardMode { review, generateReport }

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

  @override
  Widget build(BuildContext context) {
    final scanProvider = context.read<ScanProvider>();
    final isReview = widget.mode == _CardMode.review;

    final Color accentColor = isReview ? Colors.amber : const Color(0xFF6C63FF);
    final IconData leadingIcon =
        isReview ? Icons.assignment_ind : Icons.check_circle_outline;

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      elevation: 2,
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => _navigate(context, scanProvider),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          child: Row(
            children: [
              // Avatar
              CircleAvatar(
                backgroundColor: accentColor.withOpacity(0.15),
                child: Icon(leadingIcon, color: accentColor),
              ),
              const SizedBox(width: 12),

              // Info
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      widget.session.participantName.isNotEmpty
                          ? widget.session.participantName
                          : 'Sesi #${widget.session.id}',
                      style: const TextStyle(
                          fontWeight: FontWeight.bold, fontSize: 15),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Umur: ${widget.session.participantAge} th  ·  '
                      '${widget.session.completedCount}/10 Jari',
                      style:
                          TextStyle(color: Colors.grey[600], fontSize: 12),
                    ),
                    const SizedBox(height: 6),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: accentColor.withOpacity(0.12),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        isReview ? 'Perlu Tinjauan' : 'Siap Buat Laporan',
                        style: TextStyle(
                          color: accentColor,
                          fontSize: 11,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              // Action area
              if (_isLoading)
                const SizedBox(
                  width: 24,
                  height: 24,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              else if (!isReview)
                // Quick generate report button for approved sessions
                ElevatedButton.icon(
                  onPressed: () => _quickGenerateReport(context, scanProvider),
                  icon: const Icon(Icons.picture_as_pdf_rounded, size: 14),
                  label: const Text('Buat\nLaporan',
                      textAlign: TextAlign.center,
                      style: TextStyle(fontSize: 11)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF6C63FF),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(
                        horizontal: 10, vertical: 8),
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8)),
                    minimumSize: Size.zero,
                    tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  ),
                )
              else
                const Icon(Icons.chevron_right, color: Colors.grey),
            ],
          ),
        ),
      ),
    );
  }

  // Navigate to the review screen (loads session first)
  Future<void> _navigate(
      BuildContext context, ScanProvider scanProvider) async {
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
              backgroundColor: const Color(0xFF6C63FF),
              foregroundColor: Colors.white,
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
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Laporan berhasil dibuat!'),
              backgroundColor: Colors.green,
            ),
          );
          context.push('/report/${widget.session.id}');
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content:
                  Text(scanProvider.error ?? 'Gagal membuat laporan'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    }
  }
}

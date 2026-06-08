import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../../config/app_config.dart';
import '../../providers/auth_provider.dart';
import '../../providers/scan_provider.dart';
import '../../models/scan_model.dart';
import '../../widgets/fingerprint_image.dart';

class ReviewCapturedFingersScreen extends StatefulWidget {
  final int sessionId;

  const ReviewCapturedFingersScreen({
    Key? key,
    required this.sessionId,
  }) : super(key: key);

  @override
  State<ReviewCapturedFingersScreen> createState() => _ReviewCapturedFingersScreenState();
}

class _ReviewCapturedFingersScreenState extends State<ReviewCapturedFingersScreen> {
  bool _isActionLoading = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ScanProvider>().loadSession(widget.sessionId);
    });
  }

  Map<String, dynamic> _getStatusMetadata(String status) {
    switch (status) {
      case 'draft':
        return {'label': 'Draf', 'color': Colors.grey};
      case 'registered':
        return {'label': 'Terdaftar', 'color': Colors.blue};
      case 'scanning':
        return {'label': 'Memindai', 'color': Colors.orange};
      case 'scan_completed':
        return {'label': 'Pindai Selesai', 'color': Colors.teal};
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
        return {'label': 'Laporan Selesai', 'color': Colors.green};
      default:
        return {'label': status, 'color': Colors.grey};
    }
  }

  double _calculateAverageQuality(ScanSession session) {
    if (session.fingerprints.isEmpty) return 0;
    final total = session.fingerprints
        .fold<double>(0, (sum, fp) => sum + (fp.qualityScore ?? 0));
    return total / session.fingerprints.length;
  }

  // _buildFingerprintImage is replaced by the FingerprintImage widget
  // which fetches from the authenticated backend proxy endpoint.

  void _showFingerDetail(BuildContext context, Fingerprint fp, String label) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(label),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: Container(
                color: Colors.grey[100],
                width: double.infinity,
                height: 200,
                child: FingerprintImage(
                  fingerprintId: fp.id,
                  height: 200,
                  fit: BoxFit.cover,
                ),
              ),
            ),
            const SizedBox(height: 16),
            Text(
              'Kualitas: ${fp.qualityScore?.toStringAsFixed(1) ?? "N/A"}%',
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            const SizedBox(height: 8),
            Text('Tanggal Pengambilan: ${_formatDate(fp.createdAt)}'),
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

  String _formatDate(DateTime dateTime) {
    return '${dateTime.day}/${dateTime.month}/${dateTime.year} ${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
  }

  Future<void> _handleSubmitForReview(BuildContext context, ScanProvider scanProvider) async {
    setState(() {
      _isActionLoading = true;
    });

    final success = await scanProvider.submitForReview(widget.sessionId);
    if (mounted) {
      setState(() {
        _isActionLoading = false;
      });
      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Sesi pemindaian berhasil dikirim untuk ditinjau'),
            backgroundColor: Colors.green,
          ),
        );
        context.go('/home');
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(scanProvider.error ?? 'Gagal mengirim untuk ditinjau'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _handleApprove(BuildContext context, ScanProvider scanProvider) async {
    setState(() => _isActionLoading = true);

    final success = await scanProvider.approveSession(widget.sessionId);
    if (mounted) {
      setState(() => _isActionLoading = false);
      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Sesi disetujui. Admin dapat membuat laporan sekarang.'),
            backgroundColor: Colors.green,
          ),
        );
        context.go('/home');
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(scanProvider.error ?? 'Gagal menyetujui sesi pemindaian'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _handleGenerateReport(BuildContext context, ScanProvider scanProvider) async {
    setState(() => _isActionLoading = true);

    final success = await scanProvider.generateReport(widget.sessionId);
    if (mounted) {
      setState(() => _isActionLoading = false);
      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Laporan berhasil dibuat!'),
            backgroundColor: Colors.green,
          ),
        );
        context.go('/report/${widget.sessionId}');
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(scanProvider.error ?? 'Gagal membuat laporan'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _showRejectDialog(BuildContext context, ScanProvider scanProvider) async {
    final reasonController = TextEditingController();
    final formKey = GlobalKey<FormState>();

    await showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Tolak Sesi Pemindaian'),
          content: Form(
            key: formKey,
            child: TextFormField(
              controller: reasonController,
              decoration: const InputDecoration(
                labelText: 'Alasan Penolakan',
                border: OutlineInputBorder(),
                hintText: 'Masukkan alasan menolak sesi ini...',
              ),
              maxLines: 3,
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'Alasan penolakan wajib diisi';
                }
                return null;
              },
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Batal'),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.red,
                foregroundColor: Colors.white,
              ),
              onPressed: () {
                if (!formKey.currentState!.validate()) return;
                Navigator.pop(context, reasonController.text.trim());
              },
              child: const Text('Tolak Sesi'),
            ),
          ],
        );
      },
    ).then((reason) async {
      if (reason != null && reason.isNotEmpty) {
        setState(() {
          _isActionLoading = true;
        });
        final success = await scanProvider.rejectSession(widget.sessionId, reason);
        if (mounted) {
          setState(() {
            _isActionLoading = false;
          });
          if (success) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Sesi pemindaian telah ditolak'),
                backgroundColor: Colors.orange,
              ),
            );
            context.go('/home');
          } else {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(scanProvider.error ?? 'Gagal menolak sesi pemindaian'),
                backgroundColor: Colors.red,
              ),
            );
          }
        }
      }
    });
  }

  Future<void> _showRescanDialog(BuildContext context, ScanSession session, ScanProvider scanProvider) async {
    final selectedFingers = <String>[];
    final reasonController = TextEditingController();
    final formKey = GlobalKey<FormState>();

    await showDialog(
      context: context,
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setStateDialog) {
            return AlertDialog(
              title: const Text('Minta Scan Ulang'),
              content: SizedBox(
                width: double.maxFinite,
                child: Form(
                  key: formKey,
                  child: SingleChildScrollView(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Pilih jari yang perlu dipindai ulang:',
                          style: TextStyle(fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 8),
                        ...session.fingerprints.map((fp) {
                          final label = AppConstants.fingerLabels[fp.fingerPosition] ?? fp.fingerPosition;
                          final isSelected = selectedFingers.contains(fp.fingerPosition);
                          return CheckboxListTile(
                            title: Text(label),
                            subtitle: Text('Kualitas: ${fp.qualityScore?.toStringAsFixed(1) ?? "N/A"}%'),
                            value: isSelected,
                            dense: true,
                            controlAffinity: ListTileControlAffinity.leading,
                            onChanged: (val) {
                              setStateDialog(() {
                                if (val == true) {
                                  selectedFingers.add(fp.fingerPosition);
                                } else {
                                  selectedFingers.remove(fp.fingerPosition);
                                }
                              });
                            },
                          );
                        }).toList(),
                        const SizedBox(height: 16),
                        TextFormField(
                          controller: reasonController,
                          decoration: const InputDecoration(
                            labelText: 'Alasan / Instruksi Scan Ulang',
                            border: OutlineInputBorder(),
                            hintText: 'Contoh: Gambar buram pada kelingking kanan.',
                          ),
                          maxLines: 3,
                          validator: (value) {
                            if (value == null || value.trim().isEmpty) {
                              return 'Alasan wajib diisi';
                            }
                            return null;
                          },
                        ),
                      ],
                    ),
                  ),
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text('Batal'),
                ),
                ElevatedButton(
                  onPressed: () {
                    if (!formKey.currentState!.validate()) return;
                    if (selectedFingers.isEmpty) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Pilih minimal satu jari untuk dipindai ulang'),
                          backgroundColor: Colors.orange,
                        ),
                      );
                      return;
                    }
                    Navigator.pop(context, {
                      'fingers': selectedFingers,
                      'reason': reasonController.text.trim(),
                    });
                  },
                  child: const Text('Kirim Permintaan'),
                ),
              ],
            );
          },
        );
      },
    ).then((result) async {
      if (result != null) {
        setState(() {
          _isActionLoading = true;
        });
        final fingers = result['fingers'] as List<String>;
        final reason = result['reason'] as String;
        final success = await scanProvider.requestRescan(widget.sessionId, fingers, reason);
        if (mounted) {
          setState(() {
            _isActionLoading = false;
          });
          if (success) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Permintaan scan ulang berhasil dikirim'),
                backgroundColor: Colors.green,
              ),
            );
            context.go('/home');
          } else {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(scanProvider.error ?? 'Gagal meminta scan ulang'),
                backgroundColor: Colors.red,
              ),
            );
          }
        }
      }
    });
  }

  Widget _buildActionPanel(
    BuildContext context,
    ScanSession session,
    ScanProvider scanProvider,
    bool isAdmin,
  ) {
    const btnShape = RoundedRectangleBorder(
      borderRadius: BorderRadius.all(Radius.circular(12)),
    );
    const btnPadding = EdgeInsets.symmetric(vertical: 14);

    if (isAdmin) {
      if (session.status == 'waiting_for_review') {
        return Row(
          children: [
            Expanded(
              child: OutlinedButton.icon(
                onPressed: () => _showRejectDialog(context, scanProvider),
                icon: const Icon(Icons.close_rounded, color: Colors.redAccent),
                label: const Text('Tolak', style: TextStyle(color: Colors.redAccent)),
                style: OutlinedButton.styleFrom(
                  side: const BorderSide(color: Colors.redAccent),
                  padding: btnPadding,
                  shape: btnShape,
                ),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: OutlinedButton.icon(
                onPressed: () => _showRescanDialog(context, session, scanProvider),
                icon: const Icon(Icons.replay_rounded, color: Colors.orange),
                label: const Text('Scan Ulang', style: TextStyle(color: Colors.orange)),
                style: OutlinedButton.styleFrom(
                  side: const BorderSide(color: Colors.orange),
                  padding: btnPadding,
                  shape: btnShape,
                ),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: ElevatedButton.icon(
                onPressed: () => _handleApprove(context, scanProvider),
                icon: const Icon(Icons.check_rounded),
                label: const Text('Setujui'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                  foregroundColor: Colors.white,
                  padding: btnPadding,
                  shape: btnShape,
                ),
              ),
            ),
          ],
        );
      } else if (session.status == 'approved') {
        // Admin: session approved — show generate report button
        return Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              margin: const EdgeInsets.only(bottom: 12),
              decoration: BoxDecoration(
                color: Colors.green.withOpacity(0.1),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: Colors.green.withOpacity(0.3)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.check_circle_outline, color: Colors.green, size: 18),
                  const SizedBox(width: 8),
                  const Expanded(
                    child: Text(
                      'Sesi telah disetujui. Klik di bawah untuk membuat laporan analisis.',
                      style: TextStyle(color: Colors.green, fontSize: 12),
                    ),
                  ),
                ],
              ),
            ),
            ElevatedButton.icon(
              onPressed: () => _handleGenerateReport(context, scanProvider),
              icon: const Icon(Icons.picture_as_pdf_rounded),
              label: const Text('Buat Laporan'),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF6C63FF),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: const RoundedRectangleBorder(
                  borderRadius: BorderRadius.all(Radius.circular(12)),
                ),
                textStyle: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
              ),
            ),
          ],
        );
      } else if (session.status == 'generating_report' ||
                 session.status == 'report_generated') {
        return ElevatedButton.icon(
          onPressed: () => context.go('/report/${session.id}'),
          icon: const Icon(Icons.description),
          label: const Text('Lihat Laporan'),
          style: ElevatedButton.styleFrom(
            padding: const EdgeInsets.symmetric(vertical: 16),
            shape: const RoundedRectangleBorder(
              borderRadius: BorderRadius.all(Radius.circular(12)),
            ),
          ),
        );
      } else {
        return ElevatedButton.icon(
          onPressed: () => context.go('/home'),
          icon: const Icon(Icons.home),
          label: const Text('Kembali ke Beranda'),
          style: ElevatedButton.styleFrom(
            padding: const EdgeInsets.symmetric(vertical: 16),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        );
      }
    } else {
      if (session.status == 'scanning' ||
          session.status == 'scan_completed' ||
          session.status == 'need_rescan') {
        
        final canSubmit = session.completedCount == 10;
        
        return Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (!canSubmit) ...[
              Padding(
                padding: const EdgeInsets.only(bottom: 8.0),
                child: Text(
                  'Harap selesaikan pemindaian 10 jari sebelum mengirim (${session.completedCount}/10).',
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: Colors.redAccent, fontSize: 12, fontWeight: FontWeight.w500),
                ),
              ),
            ],
            Row(
              children: [
                if (!canSubmit)
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () => context.go('/scan'),
                      icon: const Icon(Icons.fingerprint),
                      label: const Text('Lanjutkan Pemindaian'),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: const RoundedRectangleBorder(
                          borderRadius: BorderRadius.all(Radius.circular(12)),
                        ),
                      ),
                    ),
                  )
                else ...[
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () => context.go('/scan'),
                      icon: const Icon(Icons.edit_rounded),
                      label: const Text('Ubah Pindaian'),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: const RoundedRectangleBorder(
                          borderRadius: BorderRadius.all(Radius.circular(12)),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () => _handleSubmitForReview(context, scanProvider),
                      icon: const Icon(Icons.send_rounded),
                      label: const Text('Kirim untuk Ditinjau'),
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: const RoundedRectangleBorder(
                          borderRadius: BorderRadius.all(Radius.circular(12)),
                        ),
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ],
        );
      } else if (session.status == 'waiting_for_review') {
        return Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.hourglass_top_rounded, color: Colors.amber),
            const SizedBox(width: 8),
            const Text(
              'Menunggu Tinjauan Admin',
              style: TextStyle(
                color: Colors.amber,
                fontWeight: FontWeight.bold,
                fontSize: 16,
              ),
            ),
          ],
        );
      } else if (session.status == 'approved' ||
                 session.status == 'generating_report' ||
                 session.status == 'report_generated') {
        return SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: () => context.go('/report/${session.id}'),
            icon: const Icon(Icons.description_rounded),
            label: const Text('Lihat Laporan'),
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: const RoundedRectangleBorder(
                borderRadius: BorderRadius.all(Radius.circular(12)),
              ),
            ),
          ),
        );
      } else {
        return SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: () => context.go('/home'),
            icon: const Icon(Icons.home_rounded),
            label: const Text('Kembali ke Beranda'),
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: const RoundedRectangleBorder(
                borderRadius: BorderRadius.all(Radius.circular(12)),
              ),
            ),
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();
    final user = authProvider.user;
    final isAdmin = user?.role == 'admin';

    return Scaffold(
      appBar: AppBar(
        title: Text(isAdmin ? 'Tinjauan Sidik Jari (Admin)' : 'Review Sidik Jari'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go('/home'),
        ),
      ),
      body: Consumer<ScanProvider>(
        builder: (context, scanProvider, _) {
          final session = scanProvider.currentSession;
          
          if (scanProvider.isLoading && session == null) {
            return const Center(child: CircularProgressIndicator());
          }

          if (session == null) {
            return const Center(child: Text('Data sesi pemindaian tidak ditemukan'));
          }

          final statusMeta = _getStatusMetadata(session.status);
          final avgQuality = _calculateAverageQuality(session);

          return Stack(
            children: [
              SingleChildScrollView(
                padding: const EdgeInsets.fromLTRB(16, 16, 16, 100),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // Participant Info Card
                    Card(
                      elevation: 2,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Expanded(
                                  child: Text(
                                    session.participantName.isNotEmpty
                                        ? session.participantName
                                        : 'Sesi #${session.id}',
                                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                                          fontWeight: FontWeight.bold,
                                        ),
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                  decoration: BoxDecoration(
                                    color: (statusMeta['color'] as Color).withOpacity(0.12),
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  child: Text(
                                    statusMeta['label'],
                                    style: TextStyle(
                                      color: statusMeta['color'] as Color,
                                      fontWeight: FontWeight.bold,
                                      fontSize: 12,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            const Divider(height: 24),
                            Row(
                              children: [
                                const Icon(Icons.calendar_today_outlined, size: 16, color: Colors.grey),
                                const SizedBox(width: 8),
                                Text('Umur: ${session.participantAge} tahun'),
                                const SizedBox(width: 24),
                                const Icon(Icons.wc_outlined, size: 16, color: Colors.grey),
                                const SizedBox(width: 8),
                                Text(
                                  'Jenis Kelamin: ${session.participantGender == 'male' ? 'Laki-laki' : session.participantGender == 'female' ? 'Perempuan' : '-'}',
                                ),
                              ],
                            ),
                            if (session.notes != null && session.notes!.isNotEmpty) ...[
                              const SizedBox(height: 12),
                              Row(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const Icon(Icons.notes_outlined, size: 16, color: Colors.grey),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      'Catatan: ${session.notes}',
                                      style: TextStyle(color: Colors.grey[700]),
                                    ),
                                  ),
                                ],
                              ),
                            ],
                            if ((session.status == 'need_rescan' || session.status == 'rejected') &&
                                session.rejectionReason != null &&
                                session.rejectionReason!.isNotEmpty) ...[
                              const SizedBox(height: 16),
                              Container(
                                width: double.infinity,
                                padding: const EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  color: Colors.red[50],
                                  borderRadius: BorderRadius.circular(8),
                                  border: Border.all(color: Colors.red[200]!),
                                ),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      session.status == 'need_rescan'
                                          ? 'Alasan Permintaan Scan Ulang:'
                                          : 'Alasan Penolakan Sesi:',
                                      style: TextStyle(
                                        color: Colors.red[800],
                                        fontWeight: FontWeight.bold,
                                        fontSize: 13,
                                      ),
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      session.rejectionReason!,
                                      style: TextStyle(
                                        color: Colors.red[900],
                                        fontSize: 13,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Ringkasan Kualitas Sidik Jari — Gradient Card
                    Container(
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [Color(0xFF1E1E2E), Color(0xFF252540)],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                        borderRadius: BorderRadius.circular(16),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.3),
                            blurRadius: 10,
                            offset: const Offset(0, 4),
                          ),
                        ],
                      ),
                      padding: const EdgeInsets.all(20),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(Icons.analytics_outlined, color: Colors.blue[300], size: 18),
                              const SizedBox(width: 8),
                              Text(
                                'Ringkasan Kualitas Sidik Jari',
                                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                  fontWeight: FontWeight.bold,
                                  color: Colors.white,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 20),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceAround,
                            children: [
                              Column(
                                children: [
                                  const Text(
                                    'Total Jari Pindai',
                                    style: TextStyle(color: Colors.grey, fontSize: 12),
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    '${session.completedCount}/10',
                                    style: const TextStyle(
                                      fontSize: 32,
                                      fontWeight: FontWeight.bold,
                                      color: Color(0xFF00D4FF),
                                    ),
                                  ),
                                ],
                              ),
                              Container(width: 1, height: 60, color: Colors.white12),
                              Column(
                                children: [
                                  const Text(
                                    'Rata-rata Kualitas',
                                    style: TextStyle(color: Colors.grey, fontSize: 12),
                                  ),
                                  const SizedBox(height: 8),
                                  SizedBox(
                                    width: 72,
                                    height: 72,
                                    child: Stack(
                                      alignment: Alignment.center,
                                      children: [
                                        CircularProgressIndicator(
                                          value: (avgQuality / 100).clamp(0.0, 1.0),
                                          strokeWidth: 6,
                                          backgroundColor: Colors.white12,
                                          valueColor: AlwaysStoppedAnimation<Color>(
                                            avgQuality >= 70
                                                ? Colors.greenAccent
                                                : avgQuality >= 50
                                                    ? Colors.orange
                                                    : Colors.redAccent,
                                          ),
                                        ),
                                        Text(
                                          '${avgQuality.toStringAsFixed(1)}%',
                                          style: TextStyle(
                                            fontWeight: FontWeight.bold,
                                            fontSize: 13,
                                            color: avgQuality >= 70
                                                ? Colors.greenAccent
                                                : avgQuality >= 50
                                                    ? Colors.orange
                                                    : Colors.redAccent,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 24),

                    // Detail Sidik Jari List
                    Text(
                      'Detail Sidik Jari',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    const SizedBox(height: 12),
                    ListView.builder(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      itemCount: session.fingerprints.length,
                      itemBuilder: (context, index) {
                        final fp = session.fingerprints[index];
                        final label = AppConstants.fingerLabels[fp.fingerPosition] ?? fp.fingerPosition;
                        final Color qualityColor = fp.isGoodQuality
                            ? Colors.greenAccent
                            : fp.isFairQuality
                                ? Colors.orange
                                : Colors.redAccent;

                        return Container(
                          margin: const EdgeInsets.only(bottom: 10),
                          decoration: BoxDecoration(
                            color: Theme.of(context).cardColor,
                            borderRadius: BorderRadius.circular(12),
                            border: Border(
                              left: BorderSide(
                                color: qualityColor,
                                width: 4,
                              ),
                            ),
                            boxShadow: [
                              BoxShadow(
                                color: qualityColor.withOpacity(0.08),
                                blurRadius: 6,
                                offset: const Offset(0, 2),
                              ),
                            ],
                          ),
                          child: ListTile(
                            contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
                            leading: CircleAvatar(
                              backgroundColor: qualityColor.withOpacity(0.15),
                              child: Text(
                                '${index + 1}',
                                style: TextStyle(
                                  color: qualityColor,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                            title: Text(
                              label,
                              style: const TextStyle(fontWeight: FontWeight.w600),
                            ),
                            subtitle: Text(
                              'Kualitas: ${fp.qualityScore?.toStringAsFixed(1) ?? "N/A"}%',
                              style: TextStyle(color: qualityColor, fontSize: 12),
                            ),
                            trailing: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(
                                  fp.isGoodQuality
                                      ? Icons.check_circle_rounded
                                      : fp.isFairQuality
                                          ? Icons.warning_amber_rounded
                                          : Icons.error_outline_rounded,
                                  color: qualityColor,
                                  size: 22,
                                ),
                                const SizedBox(width: 4),
                                Icon(Icons.chevron_right_rounded, color: Colors.grey[600], size: 20),
                              ],
                            ),
                            onTap: () => _showFingerDetail(context, fp, label),
                          ),
                        );
                      },
                    ),
                  ],
                ),
              ),

              // Bottom Action Button / Panel
              Positioned(
                bottom: 0,
                left: 0,
                right: 0,
                child: Container(
                  padding: const EdgeInsets.fromLTRB(16, 14, 16, 20),
                  decoration: BoxDecoration(
                    color: const Color(0xFF1A1A2E),
                    borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.5),
                        blurRadius: 16,
                        offset: const Offset(0, -4),
                      ),
                    ],
                  ),
                  child: SafeArea(
                    top: false,
                    child: _buildActionPanel(context, session, scanProvider, isAdmin),
                  ),
                ),
              ),

              // Full Screen Loading Indicator overlay
              if (_isActionLoading)
                Container(
                  color: Colors.black.withOpacity(0.5),
                  child: const Center(
                    child: Card(
                      child: Padding(
                        padding: EdgeInsets.all(24),
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            CircularProgressIndicator(),
                            SizedBox(height: 16),
                            Text(
                              'Memproses...',
                              style: TextStyle(fontWeight: FontWeight.bold),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
            ],
          );
        },
      ),
    );
  }
}

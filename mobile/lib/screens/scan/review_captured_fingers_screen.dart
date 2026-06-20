import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../../config/app_config.dart';
import '../../providers/auth_provider.dart';
import '../../providers/scan_provider.dart';
import '../../models/scan_model.dart';
import '../../widgets/fingerprint_image.dart';
import '../../widgets/app_toast.dart';
import '../../theme/app_theme.dart';

class ReviewCapturedFingersScreen extends StatefulWidget {
  final int sessionId;

  const ReviewCapturedFingersScreen({
    super.key,
    required this.sessionId,
  });

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
    String selectedPattern = fp.patternType ?? 'unknown';
    final ridgeController = TextEditingController(text: fp.ridgeCount?.toString() ?? '0');
    bool isSaving = false;

    showDialog(
      context: context,
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setState) {
            return AlertDialog(
              title: Text(label),
              content: SingleChildScrollView(
                child: Column(
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
                    const Divider(height: 24),
                    const Text(
                      'Hasil Analisis Jari',
                      style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                    ),
                    const SizedBox(height: 12),
                    DropdownButtonFormField<String>(
                      initialValue: selectedPattern,
                      decoration: const InputDecoration(
                        labelText: 'Tipe Pola Jari',
                        border: OutlineInputBorder(),
                        contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                      ),
                      items: const [
                        DropdownMenuItem(value: 'loop', child: Text('Loop (Sangkutan)')),
                        DropdownMenuItem(value: 'whorl', child: Text('Whorl (Pusaran)')),
                        DropdownMenuItem(value: 'arch', child: Text('Arch (Busur)')),
                        DropdownMenuItem(value: 'tented_arch', child: Text('Tented Arch (Tenda)')),
                        DropdownMenuItem(value: 'composite', child: Text('Composite (Campuran)')),
                        DropdownMenuItem(value: 'unknown', child: Text('Tidak Diketahui')),
                      ],
                      onChanged: isSaving
                          ? null
                          : (val) {
                              if (val != null) {
                                setState(() {
                                  selectedPattern = val;
                                });
                              }
                            },
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: ridgeController,
                      keyboardType: TextInputType.number,
                      enabled: !isSaving,
                      decoration: const InputDecoration(
                        labelText: 'Jumlah Garis (Ridge Count)',
                        border: OutlineInputBorder(),
                        contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                      ),
                    ),
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: isSaving ? null : () => Navigator.pop(context),
                  child: const Text('Batal'),
                ),
                ElevatedButton(
                  onPressed: isSaving
                      ? null
                      : () async {
                          final count = int.tryParse(ridgeController.text) ?? 0;
                          setState(() {
                            isSaving = true;
                          });
                          final scanProvider = context.read<ScanProvider>();
                          final success = await scanProvider.updateFingerprintFeatures(
                            fingerprintId: fp.id,
                            patternType: selectedPattern,
                            ridgeCount: count,
                          );
                          if (context.mounted) {
                            setState(() {
                              isSaving = false;
                            });
                            if (success) {
                              AppToast.showSuccess(context, 'Hasil analisis jari berhasil disimpan');
                              Navigator.pop(context);
                            } else {
                              AppToast.showError(context, scanProvider.error ?? 'Gagal menyimpan hasil analisis');
                            }
                          }
                        },
                  child: isSaving
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Simpan'),
                ),
              ],
            );
          },
        );
      },
    );
  }

  String _formatDate(DateTime dateTime) {
    return '${dateTime.day}/${dateTime.month}/${dateTime.year} ${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
  }

  Future<void> _handleSubmitForReview(BuildContext context, ScanProvider scanProvider) async {
    if (_isActionLoading) return;
    setState(() {
      _isActionLoading = true;
    });

    final success = await scanProvider.submitForReview(widget.sessionId);
    if (context.mounted) {
      setState(() {
        _isActionLoading = false;
      });
      if (success) {
        AppToast.showSuccess(context, 'Sesi pemindaian berhasil dikirim untuk ditinjau');
        context.go('/home');
      } else {
        AppToast.showError(context, scanProvider.error ?? 'Gagal mengirim untuk ditinjau');
      }
    }
  }

  Future<void> _handleApprove(BuildContext context, ScanProvider scanProvider) async {
    if (_isActionLoading) return;
    setState(() => _isActionLoading = true);

    final success = await scanProvider.approveSession(widget.sessionId);
    if (context.mounted) {
      setState(() => _isActionLoading = false);
      if (success) {
        AppToast.showSuccess(context, 'Sesi disetujui. Admin dapat membuat laporan sekarang.');
        context.go('/home');
      } else {
        AppToast.showError(context, scanProvider.error ?? 'Gagal menyetujui sesi pemindaian');
      }
    }
  }

  Future<void> _handleGenerateReport(BuildContext context, ScanProvider scanProvider) async {
    if (_isActionLoading) return;
    setState(() => _isActionLoading = true);

    final success = await scanProvider.generateReport(widget.sessionId);
    if (context.mounted) {
      setState(() => _isActionLoading = false);
      if (success) {
        AppToast.showSuccess(context, 'Laporan berhasil dibuat!');
        context.go('/report/${widget.sessionId}');
      } else {
        AppToast.showError(context, scanProvider.error ?? 'Gagal membuat laporan');
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
                backgroundColor: AppTheme.errorColor,
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
        if (context.mounted) {
          setState(() {
            _isActionLoading = false;
          });
          if (success) {
            AppToast.showWarning(context, 'Sesi pemindaian telah ditolak');
            context.go('/home');
          } else {
            AppToast.showError(context, scanProvider.error ?? 'Gagal menolak sesi pemindaian');
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
                        }),
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
                      AppToast.showWarning(context, 'Pilih minimal satu jari untuk dipindai ulang');
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
        if (context.mounted) {
          setState(() {
            _isActionLoading = false;
          });
          if (success) {
            AppToast.showSuccess(context, 'Permintaan scan ulang berhasil dikirim');
            context.go('/home');
          } else {
            AppToast.showError(context, scanProvider.error ?? 'Gagal meminta scan ulang');
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
      borderRadius: BorderRadius.all(Radius.circular(8)),
    );
    const btnPadding = EdgeInsets.symmetric(vertical: 14);

    if (isAdmin) {
      if (session.status == 'waiting_for_review') {
        return Row(
          children: [
            Expanded(
              child: OutlinedButton.icon(
                onPressed: _isActionLoading ? null : () => _showRejectDialog(context, scanProvider),
                icon: const Icon(Icons.close_rounded, color: AppTheme.errorColor),
                label: const Text('Tolak', style: TextStyle(color: AppTheme.errorColor)),
                style: OutlinedButton.styleFrom(
                  side: const BorderSide(color: AppTheme.errorColor),
                  padding: btnPadding,
                  shape: btnShape,
                ),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: OutlinedButton.icon(
                onPressed: _isActionLoading ? null : () => _showRescanDialog(context, session, scanProvider),
                icon: const Icon(Icons.replay_rounded, color: AppTheme.warningColor),
                label: const Text('Scan Ulang', style: TextStyle(color: AppTheme.warningColor)),
                style: OutlinedButton.styleFrom(
                  side: const BorderSide(color: AppTheme.warningColor),
                  padding: btnPadding,
                  shape: btnShape,
                ),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: ElevatedButton.icon(
                onPressed: _isActionLoading ? null : () => _handleApprove(context, scanProvider),
                icon: _isActionLoading
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                      )
                    : const Icon(Icons.check_rounded),
                label: const Text('Setujui'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.successColor,
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
                color: AppTheme.successColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: AppTheme.successColor.withOpacity(0.3)),
              ),
              child: const Row(
                children: [
                  Icon(Icons.check_circle_outline, color: AppTheme.successColor, size: 18),
                  SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Sesi telah disetujui. Klik di bawah untuk membuat laporan analisis.',
                      style: TextStyle(color: AppTheme.successColor, fontSize: 12),
                    ),
                  ),
                ],
              ),
            ),
            ElevatedButton.icon(
              onPressed: _isActionLoading ? null : () => _handleGenerateReport(context, scanProvider),
              icon: _isActionLoading
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                    )
                  : const Icon(Icons.picture_as_pdf_rounded),
              label: Text(_isActionLoading ? 'Membuat Laporan...' : 'Buat Laporan'),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.primaryColor,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: const RoundedRectangleBorder(
                  borderRadius: BorderRadius.all(Radius.circular(8)),
                ),
                textStyle: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
              ),
            ),
          ],
        );
      } else if (session.status == 'generating_report' ||
                 session.status == 'report_generated') {
        return ElevatedButton.icon(
          onPressed: _isActionLoading ? null : () => context.go('/report/${session.id}'),
          icon: const Icon(Icons.description),
          label: const Text('Lihat Laporan'),
          style: ElevatedButton.styleFrom(
            padding: const EdgeInsets.symmetric(vertical: 16),
            shape: const RoundedRectangleBorder(
              borderRadius: BorderRadius.all(Radius.circular(8)),
            ),
          ),
        );
      } else {
        return ElevatedButton.icon(
          onPressed: _isActionLoading ? null : () => context.go('/home'),
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
                  style: const TextStyle(color: AppTheme.errorColor, fontSize: 12, fontWeight: FontWeight.w500),
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
                          borderRadius: BorderRadius.all(Radius.circular(8)),
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
                          borderRadius: BorderRadius.all(Radius.circular(8)),
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
                          borderRadius: BorderRadius.all(Radius.circular(8)),
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
        return const Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.hourglass_top_rounded, color: AppTheme.warningColor),
            SizedBox(width: 8),
            Text(
              'Menunggu Tinjauan Admin',
              style: TextStyle(
                color: AppTheme.warningColor,
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
                borderRadius: BorderRadius.all(Radius.circular(8)),
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
                borderRadius: BorderRadius.all(Radius.circular(8)),
              ),
            ),
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final authProvider = context.watch<AuthProvider>();
    final user = authProvider.user;
    final isAdmin = user?.role == 'admin';

    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFFFAFAFA),
        elevation: 0,
        scrolledUnderElevation: 0,
        title: Text(
          isAdmin ? 'Tinjauan Sidik Jari' : 'Review Sidik Jari',
          style: theme.textTheme.titleLarge?.copyWith(
            color: AppTheme.primaryColor,
            fontWeight: FontWeight.bold,
          ),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, color: AppTheme.primaryColor, size: 20),
          onPressed: () => context.go('/home'),
        ),
      ),
      body: SafeArea(
        child: Consumer<ScanProvider>(
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
                      Container(
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
                                            color: AppTheme.primaryColor,
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
                                    color: AppTheme.errorColor.withOpacity(0.05),
                                    borderRadius: BorderRadius.circular(8),
                                    border: Border.all(color: AppTheme.errorColor.withOpacity(0.2)),
                                  ),
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        session.status == 'need_rescan'
                                            ? 'Alasan Permintaan Scan Ulang:'
                                            : 'Alasan Penolakan Sesi:',
                                        style: const TextStyle(
                                          color: AppTheme.errorColor,
                                          fontWeight: FontWeight.bold,
                                          fontSize: 13,
                                        ),
                                      ),
                                      const SizedBox(height: 4),
                                      Text(
                                        session.rejectionReason!,
                                        style: TextStyle(
                                          color: AppTheme.errorColor.withOpacity(0.9),
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

                      // Ringkasan Kualitas Sidik Jari — Card
                      Container(
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
                        padding: const EdgeInsets.all(20),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                const Icon(Icons.analytics_outlined, color: AppTheme.primaryColor, size: 18),
                                const SizedBox(width: 8),
                                Text(
                                  'Ringkasan Kualitas Sidik Jari',
                                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                    fontWeight: FontWeight.bold,
                                    color: AppTheme.primaryColor,
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
                                    Text(
                                      'Total Jari Pindai',
                                      style: TextStyle(color: Colors.grey[600], fontSize: 12),
                                    ),
                                    const SizedBox(height: 8),
                                    Text(
                                      '${session.completedCount}/10',
                                      style: const TextStyle(
                                        fontSize: 32,
                                        fontWeight: FontWeight.bold,
                                        color: AppTheme.primaryColor,
                                      ),
                                    ),
                                  ],
                                ),
                                Container(width: 1, height: 60, color: const Color(0xFFE0E0E0)),
                                Column(
                                  children: [
                                    Text(
                                      'Rata-rata Kualitas',
                                      style: TextStyle(color: Colors.grey[600], fontSize: 12),
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
                                            backgroundColor: const Color(0xFFF1F5F9),
                                            valueColor: AlwaysStoppedAnimation<Color>(
                                              avgQuality >= 70
                                                  ? AppTheme.successColor
                                                  : avgQuality >= 50
                                                      ? AppTheme.warningColor
                                                      : AppTheme.errorColor,
                                            ),
                                          ),
                                          Text(
                                            '${avgQuality.toStringAsFixed(1)}%',
                                            style: TextStyle(
                                              fontWeight: FontWeight.bold,
                                              fontSize: 13,
                                              color: avgQuality >= 70
                                                  ? AppTheme.successColor
                                                  : avgQuality >= 50
                                                      ? AppTheme.warningColor
                                                      : AppTheme.errorColor,
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
                            ? AppTheme.successColor
                            : fp.isFairQuality
                                ? AppTheme.warningColor
                                : AppTheme.errorColor;

                        return Container(
                          margin: const EdgeInsets.only(bottom: 10),
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
                          child: ClipRRect(
                            borderRadius: BorderRadius.circular(8),
                            child: Container(
                              decoration: BoxDecoration(
                                border: Border(
                                  left: BorderSide(
                                    color: qualityColor,
                                    width: 4,
                                  ),
                                ),
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
                            ),
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
                  decoration: const BoxDecoration(
                    color: Colors.white,
                    border: Border(
                      top: BorderSide(color: Color(0xFFE0E0E0), width: 1),
                    ),
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
    ),
  );
}
}

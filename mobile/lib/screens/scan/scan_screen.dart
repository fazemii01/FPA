import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../../config/app_config.dart';
import '../../providers/scan_provider.dart';
import '../../models/scan_model.dart';
import '../../widgets/fingerprint_image.dart';
import '../../theme/app_theme.dart';

class ScanScreen extends StatefulWidget {
  const ScanScreen({super.key});

  @override
  State<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends State<ScanScreen> {
  static const List<String> leftFingers = [
    'left_thumb',
    'left_index',
    'left_middle',
    'left_ring',
    'left_pinky',
  ];

  static const List<String> rightFingers = [
    'right_thumb',
    'right_index',
    'right_middle',
    'right_ring',
    'right_pinky',
  ];

  void _showFingerDetail(BuildContext context, int sessionId, Fingerprint fp, String label) {
    final theme = Theme.of(context);
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.white,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        title: Text(
          label,
          style: theme.textTheme.titleLarge?.copyWith(
            color: AppTheme.primaryColor,
            fontWeight: FontWeight.bold,
          ),
        ),
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
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Kualitas Indeks:',
                  style: TextStyle(color: Colors.grey[600], fontSize: 13, fontWeight: FontWeight.bold),
                ),
                Text(
                  '${fp.qualityScore?.toStringAsFixed(1) ?? "N/A"}%',
                  style: TextStyle(
                    color: (fp.qualityScore ?? 0) >= 70
                        ? AppTheme.successColor
                        : (fp.qualityScore ?? 0) >= 50
                            ? AppTheme.warningColor
                            : AppTheme.errorColor,
                    fontWeight: FontWeight.bold,
                    fontSize: 15,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              'Tanggal Pengambilan:\n${_formatDate(fp.createdAt)}',
              style: TextStyle(color: Colors.grey[500], fontSize: 12),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Tutup', style: TextStyle(color: Colors.grey)),
          ),
          ElevatedButton.icon(
            onPressed: () {
              Navigator.pop(context); // Close the dialog
              context.go('/scan/capture/$sessionId/${fp.fingerPosition}');
            },
            icon: const Icon(Icons.refresh_rounded, size: 18),
            label: const Text('Scan Ulang'),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.primaryColor,
              foregroundColor: Colors.white,
              elevation: 0,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
          ),
        ],
      ),
    );
  }

  String _formatDate(DateTime dateTime) {
    return '${dateTime.day}/${dateTime.month}/${dateTime.year} ${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
  }

  String? _getNextFingerToScan(ScanSession session) {
    for (final pos in AppConstants.fingerPositions) {
      final isScanned = session.fingerprints.any((fp) => fp.fingerPosition == pos);
      if (!isScanned) return pos;
    }
    return null;
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      backgroundColor: const Color(0xFFFAFAFA),
      appBar: AppBar(
        backgroundColor: const Color(0xFFFAFAFA),
        elevation: 0,
        scrolledUnderElevation: 0,
        title: Text(
          'Sesi Pemindaian',
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
      body: Consumer<ScanProvider>(
        builder: (context, scanProvider, _) {
          final session = scanProvider.currentSession;
          
          if (session == null) {
            return const Center(
              child: Text('Tidak ada sesi aktif'),
            );
          }

          return SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Progress Card
                _buildProgressCard(context, session, theme),
                const SizedBox(height: 32),

                // Tangan Kanan Section
                _buildHandSectionHeader(context, 'Tangan Kanan', Colors.blue),
                const SizedBox(height: 16),
                _buildHandGrid(context, session, rightFingers),
                const SizedBox(height: 32),

                // Tangan Kiri Section
                _buildHandSectionHeader(context, 'Tangan Kiri', Colors.teal),
                const SizedBox(height: 16),
                _buildHandGrid(context, session, leftFingers),
                
                if (session.isComplete) ...[
                  const SizedBox(height: 40),
                  ElevatedButton.icon(
                    onPressed: () => context.go('/scan/review/${session.id}'),
                    icon: const Icon(Icons.rate_review_rounded, size: 20),
                    label: const Text('Tinjau Hasil Pemindaian'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.primaryColor,
                      foregroundColor: Colors.white,
                      elevation: 0,
                      shadowColor: Colors.transparent,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                      textStyle: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                    ),
                  ),
                ],
                const SizedBox(height: 16),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildProgressCard(BuildContext context, ScanSession session, ThemeData theme) {
    final completed = session.completedCount;
    final progress = completed / 10.0;
    
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
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'KEMAJUAN PEMINDAIAN',
                style: TextStyle(
                  color: Colors.grey[500],
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.5,
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: AppTheme.primaryColor.withOpacity(0.05),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  '$completed / 10 Selesai',
                  style: const TextStyle(
                    color: AppTheme.primaryColor,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: progress,
              minHeight: 6,
              backgroundColor: const Color(0xFFF0F0F0),
              valueColor: const AlwaysStoppedAnimation<Color>(AppTheme.primaryColor),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHandSectionHeader(BuildContext context, String label, Color color) {
    return Row(
      children: [
        Container(
          width: 4,
          height: 18,
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(2),
          ),
        ),
        const SizedBox(width: 8),
        Text(
          label,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 15,
            color: AppTheme.primaryColor,
            letterSpacing: 0.5,
          ),
        ),
      ],
    );
  }

  Widget _buildHandGrid(BuildContext context, ScanSession session, List<String> positions) {
    final thumbPosition = positions[0]; 
    final otherPositions = positions.sublist(1); 
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _buildFingerItemCard(context, session, thumbPosition, isHero: true),
        const SizedBox(height: 12),
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
            childAspectRatio: 1.5,
          ),
          itemCount: otherPositions.length,
          itemBuilder: (context, index) {
            return _buildFingerItemCard(context, session, otherPositions[index], isHero: false);
          },
        ),
      ],
    );
  }

  Widget _buildFingerItemCard(BuildContext context, ScanSession session, String position, {required bool isHero}) {
    final label = AppConstants.fingerLabels[position]!;
    
    Fingerprint? fingerprint;
    for (final fp in session.fingerprints) {
      if (fp.fingerPosition == position) {
        fingerprint = fp;
        break;
      }
    }
    final isScanned = fingerprint != null;
    final nextToScan = _getNextFingerToScan(session);
    final isActive = position == nextToScan;

    Color cardColor;
    Color borderColor;
    Color iconColor;
    Color textColor;
    IconData iconData;

    if (isScanned) {
      cardColor = AppTheme.successColor.withOpacity(0.06);
      borderColor = AppTheme.successColor.withOpacity(0.3);
      iconColor = AppTheme.successColor;
      textColor = AppTheme.primaryColor;
      iconData = Icons.check_circle_rounded;
    } else if (isActive) {
      cardColor = AppTheme.primaryColor.withOpacity(0.04);
      borderColor = AppTheme.primaryColor;
      iconColor = AppTheme.primaryColor;
      textColor = AppTheme.primaryColor;
      iconData = Icons.fingerprint_rounded;
    } else {
      cardColor = Colors.white;
      borderColor = const Color(0xFFE0E0E0);
      iconColor = Colors.grey[400]!;
      textColor = Colors.grey[600]!;
      iconData = Icons.fingerprint_rounded;
    }

    return Container(
      height: isHero ? 80 : null,
      decoration: BoxDecoration(
        color: cardColor,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: borderColor, width: isActive ? 1.5 : 1),
        boxShadow: isActive ? [
          BoxShadow(
            color: AppTheme.primaryColor.withOpacity(0.05),
            blurRadius: 8,
            offset: const Offset(0, 4),
          )
        ] : null,
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(8),
        onTap: () {
          if (fingerprint != null) {
            _showFingerDetail(context, session.id, fingerprint, label);
          } else {
            context.go('/scan/capture/${session.id}/$position');
          }
        },
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          child: Row(
            mainAxisAlignment: isHero ? MainAxisAlignment.start : MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: iconColor.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: Icon(iconData, color: iconColor, size: 24),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      label,
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: isHero ? 14 : 12,
                        color: textColor,
                      ),
                    ),
                    if (isScanned && fingerprint.qualityScore != null)
                      Padding(
                        padding: const EdgeInsets.only(top: 2),
                        child: Text(
                          'Kualitas: ${fingerprint.qualityScore!.toStringAsFixed(0)}%',
                          style: TextStyle(
                            color: Colors.grey[600],
                            fontSize: 10,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      )
                    else if (isActive)
                      const Padding(
                        padding: EdgeInsets.only(top: 2),
                        child: Text(
                          'Siap pindai',
                          style: TextStyle(
                            color: AppTheme.primaryColor,
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                  ],
                ),
              ),
              if (isScanned)
                const Icon(Icons.arrow_forward_ios_rounded, color: Colors.grey, size: 14)
              else if (isActive)
                const Icon(Icons.arrow_forward_ios_rounded, color: AppTheme.primaryColor, size: 14),
            ],
          ),
        ),
      ),
    );
  }
}

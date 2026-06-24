import 'package:flutter/material.dart';

/// Guide size in logical pixels — must match the guideSize constant in
/// _cropToGuide() in both camera screens.
const double kGuideSize = 200.0;

class CircularGuideOverlay extends StatelessWidget {
  final String fingerLabel;
  final double qualityScore;
  final double overlayOpacity;

  const CircularGuideOverlay({
    super.key,
    required this.fingerLabel,
    required this.qualityScore,
    this.overlayOpacity = 0.05,
  });

  @override
  Widget build(BuildContext context) {
    final screenSize = MediaQuery.of(context).size;

    return SizedBox.expand(
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Dimmed background with transparent square hole cut out
          ColoredBox(
            color: Colors.black.withValues(alpha: overlayOpacity),
            child: const SizedBox.expand(),
          ),
          ClipPath(
            clipper: _SquareHoleClipper(),
            child: Container(color: Colors.transparent),
          ),

          // Square guide border + ghost fingerprint icon
          Container(
            width: kGuideSize,
            height: kGuideSize,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: _getQualityColor(),
                width: 2.5,
              ),
            ),
            child: Center(
              child: Icon(
                Icons.fingerprint,
                size: 90,
                color: _getQualityColor().withValues(alpha: 0.22),
              ),
            ),
          ),

          // Corner tick marks painted on top
          CustomPaint(
            painter: _CornerTickPainter(
              color: _getQualityColor(),
              guideSize: kGuideSize,
              armLen: 18.0,
              thick: 2.5,
            ),
            child: const SizedBox(width: kGuideSize + 40, height: kGuideSize + 40),
          ),

          // Instruction text below the box
          Positioned(
            top: screenSize.height / 2 + kGuideSize / 2 + 12,
            left: 24,
            right: 24,
            child: Column(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                  decoration: BoxDecoration(
                    color: Colors.black.withValues(alpha: 0.65),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    _getQualityText(),
                    style: TextStyle(
                      color: _getQualityColor(),
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ),
                if (qualityScore == 0) ...[
                  const SizedBox(height: 6),
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: Colors.black.withValues(alpha: 0.55),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: const Text(
                      '📍 Arahkan UJUNG jari (bukan ruas / sendi)',
                      style:
                          TextStyle(color: Colors.white70, fontSize: 11),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  Color _getQualityColor() {
    if (qualityScore >= 70) return Colors.greenAccent;
    if (qualityScore >= 50) return Colors.orange;
    if (qualityScore > 0) return Colors.redAccent;
    return Colors.white;
  }

  String _getQualityText() {
    if (qualityScore >= 70) return '✅ Kualitas Baik';
    if (qualityScore >= 50) return '⚠️ Kualitas Cukup';
    if (qualityScore > 0) return '❌ Kualitas Rendah';
    return 'Posisikan bantalan UJUNG jari di sini';
  }
}

class _SquareHoleClipper extends CustomClipper<Path> {
  @override
  Path getClip(Size size) {
    final path = Path()..addRect(Rect.fromLTWH(0, 0, size.width, size.height));
    final hole = Path()
      ..addRRect(
        RRect.fromRectAndRadius(
          Rect.fromCenter(
            center: Offset(size.width / 2, size.height / 2),
            width: kGuideSize,
            height: kGuideSize,
          ),
          const Radius.circular(16),
        ),
      );
    return Path.combine(PathOperation.difference, path, hole);
  }

  @override
  bool shouldReclip(_SquareHoleClipper oldClipper) => false;
}

class _CornerTickPainter extends CustomPainter {
  final Color color;
  final double guideSize;
  final double armLen;
  final double thick;

  const _CornerTickPainter({
    required this.color,
    required this.guideSize,
    required this.armLen,
    required this.thick,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = thick
      ..strokeCap = StrokeCap.round
      ..style = PaintingStyle.stroke;

    final cx = size.width / 2;
    final cy = size.height / 2;
    final half = guideSize / 2;
    const r = 16.0; // matches border radius

    // Top-left corner
    canvas.drawLine(
        Offset(cx - half + r, cy - half), Offset(cx - half + r + armLen, cy - half), paint);
    canvas.drawLine(
        Offset(cx - half, cy - half + r), Offset(cx - half, cy - half + r + armLen), paint);
    // Top-right corner
    canvas.drawLine(
        Offset(cx + half - r, cy - half), Offset(cx + half - r - armLen, cy - half), paint);
    canvas.drawLine(
        Offset(cx + half, cy - half + r), Offset(cx + half, cy - half + r + armLen), paint);
    // Bottom-left corner
    canvas.drawLine(
        Offset(cx - half + r, cy + half), Offset(cx - half + r + armLen, cy + half), paint);
    canvas.drawLine(
        Offset(cx - half, cy + half - r), Offset(cx - half, cy + half - r - armLen), paint);
    // Bottom-right corner
    canvas.drawLine(
        Offset(cx + half - r, cy + half), Offset(cx + half - r - armLen, cy + half), paint);
    canvas.drawLine(
        Offset(cx + half, cy + half - r), Offset(cx + half, cy + half - r - armLen), paint);
  }

  @override
  bool shouldRepaint(_CornerTickPainter oldDelegate) =>
      oldDelegate.color != color;
}

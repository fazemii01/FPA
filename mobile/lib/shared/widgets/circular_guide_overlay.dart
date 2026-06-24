import 'dart:ui';
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
          CustomPaint(
            painter: _DashedRoundedRectPainter(
              color: _getQualityColor(),
              strokeWidth: 2.5,
              dashWidth: 10.0,
              dashSpace: 6.0,
              radius: 16.0,
            ),
            child: SizedBox(
              width: kGuideSize,
              height: kGuideSize,
              child: Center(
                child: Icon(
                  Icons.fingerprint,
                  size: 90,
                  color: _getQualityColor().withValues(alpha: 0.22),
                ),
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

class _DashedRoundedRectPainter extends CustomPainter {
  final Color color;
  final double strokeWidth;
  final double dashWidth;
  final double dashSpace;
  final double radius;

  _DashedRoundedRectPainter({
    required this.color,
    this.strokeWidth = 2.5,
    this.dashWidth = 8.0,
    this.dashSpace = 4.0,
    this.radius = 16.0,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = strokeWidth
      ..style = PaintingStyle.stroke;

    final rect = Rect.fromLTWH(0, 0, size.width, size.height);
    final rrect = RRect.fromRectAndRadius(rect, Radius.circular(radius));
    final path = Path()..addRRect(rrect);
    
    final dashPath = _createDashedPath(path, dashWidth, dashSpace);
    canvas.drawPath(dashPath, paint);
  }

  Path _createDashedPath(Path source, double dashWidth, double dashSpace) {
    final Path dest = Path();
    for (final PathMetric metric in source.computeMetrics()) {
      double distance = 0.0;
      bool draw = true;
      while (distance < metric.length) {
        final double len = draw ? dashWidth : dashSpace;
        if (distance + len > metric.length) {
          dest.addPath(
            metric.extractPath(distance, metric.length),
            Offset.zero,
          );
          break;
        }
        if (draw) {
          dest.addPath(
            metric.extractPath(distance, distance + len),
            Offset.zero,
          );
        }
        distance += len;
        draw = !draw;
      }
    }
    return dest;
  }

  @override
  bool shouldRepaint(_DashedRoundedRectPainter oldDelegate) =>
      oldDelegate.color != color;
}

import 'package:flutter/material.dart';

class CircularGuideOverlay extends StatelessWidget {
  final String fingerLabel;
  final double qualityScore;

  const CircularGuideOverlay({
    Key? key,
    required this.fingerLabel,
    required this.qualityScore,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return SizedBox.expand(
      child: Stack(
        alignment: Alignment.center,
        children: [
          ColoredBox(
            color: Colors.black.withValues(alpha: 0.28),
            child: const SizedBox.expand(),
          ),
          ClipPath(
            clipper: _OvalHoleClipper(),
            child: Container(
              color: Colors.transparent,
            ),
          ),
          Container(
            width: 160,
            height: 220,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(110),
              border: Border.all(
                color: _getQualityColor(),
                width: 2.5,
              ),
            ),
            child: Center(
              child: Icon(
                Icons.fingerprint,
                size: 64,
                color: _getQualityColor().withValues(alpha: 0.35),
              ),
            ),
          ),
          Positioned(
            top: MediaQuery.of(context).size.height * 0.5 + 140,
            child: Container(
              padding: const EdgeInsets.symmetric(
                horizontal: 14,
                vertical: 6,
              ),
              decoration: BoxDecoration(
                color: Colors.black.withValues(alpha: 0.6),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Text(
                _getQualityText(),
                style: TextStyle(
                  color: _getQualityColor(),
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Color _getQualityColor() {
    if (qualityScore >= 70) return Colors.green;
    if (qualityScore >= 50) return Colors.orange;
    if (qualityScore > 0) return Colors.red;
    return Colors.white;
  }

  String _getQualityText() {
    if (qualityScore >= 70) return 'Kualitas Baik';
    if (qualityScore >= 50) return 'Kualitas Cukup';
    if (qualityScore > 0) return 'Kualitas Rendah';
    return 'Posisikan jari di dalam bingkai';
  }
}

class _OvalHoleClipper extends CustomClipper<Path> {
  @override
  Path getClip(Size size) {
    final path = Path()..addRect(Rect.fromLTWH(0, 0, size.width, size.height));
    final hole = Path()
      ..addRRect(
        RRect.fromRectAndRadius(
          Rect.fromCenter(
            center: Offset(size.width / 2, size.height / 2),
            width: 160,
            height: 220,
          ),
          const Radius.circular(110),
        ),
      );
    return Path.combine(PathOperation.difference, path, hole);
  }

  @override
  bool shouldReclip(_OvalHoleClipper oldClipper) => false;
}

import 'package:flutter/material.dart';

class QualityIndicator extends StatelessWidget {
  final double qualityScore;
  final bool showLabel;

  const QualityIndicator({
    Key? key,
    required this.qualityScore,
    this.showLabel = true,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: _getQualityColor().withValues(alpha: 0.2),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: _getQualityColor(),
          width: 2,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            _getQualityIcon(),
            color: _getQualityColor(),
            size: 20,
          ),
          if (showLabel) ...[
            const SizedBox(width: 8),
            Text(
              _getQualityText(),
              style: TextStyle(
                color: _getQualityColor(),
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Color _getQualityColor() {
    if (qualityScore >= 70) return Colors.green;
    if (qualityScore >= 50) return Colors.orange;
    return Colors.red;
  }

  IconData _getQualityIcon() {
    if (qualityScore >= 70) return Icons.check_circle;
    if (qualityScore >= 50) return Icons.warning;
    return Icons.error;
  }

  String _getQualityText() {
    if (qualityScore >= 70) return 'Baik';
    if (qualityScore >= 50) return 'Cukup';
    return 'Rendah';
  }
}

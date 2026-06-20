import 'package:flutter/material.dart';

class FingerProgressWidget extends StatelessWidget {
  final int completedCount;
  final int totalCount;

  const FingerProgressWidget({
    super.key,
    required this.completedCount,
    required this.totalCount,
  });

  @override
  Widget build(BuildContext context) {
    final progress = completedCount / totalCount;
    
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Progres Pemindaian',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                Text(
                  '$completedCount/$totalCount',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: LinearProgressIndicator(
                value: progress,
                minHeight: 10,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

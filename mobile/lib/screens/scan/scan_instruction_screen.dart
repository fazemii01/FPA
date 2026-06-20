import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class ScanInstructionScreen extends StatelessWidget {
  const ScanInstructionScreen({super.key});

  static const _leftHand = [
    ('left_thumb',  'Ibu Jari'),
    ('left_index',  'Telunjuk'),
    ('left_middle', 'Jari Tengah'),
    ('left_ring',   'Jari Manis'),
    ('left_pinky',  'Kelingking'),
  ];

  static const _rightHand = [
    ('right_thumb',  'Ibu Jari'),
    ('right_index',  'Telunjuk'),
    ('right_middle', 'Jari Tengah'),
    ('right_ring',   'Jari Manis'),
    ('right_pinky',  'Kelingking'),
  ];



  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Petunjuk Pemindaian'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(16, 20, 16, 32),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // ── Page title ───────────────────────────────────────────────
            Text(
              'Panduan Pemindaian\nSidik Jari',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    height: 1.3,
                  ),
            ),
            const SizedBox(height: 24),

            // ── Instruction cards ────────────────────────────────────────
            const _InstructionCard(
              step: '01',
              icon: Icons.clean_hands_outlined,
              title: 'Persiapan',
              description:
                  'Pastikan tangan bersih dan kering sebelum memulai pemindaian.',
              color: Color(0xFF4FC3F7),
            ),
            const SizedBox(height: 12),
            const _InstructionCard(
              step: '02',
              icon: Icons.touch_app_outlined,
              title: 'Posisi Jari',
              description:
                  'Letakkan jari di tengah lingkaran panduan dengan tekanan ringan dan stabil.',
              color: Color(0xFF81C784),
            ),
            const SizedBox(height: 12),
            const _InstructionCard(
              step: '03',
              icon: Icons.wb_sunny_outlined,
              title: 'Pencahayaan',
              description:
                  'Pastikan area memiliki pencahayaan yang cukup untuk hasil terbaik.',
              color: Color(0xFFFFB74D),
            ),
            const SizedBox(height: 12),
            const _InstructionCard(
              step: '04',
              icon: Icons.verified_outlined,
              title: 'Kualitas',
              description:
                  'Tunggu hingga indikator kualitas menunjukkan "Baik" sebelum menangkap.',
              color: Color(0xFFCE93D8),
            ),

            const SizedBox(height: 32),

            // ── Scanning order ───────────────────────────────────────────
            Row(
              children: [
                const Icon(Icons.reorder_rounded, size: 20),
                const SizedBox(width: 8),
                Text(
                  'Urutan Pemindaian',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const Spacer(),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: Theme.of(context).primaryColor.withOpacity(0.12),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    '10 jari',
                    style: TextStyle(
                      color: Theme.of(context).primaryColor,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // Hand columns card
            Container(
              decoration: BoxDecoration(
                color: Theme.of(context).cardColor,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: Theme.of(context).dividerColor.withOpacity(0.5),
                ),
              ),
              child: Column(
                children: [
                  // Header row
                  Container(
                    decoration: BoxDecoration(
                      color: Theme.of(context).primaryColor.withOpacity(0.08),
                      borderRadius: const BorderRadius.vertical(
                          top: Radius.circular(16)),
                    ),
                    padding: const EdgeInsets.symmetric(
                        vertical: 10, horizontal: 16),
                    child: Row(
                      children: [
                        Expanded(
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              const Icon(Icons.back_hand_outlined, size: 16),
                              const SizedBox(width: 6),
                              Text(
                                'Tangan Kanan  (1–5)',
                                style: Theme.of(context)
                                    .textTheme
                                    .labelMedium
                                    ?.copyWith(fontWeight: FontWeight.bold),
                              ),
                            ],
                          ),
                        ),
                        Container(
                            width: 1,
                            height: 18,
                            color: Theme.of(context).dividerColor),
                        Expanded(
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              const Icon(Icons.back_hand_outlined,
                                  size: 16,
                                  textDirection: TextDirection.rtl),
                              const SizedBox(width: 6),
                              Text(
                                'Tangan Kiri  (6–10)',
                                style: Theme.of(context)
                                    .textTheme
                                    .labelMedium
                                    ?.copyWith(fontWeight: FontWeight.bold),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),

                  // Finger rows
                  ...List.generate(5, (i) {
                    final rightFinger = _rightHand[i];
                    final leftFinger = _leftHand[i];
                    final rightNo = i + 1;
                    final leftNo = i + 6;
                    final isLast = i == 4;

                    return Container(
                      decoration: BoxDecoration(
                        border: isLast
                            ? null
                            : Border(
                                bottom: BorderSide(
                                  color: Theme.of(context)
                                      .dividerColor
                                      .withOpacity(0.4),
                                ),
                              ),
                      ),
                      child: IntrinsicHeight(
                        child: Row(
                          children: [
                            // Right hand finger
                            Expanded(
                              child: _FingerRow(
                                number: rightNo,
                                label: rightFinger.$2,
                                color: const Color(0xFF4FC3F7),
                              ),
                            ),
                            // Vertical divider
                            VerticalDivider(
                              width: 1,
                              thickness: 1,
                              color: Theme.of(context)
                                  .dividerColor
                                  .withOpacity(0.4),
                            ),
                            // Left hand finger
                            Expanded(
                              child: _FingerRow(
                                number: leftNo,
                                label: leftFinger.$2,
                                color: const Color(0xFFCE93D8),
                              ),
                            ),
                          ],
                        ),
                      ),
                    );
                  }),
                ],
              ),
            ),

            const SizedBox(height: 32),

            // ── CTA Button ───────────────────────────────────────────────
            FilledButton.icon(
              onPressed: () => context.go('/scan'),
              icon: const Icon(Icons.fingerprint_rounded),
              label: const Text('Mulai Pemindaian'),
              style: FilledButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                textStyle: const TextStyle(
                    fontSize: 16, fontWeight: FontWeight.bold),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ── Instruction step card ──────────────────────────────────────────────────

class _InstructionCard extends StatelessWidget {
  const _InstructionCard({
    required this.step,
    required this.icon,
    required this.title,
    required this.description,
    required this.color,
  });

  final String step;
  final IconData icon;
  final String title;
  final String description;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: Theme.of(context).dividerColor.withOpacity(0.4),
        ),
      ),
      padding: const EdgeInsets.all(14),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Step icon circle
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: color.withOpacity(0.15),
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: color, size: 22),
          ),
          const SizedBox(width: 14),
          // Content
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      step,
                      style: TextStyle(
                        color: color,
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                        letterSpacing: 1.2,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      title,
                      style: Theme.of(context)
                          .textTheme
                          .titleSmall
                          ?.copyWith(fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  description,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Theme.of(context)
                            .textTheme
                            .bodySmall
                            ?.color
                            ?.withOpacity(0.75),
                        height: 1.5,
                      ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// ── Finger row inside the two-column table ─────────────────────────────────

class _FingerRow extends StatelessWidget {
  const _FingerRow({
    required this.number,
    required this.label,
    required this.color,
  });

  final int number;
  final String label;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 14),
      child: Row(
        children: [
          // Number badge
          Container(
            width: 26,
            height: 26,
            decoration: BoxDecoration(
              color: color.withOpacity(0.15),
              shape: BoxShape.circle,
            ),
            alignment: Alignment.center,
            child: Text(
              '$number',
              style: TextStyle(
                color: color,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              label,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w500,
                  ),
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }
}

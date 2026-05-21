import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class ScanInstructionScreen extends StatelessWidget {
  const ScanInstructionScreen({Key? key}) : super(key: key);

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
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'Panduan Pemindaian Sidik Jari',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 24),
            _buildInstructionCard(
              context,
              icon: Icons.info,
              title: 'Persiapan',
              description: 'Pastikan tangan Anda bersih dan kering sebelum memulai pemindaian.',
            ),
            const SizedBox(height: 16),
            _buildInstructionCard(
              context,
              icon: Icons.touch_app,
              title: 'Posisi Jari',
              description: 'Letakkan jari Anda di tengah lingkaran panduan dengan tekanan ringan.',
            ),
            const SizedBox(height: 16),
            _buildInstructionCard(
              context,
              icon: Icons.camera_alt,
              title: 'Pencahayaan',
              description: 'Pastikan area memiliki pencahayaan yang cukup untuk hasil terbaik.',
            ),
            const SizedBox(height: 16),
            _buildInstructionCard(
              context,
              icon: Icons.check_circle,
              title: 'Kualitas',
              description: 'Tunggu hingga indikator kualitas menunjukkan status "Baik" sebelum menangkap.',
            ),
            const SizedBox(height: 32),
            Text(
              'Urutan Pemindaian',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            _buildFingerSequence(),
            const SizedBox(height: 32),
            ElevatedButton(
              onPressed: () => context.go('/scan'),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: const Text('Mulai Pemindaian'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInstructionCard(
    BuildContext context, {
    required IconData icon,
    required String title,
    required String description,
  }) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, size: 32, color: Theme.of(context).primaryColor),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    description,
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFingerSequence() {
    final fingers = [
      'Ibu Jari Kanan',
      'Telunjuk Kanan',
      'Jari Tengah Kanan',
      'Jari Manis Kanan',
      'Jari Kelingking Kanan',
      'Ibu Jari Kiri',
      'Telunjuk Kiri',
      'Jari Tengah Kiri',
      'Jari Manis Kiri',
      'Jari Kelingking Kiri',
    ];

    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: List.generate(
        fingers.length,
        (index) => Chip(
          label: Text('${index + 1}. ${fingers[index]}'),
          avatar: CircleAvatar(
            child: Text('${index + 1}'),
          ),
        ),
      ),
    );
  }
}

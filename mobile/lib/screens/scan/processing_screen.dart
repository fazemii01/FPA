import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../../providers/scan_provider.dart';

class ProcessingScreen extends StatefulWidget {
  final int sessionId;

  const ProcessingScreen({
    super.key,
    required this.sessionId,
  });

  @override
  State<ProcessingScreen> createState() => _ProcessingScreenState();
}

class _ProcessingScreenState extends State<ProcessingScreen> {
  bool _isProcessing = true;
  String _currentStep = 'Memproses sidik jari...';
  double _progress = 0.0;

  @override
  void initState() {
    super.initState();
    _startProcessing();
  }

  Future<void> _startProcessing() async {
    await _updateProgress('Menganalisis kualitas gambar...', 0.2);
    await Future.delayed(const Duration(seconds: 2));
    
    await _updateProgress('Mengekstrak fitur sidik jari...', 0.4);
    await Future.delayed(const Duration(seconds: 2));
    
    await _updateProgress('Menghitung skor kualitas...', 0.6);
    await Future.delayed(const Duration(seconds: 2));
    
    await _updateProgress('Membuat laporan...', 0.8);
    
    if (!mounted) return;
    
    final scanProvider = context.read<ScanProvider>();
    final success = await scanProvider.generateReport(widget.sessionId);
    
    if (success && mounted) {
      await _updateProgress('Selesai!', 1.0);
      await Future.delayed(const Duration(seconds: 1));
      
      if (mounted) {
        context.go('/report/summary/${widget.sessionId}');
      }
    } else {
      setState(() {
        _isProcessing = false;
        _currentStep = 'Gagal memproses laporan';
      });
    }
  }

  Future<void> _updateProgress(String step, double progress) async {
    if (!mounted) return;
    setState(() {
      _currentStep = step;
      _progress = progress;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Memproses'),
        automaticallyImplyLeading: false,
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              if (_isProcessing) ...[
                const CircularProgressIndicator(
                  strokeWidth: 6,
                ),
                const SizedBox(height: 48),
                Text(
                  _currentStep,
                  style: Theme.of(context).textTheme.titleMedium,
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 24),
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: LinearProgressIndicator(
                    value: _progress,
                    minHeight: 8,
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  '${(_progress * 100).toStringAsFixed(0)}%',
                  style: Theme.of(context).textTheme.bodyLarge,
                ),
              ] else ...[
                const Icon(
                  Icons.error_outline,
                  size: 64,
                  color: Colors.red,
                ),
                const SizedBox(height: 24),
                Text(
                  _currentStep,
                  style: Theme.of(context).textTheme.titleMedium,
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 24),
                ElevatedButton(
                  onPressed: () => context.go('/home'),
                  child: const Text('Kembali ke Beranda'),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

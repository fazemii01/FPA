import 'package:flutter/material.dart';
import '../../../theme/app_theme.dart';

class UserManualScreen extends StatelessWidget {
  const UserManualScreen({super.key});

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
          'Panduan Pengguna',
          style: theme.textTheme.titleLarge?.copyWith(
            color: AppTheme.primaryColor,
            fontWeight: FontWeight.bold,
          ),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, color: AppTheme.primaryColor, size: 20),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Title Header with Gradient Accent
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(16),
                gradient: const LinearGradient(
                  colors: [AppTheme.primaryColor, Color(0xFF3F51B5)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                boxShadow: [
                  BoxShadow(
                    color: AppTheme.primaryColor.withOpacity(0.15),
                    blurRadius: 12,
                    offset: const Offset(0, 6),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'PANDUAN VISUAL',
                    style: TextStyle(
                      color: Colors.white70,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 1.5,
                    ),
                  ),
                  const SizedBox(height: 4),
                  const Text(
                    'Tab Allia Finger',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    'Pelajari seluruh alur operasional aplikasi secara cepat melalui panduan gambar interaktif di bawah.',
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.87),
                      fontSize: 12,
                      height: 1.4,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Warning Box: Safety Device Lock
            _buildWarningBox(),
            const SizedBox(height: 32),

            Text(
              'LANGKAH-LANGKAH PENGGUNAAN',
              style: TextStyle(
                color: Colors.grey[500],
                fontSize: 10,
                fontWeight: FontWeight.bold,
                letterSpacing: 1.5,
              ),
            ),
            const SizedBox(height: 16),

            // STEP 1: LOGIN & AUTH
            _buildVisualStepSection(
              stepNumber: '1',
              title: 'Login & Otentikasi Pengguna',
              description: 'Masuk menggunakan kredensial lembaga Anda. Pastikan mencentang Syarat & Ketentuan sebelum masuk.',
              bullets: [
                'Masukkan Username & Password.',
                'Centang persetujuan lisensi.',
                'Ketuk tombol Continue yang melayang (floating).',
              ],
              mockup: _buildPhoneFrame(
                title: 'Tampilan Login',
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.fingerprint_rounded, size: 36, color: AppTheme.primaryColor),
                      const SizedBox(height: 16),
                      _buildMiniInputField('Email / Username'),
                      const SizedBox(height: 8),
                      _buildMiniInputField('Password'),
                      const SizedBox(height: 16),
                      _buildMiniButton('Continue', AppTheme.primaryColor),
                    ],
                  ),
                ),
              ),
            ),

            // STEP 2: DASHBOARD & CREDITS
            _buildVisualStepSection(
              stepNumber: '2',
              title: 'Dashboard & Kredit Lembaga',
              description: 'Layar beranda menampilkan sisa kredit aktif institusi dalam format kartu gradien premium dengan bayangan taktil.',
              bullets: [
                'Periksa saldo kredit aktif lembaga.',
                'Gunakan navigasi bawah untuk akses menu cepat.',
                'Klik tombol "+" di menu Sesi untuk memindai klien baru.',
              ],
              mockup: _buildPhoneFrame(
                title: 'Tampilan Dashboard',
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const SizedBox(height: 32),
                    // Welcome
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 10),
                      child: Row(
                        children: [
                          const CircleAvatar(
                            radius: 8,
                            backgroundColor: AppTheme.primaryColor,
                            child: Text('U', style: TextStyle(color: Colors.white, fontSize: 6)),
                          ),
                          const SizedBox(width: 4),
                          Text('Selamat Datang, Operator', style: TextStyle(fontSize: 8, fontWeight: FontWeight.bold, color: Colors.grey[800])),
                        ],
                      ),
                    ),
                    const SizedBox(height: 12),
                    // Premium Gradient Balance Card
                    Container(
                      margin: const EdgeInsets.symmetric(horizontal: 10),
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(10),
                        gradient: const LinearGradient(
                          colors: [Color(0xFF3F51B5), Color(0xFF2196F3), Color(0xFF00BCD4)],
                        ),
                      ),
                      child: const Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('KREDIT AKTIF LEMBAGA', style: TextStyle(color: Colors.white70, fontSize: 5, fontWeight: FontWeight.bold)),
                          SizedBox(height: 4),
                          Text('150 Kredit', style: TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.bold)),
                          SizedBox(height: 2),
                          Text('Lembaga Terdaftar', style: TextStyle(color: Colors.white70, fontSize: 6)),
                        ],
                      ),
                    ),
                    const SizedBox(height: 12),
                    // Statistics Bento Row
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 10),
                      child: Row(
                        children: [
                          Expanded(child: _buildMiniBentoCard(Icons.folder_shared_rounded, '12 Sesi', Colors.blue)),
                          const SizedBox(width: 6),
                          Expanded(child: _buildMiniBentoCard(Icons.hourglass_empty_rounded, '2 Review', Colors.amber)),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),

            // STEP 3: VIEWFINDER SCANNING
            _buildVisualStepSection(
              stepNumber: '3',
              title: 'Kamera & Viewfinder Dashed',
              description: 'Kotak panduan oval menggunakan garis putus-putus (dashed viewfinder) untuk visualisasi capture yang presisi.',
              bullets: [
                'Atur zoom slider ke 1.8x s.d 2.0x.',
                '💧 Ketuk Opacity untuk meredupkan/menerangkan overlay (0.05 s.d 0.45).',
                '⚡ Aktifkan senter/torch untuk guratan sidik jari lebih tajam.',
                'Sentuh layar pada area jari untuk autofocus manual.',
              ],
              mockup: _buildPhoneFrame(
                title: 'Tampilan Kamera',
                child: Stack(
                  children: [
                    Positioned.fill(
                      child: Container(color: Colors.grey[900]),
                    ),
                    // Dashed Box
                    Center(
                      child: Container(
                        width: 100,
                        height: 100,
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(color: Colors.greenAccent, style: BorderStyle.none),
                        ),
                        child: CustomPaint(
                          painter: _MockDashedPainter(),
                          child: const Center(
                            child: Icon(Icons.fingerprint, color: Colors.white24, size: 40),
                          ),
                        ),
                      ),
                    ),
                    // Right Button Column
                    Positioned(
                      top: 36,
                      right: 8,
                      child: Column(
                        children: [
                          _buildMiniIcon(Icons.flash_on, Colors.yellow),
                          const SizedBox(height: 8),
                          _buildMiniIcon(Icons.opacity, Colors.white),
                        ],
                      ),
                    ),
                    // Instructions
                    Align(
                      alignment: Alignment.bottomCenter,
                      child: Container(
                        margin: const EdgeInsets.only(bottom: 12, left: 10, right: 10),
                        padding: const EdgeInsets.all(6),
                        decoration: BoxDecoration(
                          color: Colors.black54,
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: const Text(
                          'Posisikan ujung jari Anda',
                          style: TextStyle(color: Colors.white, fontSize: 7),
                          textAlign: TextAlign.center,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),

            // STEP 4: INSTANT CROP EVALUATION
            _buildVisualStepSection(
              stepNumber: '4',
              title: 'Evaluasi Gambar Crop Instan',
              description: 'Operator wajib memeriksa kejelasan sidik jari sebelum diunggah ke server untuk meminimalkan penolakan.',
              bullets: [
                'Scan Ulang (ikon reload): membuang foto saat ini dan langsung membuka kamera.',
                'Gunakan (ikon centang): mengirim ke server pemrosesan citra.',
              ],
              mockup: _buildPhoneFrame(
                title: 'Tampilan Konfirmasi',
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Text(
                        'TINJAU KUALITAS GAMBAR',
                        style: TextStyle(fontSize: 7, fontWeight: FontWeight.bold, color: Colors.grey),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 12),
                      Container(
                        width: 90,
                        height: 90,
                        decoration: BoxDecoration(
                          color: Colors.grey[200],
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: Colors.grey.shade300),
                        ),
                        child: const Icon(Icons.fingerprint, size: 54, color: AppTheme.primaryColor),
                      ),
                      const SizedBox(height: 16),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Expanded(
                            child: _buildMiniActionButton(Icons.refresh_rounded, 'Ulang', Colors.grey[700]!),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: _buildMiniActionButton(Icons.check_rounded, 'Gunakan', AppTheme.primaryColor),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ),

            // STEP 5: REPORTS & FINGER DETAIL
            _buildVisualStepSection(
              stepNumber: '5',
              title: 'Laporan & Detail Sidik Jari',
              description: 'Setelah disetujui admin dan laporan terbit, operator tetap dapat meninjau detail sidik jari subjek secara offline.',
              bullets: [
                'Klik Lihat Detail Sidik Jari pada tab Riwayat.',
                'Tampilan Bottom Sheet menampilkan 10 jari terdaftar.',
                'Ketuk salah satu jari untuk dialog pratinjau diperbesar beserta metrik ridge & pola.',
              ],
              mockup: _buildPhoneFrame(
                title: 'Tampilan Laporan',
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  child: Column(
                    children: [
                      const SizedBox(height: 36),
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: Colors.green[50],
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Row(
                          children: [
                            Icon(Icons.check_circle, color: Colors.green, size: 16),
                            SizedBox(width: 8),
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text('Skor Kualitas: 92.5%', style: TextStyle(fontSize: 8, fontWeight: FontWeight.bold, color: Colors.green)),
                                Text('Kualitas Sangat Baik', style: TextStyle(fontSize: 6, color: Colors.grey)),
                              ],
                            ),
                          ],
                        ),
                      ),
                      const Spacer(),
                      _buildMiniButton('Unduh Laporan PDF', AppTheme.primaryColor),
                      const SizedBox(height: 8),
                      // Outlined button style mockup
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.symmetric(vertical: 8),
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(6),
                          border: Border.all(color: AppTheme.primaryColor),
                        ),
                        child: const Center(
                          child: Text(
                            'Lihat Detail Sidik Jari',
                            style: TextStyle(color: AppTheme.primaryColor, fontWeight: FontWeight.bold, fontSize: 8),
                          ),
                        ),
                      ),
                      const SizedBox(height: 24),
                    ],
                  ),
                ),
              ),
            ),

            const SizedBox(height: 16),

            // FAQ SECTION
            Text(
              'PERTANYAAN UMUM (FAQ)',
              style: TextStyle(
                color: Colors.grey[500],
                fontSize: 10,
                fontWeight: FontWeight.bold,
                letterSpacing: 1.5,
              ),
            ),
            const SizedBox(height: 16),
            _buildFAQSection(),
            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }

  Widget _buildWarningBox() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.red[50],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.red.shade100),
      ),
      child: const Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.warning_amber_rounded, color: Colors.redAccent, size: 22),
          SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Multi-Device Safety Lock',
                  style: TextStyle(
                    color: Colors.red,
                    fontSize: 13,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                SizedBox(height: 4),
                Text(
                  'Satu sesi pemindaian hanya dapat diakses oleh satu perangkat dalam satu waktu. Akses ganda bersamaan pada sesi yang sama akan otomatis diblokir.',
                  style: TextStyle(
                    color: Colors.black87,
                    fontSize: 12,
                    height: 1.4,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildVisualStepSection({
    required String stepNumber,
    required String title,
    required String description,
    required List<String> bullets,
    required Widget mockup,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Step Header
          Row(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              CircleAvatar(
                radius: 14,
                backgroundColor: AppTheme.primaryColor,
                child: Text(
                  stepNumber,
                  style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  title,
                  style: const TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.primaryColor,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Explanatory Card
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: const Color(0xFFE0E0E0)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  description,
                  style: const TextStyle(color: Colors.black87, fontSize: 13, height: 1.4),
                ),
                const SizedBox(height: 12),
                ...bullets.map((bullet) => Padding(
                      padding: const EdgeInsets.only(bottom: 6),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('• ', style: TextStyle(fontWeight: FontWeight.bold, color: AppTheme.primaryColor)),
                          Expanded(
                            child: Text(
                              bullet,
                              style: TextStyle(color: Colors.grey[700], fontSize: 12.5),
                            ),
                          ),
                        ],
                      ),
                    )),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Centered Phone Mockup
          mockup,
        ],
      ),
    );
  }

  Widget _buildPhoneFrame({required String title, required Widget child}) {
    return Column(
      children: [
        Container(
          width: 210,
          height: 400,
          decoration: BoxDecoration(
            color: Colors.black,
            borderRadius: BorderRadius.circular(32),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.18),
                blurRadius: 20,
                offset: const Offset(0, 10),
              ),
              BoxShadow(
                color: Colors.black.withOpacity(0.08),
                blurRadius: 8,
                offset: const Offset(0, 4),
              ),
            ],
            border: Border.all(color: const Color(0xFF2E2E2E), width: 4.5), // 3D Depth Border
          ),
          padding: const EdgeInsets.all(6),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(24),
            child: Stack(
              children: [
                Container(
                  color: const Color(0xFFFAFAFA),
                  child: child,
                ),
                // Camera Notch
                Align(
                  alignment: Alignment.topCenter,
                  child: Container(
                    margin: const EdgeInsets.only(top: 4),
                    width: 55,
                    height: 14,
                    decoration: BoxDecoration(
                      color: Colors.black,
                      borderRadius: BorderRadius.circular(7),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 10),
        Text(
          title,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 12,
            color: AppTheme.primaryColor,
          ),
        ),
      ],
    );
  }

  Widget _buildMiniInputField(String hint) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: Colors.grey[300]!),
      ),
      child: Text(
        hint,
        style: const TextStyle(color: Colors.grey, fontSize: 8),
      ),
    );
  }

  Widget _buildMiniButton(String label, Color color) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 8),
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(6),
      ),
      child: Center(
        child: Text(
          label,
          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 8),
        ),
      ),
    );
  }

  Widget _buildMiniBentoCard(IconData icon, String val, Color col) {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.shade300),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: col, size: 12),
          const SizedBox(height: 8),
          Text(val, style: const TextStyle(fontSize: 8, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Widget _buildMiniIcon(IconData icon, Color col) {
    return Container(
      padding: const EdgeInsets.all(4),
      decoration: const BoxDecoration(
        color: Colors.black54,
        shape: BoxShape.circle,
      ),
      child: Icon(icon, color: col, size: 10),
    );
  }

  Widget _buildMiniActionButton(IconData icon, String label, Color col) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 6),
      decoration: BoxDecoration(
        color: col,
        borderRadius: BorderRadius.circular(4),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, color: Colors.white, size: 8),
          const SizedBox(width: 4),
          Text(label, style: const TextStyle(color: Colors.white, fontSize: 7, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Widget _buildFAQSection() {
    final faqs = [
      {
        'q': 'Mengapa layar kamera terlalu gelap saat saya memindai?',
        'a': 'Aplikasi menyertakan overlay gelap untuk membantu isolasi cahaya sidik jari. Jika ini menyulitkan Anda melihat jari, ketuk tombol 💧 (Opacity) di sudut kanan atas untuk menurunkan ke tingkat Low (0.05).'
      },
      {
        'q': 'Bagaimana cara mencegah hasil foto terdeteksi buram/blur?',
        'a': 'Jaga jarak ponsel minimal 10 cm dari jari subjek. Atur zoom kamera bawaan pada tingkat 1.8x s.d 2.0x agar guratan sidik jari terlihat tajam tanpa bayangan ponsel menghalangi pencahayaan.'
      },
      {
        'q': 'Saya tidak sengaja menutup aplikasi di tengah jalan.',
        'a': 'Semua data sidik jari yang terunggah otomatis tersimpan di server. Anda dapat membuka tab Sesi, klik subjek Anda, dan klik "Lanjutkan Pemindaian" kapan saja.'
      }
    ];

    return Column(
      children: faqs.map((faq) {
        return Container(
          margin: const EdgeInsets.only(bottom: 10),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: const Color(0xFFE0E0E0)),
          ),
          child: ExpansionTile(
            title: Text(
              faq['q']!,
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Colors.black87),
            ),
            children: [
              Padding(
                padding: const EdgeInsets.only(left: 16, right: 16, bottom: 16),
                child: Text(
                  faq['a']!,
                  style: TextStyle(color: Colors.grey[700], fontSize: 12, height: 1.4),
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }
}

class _MockDashedPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.greenAccent
      ..strokeWidth = 1.5
      ..style = PaintingStyle.stroke;

    final rect = Rect.fromLTWH(0, 0, size.width, size.height);
    final rrect = RRect.fromRectAndRadius(rect, const Radius.circular(10));
    
    const dashWidth = 6.0;
    const dashSpace = 4.0;
    
    final path = Path()..addRRect(rrect);
    double distance = 0.0;
    bool draw = true;
    
    for (final metric in path.computeMetrics()) {
      while (distance < metric.length) {
        final len = draw ? dashWidth : dashSpace;
        if (draw) {
          canvas.drawPath(metric.extractPath(distance, distance + len), paint);
        }
        distance += len;
        draw = !draw;
      }
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

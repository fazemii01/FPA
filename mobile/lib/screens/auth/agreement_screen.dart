import 'package:flutter/material.dart';
import '../../theme/app_theme.dart';

class AgreementScreen extends StatelessWidget {
  const AgreementScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Syarat & Ketentuan'),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black87,
        elevation: 0.5,
      ),
      backgroundColor: const Color(0xFFFAFAFA),
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(24),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Persetujuan Pengguna Allia Tap finger',
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: AppTheme.primaryColor,
                      ),
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Harap baca syarat dan ketentuan berikut dengan seksama sebelum menggunakan aplikasi Allia Tap finger. Dengan melanjutkan login, Anda menyatakan menyetujui poin-poin berikut:',
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: Colors.grey[700],
                        height: 1.5,
                      ),
                    ),
                    const SizedBox(height: 24),
                    _buildSection(
                      context,
                      '1. Pengumpulan Data Biometrik',
                      'Aplikasi ini mengumpulkan citra foto sidik jari menggunakan kamera perangkat Anda. Data ini dianalisis untuk menghasilkan fitur/pola sidik jari dan tidak disebarluaskan kepada pihak ketiga di luar kepentingan operasional lembaga Anda.',
                    ),
                    _buildSection(
                      context,
                      '2. Keamanan & Enkripsi Data',
                      'Seluruh sidik jari, laporan hasil pemindaian, dan data klien dienkripsi secara aman saat dikirim ke server backend serta disimpan menggunakan mekanisme penyimpanan yang terenkripsi dan terlindungi.',
                    ),
                    _buildSection(
                      context,
                      '3. Hak Akses & Akun Pengguna',
                      'Akun Anda (Admin/Staff) hanya boleh digunakan oleh Anda sendiri. Anda bertanggung jawab penuh untuk menjaga kerahasiaan kata sandi Anda dan aktivitas yang terjadi di bawah akun Anda.',
                    ),
                    _buildSection(
                      context,
                      '4. Pemotongan Kredit Lembaga',
                      'Setiap pemrosesan sidik jari baru dan pembuatan laporan hasil analisis akan memotong saldo kredit lembaga Anda secara otomatis. Pastikan saldo kredit lembaga mencukupi sebelum memulai sesi pemindaian.',
                    ),
                    _buildSection(
                      context,
                      '5. Pembaruan Aplikasi Otomatis',
                      'Untuk menjaga keamanan dan kompatibilitas sistem analisis, Anda diwajibkan untuk selalu memperbarui aplikasi ke versi terbaru saat notifikasi pembaruan sistem OTA tersedia.',
                    ),
                  ],
                ),
              ),
            ),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.05),
                    blurRadius: 10,
                    offset: const Offset(0, -4),
                  ),
                ],
              ),
              child: Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () => Navigator.of(context).pop(false),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        side: const BorderSide(color: Colors.grey),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                      child: const Text(
                        'Kembali',
                        style: TextStyle(color: Colors.grey, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () => Navigator.of(context).pop(true),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppTheme.primaryColor,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                        elevation: 0,
                      ),
                      child: const Text(
                        'Saya Setuju',
                        style: TextStyle(fontWeight: FontWeight.bold),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSection(BuildContext context, String title, String body) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.only(bottom: 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: theme.textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.bold,
              color: Colors.black87,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            body,
            style: theme.textTheme.bodyMedium?.copyWith(
              color: Colors.grey[600],
              height: 1.5,
            ),
          ),
        ],
      ),
    );
  }
}

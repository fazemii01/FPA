import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'package:package_info_plus/package_info_plus.dart';
import '../../../providers/auth_provider.dart';
import '../../../theme/app_theme.dart';

class ProfileTab extends StatelessWidget {
  const ProfileTab({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final authProvider = context.watch<AuthProvider>();
    final user = authProvider.user;
    final isAdmin = user?.role == 'admin';

    return Scaffold(
      backgroundColor: const Color(0xFFFAFAFA),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const SizedBox(height: 12),
            // Profile Header Card
            Container(
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: const Color(0xFFE0E0E0)),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.01),
                    blurRadius: 10,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 16),
              child: Column(
                children: [
                  CircleAvatar(
                    radius: 36,
                    backgroundColor: AppTheme.primaryColor.withOpacity(0.08),
                    child: Text(
                      (user?.fullName ?? user?.email ?? 'U').substring(0, 1).toUpperCase(),
                      style: const TextStyle(
                        color: AppTheme.primaryColor,
                        fontWeight: FontWeight.bold,
                        fontSize: 28,
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    user?.fullName ?? user?.email ?? "User",
                    style: theme.textTheme.titleMedium?.copyWith(
                      color: AppTheme.primaryColor,
                      fontWeight: FontWeight.bold,
                      fontSize: 18,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    user?.email ?? '',
                    style: TextStyle(color: Colors.grey[500], fontSize: 13),
                  ),
                  if (user?.lembagaName != null && user!.lembagaName!.isNotEmpty) ...[
                    const SizedBox(height: 4),
                    Text(
                      '${user.lembagaName!} • ${user.lembagaCredits ?? 0} Kredit',
                      style: TextStyle(color: Colors.grey[700], fontSize: 13, fontWeight: FontWeight.w500),
                    ),
                  ],
                  const SizedBox(height: 12),
                  Container(
                    padding: const EdgeInsets.symmetric(vertical: 4, horizontal: 10),
                    decoration: BoxDecoration(
                      color: isAdmin ? Colors.blue.withOpacity(0.08) : Colors.green.withOpacity(0.08),
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Text(
                      isAdmin ? 'Administrator' : 'Staf Pemindaian',
                      style: TextStyle(
                        color: isAdmin ? Colors.blue : Colors.green,
                        fontWeight: FontWeight.bold,
                        fontSize: 11,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            
            const SizedBox(height: 24),
            
            // Actions Section
            Text(
              'PENGATURAN AKUN',
              style: TextStyle(
                color: Colors.grey[500],
                fontSize: 10,
                fontWeight: FontWeight.bold,
                letterSpacing: 1.5,
              ),
            ),
            const SizedBox(height: 12),
            
            if (isAdmin) ...[
              BouncingWidget(
                onTap: () => context.push('/topup'),
                child: Container(
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: const Color(0xFFE0E0E0)),
                  ),
                  child: ListTile(
                    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                    leading: Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: AppTheme.primaryColor.withOpacity(0.05),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.add_card_rounded, color: AppTheme.primaryColor),
                    ),
                    title: const Text(
                      'Top Up Kredit Lembaga',
                      style: TextStyle(fontWeight: FontWeight.bold, color: AppTheme.primaryColor, fontSize: 14),
                    ),
                    subtitle: Text(
                      'Beli/tambah kredit pemindaian',
                      style: TextStyle(color: Colors.grey[600], fontSize: 12),
                    ),
                    trailing: const Icon(Icons.chevron_right_rounded, color: Colors.grey),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              BouncingWidget(
                onTap: () => context.push('/register'),
                child: Container(
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: const Color(0xFFE0E0E0)),
                  ),
                  child: ListTile(
                    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                    leading: Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: AppTheme.primaryColor.withOpacity(0.05),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.person_add_rounded, color: AppTheme.primaryColor),
                    ),
                    title: const Text(
                      'Daftarkan Akun Baru',
                      style: TextStyle(fontWeight: FontWeight.bold, color: AppTheme.primaryColor, fontSize: 14),
                    ),
                    subtitle: Text(
                      'Buat akun staf atau admin baru',
                      style: TextStyle(color: Colors.grey[600], fontSize: 12),
                    ),
                    trailing: const Icon(Icons.chevron_right_rounded, color: Colors.grey),
                  ),
                ),
              ),
            ],
            const SizedBox(height: 12),
            BouncingWidget(
              onTap: () => context.push('/profile/manual'),
              child: Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: const Color(0xFFE0E0E0)),
                ),
                child: ListTile(
                  contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                  leading: Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: AppTheme.primaryColor.withOpacity(0.05),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Icons.book_rounded, color: AppTheme.primaryColor),
                  ),
                  title: const Text(
                    'Panduan Pengguna',
                    style: TextStyle(fontWeight: FontWeight.bold, color: AppTheme.primaryColor, fontSize: 14),
                  ),
                  subtitle: Text(
                    'Panduan pemindaian dan pembuatan laporan',
                    style: TextStyle(color: Colors.grey[600], fontSize: 12),
                  ),
                  trailing: const Icon(Icons.chevron_right_rounded, color: Colors.grey),
                ),
              ),
            ),
            const SizedBox(height: 12),
            
            BouncingWidget(
              onTap: () => _showAppInfo(context),
              child: Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: const Color(0xFFE0E0E0)),
                ),
                child: ListTile(
                  contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                  leading: Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: AppTheme.primaryColor.withOpacity(0.05),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Icons.info_outline_rounded, color: AppTheme.primaryColor),
                  ),
                  title: const Text(
                    'Informasi Aplikasi',
                    style: TextStyle(fontWeight: FontWeight.bold, color: AppTheme.primaryColor, fontSize: 14),
                  ),
                  subtitle: Text(
                    'Tentang developer dan versi aplikasi',
                    style: TextStyle(color: Colors.grey[600], fontSize: 12),
                  ),
                  trailing: const Icon(Icons.chevron_right_rounded, color: Colors.grey),
                ),
              ),
            ),
            const SizedBox(height: 12),
            
            BouncingWidget(
              onTap: () => _handleLogout(context, authProvider),
              child: Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: AppTheme.errorColor.withOpacity(0.2)),
                ),
                child: ListTile(
                  contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                  leading: Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: AppTheme.errorColor.withOpacity(0.08),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Icons.logout_rounded, color: AppTheme.errorColor),
                  ),
                  title: const Text(
                    'Keluar dari Akun',
                    style: TextStyle(fontWeight: FontWeight.bold, color: AppTheme.errorColor, fontSize: 14),
                  ),
                  subtitle: Text(
                    'Keluar dari sesi aktif Anda',
                    style: TextStyle(color: Colors.grey[600], fontSize: 12),
                  ),
                  trailing: const Icon(Icons.chevron_right_rounded, color: AppTheme.errorColor),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _handleLogout(BuildContext context, AuthProvider authProvider) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.white,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        title: const Text(
          'Keluar',
          style: TextStyle(color: AppTheme.primaryColor, fontWeight: FontWeight.bold),
        ),
        content: const Text('Apakah Anda yakin ingin keluar?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Batal', style: TextStyle(color: Colors.grey)),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.errorColor,
              foregroundColor: Colors.white,
              elevation: 0,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
            child: const Text('Keluar'),
          ),
        ],
      ),
    );

    if (confirmed == true && context.mounted) {
      await authProvider.logout();
      if (context.mounted) {
        context.go('/login');
      }
    }
  }

  Future<void> _showAppInfo(BuildContext context) async {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const Center(child: CircularProgressIndicator()),
    );

    String version = '1.0.0';
    try {
      final packageInfo = await PackageInfo.fromPlatform();
      version = packageInfo.version;
    } catch (e) {
      // ignore
    }

    if (context.mounted) {
      Navigator.pop(context); // Close the progress indicator
      
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          backgroundColor: Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
          title: const Text(
            'Informasi Aplikasi',
            style: TextStyle(color: AppTheme.primaryColor, fontWeight: FontWeight.bold),
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Nama Aplikasi:',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Colors.grey),
              ),
              const Text(
                'FPA (Fingerprint Analysis)',
                style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
              ),
              const SizedBox(height: 12),
              const Text(
                'Developer:',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Colors.grey),
              ),
              const Text(
                'PT. Allia Mitra Utama',
                style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
              ),
              const SizedBox(height: 12),
              const Text(
                'Versi:',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Colors.grey),
              ),
              Text(
                'v$version',
                style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Tutup', style: TextStyle(color: AppTheme.primaryColor, fontWeight: FontWeight.bold)),
            ),
          ],
        ),
      );
    }
  }
}

// ── Bouncing Click Scale Animation Widget ──────────────────────────────────────

class BouncingWidget extends StatefulWidget {
  final Widget child;
  final VoidCallback onTap;

  const BouncingWidget({
    super.key,
    required this.child,
    required this.onTap,
  });

  @override
  State<BouncingWidget> createState() => _BouncingWidgetState();
}

class _BouncingWidgetState extends State<BouncingWidget> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 100),
      lowerBound: 0.0,
      upperBound: 0.05,
    );
    _scaleAnimation = Tween<double>(begin: 1.0, end: 0.95).animate(_controller);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTapDown: (_) => _controller.forward(),
      onTapUp: (_) {
        _controller.reverse();
        widget.onTap();
      },
      onTapCancel: () => _controller.reverse(),
      child: ScaleTransition(
        scale: _scaleAnimation,
        child: widget.child,
      ),
    );
  }
}

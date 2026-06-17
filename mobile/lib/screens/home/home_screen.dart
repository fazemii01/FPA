import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../providers/scan_provider.dart';
import '../../theme/app_theme.dart';

import 'tabs/dashboard_tab.dart';
import 'tabs/session_tab.dart';
import 'tabs/review_tab.dart';
import 'tabs/report_history_tab.dart';
import 'tabs/profile_tab.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _refreshData();
    });
  }

  Future<void> _refreshData() async {
    final scanProvider = context.read<ScanProvider>();
    final authProvider = context.read<AuthProvider>();

    await scanProvider.loadSessions();
    if (authProvider.user?.role == 'admin') {
      await scanProvider.loadReviewQueue();
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final authProvider = context.watch<AuthProvider>();
    final user = authProvider.user;
    final isAdmin = user?.role == 'admin';

    final List<Widget> tabs = [];
    final List<BottomNavigationBarItem> navItems = [];

    // Dashboard Tab
    tabs.add(const DashboardTab());
    navItems.add(BottomNavigationBarItem(
      icon: Icon(_currentIndex == 0 ? Icons.dashboard_rounded : Icons.dashboard_outlined),
      label: 'Beranda',
    ));

    // Session Tab
    tabs.add(const SessionTab());
    navItems.add(BottomNavigationBarItem(
      icon: Icon(_currentIndex == 1 ? Icons.list_alt_rounded : Icons.list_alt_outlined),
      label: 'Sesi',
    ));

    // Review Tab (Admin Only)
    int reviewIndex = -1;
    if (isAdmin) {
      reviewIndex = tabs.length;
      tabs.add(const ReviewTab());
      navItems.add(BottomNavigationBarItem(
        icon: Icon(_currentIndex == reviewIndex ? Icons.assignment_turned_in_rounded : Icons.assignment_turned_in_outlined),
        label: 'Tinjauan',
      ));
    }

    // Report History Tab
    int historyIndex = tabs.length;
    tabs.add(const ReportHistoryTab());
    navItems.add(BottomNavigationBarItem(
      icon: Icon(_currentIndex == historyIndex ? Icons.history_rounded : Icons.history_outlined),
      label: 'Riwayat',
    ));

    // Profile Tab
    int profileIndex = tabs.length;
    tabs.add(const ProfileTab());
    navItems.add(BottomNavigationBarItem(
      icon: Icon(_currentIndex == profileIndex ? Icons.person_rounded : Icons.person_outline_rounded),
      label: 'Profil',
    ));

    // Guard against index out of bounds if role changes dynamically
    if (_currentIndex >= tabs.length) {
      _currentIndex = 0;
    }

    String getTitle() {
      if (_currentIndex == 0) {
        return isAdmin ? 'FPA Portal - Admin' : '10-Finger Scanner';
      }
      if (_currentIndex == 1) return 'Daftar Sesi Pemindaian';

      if (isAdmin) {
        if (_currentIndex == 2) return 'Antrean Tinjauan';
        if (_currentIndex == 3) return 'Riwayat Laporan';
        if (_currentIndex == 4) return 'Profil Akun';
      } else {
        if (_currentIndex == 2) return 'Riwayat Laporan';
        if (_currentIndex == 3) return 'Profil Akun';
      }
      return 'FPA - Fingerprint Scanner';
    }

    return Scaffold(
      backgroundColor: const Color(0xFFFAFAFA),
      appBar: AppBar(
        backgroundColor: const Color(0xFFFAFAFA),
        elevation: 0,
        scrolledUnderElevation: 0,
        title: Text(
          getTitle(),
          style: theme.textTheme.titleLarge?.copyWith(
            color: AppTheme.primaryColor,
            fontWeight: FontWeight.bold,
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded, color: AppTheme.primaryColor),
            tooltip: 'Segarkan data',
            onPressed: _refreshData,
          ),
        ],
      ),
      body: IndexedStack(
        index: _currentIndex,
        children: tabs,
      ),
      bottomNavigationBar: Container(
        decoration: const BoxDecoration(
          border: Border(
            top: BorderSide(color: Color(0xFFE0E0E0), width: 1),
          ),
        ),
        child: BottomNavigationBar(
          currentIndex: _currentIndex,
          onTap: (index) {
            setState(() {
              _currentIndex = index;
            });
          },
          type: BottomNavigationBarType.fixed,
          backgroundColor: Colors.white,
          selectedItemColor: AppTheme.primaryColor,
          unselectedItemColor: Colors.grey[500],
          selectedLabelStyle: const TextStyle(fontWeight: FontWeight.bold, fontSize: 11, fontFamily: 'Inter'),
          unselectedLabelStyle: const TextStyle(fontWeight: FontWeight.normal, fontSize: 11, fontFamily: 'Inter'),
          elevation: 0,
          items: navItems,
        ),
      ),
    );
  }
}

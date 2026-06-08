import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../providers/scan_provider.dart';

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
    final authProvider = context.watch<AuthProvider>();
    final user = authProvider.user;
    final isAdmin = user?.role == 'admin';

    final List<Widget> tabs = [];
    final List<BottomNavigationBarItem> navItems = [];

    // Dashboard Tab
    tabs.add(const DashboardTab());
    navItems.add(const BottomNavigationBarItem(
        icon: Icon(Icons.dashboard), label: 'Beranda'));

    // Session Tab
    tabs.add(const SessionTab());
    navItems.add(const BottomNavigationBarItem(
        icon: Icon(Icons.list_alt), label: 'Sesi'));

    // Review Tab (Admin Only)
    if (isAdmin) {
      tabs.add(const ReviewTab());
      navItems.add(const BottomNavigationBarItem(
          icon: Icon(Icons.assignment_turned_in), label: 'Tinjauan'));
    }

    // Report History Tab
    tabs.add(const ReportHistoryTab());
    navItems.add(const BottomNavigationBarItem(
        icon: Icon(Icons.history), label: 'Riwayat'));

    // Profile Tab
    tabs.add(const ProfileTab());
    navItems.add(const BottomNavigationBarItem(
        icon: Icon(Icons.person), label: 'Profil'));

    // Guard against index out of bounds if role changes dynamically
    if (_currentIndex >= tabs.length) {
      _currentIndex = 0;
    }

    String getTitle() {
      // Provide dynamic titles based on the selected tab and role
      if (_currentIndex == 0)
        return isAdmin ? 'FPA Portal - Admin' : '10-Finger Scanner';
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
      appBar: AppBar(
        title: Text(getTitle()),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Segarkan data',
            onPressed: _refreshData,
          ),
        ],
      ),
      body: IndexedStack(
        index: _currentIndex,
        children: tabs,
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        type: BottomNavigationBarType.fixed,
        selectedItemColor: Theme.of(context).primaryColor,
        unselectedItemColor: Colors.grey,
        items: navItems,
      ),
    );
  }
}

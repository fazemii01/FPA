import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../providers/auth_provider.dart';
import '../../theme/app_theme.dart';

class TopUpScreen extends StatefulWidget {
  const TopUpScreen({super.key});

  @override
  State<TopUpScreen> createState() => _TopUpScreenState();
}

class _TopUpScreenState extends State<TopUpScreen> {
  int? _selectedPackageIndex;
  final _customCreditController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  
  int getPricePerCredit(String? type) {
    if (type == 'partner') {
      return 95000;
    }
    return 125000;
  }
  
  final List<int> _packages = [5, 10, 20, 50];

  @override
  void initState() {
    super.initState();
    _customCreditController.addListener(() {
      if (_customCreditController.text.isNotEmpty && _selectedPackageIndex != null) {
        setState(() {
          _selectedPackageIndex = null;
        });
      } else {
        setState(() {});
      }
    });
  }

  @override
  void dispose() {
    _customCreditController.dispose();
    super.dispose();
  }

  int get _currentCredits {
    if (_selectedPackageIndex != null) {
      return _packages[_selectedPackageIndex!];
    }
    final customVal = int.tryParse(_customCreditController.text);
    return customVal ?? 0;
  }

  String _formatCurrency(int amount) {
    final buffer = StringBuffer();
    final str = amount.toString();
    int len = str.length;
    for (int i = 0; i < len; i++) {
      if (i > 0 && (len - i) % 3 == 0) {
        buffer.write('.');
      }
      buffer.write(str[i]);
    }
    return 'Rp $buffer';
  }

  Future<void> _handleRequest(String? nameLembaga) async {
    final credits = _currentCredits;
    if (credits <= 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Silakan pilih atau masukkan jumlah kredit.')),
      );
      return;
    }

    final String name = nameLembaga ?? 'Lembaga FPA';
    final String message = 'Hallo admin alliakids, kami dari $name ingin topup creadit dengan nominal $credits. mohon bantuanya!';
    const String phoneNumber = '6285138511348'; 
    final Uri url = Uri.parse('https://wa.me/$phoneNumber?text=${Uri.encodeComponent(message)}');

    try {
      if (await canLaunchUrl(url)) {
        await launchUrl(url, mode: LaunchMode.externalApplication);
      } else {
        throw 'Could not launch $url';
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Gagal membuka WhatsApp: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final authProvider = context.watch<AuthProvider>();
    final user = authProvider.user;
    final String? nameLembaga = user?.lembagaName;

    return Scaffold(
      backgroundColor: const Color(0xFFFAFAFA),
      appBar: AppBar(
        backgroundColor: const Color(0xFFFAFAFA),
        elevation: 0,
        scrolledUnderElevation: 0,
        title: Text(
          'Top Up Kredit',
          style: theme.textTheme.titleLarge?.copyWith(
            color: AppTheme.primaryColor,
            fontWeight: FontWeight.bold,
          ),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, color: AppTheme.primaryColor, size: 20),
          onPressed: () {
            if (Navigator.canPop(context)) {
              Navigator.pop(context);
            }
          },
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Info Box
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: AppTheme.primaryColor.withOpacity(0.04),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: AppTheme.primaryColor.withOpacity(0.1)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        nameLembaga ?? 'Lembaga FPA',
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: AppTheme.primaryColor,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Kredit saat ini: ${user?.lembagaCredits ?? 0} Kredit',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 28),

                // Choose Package Section
                const Text(
                  'PILIH PAKET KREDIT',
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 1.5,
                    color: Colors.grey,
                  ),
                ),
                const SizedBox(height: 12),
                
                // Package Grid (2x2)
                GridView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 2,
                    crossAxisSpacing: 12,
                    mainAxisSpacing: 12,
                    childAspectRatio: 1.5,
                  ),
                  itemCount: _packages.length,
                  itemBuilder: (context, index) {
                    final pkgCredits = _packages[index];
                    final isSelected = _selectedPackageIndex == index;
                    return InkWell(
                      onTap: () {
                        setState(() {
                          _selectedPackageIndex = index;
                          _customCreditController.clear();
                        });
                      },
                      child: Container(
                        decoration: BoxDecoration(
                          color: isSelected ? AppTheme.primaryColor : Colors.white,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: isSelected ? AppTheme.primaryColor : const Color(0xFFE0E0E0),
                          ),
                          boxShadow: isSelected
                              ? [
                                  BoxShadow(
                                    color: AppTheme.primaryColor.withOpacity(0.15),
                                    blurRadius: 10,
                                    offset: const Offset(0, 4),
                                  )
                                ]
                              : null,
                        ),
                        padding: const EdgeInsets.all(12),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(
                              '$pkgCredits Kredit',
                              style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                                color: isSelected ? Colors.white : AppTheme.primaryColor,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              _formatCurrency(pkgCredits * getPricePerCredit(user?.lembagaType)),
                              style: TextStyle(
                                fontSize: 12,
                                color: isSelected ? Colors.white.withOpacity(0.8) : Colors.grey[600],
                              ),
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
                const SizedBox(height: 24),

                // Custom Input Section
                const Text(
                  'ATAU MASUKKAN SECARA MANUAL',
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 1.5,
                    color: Colors.grey,
                  ),
                ),
                const SizedBox(height: 12),
                
                TextFormField(
                  controller: _customCreditController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(
                    labelText: 'Jumlah Kredit Kustom',
                    hintText: 'Contoh: 15',
                    prefixIcon: Icon(Icons.add_card_rounded, color: Colors.grey),
                  ),
                  validator: (value) {
                    if (value != null && value.isNotEmpty) {
                      final val = int.tryParse(value);
                      if (val == null || val <= 0) {
                        return 'Masukkan jumlah kredit yang valid';
                      }
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 32),

                // Price Summary Panel
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: const Color(0xFFE0E0E0)),
                  ),
                  child: Column(
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text(
                            'Kredit dipesan',
                            style: TextStyle(color: Colors.grey, fontSize: 14),
                          ),
                          Text(
                            '$sessionsDipesan Kredit',
                            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: AppTheme.primaryColor),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      const Divider(height: 1, color: Color(0xFFE0E0E0)),
                      const SizedBox(height: 12),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text(
                            'Total Pembayaran',
                            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: AppTheme.primaryColor),
                          ),
                          Text(
                            _formatCurrency(sessionsDipesan * getPricePerCredit(user?.lembagaType)),
                            style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 18, color: AppTheme.primaryColor),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 32),

                // Submit Button
                ElevatedButton.icon(
                  onPressed: () {
                    if (_formKey.currentState!.validate()) {
                      _handleRequest(nameLembaga);
                    }
                  },
                  icon: const Icon(Icons.send_rounded, size: 20),
                  label: const Text('Kirim Permintaan via WhatsApp'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppTheme.primaryColor,
                    foregroundColor: Colors.white,
                    elevation: 0,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  int get sessionsDipesan => _currentCredits;
}

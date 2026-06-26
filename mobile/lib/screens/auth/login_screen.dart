import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'package:package_info_plus/package_info_plus.dart';
import '../../providers/auth_provider.dart';
import '../../theme/app_theme.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  bool _agreedToTerms = false;
  String _apkVersion = '';

  @override
  void initState() {
    super.initState();
    _loadApkVersion();
  }

  Future<void> _loadApkVersion() async {
    try {
      final packageInfo = await PackageInfo.fromPlatform();
      setState(() {
        _apkVersion = packageInfo.version;
      });
    } catch (e) {
      // ignore
    }
  }

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      backgroundColor: const Color(0xFFFAFAFA),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
            child: Form(
              key: _formKey,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Center(
                    child: Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        shape: BoxShape.circle,
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.03),
                            blurRadius: 10,
                            offset: const Offset(0, 4),
                          ),
                        ],
                      ),
                      child: Image.asset(
                        'assets/images/jaribakat.jpeg',
                        height: 64,
                        width: 64,
                        fit: BoxFit.contain,
                        errorBuilder: (context, error, stackTrace) {
                          return const Icon(
                            Icons.fingerprint_rounded,
                            size: 64,
                            color: AppTheme.primaryColor,
                          );
                        },
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),
                  Text(
                    'FPA',
                    style: theme.textTheme.headlineLarge?.copyWith(
                      color: AppTheme.primaryColor,
                      letterSpacing: 2,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Fingerprint Analysis System',
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: Colors.grey[600],
                      letterSpacing: 0.5,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 40),
                  
                  // Login card
                  Container(
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: const Color(0xFFE0E0E0)),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.02),
                          blurRadius: 15,
                          offset: const Offset(0, 8),
                        ),
                      ],
                    ),
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Text(
                          'Sign In',
                          style: theme.textTheme.titleLarge?.copyWith(
                            color: AppTheme.primaryColor,
                          ),
                          textAlign: TextAlign.left,
                        ),
                        const SizedBox(height: 24),
                        Container(
                          decoration: BoxDecoration(
                            boxShadow: [
                              BoxShadow(
                                color: Colors.black.withOpacity(0.03),
                                blurRadius: 10,
                                offset: const Offset(0, 4),
                              ),
                            ],
                          ),
                          child: TextFormField(
                            controller: _emailController,
                            decoration: const InputDecoration(
                              labelText: 'Email',
                              prefixIcon: Icon(Icons.email_outlined, color: Colors.grey),
                            ),
                            keyboardType: TextInputType.emailAddress,
                            validator: (value) {
                              if (value?.isEmpty ?? true) {
                                return 'Email is required';
                              }
                              if (!value!.contains('@')) {
                                return 'Enter a valid email';
                              }
                              return null;
                            },
                          ),
                        ),
                        const SizedBox(height: 16),
                        Container(
                          decoration: BoxDecoration(
                            boxShadow: [
                              BoxShadow(
                                color: Colors.black.withOpacity(0.03),
                                blurRadius: 10,
                                offset: const Offset(0, 4),
                              ),
                            ],
                          ),
                          child: TextFormField(
                            controller: _passwordController,
                            decoration: const InputDecoration(
                              labelText: 'Password',
                              prefixIcon: Icon(Icons.lock_outlined, color: Colors.grey),
                            ),
                            obscureText: true,
                            validator: (value) {
                              if (value?.isEmpty ?? true) {
                                return 'Password is required';
                              }
                              if (value!.length < 6) {
                                return 'Password must be at least 6 characters';
                              }
                              return null;
                            },
                          ),
                        ),
                        const SizedBox(height: 16),
                        Row(
                          children: [
                            SizedBox(
                              width: 24,
                              height: 24,
                              child: Checkbox(
                                value: _agreedToTerms,
                                activeColor: AppTheme.primaryColor,
                                onChanged: (value) {
                                  setState(() {
                                    _agreedToTerms = value ?? false;
                                  });
                                },
                              ),
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: GestureDetector(
                                onTap: () async {
                                  final result = await context.push<bool>('/agreement');
                                  if (result == true) {
                                    setState(() {
                                      _agreedToTerms = true;
                                    });
                                  }
                                },
                                child: const Text.rich(
                                  TextSpan(
                                    text: 'Saya menyetujui ',
                                    style: TextStyle(color: Colors.black54, fontSize: 13),
                                    children: [
                                      TextSpan(
                                        text: 'Syarat & Ketentuan Penggunaan Aplikasi',
                                        style: TextStyle(
                                          color: AppTheme.primaryColor,
                                          fontWeight: FontWeight.bold,
                                          decoration: TextDecoration.underline,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 24),
                        Consumer<AuthProvider>(
                          builder: (context, authProvider, _) {
                            return Container(
                              decoration: BoxDecoration(
                                boxShadow: [
                                  BoxShadow(
                                    color: AppTheme.primaryColor.withOpacity(0.15),
                                    blurRadius: 12,
                                    offset: const Offset(0, 6),
                                  ),
                                ],
                              ),
                              child: ElevatedButton(
                                onPressed: authProvider.isLoading
                                    ? null
                                    : () => _handleLogin(context, authProvider),
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: AppTheme.primaryColor,
                                  foregroundColor: Colors.white,
                                  elevation: 0,
                                  shadowColor: Colors.transparent,
                                  padding: const EdgeInsets.symmetric(vertical: 16),
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                ),
                                child: authProvider.isLoading
                                    ? const SizedBox(
                                        height: 20,
                                        width: 20,
                                        child: CircularProgressIndicator(
                                          strokeWidth: 2,
                                          valueColor: AlwaysStoppedAnimation<Color>(
                                            Colors.white,
                                          ),
                                        ),
                                      )
                                    : const Text(
                                        'Continue',
                                        style: TextStyle(
                                          fontWeight: FontWeight.bold,
                                          letterSpacing: 0.5,
                                        ),
                                      ),
                              ),
                            );
                          },
                        ),
                      ],
                    ),
                  ),
                  
                  const SizedBox(height: 24),
                  Consumer<AuthProvider>(
                    builder: (context, authProvider, _) {
                      if (authProvider.error != null) {
                        return Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: Colors.red[50],
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(color: Colors.red.shade100),
                          ),
                          child: Row(
                            children: [
                              Icon(Icons.error_outline, color: Colors.red[800], size: 20),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  authProvider.error!,
                                  style: TextStyle(color: Colors.red[900], fontSize: 13),
                                ),
                              ),
                            ],
                          ),
                        );
                      }
                      return const SizedBox.shrink();
                    },
                  ),
                  if (_apkVersion.isNotEmpty) ...[
                    const SizedBox(height: 24),
                    Text(
                      'v$_apkVersion',
                      style: TextStyle(
                        color: Colors.grey[500],
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _handleLogin(
      BuildContext context, AuthProvider authProvider) async {
    if (!_agreedToTerms) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Anda harus menyetujui Syarat & Ketentuan Penggunaan Aplikasi sebelum masuk.'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    if (_formKey.currentState!.validate()) {
      final success = await authProvider.login(
        email: _emailController.text,
        password: _passwordController.text,
      );

      if (success && context.mounted) {
        context.go('/home');
      }
    }
  }
}

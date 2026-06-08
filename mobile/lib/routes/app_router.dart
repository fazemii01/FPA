import 'package:go_router/go_router.dart';
import 'navigator_key.dart';
import '../screens/splash/splash_screen.dart';
import '../screens/auth/login_screen.dart';
import '../screens/auth/register_screen.dart';
import '../screens/home/home_screen.dart';
import '../screens/clients/create_client_screen.dart';
import '../screens/scan/scan_screen.dart';
import '../screens/scan/scan_instruction_screen.dart';
import '../screens/scan/camera_scanner_screen.dart';
import '../screens/scan/scan_progress_screen.dart';
import '../screens/scan/review_captured_fingers_screen.dart';
import '../screens/scan/processing_screen.dart';
import '../screens/scan/fingerprint_capture_screen.dart';
import '../screens/report/report_screen.dart';
import '../screens/report/report_summary_screen.dart';
import '../screens/report/report_view_screen.dart';

class AppRouter {
  static final GoRouter router = GoRouter(
    navigatorKey: navigatorKey,
    initialLocation: '/splash',
    routes: [
      GoRoute(
        path: '/splash',
        builder: (context, state) => const SplashScreen(),
      ),
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/register',
        builder: (context, state) => const RegisterScreen(),
      ),
      GoRoute(
        path: '/home',
        builder: (context, state) => const HomeScreen(),
      ),
      GoRoute(
        path: '/clients/create',
        builder: (context, state) => const CreateClientScreen(),
      ),
      GoRoute(
        path: '/scan',
        builder: (context, state) => const ScanScreen(),
      ),
      GoRoute(
        path: '/scan/instruction',
        builder: (context, state) => const ScanInstructionScreen(),
      ),
      GoRoute(
        path: '/scan/camera/:sessionId/:fingerPosition/:fingerIndex',
        builder: (context, state) {
          final sessionId = int.parse(state.pathParameters['sessionId']!);
          final fingerPosition = state.pathParameters['fingerPosition']!;
          final fingerIndex = int.parse(state.pathParameters['fingerIndex']!);
          return CameraScannerScreen(
            sessionId: sessionId,
            fingerPosition: fingerPosition,
            fingerIndex: fingerIndex,
          );
        },
      ),
      GoRoute(
        path: '/scan/progress/:sessionId/:fingerIndex',
        builder: (context, state) {
          final sessionId = int.parse(state.pathParameters['sessionId']!);
          final fingerIndex = int.parse(state.pathParameters['fingerIndex']!);
          return ScanProgressScreen(
            sessionId: sessionId,
            currentFingerIndex: fingerIndex,
          );
        },
      ),
      GoRoute(
        path: '/scan/review/:sessionId',
        builder: (context, state) {
          final sessionId = int.parse(state.pathParameters['sessionId']!);
          return ReviewCapturedFingersScreen(sessionId: sessionId);
        },
      ),
      GoRoute(
        path: '/scan/processing/:sessionId',
        builder: (context, state) {
          final sessionId = int.parse(state.pathParameters['sessionId']!);
          return ProcessingScreen(sessionId: sessionId);
        },
      ),
      GoRoute(
        path: '/scan/capture/:sessionId/:fingerPosition',
        builder: (context, state) {
          final sessionId = int.parse(state.pathParameters['sessionId']!);
          final fingerPosition = state.pathParameters['fingerPosition']!;
          return FingerprintCaptureScreen(
            sessionId: sessionId,
            fingerPosition: fingerPosition,
          );
        },
      ),
      GoRoute(
        path: '/report/summary/:sessionId',
        builder: (context, state) {
          final sessionId = int.parse(state.pathParameters['sessionId']!);
          return ReportSummaryScreen(sessionId: sessionId);
        },
      ),
      GoRoute(
        path: '/report/view/:reportId',
        builder: (context, state) {
          final reportId = int.parse(state.pathParameters['reportId']!);
          return ReportViewScreen(reportId: reportId);
        },
      ),
      GoRoute(
        path: '/report/:sessionId',
        builder: (context, state) {
          final sessionId = int.parse(state.pathParameters['sessionId']!);
          return ReportScreen(sessionId: sessionId);
        },
      ),
    ],
  );
}

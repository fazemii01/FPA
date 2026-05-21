# Flutter MVP - 10-Finger Fingerprint Scanner

## Project Structure

```
lib/
├── config/
│   └── app_config.dart              # API & app constants
├── main.dart                         # App entry point
├── models/
│   ├── scan_model.dart              # ScanSession, Fingerprint, Report models
│   └── user_model.dart              # User & Auth models
├── providers/
│   ├── auth_provider.dart           # Authentication state management
│   └── scan_provider.dart           # Scan session state management
├── routes/
│   └── app_router.dart              # GoRouter navigation configuration
├── screens/
│   ├── splash/
│   │   └── splash_screen.dart       # Splash screen with auth check
│   ├── auth/
│   │   ├── login_screen.dart        # Login screen
│   │   └── register_screen.dart     # Registration screen
│   ├── home/
│   │   └── home_screen.dart         # Dashboard with session list
│   ├── clients/
│   │   └── create_client_screen.dart # Client data entry form
│   ├── scan/
│   │   ├── scan_screen.dart         # Scan session overview
│   │   ├── scan_instruction_screen.dart # Scanning guidelines
│   │   ├── camera_scanner_screen.dart   # Camera capture with circular guide
│   │   ├── scan_progress_screen.dart    # Progress tracking
│   │   ├── review_captured_fingers_screen.dart # Review all captures
│   │   ├── processing_screen.dart   # Processing animation
│   │   └── fingerprint_capture_screen.dart # Legacy capture (deprecated)
│   ├── report/
│   │   ├── report_screen.dart       # Report display
│   │   ├── report_summary_screen.dart   # Summary with metrics
│   │   └── report_view_screen.dart  # PDF viewer
├── services/
│   ├── api_service.dart             # HTTP client with JWT
│   └── storage/
│       └── storage_service.dart     # Local image storage
├── shared/
│   └── widgets/
│       ├── circular_guide_overlay.dart  # Camera guide overlay
│       ├── finger_progress_widget.dart  # Progress indicator
│       └── quality_indicator.dart   # Quality status badge
└── theme/
    └── app_theme.dart              # Material Design 3 theme
```

## Screens Implemented

### 1. Splash Screen (`splash_screen.dart`)
- Auto-checks authentication token
- Routes to login or home based on auth status
- Shows loading animation

### 2. Login & Register (`auth/`)
- Email/password authentication
- JWT token storage
- Form validation

### 3. Home Screen (`home_screen.dart`)
- Dashboard with recent sessions
- Create new scan session button
- Session list with progress indicators
- Indonesian UI labels

### 4. Create Client Screen (`create_client_screen.dart`)
- Client data entry form
- Fields: Name, NIK, Phone, Address
- Form validation
- Indonesian labels

### 5. Scan Instruction Screen (`scan_instruction_screen.dart`)
- Scanning guidelines with icons
- 10-finger sequence display
- Best practices for quality

### 6. Camera Scanner Screen (`camera_scanner_screen.dart`)
- **Circular guide overlay** with finger name
- Quality score display (0-100%)
- Capture from camera or gallery
- Image preview with quality feedback
- Accept/Retry flow
- Uploads to backend endpoint

### 7. Scan Progress Screen (`scan_progress_screen.dart`)
- Overall progress bar (X/10)
- List of scanned fingers with chips
- Next finger indicator
- Continue to next finger button

### 8. Review Captured Fingers Screen (`review_captured_fingers_screen.dart`)
- Grid/list of all captured fingerprints
- Quality scores per finger
- Image preview on tap
- Average quality calculation
- Proceed to processing button

### 9. Processing Screen (`processing_screen.dart`)
- Multi-step progress animation
- Steps: Analyze → Extract → Calculate → Generate
- Progress percentage display
- Error handling with retry

### 10. Report Summary Screen (`report_summary_screen.dart`)
- Overall score display with color coding
- Metrics breakdown
- Report metadata (ID, date, session)
- PDF download button
- Return to home button

### 11. Report View Screen (`report_view_screen.dart`)
- PDF report display
- Download functionality
- Report details and notes
- Quality assessment summary

## Key Features

### Camera Scanner with Circular Guide
- Real-time circular overlay centered on screen
- Finger position label display
- Quality status indicator (Good/Fair/Low)
- Color-coded border (Green/Orange/Red)
- Capture button with loading state
- Gallery picker fallback

### 10-Finger Scan Flow
1. Create scan session
2. Enter client data (optional)
3. View scanning instructions
4. Capture each finger sequentially
5. Review all captures
6. Process and generate report
7. View report summary
8. Download PDF

### State Management
- **AuthProvider**: Handles login, logout, token management
- **ScanProvider**: Manages scan sessions, fingerprint uploads, report generation
- Provider pattern with ChangeNotifier

### Navigation
- GoRouter with named routes
- Deep linking support
- Splash screen auth check
- Proper back navigation

### Indonesian UI
- All labels in Indonesian
- Finger names in Indonesian
- Status messages in Indonesian
- Form validation messages in Indonesian

## API Integration

Endpoints used:
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /scans/sessions` - Create scan session
- `POST /scans/sessions/{id}/fingerprints` - Upload fingerprint
- `POST /reports/sessions/{id}/generate` - Generate report
- `GET /scans/sessions` - List sessions
- `GET /reports/{id}` - Get report

## Dependencies

- `provider: ^6.0.0` - State management
- `go_router: ^12.0.0` - Navigation
- `dio: ^5.3.0` - HTTP client
- `camera: ^0.10.5` - Camera access
- `image_picker: ^1.0.0` - Gallery picker
- `shared_preferences: ^2.2.0` - Local storage
- `hive: ^2.2.0` - Local database

## Running the App

```bash
cd mobile
flutter pub get
flutter run
```

## Notes

- Backend owns all image processing (quality analysis, feature extraction)
- Flutter only handles capture, preview, and upload
- Quality scores are placeholders (75% for camera, 70% for gallery)
- All image paths stored temporarily during session
- JWT token automatically injected in API requests
- Proper error handling with user feedback

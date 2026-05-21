# 10-Finger Fingerprint Scanner - Mobile App

Flutter mobile application for the 10-finger fingerprint scanning system.

## Features

- User authentication (login/register)
- Create scan sessions
- Capture fingerprints using camera
- Real-time quality feedback
- View scan progress
- Generate and view reports
- Session history

## Tech Stack

- **Framework**: Flutter 3.0+
- **State Management**: Provider
- **Navigation**: GoRouter
- **HTTP Client**: Dio
- **Local Storage**: SharedPreferences, Hive
- **Camera**: camera package
- **Image Handling**: image_picker, image

## Prerequisites

- Flutter SDK 3.0 or higher
- Dart SDK 3.0 or higher
- Android Studio / Xcode (for mobile development)
- Backend API running (see backend/README.md)

## Setup

### 1. Install Flutter

Follow the official Flutter installation guide:
https://flutter.dev/docs/get-started/install

### 2. Install Dependencies

```bash
cd mobile
flutter pub get
```

### 3. Configure API Endpoint

Edit `lib/config/app_config.dart` and update the `baseUrl`:

```dart
static const String baseUrl = 'http://your-backend-url:8000';
```

For local development:
- Android Emulator: `http://10.0.2.2:8000`
- iOS Simulator: `http://localhost:8000`
- Physical Device: `http://YOUR_COMPUTER_IP:8000`

### 4. Run the App

```bash
flutter run
```

## Project Structure

```
mobile/
├── lib/
│   ├── config/
│   │   └── app_config.dart          # API and app configuration
│   ├── models/
│   │   ├── user_model.dart          # User data models
│   │   └── scan_model.dart          # Scan session models
│   ├── providers/
│   │   ├── auth_provider.dart       # Authentication state
│   │   └── scan_provider.dart       # Scan session state
│   ├── routes/
│   │   └── app_router.dart          # Navigation routes
│   ├── screens/
│   │   ├── auth/
│   │   │   ├── login_screen.dart
│   │   │   └── register_screen.dart
│   │   ├── home/
│   │   │   └── home_screen.dart
│   │   ├── scan/
│   │   │   ├── scan_screen.dart
│   │   │   └── fingerprint_capture_screen.dart
│   │   └── report/
│   │       └── report_screen.dart
│   ├── services/
│   │   └── api_service.dart         # HTTP API client
│   ├── theme/
│   │   └── app_theme.dart           # App theme configuration
│   └── main.dart                    # App entry point
├── assets/
│   ├── images/
│   ├── icons/
│   └── fonts/
├── pubspec.yaml                     # Dependencies
└── README.md
```

## Screens

### 1. Login Screen
- Email and password authentication
- Navigate to registration
- Error handling

### 2. Register Screen
- Create new user account
- Full name, email, password
- Navigate back to login

### 3. Home Screen
- Start new scan session
- View recent sessions
- Session history with status
- Logout functionality

### 4. Scan Screen
- View session progress (X/10 fingerprints)
- Grid of 10 finger positions
- Visual indicators for completed scans
- Generate report when complete

### 5. Fingerprint Capture Screen
- Live camera preview
- Capture fingerprint image
- Pick from gallery option
- Upload to backend

### 6. Report Screen
- Overall quality score
- Summary statistics
- Individual finger quality scores
- Download PDF report
- Visual quality indicators

## State Management

### AuthProvider
- User authentication state
- Login/register/logout
- Token management
- Error handling

### ScanProvider
- Current scan session
- Session list
- Fingerprint upload
- Report generation
- Loading states

## API Integration

All API calls are handled through `ApiService`:

```dart
// Example usage
final apiService = ApiService();
final response = await apiService.post('/auth/login', data: {
  'email': 'user@example.com',
  'password': 'password',
});
```

### Endpoints Used

- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /scans/sessions` - Create scan session
- `GET /scans/sessions` - List sessions
- `POST /scans/sessions/{id}/fingerprints` - Upload fingerprint
- `POST /reports/sessions/{id}/generate` - Generate report

## Building for Production

### Android

```bash
flutter build apk --release
```

Output: `build/app/outputs/flutter-apk/app-release.apk`

### iOS

```bash
flutter build ios --release
```

## Configuration

### Android Permissions

Add to `android/app/src/main/AndroidManifest.xml`:

```xml
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
```

### iOS Permissions

Add to `ios/Runner/Info.plist`:

```xml
<key>NSCameraUsageDescription</key>
<string>Camera access is required to capture fingerprints</string>
<key>NSPhotoLibraryUsageDescription</key>
<string>Photo library access is required to select fingerprint images</string>
```

## Development

### Run Tests

```bash
flutter test
```

### Format Code

```bash
flutter format lib/
```

### Analyze Code

```bash
flutter analyze
```

## Dependencies

### Core
- `flutter` - Flutter SDK
- `provider` - State management
- `go_router` - Navigation

### Networking
- `http` - HTTP client
- `dio` - Advanced HTTP client

### Storage
- `shared_preferences` - Key-value storage
- `hive` - NoSQL database
- `hive_flutter` - Hive Flutter integration

### Camera & Images
- `camera` - Camera access
- `image_picker` - Image selection
- `image` - Image processing

### UI
- `flutter_svg` - SVG support
- `google_fonts` - Custom fonts

### Utilities
- `intl` - Internationalization
- `uuid` - UUID generation
- `logger` - Logging

## Troubleshooting

### Camera Not Working
- Check permissions in AndroidManifest.xml / Info.plist
- Ensure camera permission is granted in device settings
- Test on physical device (emulator camera may not work properly)

### API Connection Failed
- Verify backend is running
- Check API endpoint URL in app_config.dart
- For physical devices, use computer's IP address
- Ensure firewall allows connections

### Build Errors
- Run `flutter clean`
- Run `flutter pub get`
- Delete `build/` folder
- Restart IDE

## Next Steps

1. Add offline support with local database
2. Implement biometric authentication
3. Add image quality preview before upload
4. Implement PDF viewer
5. Add multi-language support
6. Implement push notifications
7. Add analytics and crash reporting

## License

Proprietary

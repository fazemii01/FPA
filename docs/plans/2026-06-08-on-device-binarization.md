# On-Device Fingerprint Binarization & Preview Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement client-side fingerprint binarization and cleaning using the native `opencv_dart` library in FPA mobile. This enables operators to see a precise, clean, black-and-white fingerprint stamp preview in real-time, preventing JPEG compression artifacts from degrading the binarization quality.

**Architecture:** We will create an on-device image processing service using OpenCV's native bindings. The app will process the cropped image, generate a clean binarized image, display it in the preview card, and upload both the raw cropped image (for backend quality analysis) and the enhanced binarized image (for direct database storage and report generation).

**Tech Stack:** Flutter, Dart, `opencv_dart` (OpenCV C++ bindings via FFI), FastAPI, Python.

---

## User Review Required

> [!IMPORTANT]
> **Manual Environment Sync:** Although `opencv_dart` is already listed in the mobile app's `pubspec.yaml`, you must run `flutter pub get` in the mobile directory to ensure the packages are fully synced and built for your target OS (Windows/Android/iOS).

---

## Open Questions

None identified. The design is fully backward-compatible with the existing database and API schemas.

---

## Proposed Changes

### Task 1: Initialize and Test OpenCV Package Sync

**Files:**
- Modify: [pubspec.yaml](file:///e:/my%20project/ALLIA/FPA/mobile/pubspec.yaml) (Verify/Sync)

**Step 1: Verify dependency list**
Ensure `opencv_dart: ^1.4.5` is present in dependencies.

**Step 2: Sync dependencies**
Let the user run `flutter pub get` in `e:\my project\ALLIA\FPA\mobile` to fetch and compile the OpenCV library binaries.

---

### Task 2: Create On-Device OpenCV Service

**Files:**
- Create: `mobile/lib/services/opencv_service.dart`

**Step 1: Write OpenCVService skeleton**
Create a new file `mobile/lib/services/opencv_service.dart` and implement a static method to perform grayscale, CLAHE, Gaussian blur, unsharp masking, and adaptive binarization.

```dart
import 'dart:io';
import 'package:opencv_dart/opencv_dart.dart' as cv;

class OpenCVService {
  /// Processes a raw fingerprint crop and saves a clean binarized PNG.
  /// Returns the path to the saved binarized image.
  static Future<String> binarizeFingerprint(String inputPath) async {
    final file = File(inputPath);
    if (!await file.exists()) {
      throw Exception('Input file does not exist: $inputPath');
    }

    // 1. Read input image into Mat
    final src = cv.imread(inputPath);
    if (src.isEmpty) {
      throw Exception('Failed to load image into OpenCV Mat');
    }

    cv.Mat? gray;
    cv.Mat? enhanced;
    cv.Mat? blurred;
    cv.Mat? sharpened;
    cv.Mat? binary;
    cv.Mat? inverted;
    cv.CLAHE? clahe;

    try {
      // 2. Convert to Grayscale
      gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY);

      // 3. Contrast enhancement using CLAHE (clipLimit = 3.0, tileGridSize = 8x8)
      clahe = cv.createCLAHE(clipLimit: 3.0, tileGridSize: cv.Size(8, 8));
      enhanced = clahe.apply(gray);

      // 4. Denoising using Gaussian Blur
      blurred = cv.GaussianBlur(enhanced, cv.Size(5, 5), 0);

      // 5. Sharpening using Unsharp Masking (addWeighted: 2.0 * enhanced - 1.0 * blurred)
      sharpened = cv.addWeighted(enhanced, 2.0, blurred, -1.0, 0.0);

      // 6. Gaussian Adaptive Thresholding (invert binarized ridges)
      binary = cv.adaptiveThreshold(
        sharpened,
        255,
        cv.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv.THRESH_BINARY_INV,
        41, // block size
        4.0, // C parameter
      );

      // 7. Revert polarity to standard black ridges on white background
      inverted = cv.bitwise_not(binary);

      // 8. Write output to enhanced file path (PNG for zero compression loss)
      final outputPath = inputPath.replaceAll(RegExp(r'\.(jpg|jpeg|png)$'), '_enhanced.png');
      cv.imwrite(outputPath, inverted);

      return outputPath;
    } finally {
      // Clean up all native resources to prevent memory leaks
      src.dispose();
      gray?.dispose();
      enhanced?.dispose();
      blurred?.dispose();
      sharpened?.dispose();
      binary?.dispose();
      inverted?.dispose();
      clahe?.dispose();
    }
  }
}
```

---

### Task 3: Update API and Scan Provider for Multi-File Upload

**Files:**
- Modify: [api_service.dart](file:///e:/my%20project/ALLIA/FPA/mobile/lib/services/api_service.dart:99-118)
- Modify: [scan_provider.dart](file:///e:/my%20project/ALLIA/FPA/mobile/lib/providers/scan_provider.dart:85-142)

**Step 1: Modify ApiService.uploadFile**
Update the upload method to accept an optional `enhancedImagePath` and attach it to the `FormData` body as `'enhanced_file'`.

```dart
  Future<dynamic> uploadFile(
    String endpoint, {
    required String imagePath,
    String? enhancedImagePath,
    required String fingerPosition,
  }) async {
    try {
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(imagePath, filename: 'raw.jpg'),
        if (enhancedImagePath != null)
          'enhanced_file': await MultipartFile.fromFile(enhancedImagePath, filename: 'enhanced.png'),
      });

      final response = await _dio.post(
        endpoint,
        data: formData,
        queryParameters: {'finger_position': fingerPosition},
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }
```

**Step 2: Modify ScanProvider.uploadFingerprint**
Update the method signature and call parameters to support passing the enhanced file path.

```dart
  Future<bool> uploadFingerprint({
    required int sessionId,
    required String fingerPosition,
    required String imagePath,
    String? enhancedImagePath,
  }) async {
    _isLoading = true;
    _error = null;
    _lastDebugImages = null;
    notifyListeners();

    try {
      final response = await _apiService.uploadFile(
        '/scans/sessions/$sessionId/fingerprints',
        imagePath: imagePath,
        enhancedImagePath: enhancedImagePath,
        fingerPosition: fingerPosition,
      );
      // ... (rest remains unchanged)
```

---

### Task 4: Integrate Binarization and Preview into Capture UI

**Files:**
- Modify: [camera_scanner_screen.dart](file:///e:/my%20project/ALLIA/FPA/mobile/lib/screens/scan/camera_scanner_screen.dart)

**Step 1: Add state variable for enhanced image path**
In `_CameraScannerScreenState`, add:
```dart
  String? _enhancedImagePath;
```

**Step 2: Update _captureImage and _pickFromGallery to run binarization**
Import `opencv_service.dart`. Enhance the image immediately after cropping.

```dart
  Future<void> _captureImage() async {
    if (_cameraController == null || _isCapturing) return;

    try {
      setState(() => _isCapturing = true);
      final image = await _cameraController!.takePicture();
      await _cropToGuide(image.path);
      
      // Run local OpenCV binarization
      final enhancedPath = await OpenCVService.binarizeFingerprint(image.path);

      setState(() {
        _capturedImage = image;
        _enhancedImagePath = enhancedPath;
        _showPreview = true;
        _qualityScore = 75.0;
        _isCapturing = false;
      });
    } catch (e) {
      print('Error capturing image: $e');
      setState(() => _isCapturing = false);
    }
  }
```
*Apply the same logical change to `_pickFromGallery()`.*

**Step 3: Update preview image widget to display the enhanced version**
Modify `_buildPreview(String label)` to render the local binarized PNG instead of the raw image, giving the operator instant precision validation:

```dart
  Widget _buildPreview(String label) {
    return Column(
      children: [
        Expanded(
          child: Image.file(
            File(_enhancedImagePath ?? _capturedImage!.path),
            fit: BoxFit.contain, // Contain fits the square fingerprint guide cleanly
          ),
        ),
        // ... (rest remains unchanged)
```

**Step 4: Pass enhanced image path during upload**
Update `_uploadFingerprint()` to pass the enhanced path:
```dart
    final success = await scanProvider.uploadFingerprint(
      sessionId: widget.sessionId,
      fingerPosition: widget.fingerPosition,
      imagePath: _capturedImage!.path,
      enhancedImagePath: _enhancedImagePath,
    );
```

**Step 5: Reset path on retry**
In `_retryCapture()`, reset `_enhancedImagePath = null;`.

---

### Task 5: Handle Enhanced Uploads on FastAPI Backend

**Files:**
- Modify: [scan.py](file:///e:/my%20project/ALLIA/FPA/backend/app/routers/scan.py:90-155)

**Step 6.1: Update upload_fingerprint route parameters**
Modify the endpoint signature to accept the optional `enhanced_file` multipart file.

```python
async def upload_fingerprint(
    session_id: int,
    finger_position: FingerPositionEnum,
    file: UploadFile = File(...),
    enhanced_file: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin),
):
```

**Step 6.2: Store client-binarized image if uploaded**
Read the `enhanced_file` bytes if present. Use it as the `normalized_data` that goes to MinIO, bypassing backend image binarization.

```python
    file_data = await file.read()
    
    # Process features on the raw crop to keep scoring consistent
    processing_result = image_processor.process_fingerprint(file_data)
    quality_score = processing_result["quality_score"]

    if quality_score < 70.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": processing_result.get("reject_reason", "Kualitas sidik jari terlalu rendah."),
                "debug_images": processing_result.get("debug_images", {})
            }
        )

    features = processing_result["features"]
    
    # Use client-processed lossless binary PNG if available, fallback to server normalization
    if enhanced_file:
        normalized_data = await enhanced_file.read()
    else:
        normalized_data = image_processor.normalize_fingerprint(file_data)

    object_name = (
        f"fingerprints/{current_user.id}/{session_id}/"
        f"{finger_position.value}_{uuid.uuid4()}.png"
    )
    minio_service.upload_fingerprint(normalized_data, object_name)
```

---

## Verification Plan

### Automated Tests
* We can run the backend tests to ensure the endpoints are still fully compatible:
  * `pytest backend/tests/` or running the `test_binarization.py` script.

### Manual Verification
1. **Dependency Sync:** Run `flutter pub get` and verify compilation succeeds.
2. **On-device Processing:** Run the Flutter app, capture a fingerprint, and verify that the preview card immediately displays a sharp, binarized black-and-white fingerprint pattern (not the raw color photograph).
3. **Upload Success:** Verify the upload completes successfully without backend warnings, and check that the stored image in MinIO matches the precise binarized preview from the phone.

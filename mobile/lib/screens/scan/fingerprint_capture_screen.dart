import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'package:camera/camera.dart';
import 'package:image_picker/image_picker.dart';
import 'package:image/image.dart' as img_lib;
import 'dart:io';
import 'dart:convert';
import '../../config/app_config.dart';
import '../../providers/scan_provider.dart';
import '../../shared/widgets/circular_guide_overlay.dart';

class FingerprintCaptureScreen extends StatefulWidget {
  final int sessionId;
  final String fingerPosition;

  const FingerprintCaptureScreen({
    Key? key,
    required this.sessionId,
    required this.fingerPosition,
  }) : super(key: key);

  @override
  State<FingerprintCaptureScreen> createState() =>
      _FingerprintCaptureScreenState();
}

class _FingerprintCaptureScreenState extends State<FingerprintCaptureScreen> {
  CameraController? _cameraController;
  Future<void>? _initializeControllerFuture;
  final ImagePicker _imagePicker = ImagePicker();
  bool _isCapturing = false;
  bool _isTorchOn = true;
  double _minZoom = 1.0;
  double _maxZoom = 4.0;
  double _currentZoom = 1.8;

  @override
  void initState() {
    super.initState();
    _initializeControllerFuture = _initializeCamera();
  }

  Future<void> _initializeCamera() async {
    try {
      final cameras = await availableCameras();
      if (cameras.isNotEmpty) {
        final backCamera = cameras.firstWhere(
          (c) => c.lensDirection == CameraLensDirection.back,
          orElse: () => cameras.first,
        );
        _cameraController = CameraController(
          backCamera,
          ResolutionPreset.high,
          enableAudio: false,
          imageFormatGroup: ImageFormatGroup.jpeg,
        );
        await _cameraController!.initialize();
        try {
          // Query min/max zoom to avoid out-of-bounds errors on different devices
          double minZoom = await _cameraController!.getMinZoomLevel();
          double maxZoom = await _cameraController!.getMaxZoomLevel();
          double targetZoom = 1.8;
          if (targetZoom > maxZoom) targetZoom = maxZoom;
          if (targetZoom < minZoom) targetZoom = minZoom;
          
          setState(() {
            _minZoom = minZoom;
            _maxZoom = maxZoom;
            _currentZoom = targetZoom;
          });
          await _cameraController!.setZoomLevel(_currentZoom);

          // Continuous autofocus — camera keeps re-focusing as finger moves closer
          await _cameraController!.setFocusMode(FocusMode.auto);
          await _cameraController!.setExposureMode(ExposureMode.auto);
          await _cameraController!.setFlashMode(FlashMode.torch);
          // Under-expose more strongly to prevent overexposure under the torch
          await _cameraController!.setExposureOffset(-1.5);
        } catch (e) {
          print('Error configuring camera: $e');
        }
      }
    } catch (e) {
      print('Error initializing camera: $e');
    }
  }

  @override
  void dispose() {
    try {
      _cameraController?.setFlashMode(FlashMode.off);
    } catch (_) {}
    _cameraController?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final label = AppConstants.fingerLabels[widget.fingerPosition]!;

    return Scaffold(
      appBar: AppBar(
        title: Text('Capture $label'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go('/scan'),
        ),
      ),
      body: _initializeControllerFuture == null
          ? const Center(child: CircularProgressIndicator())
          : FutureBuilder<void>(
        future: _initializeControllerFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.done) {
            if (_cameraController == null || snapshot.hasError) {
              return Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.camera_alt_outlined,
                        size: 64, color: Colors.grey),
                    const SizedBox(height: 16),
                    const Text('Kamera tidak tersedia'),
                    const SizedBox(height: 24),
                    ElevatedButton.icon(
                      onPressed: _pickFromGallery,
                      icon: const Icon(Icons.image),
                      label: const Text('Pilih dari Galeri'),
                    ),
                  ],
                ),
              );
            }
            return Stack(
              children: [
                Positioned.fill(
                  child: GestureDetector(
                    onTapDown: (details) {
                      if (_cameraController != null && _cameraController!.value.isInitialized) {
                        final size = MediaQuery.of(context).size;
                        final x = details.localPosition.dx / size.width;
                        final y = details.localPosition.dy / size.height;
                        _cameraController!.setFocusPoint(Offset(x, y)).catchError((_) {});
                        _cameraController!.setFocusMode(FocusMode.auto).catchError((_) {});
                      }
                    },
                    child: CameraPreview(_cameraController!),
                  ),
                ),
                Positioned.fill(
                  bottom: 170,
                  child: CircularGuideOverlay(
                    fingerLabel: label,
                    qualityScore: 0,
                  ),
                ),
                Positioned(
                  top: 16,
                  left: 16,
                  right: 16,
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 16,
                            vertical: 10,
                          ),
                          decoration: BoxDecoration(
                            color: Colors.black.withValues(alpha: 0.55),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text(
                            'Jangan terlalu dekat jika blur. Arahkan UJUNG jari (bukan ruas) ke kamera. Pastikan ridges/guratan terlihat jelas.',
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 13,
                              fontWeight: FontWeight.w500,
                            ),
                            textAlign: TextAlign.center,
                          ),
                        ),
                      ),
                      Container(
                        decoration: BoxDecoration(
                          color: Colors.black.withValues(alpha: 0.5),
                          shape: BoxShape.circle,
                        ),
                        child: IconButton(
                          icon: Icon(
                            _isTorchOn ? Icons.flash_on : Icons.flash_off,
                            color: _isTorchOn ? Colors.yellow : Colors.white,
                          ),
                          onPressed: _toggleTorch,
                        ),
                      ),
                    ],
                  ),
                ),
                // Floating Zoom Controller Overlay
                Positioned(
                  bottom: 110,
                  left: 24,
                  right: 24,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.black.withValues(alpha: 0.6),
                      borderRadius: BorderRadius.circular(24),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.zoom_out, color: Colors.white70, size: 20),
                        Expanded(
                          child: Slider(
                            value: _currentZoom,
                            min: _minZoom,
                            max: _maxZoom,
                            activeColor: Theme.of(context).primaryColor,
                            inactiveColor: Colors.white30,
                            onChanged: (value) async {
                              setState(() {
                                _currentZoom = value;
                              });
                              await _cameraController?.setZoomLevel(value);
                            },
                          ),
                        ),
                        Text(
                          '${_currentZoom.toStringAsFixed(1)}x',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(width: 4),
                      const Icon(Icons.zoom_in, color: Colors.white70, size: 20),
                    ],
                  ),
                ),
              ),
                Positioned(
                  bottom: 0,
                  left: 0,
                  right: 0,
                  child: Container(
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.topCenter,
                        end: Alignment.bottomCenter,
                        colors: [
                          Colors.transparent,
                          Colors.black.withValues(alpha: 0.7),
                        ],
                      ),
                    ),
                    padding: const EdgeInsets.fromLTRB(16, 32, 16, 24),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      children: [
                        _circleButton(
                          icon: Icons.image_outlined,
                          label: 'Galeri',
                          onTap: _isCapturing ? null : _pickFromGallery,
                          size: 56,
                        ),
                        _shutterButton(
                          onTap: _isCapturing ? null : _captureImage,
                        ),
                        const SizedBox(width: 56),
                      ],
                    ),
                  ),
                ),
              ],
            );
          } else {
            return const Center(child: CircularProgressIndicator());
          }
        },
      ),
    );
  }

  Widget _circleButton({
    required IconData icon,
    required String label,
    required VoidCallback? onTap,
    double size = 56,
  }) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Material(
          color: Colors.white.withValues(alpha: 0.15),
          shape: const CircleBorder(),
          child: InkWell(
            customBorder: const CircleBorder(),
            onTap: onTap,
            child: SizedBox(
              width: size,
              height: size,
              child: Icon(icon, color: Colors.white, size: 26),
            ),
          ),
        ),
        const SizedBox(height: 6),
        Text(
          label,
          style: const TextStyle(color: Colors.white, fontSize: 12),
        ),
      ],
    );
  }

  Widget _shutterButton({required VoidCallback? onTap}) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 78,
        height: 78,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          border: Border.all(color: Colors.white, width: 4),
          color: Colors.transparent,
        ),
        child: Center(
          child: Container(
            width: 60,
            height: 60,
            decoration: const BoxDecoration(
              shape: BoxShape.circle,
              color: Colors.white,
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _captureImage() async {
    if (_cameraController == null) return;

    try {
      setState(() => _isCapturing = true);
      final image = await _cameraController!.takePicture();
      // Crop to the oval guide before uploading
      final croppedPath = await _cropToGuide(image.path);
      await _uploadFingerprint(croppedPath);
    } catch (e) {
      print('Error capturing image: $e');
      setState(() => _isCapturing = false);
    }
  }

  Future<void> _toggleTorch() async {
    if (_cameraController == null) return;
    try {
      setState(() => _isTorchOn = !_isTorchOn);
      await _cameraController!.setFlashMode(
        _isTorchOn ? FlashMode.torch : FlashMode.off,
      );
    } catch (e) {
      print('Error toggling torch: $e');
    }
  }

  Future<void> _pickFromGallery() async {
    try {
      setState(() => _isCapturing = true);
      final image = await _imagePicker.pickImage(source: ImageSource.gallery);
      if (image != null) {
        // Crop to the oval guide region before uploading
        final croppedPath = await _cropToGuide(image.path);
        await _uploadFingerprint(croppedPath);
      } else {
        setState(() => _isCapturing = false);
      }
    } catch (e) {
      print('Error picking image: $e');
      setState(() => _isCapturing = false);
    }
  }

  /// Crop the captured image to the guide region.
  ///
  /// CameraPreview uses BoxFit.cover: the sensor image is scaled so it
  /// completely FILLS the screen (some sensor edges are cropped off screen).
  /// We must use cover math, not contain math, or the crop lands in the
  /// wrong part of the sensor image.
  Future<String> _cropToGuide(String imagePath) async {
    try {
      final bytes = await File(imagePath).readAsBytes();
      final raw = img_lib.decodeImage(bytes);
      if (raw == null) return imagePath;

      // Apply EXIF orientation so width/height match CameraPreview display
      final srcImage = img_lib.bakeOrientation(raw);

      final screenSize = MediaQuery.of(context).size;
      final screenW = screenSize.width;
      final screenH = screenSize.height;

      final sensorW = srcImage.width.toDouble();
      final sensorH = srcImage.height.toDouble();

      // BoxFit.cover: scale so preview FILLS the screen.
      final scaleX = screenW / sensorW;
      final scaleY = screenH / sensorH;
      final scale = scaleX > scaleY ? scaleX : scaleY; // max

      // How much the scaled sensor image overflows each screen edge
      final virtualW = sensorW * scale;
      final virtualH = sensorH * scale;
      final overflowX = (virtualW - screenW) / 2.0;
      final overflowY = (virtualH - screenH) / 2.0;

      // Guide centre on screen:
      //   X = screenW / 2  (overlay fills full width)
      //   Y = (screenH - 170) / 2  (overlay has bottom: 170 offset for the shutter bar,
      //                              so it only spans 0..screenH-170 and centres within that)
      const double overlayBottomOffset = 170.0;
      final guideCenterScreenX = screenW / 2.0;
      final guideCenterScreenY = (screenH - overlayBottomOffset) / 2.0;

      // Convert to sensor (file) coords using cover-scale offset
      final cx = (guideCenterScreenX + overflowX) / scale;
      final cy = (guideCenterScreenY + overflowY) / scale;

      // Guide is 200 logical px on screen; convert exactly to sensor pixels.
      // takePicture() saves the already-zoomed content at full output resolution,
      // so the file IS the zoomed view — no zoom correction needed here.
      const double guideSize = 200.0;
      final halfSensor = ((guideSize / 2.0) / scale).round();

      final x = (cx - halfSensor).round().clamp(0, srcImage.width - 1);
      final y = (cy - halfSensor).round().clamp(0, srcImage.height - 1);
      final w = (halfSensor * 2).clamp(1, srcImage.width - x);
      final h = (halfSensor * 2).clamp(1, srcImage.height - y);

      // Crop on the orientation-baked image; backend resizes to 512×512.
      final cropped = img_lib.copyCrop(srcImage, x: x, y: y, width: w, height: h);
      final croppedBytes = img_lib.encodeJpg(cropped, quality: 95);
      await File(imagePath).writeAsBytes(croppedBytes);
      return imagePath;
    } catch (e) {
      print('_cropToGuide failed (using original): $e');
      return imagePath;
    }
  }


  Future<void> _uploadFingerprint(String imagePath) async {
    if (!mounted) return;

    final scanProvider = context.read<ScanProvider>();
    final success = await scanProvider.uploadFingerprint(
      sessionId: widget.sessionId,
      fingerPosition: widget.fingerPosition,
      imagePath: imagePath,
    );

    if (success && mounted) {
      context.go('/scan');
    } else {
      setState(() => _isCapturing = false);
      if (mounted) {
        final debugImages = scanProvider.lastDebugImages;
        if (debugImages != null && debugImages.isNotEmpty) {
          _showRejectionDialog(context, scanProvider.error ?? 'Upload failed', debugImages);
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(scanProvider.error ?? 'Upload failed')),
          );
        }
      }
    }
  }

  void _showRejectionDialog(BuildContext context, String reason, Map<String, dynamic> debugImages) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) {
        return AlertDialog(
          title: const Text('Kualitas Tidak Memenuhi Standar', style: TextStyle(color: Colors.red)),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(reason, style: const TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(height: 16),
                const Text('Pastikan jari berada di tengah dan terlihat jelas.', style: TextStyle(fontSize: 12)),
                const SizedBox(height: 16),
                if (debugImages.containsKey('raw_crop'))
                  _buildDebugImage('Gambar yang ditangkap', debugImages['raw_crop'] as String),
                if (debugImages.containsKey('binary_image'))
                  _buildDebugImage('Hasil Analisis (Ridge)', debugImages['binary_image'] as String),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.pop(context);
              },
              child: const Text('Coba Lagi'),
            ),
          ],
        );
      },
    );
  }

  Widget _buildDebugImage(String label, String base64Str) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
        const SizedBox(height: 4),
        Container(
          height: 120,
          width: double.infinity,
          color: Colors.grey[200],
          child: Image.memory(
            base64Decode(base64Str),
            fit: BoxFit.contain,
            errorBuilder: (context, error, stackTrace) => const Icon(Icons.broken_image),
          ),
        ),
        const SizedBox(height: 12),
      ],
    );
  }
}

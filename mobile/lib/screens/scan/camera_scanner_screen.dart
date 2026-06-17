import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
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
import '../../services/opencv_service.dart';
import '../../widgets/app_toast.dart';
import 'package:screen_brightness/screen_brightness.dart';

class CameraScannerScreen extends StatefulWidget {
  final int sessionId;
  final String fingerPosition;
  final int fingerIndex;

  const CameraScannerScreen({
    Key? key,
    required this.sessionId,
    required this.fingerPosition,
    required this.fingerIndex,
  }) : super(key: key);

  @override
  State<CameraScannerScreen> createState() => _CameraScannerScreenState();
}

class _CameraScannerScreenState extends State<CameraScannerScreen> {
  CameraController? _cameraController;
  Future<void>? _initializeControllerFuture;
  final ImagePicker _imagePicker = ImagePicker();
  bool _isCapturing = false;
  XFile? _capturedImage;
  String? _enhancedImagePath;
  bool _showPreview = false;
  double _qualityScore = 0;
  FlashMode _flashMode = FlashMode.torch;
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
        _cameraController = CameraController(
          cameras.first,
          ResolutionPreset.high,
          enableAudio: false,
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

          await _cameraController!.setFocusMode(FocusMode.auto);
          await _cameraController!.setExposureMode(ExposureMode.auto);
          await _cameraController!.setFlashMode(FlashMode.torch);
          // Set focus and exposure points to the center (finger area)
          try {
            if (_cameraController!.value.focusPointSupported) {
              await _cameraController!.setFocusPoint(const Offset(0.5, 0.5));
            }
          } catch (e) {
            print('Error setting focus point: $e');
          }
          
          try {
            if (_cameraController!.value.exposurePointSupported) {
              await _cameraController!.setExposurePoint(const Offset(0.5, 0.5));
            }
          } catch (e) {
            print('Error setting exposure point: $e');
          }
          
          // Query exposure offsets to prevent crashes and set optimal under-exposure
          final minExposure = await _cameraController!.getMinExposureOffset();
          final maxExposure = await _cameraController!.getMaxExposureOffset();
          // Decrease exposure significantly because torch up close blows out the highlights
          double targetExposure = minExposure < -6.0 ? -6.0 : minExposure;
          if (targetExposure > maxExposure) targetExposure = maxExposure;
          await _cameraController!.setExposureOffset(targetExposure);
        } catch (e) {
          print('Error configuring camera: $e');
        }
        
        // Increase screen brightness to 50% while capturing
        try {
          await ScreenBrightness().setScreenBrightness(0.5);
        } catch (e) {
          print('Error setting screen brightness: $e');
        }
      }
    } catch (e) {
      print('Error initializing camera: $e');
    }
  }

  @override
  void dispose() {
    _cameraController?.dispose();
    try {
      ScreenBrightness().resetScreenBrightness();
    } catch (e) {
      print('Error resetting screen brightness: $e');
    }
    super.dispose();
  }

  Future<void> _captureImage() async {
    if (_cameraController == null || _isCapturing) return;

    try {
      setState(() => _isCapturing = true);
      
      // Lock focus before capturing to bypass the slow Camera2 autofocus lock wait
      await _cameraController!.setFocusMode(FocusMode.locked);
      
      final image = await _cameraController!.takePicture();
      // Crop to oval guide
      await _cropToGuide(image.path);
      
      // Run local OpenCV binarization
      final enhancedPath = await OpenCVService.binarizeFingerprint(image.path);

      // Upload immediately
      final scanProvider = context.read<ScanProvider>();
      final success = await scanProvider.uploadFingerprint(
        sessionId: widget.sessionId,
        fingerPosition: widget.fingerPosition,
        imagePath: image.path,
        enhancedImagePath: enhancedPath,
      );

      if (success && mounted) {
        context.go('/scan/progress/${widget.sessionId}/${widget.fingerIndex + 1}');
      } else {
        setState(() => _isCapturing = false);
        try {
          await _cameraController?.setFocusMode(FocusMode.auto);
        } catch (_) {}
        if (mounted) {
          AppToast.showError(context, scanProvider.error ?? 'Unggah gagal');
        }
      }
    } catch (e) {
      print('Error capturing image: $e');
      setState(() => _isCapturing = false);
      try {
        await _cameraController?.setFocusMode(FocusMode.auto);
      } catch (_) {}
    }
  }

  Future<void> _cycleFlashMode() async {
    if (_cameraController == null) return;
    
    FlashMode nextMode;
    switch (_flashMode) {
      case FlashMode.always:
        nextMode = FlashMode.torch;
        break;
      case FlashMode.torch:
        nextMode = FlashMode.off;
        break;
      case FlashMode.off:
      default:
        nextMode = FlashMode.always;
        break;
    }

    try {
      await _cameraController!.setFlashMode(nextMode);
      setState(() {
        _flashMode = nextMode;
      });
    } catch (e) {
      print('Error setting flash mode: $e');
    }
  }

  Future<void> _pickFromGallery() async {
    try {
      setState(() => _isCapturing = true);
      final image = await _imagePicker.pickImage(source: ImageSource.gallery);
      if (image != null) {
        // Crop to oval guide
        await _cropToGuide(image.path);
        
        // Run local OpenCV binarization
        final enhancedPath = await OpenCVService.binarizeFingerprint(image.path);

        // Upload immediately
        final scanProvider = context.read<ScanProvider>();
        final success = await scanProvider.uploadFingerprint(
          sessionId: widget.sessionId,
          fingerPosition: widget.fingerPosition,
          imagePath: image.path,
          enhancedImagePath: enhancedPath,
        );

        if (success && mounted) {
          context.go('/scan/progress/${widget.sessionId}/${widget.fingerIndex + 1}');
        } else {
          setState(() => _isCapturing = false);
          if (mounted) {
            AppToast.showError(context, scanProvider.error ?? 'Unggah gagal');
          }
        }
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
  /// Android cameras often save JPEG in the physical sensor orientation (landscape)
  /// with an EXIF rotation tag.  CameraPreview applies the EXIF rotation visually,
  /// but img_lib.decodeImage() does NOT.  We call bakeOrientation() first so
  /// srcImage.width/height match what the user sees on screen, then use
  /// BoxFit.cover math to map the 200-px guide to sensor pixels.
  Future<void> _cropToGuide(String imagePath) async {
    try {
      final screenSize = MediaQuery.of(context).size;
      final params = CameraCropParams(
        imagePath: imagePath,
        screenW: screenSize.width,
        screenH: screenSize.height,
      );
      await compute(_isolateCameraCrop, params);
    } catch (e) {
      print('_cropToGuide failed: $e');
    }
  }

  Future<void> _uploadFingerprint() async {
    if (_capturedImage == null || !mounted) return;

    final scanProvider = context.read<ScanProvider>();
    final success = await scanProvider.uploadFingerprint(
      sessionId: widget.sessionId,
      fingerPosition: widget.fingerPosition,
      imagePath: _capturedImage!.path,
      enhancedImagePath: _enhancedImagePath,
    );

    if (success && mounted) {
      context.go('/scan/progress/${widget.sessionId}/${widget.fingerIndex + 1}');
    } else {
      if (mounted) {
        final debugImages = scanProvider.lastDebugImages;
        if (debugImages != null && debugImages.isNotEmpty) {
          _showRejectionDialog(context, scanProvider.error ?? 'Upload failed', debugImages);
        } else {
          AppToast.showError(context, scanProvider.error ?? 'Upload failed');
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
                _retryCapture();
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

  void _retryCapture() {
    setState(() {
      _capturedImage = null;
      _enhancedImagePath = null;
      _showPreview = false;
      _qualityScore = 0;
    });
    try {
      _cameraController?.setFocusMode(FocusMode.auto);
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    final label = AppConstants.fingerLabels[widget.fingerPosition]!;

    return Scaffold(
      appBar: AppBar(
        title: Text('${widget.fingerIndex + 1}/10 - $label'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
      ),
      body: _showPreview ? _buildPreview(label) : _buildCamera(label),
    );
  }

  Widget _buildCamera(String label) {
    if (_cameraController == null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.camera_alt_outlined, size: 64, color: Colors.grey),
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

    if (_initializeControllerFuture == null) {
      return const Center(child: CircularProgressIndicator());
    }
    return FutureBuilder<void>(
      future: _initializeControllerFuture,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.done) {
          if (snapshot.hasError) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error_outline, size: 64, color: Colors.red),
                  const SizedBox(height: 16),
                  Text('Error: ${snapshot.error}'),
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
                  onTapDown: (details) async {
                    if (_cameraController != null && _cameraController!.value.isInitialized) {
                      final size = MediaQuery.of(context).size;
                      final x = details.localPosition.dx / size.width;
                      final y = details.localPosition.dy / size.height;
                      
                      try {
                        await _cameraController!.setFocusPoint(Offset(x, y));
                        await _cameraController!.setFocusMode(FocusMode.auto);
                        
                        // Set exposure point dynamically to where the user tapped
                        if (_cameraController!.value.exposurePointSupported) {
                          await _cameraController!.setExposurePoint(Offset(x, y));
                        }
                        
                          // Reset focus and exposure points back to center after 3 seconds
                          Future.delayed(const Duration(seconds: 3), () {
                            if (mounted && _cameraController != null && _cameraController!.value.isInitialized) {
                              if (_cameraController!.value.focusPointSupported) {
                                _cameraController!.setFocusPoint(const Offset(0.5, 0.5)).catchError((e) {
                                  print('Failed to reset focus point: $e');
                                });
                              }
                              if (_cameraController!.value.exposurePointSupported) {
                                _cameraController!.setExposurePoint(const Offset(0.5, 0.5)).catchError((e) {
                                  print('Failed to reset exposure point: $e');
                                });
                              }
                            }
                          });
                      } catch (e) {
                        print('Error setting focus/exposure point: $e');
                      }
                    }
                  },
                  child: CameraPreview(_cameraController!),
                ),
              ),
              Positioned.fill(
                child: CircularGuideOverlay(
                  fingerLabel: label,
                  qualityScore: _qualityScore,
                ),
              ),
              Positioned(
                top: 16,
                right: 16,
                child: Container(
                  decoration: BoxDecoration(
                    color: Colors.black.withValues(alpha: 0.5),
                    shape: BoxShape.circle,
                  ),
                  child: IconButton(
                    icon: Icon(
                      _flashMode == FlashMode.always
                          ? Icons.flash_on
                          : _flashMode == FlashMode.torch
                              ? Icons.highlight
                              : Icons.flash_off,
                      color: _flashMode == FlashMode.always
                          ? Colors.green
                          : _flashMode == FlashMode.torch
                              ? Colors.yellow
                              : Colors.white60,
                    ),
                    onPressed: _cycleFlashMode,
                    tooltip: _flashMode == FlashMode.always
                        ? 'Flash On Capture'
                        : _flashMode == FlashMode.torch
                            ? 'Continuous Torch'
                            : 'Flash Off',
                  ),
                ),
              ),
              // Floating Zoom Controller Overlay
              Positioned(
                bottom: 160,
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
                  color: Colors.black87,
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    children: [
                      Text(
                        'Jangan terlalu dekat jika blur. Gunakan zoom 1.5x sampai 2.0x dan ambil saat ridge mulai terlihat.',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 14,
                        ),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 24),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                        children: [
                          ElevatedButton.icon(
                            onPressed: _isCapturing ? null : _captureImage,
                            icon: const Icon(Icons.camera),
                            label: const Text('Tangkap'),
                          ),
                          ElevatedButton.icon(
                            onPressed: _isCapturing ? null : _pickFromGallery,
                            icon: const Icon(Icons.image),
                            label: const Text('Galeri'),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              if (_isCapturing)
                Container(
                  color: Colors.black.withOpacity(0.55),
                  child: const Center(
                    child: Card(
                      child: Padding(
                        padding: EdgeInsets.all(24),
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            CircularProgressIndicator(),
                            SizedBox(height: 16),
                            Text(
                              'Memproses & Mengunggah...',
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: 16,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
            ],
          );
        } else {
          return const Center(child: CircularProgressIndicator());
        }
      },
    );
  }

  Widget _buildPreview(String label) {
    return Column(
      children: [
        Expanded(
          child: Image.file(
            File(_enhancedImagePath ?? _capturedImage!.path),
            fit: BoxFit.contain,
          ),
        ),
        Container(
          color: Colors.black87,
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Card(
                color: Colors.grey[800],
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text(
                            'Kualitas Gambar',
                            style: TextStyle(color: Colors.white),
                          ),
                          Text(
                            '${_qualityScore.toStringAsFixed(0)}%',
                            style: const TextStyle(
                              color: Colors.green,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      ClipRRect(
                        borderRadius: BorderRadius.circular(4),
                        child: LinearProgressIndicator(
                          value: _qualityScore / 100,
                          minHeight: 6,
                          backgroundColor: Colors.grey[600],
                          valueColor: AlwaysStoppedAnimation<Color>(
                            _qualityScore >= 70 ? Colors.green : Colors.orange,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  OutlinedButton.icon(
                    onPressed: _retryCapture,
                    icon: const Icon(Icons.refresh),
                    label: const Text('Ulangi'),
                  ),
                  ElevatedButton.icon(
                    onPressed: _uploadFingerprint,
                    icon: const Icon(Icons.check),
                    label: const Text('Terima'),
                  ),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class CameraCropParams {
  final String imagePath;
  final double screenW;
  final double screenH;

  CameraCropParams({
    required this.imagePath,
    required this.screenW,
    required this.screenH,
  });
}

Future<void> _isolateCameraCrop(CameraCropParams params) async {
  final bytes = await File(params.imagePath).readAsBytes();
  final raw = img_lib.decodeImage(bytes);
  if (raw == null) return;

  final srcImage = img_lib.bakeOrientation(raw);

  final sensorW = srcImage.width.toDouble();
  final sensorH = srcImage.height.toDouble();

  final scaleX = params.screenW / sensorW;
  final scaleY = params.screenH / sensorH;
  final scale = scaleX > scaleY ? scaleX : scaleY;

  final virtualW = sensorW * scale;
  final virtualH = sensorH * scale;
  final overflowX = (virtualW - params.screenW) / 2.0;
  final overflowY = (virtualH - params.screenH) / 2.0;

  final cx = (params.screenW / 2.0 + overflowX) / scale;
  final cy = (params.screenH / 2.0 + overflowY) / scale;

  const double guideSize = 200.0;
  final halfSensor = ((guideSize / 2.0) / scale).round();

  final x = (cx - halfSensor).round().clamp(0, srcImage.width - 1);
  final y = (cy - halfSensor).round().clamp(0, srcImage.height - 1);
  final w = (halfSensor * 2).clamp(1, srcImage.width - x);
  final h = (halfSensor * 2).clamp(1, srcImage.height - y);

  final cropped = img_lib.copyCrop(srcImage, x: x, y: y, width: w, height: h);
  final croppedBytes = img_lib.encodeJpg(cropped, quality: 95);
  await File(params.imagePath).writeAsBytes(croppedBytes);
}

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'package:camera/camera.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import '../../config/app_config.dart';
import '../../providers/scan_provider.dart';
import '../../shared/widgets/circular_guide_overlay.dart';

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
  bool _showPreview = false;
  double _qualityScore = 0;

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
        );
        await _cameraController!.initialize();
      }
    } catch (e) {
      print('Error initializing camera: $e');
    }
  }

  @override
  void dispose() {
    _cameraController?.dispose();
    super.dispose();
  }

  Future<void> _captureImage() async {
    if (_cameraController == null || _isCapturing) return;

    try {
      setState(() => _isCapturing = true);
      final image = await _cameraController!.takePicture();
      setState(() {
        _capturedImage = image;
        _showPreview = true;
        _qualityScore = 75.0;
        _isCapturing = false;
      });
    } catch (e) {
      print('Error capturing image: $e');
      setState(() => _isCapturing = false);
    }
  }

  Future<void> _pickFromGallery() async {
    try {
      setState(() => _isCapturing = true);
      final image = await _imagePicker.pickImage(source: ImageSource.gallery);
      if (image != null) {
        setState(() {
          _capturedImage = image;
          _showPreview = true;
          _qualityScore = 70.0;
          _isCapturing = false;
        });
      } else {
        setState(() => _isCapturing = false);
      }
    } catch (e) {
      print('Error picking image: $e');
      setState(() => _isCapturing = false);
    }
  }

  Future<void> _uploadFingerprint() async {
    if (_capturedImage == null || !mounted) return;

    final scanProvider = context.read<ScanProvider>();
    final success = await scanProvider.uploadFingerprint(
      sessionId: widget.sessionId,
      fingerPosition: widget.fingerPosition,
      imagePath: _capturedImage!.path,
    );

    if (success && mounted) {
      context.go('/scan/progress/${widget.sessionId}/${widget.fingerIndex + 1}');
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(scanProvider.error ?? 'Upload failed')),
        );
      }
    }
  }

  void _retryCapture() {
    setState(() {
      _capturedImage = null;
      _showPreview = false;
      _qualityScore = 0;
    });
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
                child: CameraPreview(_cameraController!),
              ),
              Positioned.fill(
                child: CircularGuideOverlay(
                  fingerLabel: label,
                  qualityScore: _qualityScore,
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
                        'Posisikan $label di tengah lingkaran',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 16,
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
            File(_capturedImage!.path),
            fit: BoxFit.cover,
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

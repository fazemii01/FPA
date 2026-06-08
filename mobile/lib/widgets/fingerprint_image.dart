import 'dart:typed_data';
import 'package:flutter/material.dart';
import '../services/api_service.dart';

/// A widget that loads a fingerprint image from the backend proxy endpoint.
///
/// The backend endpoint `GET /scans/fingerprints/{id}/image` fetches the raw
/// PNG bytes from MinIO and streams them back — so we use [Image.memory] after
/// fetching with Dio (which adds the Authorization header automatically).
class FingerprintImage extends StatefulWidget {
  /// The fingerprint record `id` from the database.
  final int fingerprintId;

  final double height;
  final BoxFit fit;

  const FingerprintImage({
    Key? key,
    required this.fingerprintId,
    this.height = 200,
    this.fit = BoxFit.cover,
  }) : super(key: key);

  @override
  State<FingerprintImage> createState() => _FingerprintImageState();
}

class _FingerprintImageState extends State<FingerprintImage> {
  final ApiService _api = ApiService();
  late Future<Uint8List> _future;

  @override
  void initState() {
    super.initState();
    _loadImage();
  }

  void _loadImage() {
    _future = _api
        .getBytes('/scans/fingerprints/${widget.fingerprintId}/image')
        .then((bytes) => Uint8List.fromList(bytes));
  }

  @override
  void didUpdateWidget(FingerprintImage oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.fingerprintId != widget.fingerprintId) {
      setState(_loadImage);
    }
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<Uint8List>(
      future: _future,
      builder: (context, snapshot) {
        // Loading
        if (snapshot.connectionState == ConnectionState.waiting) {
          return SizedBox(
            height: widget.height,
            child: const Center(
              child: CircularProgressIndicator(strokeWidth: 2),
            ),
          );
        }

        // Error or empty
        if (snapshot.hasError || !snapshot.hasData || snapshot.data!.isEmpty) {
          return SizedBox(
            height: widget.height,
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.broken_image_outlined,
                      size: 48, color: Colors.grey[400]),
                  const SizedBox(height: 8),
                  Text(
                    'Gagal memuat gambar',
                    style: TextStyle(color: Colors.grey[500], fontSize: 12),
                  ),
                ],
              ),
            ),
          );
        }

        // Success
        return Image.memory(
          snapshot.data!,
          height: widget.height,
          fit: widget.fit,
          errorBuilder: (_, __, ___) => SizedBox(
            height: widget.height,
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.broken_image_outlined,
                      size: 48, color: Colors.grey[400]),
                  const SizedBox(height: 8),
                  Text(
                    'Gambar tidak valid',
                    style: TextStyle(color: Colors.grey[500], fontSize: 12),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }
}

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

    cv.Mat? grayToDispose;
    cv.Mat? enhancedToDispose;
    cv.Mat? blurredToDispose;
    cv.Mat? sharpenedToDispose;
    cv.Mat? binaryToDispose;
    cv.CLAHE? claheToDispose;

    try {
      // 2. Extract Red channel to suppress red blood spots / stains (noise)
      // Since blood/red spots appear bright in the Red channel, they merge with
      // the bright background skin, leaving only the neutral ridges as dark details.
      final channels = cv.split(src);
      if (channels.length < 3) {
        throw Exception('Image does not have 3 channels');
      }
      final gray = channels[2];
      channels[0].dispose();
      channels[1].dispose();
      grayToDispose = gray;

      // 3. Contrast enhancement using CLAHE (clipLimit = 3.0, tileGridSize = (8, 8) record)
      final clahe = cv.createCLAHE(clipLimit: 3.0, tileGridSize: (8, 8));
      claheToDispose = clahe;
      final enhanced = clahe.apply(gray);
      enhancedToDispose = enhanced;

      // 4. Denoising using Gaussian Blur (kernel size (5, 5) record)
      final blurred = cv.gaussianBlur(enhanced, (5, 5), 0);
      blurredToDispose = blurred;

      // 5. Sharpening using Unsharp Masking (addWeighted: 2.0 * enhanced - 1.0 * blurred)
      final sharpened = cv.addWeighted(enhanced, 2.0, blurred, -1.0, 0.0);
      sharpenedToDispose = sharpened;

      // 6. Gaussian Adaptive Thresholding (ridges become black (0), background becomes white (255))
      final binary = cv.adaptiveThreshold(
        sharpened,
        255,
        cv.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv.THRESH_BINARY,
        41, // block size
        4.0, // C parameter
      );
      binaryToDispose = binary;

      // 7. Write output to enhanced file path (PNG for zero compression loss)
      final outputPath = inputPath.replaceAll(RegExp(r'\.(jpg|jpeg|png)$'), '_enhanced.png');
      cv.imwrite(outputPath, binary);

      return outputPath;
    } finally {
      // Clean up all native resources to prevent memory leaks
      src.dispose();
      grayToDispose?.dispose();
      enhancedToDispose?.dispose();
      blurredToDispose?.dispose();
      sharpenedToDispose?.dispose();
      binaryToDispose?.dispose();
      claheToDispose?.dispose();
    }
  }
}

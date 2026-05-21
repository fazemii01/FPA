class StorageService {
  static Future<void> saveCapturedImage(String fingerPosition, String imagePath) async {
    print('Saving captured image for $fingerPosition: $imagePath');
  }

  static Future<String?> getCapturedImage(String fingerPosition) async {
    print('Retrieving captured image for $fingerPosition');
    return null;
  }

  static Future<void> clearCapturedImages() async {
    print('Clearing all captured images');
  }

  static Future<List<String>> getAllCapturedImages() async {
    print('Getting all captured images');
    return [];
  }
}

import 'package:flutter_test/flutter_test.dart';
import 'package:mobile_app/services/storage_service.dart';

void main() {
  late StorageService storageService;

  setUp(() {
    storageService = StorageService();
  });

  group('StorageService', () {
    test('can be instantiated', () {
      expect(storageService, isNotNull);
      expect(storageService, isA<StorageService>());
    });

    test('has saveTokens method', () {
      expect(storageService.saveTokens, isNotNull);
    });

    test('has getToken method', () {
      expect(storageService.getToken, isNotNull);
    });

    test('has getRefreshToken method', () {
      expect(storageService.getRefreshToken, isNotNull);
    });

    test('has clearTokens method', () {
      expect(storageService.clearTokens, isNotNull);
    });

    test('has hasTokens method', () {
      expect(storageService.hasTokens, isNotNull);
    });

    // Note: Full integration tests with actual secure storage would require
    // running on a device/emulator. These are basic interface tests.
  });
}
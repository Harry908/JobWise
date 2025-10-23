import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile_app/app.dart';
import 'package:mobile_app/config/app_config.dart';

void main() {
  setUpAll(() async {
    // Load environment configuration for tests
    try {
      await AppConfig.load();
    } catch (e) {
      // Ignore config loading errors in tests
    }
  });

  testWidgets('App starts without crashing', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(ProviderScope(child: App()));

    // Verify that the login screen is shown
    expect(find.text('JobWise'), findsOneWidget);
    expect(find.text('AI-Powered Job Application Assistant'), findsOneWidget);
  });
}

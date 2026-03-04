import 'package:cloudburst_mobile/src/app.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('App boots and shows title', (WidgetTester tester) async {
    await tester.pumpWidget(const CloudburstApp());
    expect(find.text('Himalayan Cloudburst Intelligence System'), findsOneWidget);
  });
}

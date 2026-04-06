import 'package:cloudburst_mobile/src/app.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('App boots and shows splash', (WidgetTester tester) async {
    await tester.pumpWidget(const CloudburstApp());
    await tester.pump();
    expect(find.text('Initializing district intelligence'), findsOneWidget);
  });
}

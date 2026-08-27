import 'package:flutter_test/flutter_test.dart';
import 'package:wellnexa/main.dart';

void main() {
  testWidgets('App renders Home Screen title', (WidgetTester tester) async {
    await tester.pumpWidget(const WellNexaApp());
    await tester.pumpAndSettle();
    expect(find.text('WellNexa AI'), findsWidgets);
  });
}

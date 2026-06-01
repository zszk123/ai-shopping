// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:ai_shop/app.dart';
import 'package:ai_shop/features/compare/compare_page.dart';
import 'package:ai_shop/features/compare/compare_provider.dart';
import 'package:ai_shop/shared/services/api_client.dart';

class _FakeCompareNotifier extends CompareNotifier {
  _FakeCompareNotifier() : super(ApiClient()) {
    state = const CompareState(status: CompareStatus.error, errorMsg: '识图失败');
  }

  @override
  Future<void> compareByKeyword(String keyword) async {
    state = CompareState(
      status: CompareStatus.loading,
      lastSearch: SearchContext(compareType: 3, searchSource: keyword),
    );
  }
}

void main() {
  testWidgets('App smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const ProviderScope(child: AiShopApp()));
    expect(find.byType(MaterialApp), findsOneWidget);
  });

  testWidgets('Compare error page supports manual keyword fallback',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          compareProvider.overrideWith((ref) => _FakeCompareNotifier()),
        ],
        child: const MaterialApp(home: ComparePage()),
      ),
    );

    expect(find.text('关键词比价'), findsOneWidget);
    await tester.tap(find.text('关键词比价'));
    await tester.pumpAndSettle();
    expect(find.text('手动输入商品'), findsOneWidget);
  });
}

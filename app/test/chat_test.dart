// اختبارات الواجهة. الحالات من أسئلة حقيقية وُلّدت على مقالة ويكيبيديا
// «الرعاية الملائمة في وقت مبكر» (مرحلة 3 من arabic-rag-bench).

import 'dart:convert';

import 'package:arabic_rag_app/api.dart';
import 'package:arabic_rag_app/main.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

const _q = 'في أي عام تم اقتراح مصطلح الرعاية الملائمة في وقت مبكر لأول مرة؟';

http.Response _json(Object body, [int status = 200]) => http.Response.bytes(
      utf8.encode(jsonEncode(body)),
      status,
      headers: {'content-type': 'application/json'}, // بلا charset عمداً
    );

Future<void> _ask(WidgetTester tester, http.Client client, String text) async {
  await tester.pumpWidget(
      ArabicRagApp(api: RagApi(baseUrl: 'http://t', client: client)));
  await tester.enterText(find.byKey(const Key('input')), text);
  await tester.tap(find.byKey(const Key('send')));
  await tester.pumpAndSettle();
}

void main() {
  testWidgets('answer with source card renders in RTL', (tester) async {
    final client = MockClient((req) async {
      expect(req.url.path, '/ask');
      expect(jsonDecode(req.body)['question'], _q);
      return _json({
        'answer': 'اقتُرح المصطلح لأول مرة عام 2013.',
        'sources': [
          {
            'title': 'الرعاية الملائمة في وقت مبكر',
            'url': 'https://ar.wikipedia.org/wiki/x',
            'snippet':
                'مصطلح الرعاية الملائمة في وقت مبكر اقترح لأول مرة في عام 2013',
            'score': 0.71,
          }
        ],
      });
    });
    await _ask(tester, client, _q);

    // الجواب العربي يمرّ رغم غياب charset: يثبت أن فكّ utf8 صريح
    expect(find.text('اقتُرح المصطلح لأول مرة عام 2013.'), findsOneWidget);
    expect(find.text('الرعاية الملائمة في وقت مبكر'), findsOneWidget);
    expect(Directionality.of(tester.element(find.byKey(const Key('input')))),
        TextDirection.rtl);
  });

  testWidgets('server error shows Arabic message, not a crash', (tester) async {
    final client = MockClient((_) async => _json({'detail': 'x'}, 500));
    await _ask(tester, client, _q);

    expect(find.text('خطأ من الخادم (500)'), findsOneWidget);
  });

  testWidgets('empty input sends nothing', (tester) async {
    var calls = 0;
    final client = MockClient((_) async {
      calls++;
      return _json({'answer': '', 'sources': []});
    });
    await _ask(tester, client, '   ');

    expect(calls, 0);
  });
}

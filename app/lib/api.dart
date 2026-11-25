import 'dart:convert';

import 'package:http/http.dart' as http;

import 'models.dart';

class RagApiException implements Exception {
  RagApiException(this.message);
  final String message;
  @override
  String toString() => message;
}

class RagApi {
  RagApi({required this.baseUrl, http.Client? client})
      : _client = client ?? http.Client();

  final String baseUrl;
  final http.Client _client;

  Future<Answer> ask(String question) async {
    final http.Response res;
    try {
      res = await _client
          .post(
            Uri.parse('$baseUrl/ask'),
            headers: {'Content-Type': 'application/json; charset=utf-8'},
            body: jsonEncode({'question': question}),
          )
          // الخلفية تولّد الإجابة بنموذج محلي فقد تتأخر؛ دقيقتان سقف معقول
          .timeout(const Duration(minutes: 2));
    } on Exception {
      throw RagApiException('تعذّر الاتصال بالخادم. تأكد أنه يعمل على $baseUrl');
    }
    if (res.statusCode != 200) {
      throw RagApiException('خطأ من الخادم (${res.statusCode})');
    }
    // utf8.decode صريحة: http يفترض latin1 إن غاب charset في الترويسة
    return Answer.fromJson(
      jsonDecode(utf8.decode(res.bodyBytes)) as Map<String, dynamic>,
    );
  }
}

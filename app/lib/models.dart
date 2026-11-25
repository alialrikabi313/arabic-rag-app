/// مصدر واحد مُستشهَد به: مقطع من مقالة مع رابطها ودرجة التشابه.
class Source {
  const Source({
    required this.title,
    required this.url,
    required this.snippet,
    required this.score,
  });

  final String title;
  final String url;
  final String snippet;
  final double score;

  factory Source.fromJson(Map<String, dynamic> j) => Source(
        title: j['title'] as String,
        url: j['url'] as String,
        snippet: j['snippet'] as String,
        score: (j['score'] as num).toDouble(),
      );
}

class Answer {
  const Answer({required this.text, required this.sources});

  final String text;
  final List<Source> sources;

  factory Answer.fromJson(Map<String, dynamic> j) => Answer(
        text: j['answer'] as String,
        sources: (j['sources'] as List)
            .map((s) => Source.fromJson(s as Map<String, dynamic>))
            .toList(),
      );
}

enum Role { user, assistant }

class ChatMessage {
  const ChatMessage({
    required this.role,
    required this.text,
    this.sources = const [],
    this.isError = false,
  });

  final Role role;
  final String text;
  final List<Source> sources;
  final bool isError;
}

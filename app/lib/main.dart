import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';

import 'api.dart';
import 'chat_page.dart';

// عنوان الخلفية يُمرَّر وقت البناء: --dart-define=API_URL=http://10.0.2.2:8000 على محاكي أندرويد
const _apiUrl =
    String.fromEnvironment('API_URL', defaultValue: 'http://localhost:8000');

void main() => runApp(ArabicRagApp(api: RagApi(baseUrl: _apiUrl)));

class ArabicRagApp extends StatelessWidget {
  const ArabicRagApp({super.key, required this.api});

  final RagApi api;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'اسأل ويكيبيديا',
      debugShowCheckedModeBanner: false,
      locale: const Locale('ar'),
      supportedLocales: const [Locale('ar')],
      localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      theme: ThemeData(
        colorSchemeSeed: Colors.teal,
        useMaterial3: true,
        brightness: Brightness.light,
      ),
      darkTheme: ThemeData(
        colorSchemeSeed: Colors.teal,
        useMaterial3: true,
        brightness: Brightness.dark,
      ),
      home: ChatPage(api: api),
    );
  }
}

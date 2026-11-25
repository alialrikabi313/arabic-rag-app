import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

import 'models.dart';

class SourceCard extends StatelessWidget {
  const SourceCard({super.key, required this.source, required this.index});

  final Source source;
  final int index;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Card(
      margin: const EdgeInsets.only(top: 8),
      color: scheme.surfaceContainerHighest,
      child: ListTile(
        dense: true,
        leading: CircleAvatar(
          radius: 12,
          backgroundColor: scheme.primary,
          child: Text('$index',
              style: TextStyle(fontSize: 12, color: scheme.onPrimary)),
        ),
        title: Text(source.title, maxLines: 1, overflow: TextOverflow.ellipsis),
        subtitle:
            Text(source.snippet, maxLines: 2, overflow: TextOverflow.ellipsis),
        trailing: const Icon(Icons.open_in_new, size: 18),
        onTap: () => launchUrl(Uri.parse(source.url),
            mode: LaunchMode.externalApplication),
      ),
    );
  }
}

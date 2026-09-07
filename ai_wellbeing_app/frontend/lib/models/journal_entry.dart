class JournalEntry {
  final String id;
  final String? sessionId;
  final String title;
  final String content;
  final String? promptUsed;
  final String? emotionTag;
  final DateTime createdAt;
  final DateTime updatedAt;

  JournalEntry({
    required this.id,
    this.sessionId,
    required this.title,
    required this.content,
    this.promptUsed,
    this.emotionTag,
    required this.createdAt,
    required this.updatedAt,
  });

  factory JournalEntry.fromJson(Map<String, dynamic> json) {
    return JournalEntry(
      id: json['id'] ?? '',
      sessionId: json['session_id'],
      title: json['title'] ?? 'My Reflection',
      content: json['content'] ?? '',
      promptUsed: json['prompt_used'],
      emotionTag: json['emotion_tag'],
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : DateTime.now(),
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'])
          : DateTime.now(),
    );
  }
}

class JournalPrompt {
  final String id;
  final String category;
  final String promptText;

  JournalPrompt({
    required this.id,
    required this.category,
    required this.promptText,
  });

  factory JournalPrompt.fromJson(Map<String, dynamic> json) {
    return JournalPrompt(
      id: json['id'] ?? '',
      category: json['category'] ?? 'General',
      promptText: json['prompt_text'] ?? '',
    );
  }
}

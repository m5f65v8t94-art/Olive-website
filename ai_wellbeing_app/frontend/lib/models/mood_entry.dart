class MoodEntry {
  final String id;
  final String? sessionId;
  final int moodScore; // 1 to 5
  final String moodLabel;
  final List<String> emotionTags;
  final String? notes;
  final DateTime createdAt;

  MoodEntry({
    required this.id,
    this.sessionId,
    required this.moodScore,
    required this.moodLabel,
    required this.emotionTags,
    this.notes,
    required this.createdAt,
  });

  factory MoodEntry.fromJson(Map<String, dynamic> json) {
    return MoodEntry(
      id: json['id'] ?? '',
      sessionId: json['session_id'],
      moodScore: json['mood_score'] ?? 3,
      moodLabel: json['mood_label'] ?? 'Neutral',
      emotionTags: List<String>.from(json['emotion_tags'] ?? []),
      notes: json['notes'],
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : DateTime.now(),
    );
  }
}

class MoodSummary {
  final int totalEntries;
  final double averageScore;
  final List<MoodEntry> recentLogs;
  final List<String> dominantEmotions;
  final String encouragementNote;

  MoodSummary({
    required this.totalEntries,
    required this.averageScore,
    required this.recentLogs,
    required this.dominantEmotions,
    required this.encouragementNote,
  });

  factory MoodSummary.fromJson(Map<String, dynamic> json) {
    return MoodSummary(
      totalEntries: json['total_entries'] ?? 0,
      averageScore: (json['average_score'] ?? 0.0).toDouble(),
      recentLogs: (json['recent_logs'] as List? ?? [])
          .map((e) => MoodEntry.fromJson(e))
          .toList(),
      dominantEmotions: List<String>.from(json['dominant_emotions'] ?? []),
      encouragementNote: json['encouragement_note'] ?? '',
    );
  }
}

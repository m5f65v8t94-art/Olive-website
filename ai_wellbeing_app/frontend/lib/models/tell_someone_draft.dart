class DraftVariation {
  final String title;
  final String content;
  final String recommendedMedium;
  final List<String> tips;

  DraftVariation({
    required this.title,
    required this.content,
    required this.recommendedMedium,
    required this.tips,
  });

  factory DraftVariation.fromJson(Map<String, dynamic> json) {
    return DraftVariation(
      title: json['title'] ?? '',
      content: json['content'] ?? '',
      recommendedMedium: json['recommended_medium'] ?? 'Text',
      tips: List<String>.from(json['tips'] ?? []),
    );
  }
}

class TellSomeoneDraftResponse {
  final String recipient;
  final String tone;
  final String primaryDraft;
  final List<DraftVariation> alternativeDrafts;
  final List<String> conversationTips;
  final String encouragement;

  TellSomeoneDraftResponse({
    required this.recipient,
    required this.tone,
    required this.primaryDraft,
    required this.alternativeDrafts,
    required this.conversationTips,
    required this.encouragement,
  });

  factory TellSomeoneDraftResponse.fromJson(Map<String, dynamic> json) {
    return TellSomeoneDraftResponse(
      recipient: json['recipient'] ?? '',
      tone: json['tone'] ?? '',
      primaryDraft: json['primary_draft'] ?? '',
      alternativeDrafts: (json['alternative_drafts'] as List? ?? [])
          .map((e) => DraftVariation.fromJson(e))
          .toList(),
      conversationTips: List<String>.from(json['conversation_tips'] ?? []),
      encouragement: json['encouragement'] ?? '',
    );
  }
}

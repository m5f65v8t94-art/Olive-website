class ChatMessage {
  final String id;
  final String sessionId;
  final String role; // 'user' or 'assistant'
  final String content;
  final String? mode;
  final bool isSafetyFlagged;
  final DateTime timestamp;

  ChatMessage({
    required this.id,
    required this.sessionId,
    required this.role,
    required this.content,
    this.mode,
    this.isSafetyFlagged = false,
    required this.timestamp,
  });

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      id: json['id'] ?? '',
      sessionId: json['session_id'] ?? '',
      role: json['role'] ?? 'user',
      content: json['content'] ?? '',
      mode: json['mode'],
      isSafetyFlagged: json['is_safety_flagged'] ?? false,
      timestamp: json['timestamp'] != null
          ? DateTime.parse(json['timestamp'])
          : DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'session_id': sessionId,
      'role': role,
      'content': content,
      'mode': mode,
      'is_safety_flagged': isSafetyFlagged,
      'timestamp': timestamp.toIso8601String(),
    };
  }
}

class SafetyAssessmentModel {
  final bool isCrisis;
  final bool isDiagnosticAttempt;
  final String riskLevel;
  final String? triggerDetected;
  final List<dynamic> recommendedResources;
  final String? supportMessage;
  final String nonClinicalDisclaimer;

  SafetyAssessmentModel({
    required this.isCrisis,
    required this.isDiagnosticAttempt,
    required this.riskLevel,
    this.triggerDetected,
    required this.recommendedResources,
    this.supportMessage,
    required this.nonClinicalDisclaimer,
  });

  factory SafetyAssessmentModel.fromJson(Map<String, dynamic> json) {
    return SafetyAssessmentModel(
      isCrisis: json['is_crisis'] ?? false,
      isDiagnosticAttempt: json['is_diagnostic_attempt'] ?? false,
      riskLevel: json['risk_level'] ?? 'low',
      triggerDetected: json['trigger_detected'],
      recommendedResources: json['recommended_resources'] ?? [],
      supportMessage: json['support_message'],
      nonClinicalDisclaimer: json['non_clinical_disclaimer'] ?? '',
    );
  }
}

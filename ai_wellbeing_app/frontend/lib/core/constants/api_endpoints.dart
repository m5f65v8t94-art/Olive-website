class ApiEndpoints {
  static const String baseUrl = "http://127.0.0.1:8000";

  static const String chatTurn = "$baseUrl/api/chat/turn";
  static const String chatModes = "$baseUrl/api/chat/modes";
  static const String chatSessions = "$baseUrl/api/chat/sessions";
  static const String helpMeTellSomeone = "$baseUrl/api/help-me-tell-someone";
  static const String mood = "$baseUrl/api/mood";
  static const String moodSummary = "$baseUrl/api/mood/summary";
  static const String moodHistory = "$baseUrl/api/mood/history";
  static const String journal = "$baseUrl/api/journal";
  static const String journalPrompts = "$baseUrl/api/journal/prompts";
  static const String resources = "$baseUrl/api/resources";
  static const String hashPin = "$baseUrl/api/history/hash-pin";
  static const String verifyPin = "$baseUrl/api/history/verify-pin";
}

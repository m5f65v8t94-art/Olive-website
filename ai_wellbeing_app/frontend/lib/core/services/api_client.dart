import 'dart:convert';
import 'package:http/http.dart' as http;
import '../constants/api_endpoints.dart';
import '../../models/chat_message.dart';
import '../../models/mood_entry.dart';
import '../../models/journal_entry.dart';
import '../../models/tell_someone_draft.dart';
import '../../models/conversation_mode.dart';

class ApiClient {
  static final ApiClient _instance = ApiClient._internal();
  factory ApiClient() => _instance;
  ApiClient._internal();

  final Map<String, String> _headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };

  // Chat Turn
  Future<Map<String, dynamic>> sendChatTurn({
    String? sessionId,
    required String message,
    required ConversationMode mode,
  }) async {
    final response = await http.post(
      Uri.parse(ApiEndpoints.chatTurn),
      headers: _headers,
      body: jsonEncode({
        'session_id': sessionId,
        'message': message,
        'mode': mode.apiValue,
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to communicate with support AI: ${response.body}');
    }
  }

  // Help Me Tell Someone
  Future<TellSomeoneDraftResponse> generateTellSomeoneDraft({
    required String recipient,
    required String tone,
    required String coreFeeling,
    String? whatINeed,
    String? preferredMedium,
  }) async {
    final response = await http.post(
      Uri.parse(ApiEndpoints.helpMeTellSomeone),
      headers: _headers,
      body: jsonEncode({
        'recipient': recipient,
        'tone': tone,
        'core_feeling': coreFeeling,
        'what_i_need': whatINeed,
        'preferred_medium': preferredMedium ?? 'text',
      }),
    );

    if (response.statusCode == 200) {
      return TellSomeoneDraftResponse.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to generate starter message: ${response.body}');
    }
  }

  // Mood Log
  Future<MoodEntry> logMood({
    required int moodScore,
    required String moodLabel,
    List<String> emotionTags = const [],
    String? notes,
  }) async {
    final response = await http.post(
      Uri.parse(ApiEndpoints.mood),
      headers: _headers,
      body: jsonEncode({
        'mood_score': moodScore,
        'mood_label': moodLabel,
        'emotion_tags': emotionTags,
        'notes': notes,
      }),
    );

    if (response.statusCode == 200) {
      return MoodEntry.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to log mood: ${response.body}');
    }
  }

  Future<MoodSummary> getMoodSummary() async {
    final response = await http.get(
      Uri.parse(ApiEndpoints.moodSummary),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      return MoodSummary.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to load mood summary: ${response.body}');
    }
  }

  // Journal
  Future<List<JournalPrompt>> getJournalPrompts() async {
    final response = await http.get(
      Uri.parse(ApiEndpoints.journalPrompts),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final List data = jsonDecode(response.body);
      return data.map((e) => JournalPrompt.fromJson(e)).toList();
    } else {
      throw Exception('Failed to load prompts: ${response.body}');
    }
  }

  Future<JournalEntry> createJournalEntry({
    required String title,
    required String content,
    String? promptUsed,
    String? emotionTag,
  }) async {
    final response = await http.post(
      Uri.parse(ApiEndpoints.journal),
      headers: _headers,
      body: jsonEncode({
        'title': title,
        'content': content,
        'prompt_used': promptUsed,
        'emotion_tag': emotionTag,
      }),
    );

    if (response.statusCode == 200) {
      return JournalEntry.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to save reflection: ${response.body}');
    }
  }

  Future<List<JournalEntry>> getJournalEntries() async {
    final response = await http.get(
      Uri.parse(ApiEndpoints.journal),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final List data = jsonDecode(response.body);
      return data.map((e) => JournalEntry.fromJson(e)).toList();
    } else {
      throw Exception('Failed to fetch journal: ${response.body}');
    }
  }

  // Sessions & History
  Future<List<dynamic>> getSessions() async {
    final response = await http.get(
      Uri.parse(ApiEndpoints.chatSessions),
      headers: _headers,
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    return [];
  }

  Future<void> deleteSession(String sessionId) async {
    await http.delete(
      Uri.parse('${ApiEndpoints.chatSessions}/$sessionId'),
      headers: _headers,
    );
  }

  Future<void> purgeAllHistory() async {
    await http.delete(
      Uri.parse(ApiEndpoints.chatSessions),
      headers: _headers,
    );
  }

  // PIN
  Future<String> hashPin(String pin) async {
    final response = await http.post(
      Uri.parse(ApiEndpoints.hashPin),
      headers: _headers,
      body: jsonEncode({'pin': pin}),
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body)['hashed_pin'];
    }
    throw Exception('Failed to set PIN');
  }

  Future<bool> verifyPin(String pin, String hashedPin) async {
    final response = await http.post(
      Uri.parse(ApiEndpoints.verifyPin),
      headers: _headers,
      body: jsonEncode({'pin': pin, 'hashed_pin': hashedPin}),
    );
    return response.statusCode == 200;
  }
}

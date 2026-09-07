import 'package:flutter/material.dart';
import '../models/conversation_mode.dart';
import '../models/chat_message.dart';
import '../core/services/api_client.dart';

class ChatProvider extends ChangeNotifier {
  final ApiClient _apiClient = ApiClient();

  String? _currentSessionId;
  ConversationMode _activeMode = ConversationMode.justListen;
  final List<ChatMessage> _messages = [];
  bool _isLoading = false;
  SafetyAssessmentModel? _latestSafetyAssessment;
  String? _errorMessage;

  String? get currentSessionId => _currentSessionId;
  ConversationMode get activeMode => _activeMode;
  List<ChatMessage> get messages => _messages;
  bool get isLoading => _isLoading;
  SafetyAssessmentModel? get latestSafetyAssessment => _latestSafetyAssessment;
  String? get errorMessage => _errorMessage;

  void setMode(ConversationMode mode) {
    _activeMode = mode;
    notifyListeners();
  }

  void startNewSession({ConversationMode initialMode = ConversationMode.justListen}) {
    _currentSessionId = null;
    _activeMode = initialMode;
    _messages.clear();
    _latestSafetyAssessment = null;
    _errorMessage = null;
    notifyListeners();
  }

  void loadSession(String sessionId, ConversationMode mode, List<ChatMessage> messages) {
    _currentSessionId = sessionId;
    _activeMode = mode;
    _messages.clear();
    _messages.addAll(messages);
    _latestSafetyAssessment = null;
    _errorMessage = null;
    notifyListeners();
  }

  Future<void> sendMessage(String text) async {
    if (text.trim().isEmpty) return;

    final tempUserMsg = ChatMessage(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      sessionId: _currentSessionId ?? '',
      role: 'user',
      content: text,
      mode: _activeMode.apiValue,
      timestamp: DateTime.now(),
    );

    _messages.add(tempUserMsg);
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final response = await _apiClient.sendChatTurn(
        sessionId: _currentSessionId,
        message: text,
        mode: _activeMode,
      );

      _currentSessionId = response['session_id'];
      
      final assistantMsg = ChatMessage.fromJson(response['assistant_message']);
      _messages.add(assistantMsg);

      if (response['safety_assessment'] != null) {
        _latestSafetyAssessment = SafetyAssessmentModel.fromJson(response['safety_assessment']);
      }
    } catch (e) {
      _errorMessage = "Unable to connect right now. Please check your connection.";
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void dismissSafetyBanner() {
    _latestSafetyAssessment = null;
    notifyListeners();
  }
}

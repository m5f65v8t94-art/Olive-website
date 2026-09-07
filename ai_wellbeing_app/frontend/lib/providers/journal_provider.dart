import 'package:flutter/material.dart';
import '../models/journal_entry.dart';
import '../core/services/api_client.dart';

class JournalProvider extends ChangeNotifier {
  final ApiClient _apiClient = ApiClient();

  List<JournalEntry> _entries = [];
  List<JournalPrompt> _prompts = [];
  bool _isLoading = false;
  String? _error;

  List<JournalEntry> get entries => _entries;
  List<JournalPrompt> get prompts => _prompts;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> fetchJournalData() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final results = await Future.wait([
        _apiClient.getJournalEntries(),
        _apiClient.getJournalPrompts(),
      ]);
      _entries = results[0] as List<JournalEntry>;
      _prompts = results[1] as List<JournalPrompt>;
    } catch (e) {
      _error = "Could not load journal reflections";
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> createEntry({
    required String title,
    required String content,
    String? promptUsed,
    String? emotionTag,
  }) async {
    _isLoading = true;
    notifyListeners();

    try {
      final newEntry = await _apiClient.createJournalEntry(
        title: title,
        content: content,
        promptUsed: promptUsed,
        emotionTag: emotionTag,
      );
      _entries.insert(0, newEntry);
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = "Failed to save reflection";
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }
}

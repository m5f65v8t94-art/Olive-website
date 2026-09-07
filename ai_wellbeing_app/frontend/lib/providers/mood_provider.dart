import 'package:flutter/material.dart';
import '../models/mood_entry.dart';
import '../core/services/api_client.dart';

class MoodProvider extends ChangeNotifier {
  final ApiClient _apiClient = ApiClient();

  MoodSummary? _summary;
  bool _isLoading = false;
  String? _error;

  MoodSummary? get summary => _summary;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> fetchSummary() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _summary = await _apiClient.getMoodSummary();
    } catch (e) {
      _error = "Could not load mood summary";
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> recordMood({
    required int moodScore,
    required String moodLabel,
    List<String> emotionTags = const [],
    String? notes,
  }) async {
    _isLoading = true;
    notifyListeners();

    try {
      await _apiClient.logMood(
        moodScore: moodScore,
        moodLabel: moodLabel,
        emotionTags: emotionTags,
        notes: notes,
      );
      await fetchSummary();
      return true;
    } catch (e) {
      _error = "Failed to record mood";
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }
}

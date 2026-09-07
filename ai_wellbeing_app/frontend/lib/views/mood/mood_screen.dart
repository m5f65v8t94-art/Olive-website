import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../providers/mood_provider.dart';
import '../../core/theme/app_colors.dart';

class MoodScreen extends StatefulWidget {
  const MoodScreen({super.key});

  @override
  State<MoodScreen> createState() => _MoodScreenState();
}

class _MoodScreenState extends State<MoodScreen> {
  int _selectedScore = 3;
  String _selectedLabel = "Okay / Neutral";
  final List<String> _selectedTags = [];
  final TextEditingController _notesController = TextEditingController();

  final List<Map<String, dynamic>> _moodLevels = [
    {"score": 1, "emoji": "😞", "label": "Very Down"},
    {"score": 2, "emoji": "🙁", "label": "Struggling"},
    {"score": 3, "emoji": "😐", "label": "Okay / Neutral"},
    {"score": 4, "emoji": "🙂", "label": "Good / Calm"},
    {"score": 5, "emoji": "😄", "label": "Great / Hopeful"},
  ];

  final List<String> _availableTags = [
    "Anxious", "Overwhelmed", "Tired", "Stressed", "Lonely",
    "Calm", "Hopeful", "Relieved", "Grateful", "Unsure"
  ];

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<MoodProvider>().fetchSummary();
    });
  }

  void _submitMood() async {
    final success = await context.read<MoodProvider>().recordMood(
      moodScore: _selectedScore,
      moodLabel: _selectedLabel,
      emotionTags: _selectedTags,
      notes: _notesController.text.trim().isNotEmpty ? _notesController.text.trim() : null,
    );

    if (success && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text("Check-in saved. Thank you for checking in with yourself."),
          backgroundColor: AppColors.accentSage,
        ),
      );
      _notesController.clear();
      setState(() {
        _selectedTags.clear();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final moodProvider = context.watch<MoodProvider>();
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: const Text("Feelings Check-in", style: TextStyle(fontWeight: FontWeight.w600)),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // How are you feeling card
            Container(
              padding: const EdgeInsets.all(18),
              decoration: BoxDecoration(
                color: isDark ? AppColors.cardDark : Colors.white,
                borderRadius: BorderRadius.circular(18),
                boxShadow: [
                  BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 8, offset: const Offset(0, 2)),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  const Text("How are you feeling right now?", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                  const SizedBox(height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: _moodLevels.map((m) {
                      final isSelected = _selectedScore == m["score"];
                      return GestureDetector(
                        onTap: () {
                          setState(() {
                            _selectedScore = m["score"];
                            _selectedLabel = m["label"];
                          });
                        },
                        child: AnimatedContainer(
                          duration: const Duration(milliseconds: 200),
                          padding: const EdgeInsets.all(10),
                          decoration: BoxDecoration(
                            color: isSelected ? AppColors.primary.withOpacity(0.15) : Colors.transparent,
                            borderRadius: BorderRadius.circular(14),
                            border: isSelected ? Border.all(color: AppColors.primary, width: 2) : null,
                          ),
                          child: Text(m["emoji"], style: TextStyle(fontSize: isSelected ? 36 : 28)),
                        ),
                      );
                    }).toList(),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    _selectedLabel,
                    style: const TextStyle(fontWeight: FontWeight.w600, color: AppColors.primary, fontSize: 15),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // Emotion tags
            const Text("What emotions are present?", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
            const SizedBox(height: 10),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _availableTags.map((tag) {
                final isSelected = _selectedTags.contains(tag);
                return FilterChip(
                  label: Text(tag),
                  selected: isSelected,
                  selectedColor: AppColors.primaryLight,
                  labelStyle: TextStyle(
                    color: isSelected ? AppColors.primaryDark : null,
                    fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                  ),
                  onSelected: (selected) {
                    setState(() {
                      if (selected) {
                        _selectedTags.add(tag);
                      } else {
                        _selectedTags.remove(tag);
                      }
                    });
                  },
                );
              }).toList(),
            ),
            const SizedBox(height: 20),

            // Notes
            const Text("Any thoughts to note? (Optional)", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
            const SizedBox(height: 8),
            TextField(
              controller: _notesController,
              maxLines: 2,
              decoration: InputDecoration(
                hintText: "e.g. slept poorly, or finished a big assignment...",
                hintStyle: const TextStyle(fontSize: 14, color: Colors.grey),
                filled: true,
                fillColor: isDark ? AppColors.cardDark : Colors.white,
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
            const SizedBox(height: 18),

            // Submit Button
            SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton(
                onPressed: moodProvider.isLoading ? null : _submitMood,
                child: Text(moodProvider.isLoading ? "Saving..." : "Save Today's Check-in"),
              ),
            ),

            const SizedBox(height: 28),
            const Divider(),
            const SizedBox(height: 16),

            // Summary Card
            if (moodProvider.summary != null) ...[
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: AppColors.accentSage.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.insights, color: AppColors.accentSage, size: 20),
                        SizedBox(width: 8),
                        Text("Your Reflection Summary", style: TextStyle(fontWeight: FontWeight.bold, color: AppColors.accentSage)),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      moodProvider.summary!.encouragementNote,
                      style: const TextStyle(fontSize: 14, height: 1.4),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),

              const Text("Recent Check-ins", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
              const SizedBox(height: 10),
              ...moodProvider.summary!.recentLogs.take(5).map((log) => Card(
                    margin: const EdgeInsets.only(bottom: 8),
                    child: ListTile(
                      leading: CircleAvatar(
                        backgroundColor: AppColors.primary.withOpacity(0.15),
                        child: Text("${log.moodScore}/5", style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                      ),
                      title: Text(log.moodLabel, style: const TextStyle(fontWeight: FontWeight.w600)),
                      subtitle: Text(
                        log.emotionTags.isNotEmpty ? log.emotionTags.join(", ") : "Checked in",
                        style: const TextStyle(fontSize: 12, color: Colors.grey),
                      ),
                      trailing: Text(
                        DateFormat('MMM d').format(log.createdAt),
                        style: const TextStyle(fontSize: 12, color: Colors.grey),
                      ),
                    ),
                  )),
            ],
          ],
        ),
      ),
    );
  }
}

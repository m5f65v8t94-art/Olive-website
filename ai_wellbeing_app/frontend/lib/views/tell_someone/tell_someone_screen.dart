import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../core/services/api_client.dart';
import '../../models/tell_someone_draft.dart';
import '../../core/theme/app_colors.dart';

class TellSomeoneScreen extends StatefulWidget {
  const TellSomeoneScreen({super.key});

  @override
  State<TellSomeoneScreen> createState() => _TellSomeoneScreenState();
}

class _TellSomeoneScreenState extends State<TellSomeoneScreen> {
  final ApiClient _apiClient = ApiClient();
  final TextEditingController _feelingController = TextEditingController();
  final TextEditingController _needController = TextEditingController();
  final TextEditingController _draftController = TextEditingController();

  String _selectedRecipient = "parent_guardian";
  String _selectedTone = "gentle_vulnerable";
  bool _isLoading = false;
  TellSomeoneDraftResponse? _response;

  final List<Map<String, String>> _recipients = [
    {"id": "parent_guardian", "label": "Parent / Guardian", "icon": "family_restroom"},
    {"id": "school_counselor", "label": "School Counselor", "icon": "psychology"},
    {"id": "teacher", "label": "Teacher", "icon": "school"},
    {"id": "friend", "label": "Best Friend", "icon": "people"},
    {"id": "sibling", "label": "Sibling", "icon": "group"},
    {"id": "trusted_adult", "label": "Trusted Adult", "icon": "person"},
  ];

  final List<Map<String, String>> _tones = [
    {"id": "casual_text", "label": "Casual Text"},
    {"id": "direct_honest", "label": "Direct & Honest"},
    {"id": "gentle_vulnerable", "label": "Gentle & Vulnerable"},
    {"id": "formal_letter", "label": "Formal Letter"},
    {"id": "in_person_starter", "label": "In-Person Script"},
  ];

  Future<void> _generateDraft() async {
    if (_feelingController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Please describe what's on your mind first.")),
      );
      return;
    }

    setState(() => _isLoading = true);

    try {
      final res = await _apiClient.generateTellSomeoneDraft(
        recipient: _selectedRecipient,
        tone: _selectedTone,
        coreFeeling: _feelingController.text.trim(),
        whatINeed: _needController.text.trim().isNotEmpty ? _needController.text.trim() : null,
      );

      setState(() {
        _response = res;
        _draftController.text = res.primaryDraft;
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Could not generate message draft. Check connection.")),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _copyToClipboard() {
    Clipboard.setData(ClipboardData(text: _draftController.text));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text("Message copied to clipboard!"),
        backgroundColor: AppColors.accentSage,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: const Text("Help Me Tell Someone", style: TextStyle(fontWeight: FontWeight.w600)),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Intro banner
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppColors.tellSomeone.withOpacity(0.12),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppColors.tellSomeone.withOpacity(0.3)),
              ),
              child: const Row(
                children: [
                  Icon(Icons.mark_email_read_outlined, color: AppColors.tellSomeone, size: 28),
                  SizedBox(width: 14),
                  Expanded(
                    child: Text(
                      "Putting feelings into words can be hard. We'll help you create a comfortable message for someone you trust.",
                      style: TextStyle(fontSize: 14, height: 1.4),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // Recipient Picker
            const Text("1. Who do you want to reach out to?", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
            const SizedBox(height: 10),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _recipients.map((r) {
                final isSelected = _selectedRecipient == r["id"];
                return ChoiceChip(
                  label: Text(r["label"]!),
                  selected: isSelected,
                  selectedColor: AppColors.tellSomeone,
                  labelStyle: TextStyle(
                    color: isSelected ? Colors.white : null,
                    fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                  ),
                  onSelected: (selected) {
                    if (selected) setState(() => _selectedRecipient = r["id"]!);
                  },
                );
              }).toList(),
            ),
            const SizedBox(height: 20),

            // Tone Picker
            const Text("2. What tone feels most natural?", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
            const SizedBox(height: 10),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _tones.map((t) {
                final isSelected = _selectedTone == t["id"];
                return ChoiceChip(
                  label: Text(t["label"]!),
                  selected: isSelected,
                  selectedColor: AppColors.tellSomeone,
                  labelStyle: TextStyle(
                    color: isSelected ? Colors.white : null,
                    fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                  ),
                  onSelected: (selected) {
                    if (selected) setState(() => _selectedTone = t["id"]!);
                  },
                );
              }).toList(),
            ),
            const SizedBox(height: 20),

            // Core Feeling Input
            const Text("3. What are you going through?", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
            const SizedBox(height: 6),
            TextField(
              controller: _feelingController,
              maxLines: 2,
              decoration: InputDecoration(
                hintText: "e.g. feeling stressed about exams and falling behind...",
                hintStyle: const TextStyle(fontSize: 14, color: Colors.grey),
                filled: true,
                fillColor: isDark ? AppColors.cardDark : Colors.white,
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
            const SizedBox(height: 14),

            // Optional Need Input
            const Text("4. What kind of support would help? (Optional)", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
            const SizedBox(height: 6),
            TextField(
              controller: _needController,
              decoration: InputDecoration(
                hintText: "e.g. just someone to listen without getting mad, or help finding a tutor",
                hintStyle: const TextStyle(fontSize: 14, color: Colors.grey),
                filled: true,
                fillColor: isDark ? AppColors.cardDark : Colors.white,
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
            const SizedBox(height: 20),

            // Generate Button
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton.icon(
                onPressed: _isLoading ? null : _generateDraft,
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.tellSomeone,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                ),
                icon: _isLoading
                    ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                    : const Icon(Icons.auto_awesome),
                label: Text(_isLoading ? "Drafting..." : "Create Message Draft"),
              ),
            ),

            if (_response != null) ...[
              const SizedBox(height: 28),
              const Divider(),
              const SizedBox(height: 16),
              const Text("Your Custom Message Draft:", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
              const SizedBox(height: 10),

              // Editable Draft Card
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: isDark ? AppColors.cardDark : Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [
                    BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 8, offset: const Offset(0, 2)),
                  ],
                ),
                child: Column(
                  children: [
                    TextField(
                      controller: _draftController,
                      maxLines: 5,
                      style: const TextStyle(fontSize: 15, height: 1.45),
                      decoration: const InputDecoration(
                        border: InputBorder.none,
                      ),
                    ),
                    const Divider(),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text("You can edit words before sending", style: TextStyle(fontSize: 12, color: Colors.grey)),
                        ElevatedButton.icon(
                          onPressed: _copyToClipboard,
                          icon: const Icon(Icons.copy, size: 16),
                          label: const Text("Copy Draft"),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppColors.accentSage,
                            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 20),
              // Tips card
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.08),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.tips_and_updates_outlined, size: 20, color: AppColors.primary),
                        SizedBox(width: 8),
                        Text("Gentle Communication Tips", style: TextStyle(fontWeight: FontWeight.bold, color: AppColors.primaryDark)),
                      ],
                    ),
                    const SizedBox(height: 8),
                    ..._response!.conversationTips.map((tip) => Padding(
                          padding: const EdgeInsets.symmetric(vertical: 3),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text("• ", style: TextStyle(fontWeight: FontWeight.bold)),
                              Expanded(child: Text(tip, style: const TextStyle(fontSize: 13, height: 1.35))),
                            ],
                          ),
                        )),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

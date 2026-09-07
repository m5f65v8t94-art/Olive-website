import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../providers/journal_provider.dart';
import '../../models/journal_entry.dart';
import '../../core/theme/app_colors.dart';

class JournalScreen extends StatefulWidget {
  const JournalScreen({super.key});

  @override
  State<JournalScreen> createState() => _JournalScreenState();
}

class _JournalScreenState extends State<JournalScreen> {
  final TextEditingController _titleController = TextEditingController();
  final TextEditingController _contentController = TextEditingController();
  String? _selectedPrompt;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<JournalProvider>().fetchJournalData();
    });
  }

  void _saveEntry() async {
    final content = _contentController.text.trim();
    if (content.isEmpty) return;

    final title = _titleController.text.trim().isNotEmpty
        ? _titleController.text.trim()
        : "Reflection on ${DateFormat('MMM d').format(DateTime.now())}";

    final success = await context.read<JournalProvider>().createEntry(
      title: title,
      content: content,
      promptUsed: _selectedPrompt,
    );

    if (success && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Reflection saved to your private journal.")),
      );
      _titleController.clear();
      _contentController.clear();
      setState(() => _selectedPrompt = null);
    }
  }

  @override
  Widget build(BuildContext context) {
    final journalProvider = context.watch<JournalProvider>();
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: const Text("Private Journal", style: TextStyle(fontWeight: FontWeight.w600)),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Prompt Suggestions Carousel
            if (journalProvider.prompts.isNotEmpty) ...[
              const Text("Inspiration Prompts", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
              const SizedBox(height: 8),
              SizedBox(
                height: 80,
                child: ListView.builder(
                  scrollDirection: Axis.horizontal,
                  itemCount: journalProvider.prompts.length,
                  itemBuilder: (context, index) {
                    final p = journalProvider.prompts[index];
                    final isSelected = _selectedPrompt == p.promptText;
                    return GestureDetector(
                      onTap: () {
                        setState(() {
                          _selectedPrompt = isSelected ? null : p.promptText;
                        });
                      },
                      child: Container(
                        width: 240,
                        margin: const EdgeInsets.only(right: 10),
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: isSelected
                              ? AppColors.primary.withOpacity(0.15)
                              : (isDark ? AppColors.cardDark : Colors.white),
                          borderRadius: BorderRadius.circular(14),
                          border: Border.all(
                            color: isSelected ? AppColors.primary : Colors.grey.withOpacity(0.2),
                          ),
                        ),
                        child: Text(
                          p.promptText,
                          maxLines: 3,
                          overflow: TextOverflow.ellipsis,
                          style: TextStyle(
                            fontSize: 12,
                            height: 1.3,
                            color: isSelected ? AppColors.primaryDark : null,
                          ),
                        ),
                      ),
                    );
                  },
                ),
              ),
              const SizedBox(height: 20),
            ],

            // Active prompt badge
            if (_selectedPrompt != null)
              Container(
                margin: const EdgeInsets.only(bottom: 12),
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.edit_note, size: 18, color: AppColors.primary),
                    const SizedBox(width: 8),
                    Expanded(child: Text("Prompt: $_selectedPrompt", style: const TextStyle(fontSize: 12))),
                    IconButton(
                      icon: const Icon(Icons.close, size: 16),
                      padding: EdgeInsets.zero,
                      constraints: const BoxConstraints(),
                      onPressed: () => setState(() => _selectedPrompt = null),
                    ),
                  ],
                ),
              ),

            // Reflection Editor
            TextField(
              controller: _titleController,
              decoration: InputDecoration(
                hintText: "Title (e.g., Thoughts after a long day)",
                hintStyle: const TextStyle(fontSize: 14, color: Colors.grey),
                filled: true,
                fillColor: isDark ? AppColors.cardDark : Colors.white,
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: _contentController,
              maxLines: 6,
              decoration: InputDecoration(
                hintText: "Write whatever is in your heart. No filters, no pressure...",
                hintStyle: const TextStyle(fontSize: 14, color: Colors.grey),
                filled: true,
                fillColor: isDark ? AppColors.cardDark : Colors.white,
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
            const SizedBox(height: 12),
            Align(
              alignment: Alignment.centerRight,
              child: ElevatedButton.icon(
                onPressed: journalProvider.isLoading ? null : _saveEntry,
                icon: const Icon(Icons.save_outlined, size: 18),
                label: const Text("Save to Journal"),
              ),
            ),

            const SizedBox(height: 24),
            const Divider(),
            const SizedBox(height: 16),

            // Past Reflections
            const Text("Your Reflections", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            const SizedBox(height: 12),
            if (journalProvider.entries.isEmpty)
              const Padding(
                padding: EdgeInsets.all(24.0),
                child: Center(
                  child: Text("Your journal is empty. Write your first reflection above!", style: TextStyle(color: Colors.grey)),
                ),
              )
            else
              ...journalProvider.entries.map((entry) => Card(
                    margin: const EdgeInsets.only(bottom: 12),
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(entry.title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                              Text(
                                DateFormat('MMM d, yyyy').format(entry.createdAt),
                                style: const TextStyle(fontSize: 12, color: Colors.grey),
                              ),
                            ],
                          ),
                          if (entry.promptUsed != null) ...[
                            const SizedBox(height: 4),
                            Text("Prompt: ${entry.promptUsed}", style: const TextStyle(fontSize: 11, fontStyle: FontStyle.italic, color: Colors.grey)),
                          ],
                          const SizedBox(height: 8),
                          Text(entry.content, style: const TextStyle(fontSize: 14, height: 1.4)),
                        ],
                      ),
                    ),
                  )),
          ],
        ),
      ),
    );
  }
}

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/settings_provider.dart';

class DisguiseView extends StatelessWidget {
  const DisguiseView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF3F4F6),
      appBar: AppBar(
        title: const Text("Study Notes - Chapter 4", style: TextStyle(fontSize: 16, color: Colors.black87)),
        backgroundColor: Colors.white,
        elevation: 1,
        actions: [
          IconButton(
            tooltip: "Return",
            icon: const Icon(Icons.bookmark_border, color: Colors.black54),
            onPressed: () {
              context.read<SettingsProvider>().toggleDisguise();
            },
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              "Cellular Biology & Photosynthesis",
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.black87),
            ),
            const SizedBox(height: 12),
            const Text(
              "• Chloroplasts contain chlorophyll, which absorbs light energy.\n"
              "• Light-dependent reactions occur in the thylakoid membranes.\n"
              "• The Calvin cycle occurs in the stroma and fixes carbon dioxide.\n"
              "• ATP and NADPH are synthesized during light reactions.",
              style: TextStyle(fontSize: 15, height: 1.6, color: Colors.black54),
            ),
            const Spacer(),
            Center(
              child: TextButton.icon(
                onPressed: () {
                  context.read<SettingsProvider>().toggleDisguise();
                },
                icon: const Icon(Icons.lock_open, size: 16, color: Colors.grey),
                label: const Text("Tap to resume session", style: TextStyle(color: Colors.grey)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

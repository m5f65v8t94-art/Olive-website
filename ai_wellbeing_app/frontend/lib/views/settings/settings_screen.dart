import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/settings_provider.dart';
import '../../core/theme/app_colors.dart';
import 'history_auth_screen.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final TextEditingController _pinController = TextEditingController();

  void _showSetPinDialog() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text("Set Privacy PIN"),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text("Enter a 4-to-6 digit PIN to protect your conversation history from shoulder surfing:"),
            const SizedBox(height: 14),
            TextField(
              controller: _pinController,
              keyboardType: TextInputType.number,
              obscureText: true,
              maxLength: 6,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              decoration: InputDecoration(
                hintText: "••••",
                counterText: "",
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text("Cancel")),
          ElevatedButton(
            onPressed: () async {
              final pin = _pinController.text.trim();
              if (pin.length >= 4) {
                await context.read<SettingsProvider>().setPin(pin);
                _pinController.clear();
                if (mounted) Navigator.pop(ctx);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text("Privacy PIN set successfully.")),
                );
              }
            },
            child: const Text("Save PIN"),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final settings = context.watch<SettingsProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text("Settings & Privacy", style: TextStyle(fontWeight: FontWeight.w600)),
      ),
      body: ListView(
        padding: const EdgeInsets.all(18),
        children: [
          // Privacy & History Section
          const Text("Privacy & Security", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          const SizedBox(height: 10),
          Card(
            child: Column(
              children: [
                ListTile(
                  leading: const Icon(Icons.lock_outline, color: AppColors.primary),
                  title: const Text("Conversation History Lock"),
                  subtitle: Text(settings.isPinSet ? "Protected by PIN" : "Unlocked (No PIN set)"),
                  trailing: TextButton(
                    onPressed: () {
                      if (settings.isPinSet) {
                        settings.removePin();
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text("PIN removed.")),
                        );
                      } else {
                        _showSetPinDialog();
                      }
                    },
                    child: Text(settings.isPinSet ? "Remove PIN" : "Set PIN"),
                  ),
                ),
                const Divider(height: 1),
                ListTile(
                  leading: const Icon(Icons.history_toggle_off, color: AppColors.primary),
                  title: const Text("View Protected History"),
                  subtitle: const Text("Settings → Conversation History → Authentication"),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => const HistoryAuthScreen()),
                    );
                  },
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),

          // Notifications Section
          const Text("Notifications", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          const SizedBox(height: 10),
          Card(
            child: SwitchListTile(
              secondary: const Icon(Icons.notifications_none, color: AppColors.primary),
              title: const Text("Neutral Reflection Reminders"),
              subtitle: const Text("Discreet notifications that do not reveal sensitive topics (e.g. 'You have an update.')"),
              value: settings.notificationsEnabled,
              onChanged: (val) {
                settings.setNotificationsEnabled(val);
              },
            ),
          ),
          const SizedBox(height: 20),

          // About & Non-Clinical Boundaries
          const Text("About & Non-Clinical Role", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          const SizedBox(height: 10),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Row(
                    children: [
                      Icon(Icons.shield_outlined, color: AppColors.accentSage, size: 22),
                      SizedBox(width: 10),
                      Text("Conversational Support Role", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                    ],
                  ),
                  const SizedBox(height: 10),
                  const Text(
                    "This application is designed as a gentle stepping stone to help young people put thoughts into words, reflect on feelings, and connect with trusted adults and professionals.\n\n"
                    "It is NOT a therapist, psychologist, counselor, doctor, or diagnostic tool.",
                    style: TextStyle(fontSize: 13, height: 1.45, color: Colors.grey),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

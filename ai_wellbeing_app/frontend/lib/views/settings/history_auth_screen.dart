import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../providers/settings_provider.dart';
import '../../providers/chat_provider.dart';
import '../../core/services/api_client.dart';
import '../../core/theme/app_colors.dart';
import '../../models/conversation_mode.dart';
import '../../models/chat_message.dart';
import '../chat/chat_screen.dart';

class HistoryAuthScreen extends StatefulWidget {
  const HistoryAuthScreen({super.key});

  @override
  State<HistoryAuthScreen> createState() => _HistoryAuthScreenState();
}

class _HistoryAuthScreenState extends State<HistoryAuthScreen> {
  final TextEditingController _pinController = TextEditingController();
  final ApiClient _apiClient = ApiClient();

  bool _isAuthenticated = false;
  bool _isLoading = false;
  String? _errorMessage;
  List<dynamic> _sessions = [];

  @override
  void initState() {
    super.initState();
    _checkInitialAuth();
  }

  void _checkInitialAuth() async {
    final settings = context.read<SettingsProvider>();
    if (!settings.isPinSet) {
      // If no PIN is configured, unlock directly
      _loadSessions();
      setState(() => _isAuthenticated = true);
    } else if (settings.isBiometricAvailable) {
      // Prompt biometrics
      final bioSuccess = await settings.unlockWithBiometrics();
      if (bioSuccess) {
        _loadSessions();
        setState(() => _isAuthenticated = true);
      }
    }
  }

  void _verifyPin() async {
    final pin = _pinController.text.trim();
    if (pin.length < 4) {
      setState(() => _errorMessage = "Please enter your 4-to-6 digit PIN");
      return;
    }

    setState(() => _isLoading = true);
    final isValid = await context.read<SettingsProvider>().verifyPin(pin);

    if (isValid) {
      _loadSessions();
      setState(() {
        _isAuthenticated = true;
        _errorMessage = null;
      });
    } else {
      setState(() {
        _errorMessage = "Incorrect PIN. Please try again.";
        _pinController.clear();
      });
    }
    setState(() => _isLoading = false);
  }

  void _loadSessions() async {
    setState(() => _isLoading = true);
    try {
      final list = await _apiClient.getSessions();
      setState(() => _sessions = list);
    } catch (_) {}
    setState(() => _isLoading = false);
  }

  void _deleteSession(String sessionId) async {
    await _apiClient.deleteSession(sessionId);
    _loadSessions();
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text("Conversation removed.")),
    );
  }

  void _purgeAll() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text("Delete All History?"),
        content: const Text("This will permanently wipe all conversation history from your device for privacy."),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text("Cancel")),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: AppColors.crisisRed),
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text("Wipe All"),
          ),
        ],
      ),
    );

    if (confirm == true) {
      await _apiClient.purgeAllHistory();
      _loadSessions();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("All conversation history permanently deleted.")),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (!_isAuthenticated) {
      return _buildPinGateView();
    }
    return _buildHistoryListView();
  }

  Widget _buildPinGateView() {
    return Scaffold(
      appBar: AppBar(title: const Text("Privacy Lock")),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.lock_outline, size: 48, color: AppColors.primary),
              ),
              const SizedBox(height: 20),
              const Text("Protected History", style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              const Text(
                "Enter your privacy PIN to view past conversations.",
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 14, color: Colors.grey),
              ),
              const SizedBox(height: 24),
              SizedBox(
                width: 200,
                child: TextField(
                  controller: _pinController,
                  keyboardType: TextInputType.number,
                  obscureText: true,
                  maxLength: 6,
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 24, letterSpacing: 8, fontWeight: FontWeight.bold),
                  decoration: InputDecoration(
                    counterText: "",
                    hintText: "••••",
                    filled: true,
                    fillColor: Colors.grey.withOpacity(0.1),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                  onSubmitted: (_) => _verifyPin(),
                ),
              ),
              if (_errorMessage != null) ...[
                const SizedBox(height: 12),
                Text(_errorMessage!, style: const TextStyle(color: AppColors.crisisRed, fontSize: 13)),
              ],
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: _isLoading ? null : _verifyPin,
                child: Text(_isLoading ? "Verifying..." : "Unlock History"),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHistoryListView() {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Conversation History", style: TextStyle(fontWeight: FontWeight.w600)),
        actions: [
          if (_sessions.isNotEmpty)
            IconButton(
              tooltip: "Wipe All History",
              icon: const Icon(Icons.delete_forever, color: AppColors.crisisRed),
              onPressed: _purgeAll,
            ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _sessions.isEmpty
              ? const Center(
                  child: Padding(
                    padding: EdgeInsets.all(32),
                    child: Text("No saved conversations yet.", style: TextStyle(color: Colors.grey, fontSize: 15)),
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: _sessions.length,
                  itemBuilder: (context, index) {
                    final s = _sessions[index];
                    final dateStr = DateFormat('MMM d, h:mm a').format(DateTime.parse(s['updated_at']));
                    final mode = ConversationMode.fromString(s['current_mode'] ?? 'just_listen');

                    return Card(
                      margin: const EdgeInsets.only(bottom: 12),
                      child: ListTile(
                        leading: CircleAvatar(
                          backgroundColor: AppColors.primary.withOpacity(0.12),
                          child: Icon(Icons.chat_bubble_outline, color: AppColors.primary, size: 20),
                        ),
                        title: Text(s['title'] ?? 'Conversation', style: const TextStyle(fontWeight: FontWeight.w600)),
                        subtitle: Text(
                          "${mode.displayName} • $dateStr\n${s['latest_message_preview'] ?? ''}",
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(fontSize: 12, color: Colors.grey),
                        ),
                        isThreeLine: true,
                        trailing: IconButton(
                          icon: const Icon(Icons.delete_outline, color: Colors.grey),
                          onPressed: () => _deleteSession(s['id']),
                        ),
                        onTap: () {
                          // Continue conversation with existing session
                          context.read<ChatProvider>().startNewSession(initialMode: mode);
                          Navigator.push(
                            context,
                            MaterialPageRoute(builder: (_) => ChatScreen(initialMode: mode)),
                          );
                        },
                      ),
                    );
                  },
                ),
    );
  }
}

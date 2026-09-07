import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../providers/chat_provider.dart';
import '../../providers/settings_provider.dart';
import '../../models/conversation_mode.dart';
import '../../models/chat_message.dart';
import '../../core/theme/app_colors.dart';

class ChatScreen extends StatefulWidget {
  final ConversationMode? initialMode;

  const ChatScreen({super.key, this.initialMode});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _textController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (widget.initialMode != null) {
        context.read<ChatProvider>().setMode(widget.initialMode!);
      }
    });
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  void _handleSend() {
    final text = _textController.text.trim();
    if (text.isEmpty) return;
    _textController.clear();
    context.read<ChatProvider>().sendMessage(text);
    _scrollToBottom();
  }

  @override
  Widget build(BuildContext context) {
    final chatProvider = context.watch<ChatProvider>();
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              width: 10,
              height: 10,
              decoration: const BoxDecoration(
                color: AppColors.accentSage,
                shape: BoxShape.circle,
              ),
            ),
            const SizedBox(width: 8),
            const Text("AI Support Space", style: TextStyle(fontWeight: FontWeight.w600, fontSize: 18)),
          ],
        ),
        actions: [
          IconButton(
            tooltip: "Quick Privacy Hide",
            icon: const Icon(Icons.visibility_off_outlined),
            onPressed: () {
              context.read<SettingsProvider>().toggleDisguise();
            },
          ),
          IconButton(
            tooltip: "New Conversation",
            icon: const Icon(Icons.add_comment_outlined),
            onPressed: () {
              chatProvider.startNewSession(initialMode: chatProvider.activeMode);
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // 4 Modes Switcher Pills Bar
          _buildModeSelector(chatProvider),

          // Safety Alert Banner (if crisis triggered)
          if (chatProvider.latestSafetyAssessment != null && chatProvider.latestSafetyAssessment!.isCrisis)
            _buildCrisisAlertBanner(chatProvider.latestSafetyAssessment!, chatProvider),

          // Message List
          Expanded(
            child: chatProvider.messages.isEmpty
                ? _buildEmptyState(chatProvider.activeMode)
                : ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    itemCount: chatProvider.messages.length,
                    itemBuilder: (context, index) {
                      final msg = chatProvider.messages[index];
                      return _buildMessageBubble(msg, isDark);
                    },
                  ),
          ),

          if (chatProvider.isLoading)
            Padding(
              padding: const EdgeInsets.all(8.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2)),
                  const SizedBox(width: 10),
                  Text("AI is reflecting...", style: TextStyle(fontSize: 13, color: Colors.grey.shade600)),
                ],
              ),
            ),

          // Non-Clinical Micro Disclaimer
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
            color: isDark ? Colors.black12 : Colors.grey.shade100,
            child: const Text(
              "Conversational support only • Not medical therapy or diagnosis • 988 for crisis",
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 11, color: Colors.grey),
            ),
          ),

          // Input Bar
          _buildInputBar(isDark),
        ],
      ),
    );
  }

  Widget _buildModeSelector(ChatProvider provider) {
    return Container(
      height: 48,
      padding: const EdgeInsets.symmetric(horizontal: 12),
      child: ListView(
        scrollDirection: Axis.horizontal,
        children: ConversationMode.values.map((mode) {
          final isSelected = provider.activeMode == mode;
          Color modeColor;
          IconData icon;

          switch (mode) {
            case ConversationMode.justListen:
              modeColor = AppColors.justListen;
              icon = Icons.headphones_outlined;
              break;
            case ConversationMode.giveMeAdvice:
              modeColor = AppColors.giveAdvice;
              icon = Icons.lightbulb_outline;
              break;
            case ConversationMode.helpMeUnderstand:
              modeColor = AppColors.helpUnderstand;
              icon = Icons.explore_outlined;
              break;
            case ConversationMode.helpMeTellSomeone:
              modeColor = AppColors.tellSomeone;
              icon = Icons.send_outlined;
              break;
          }

          return Padding(
            padding: const EdgeInsets.only(right: 8),
            child: ChoiceChip(
              avatar: Icon(icon, size: 16, color: isSelected ? Colors.white : modeColor),
              label: Text(mode.displayName),
              labelStyle: TextStyle(
                fontSize: 13,
                fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                color: isSelected ? Colors.white : null,
              ),
              selected: isSelected,
              selectedColor: modeColor,
              onSelected: (selected) {
                if (selected) {
                  provider.setMode(mode);
                }
              },
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildEmptyState(ConversationMode mode) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.spa_outlined, size: 54, color: AppColors.primary.withOpacity(0.7)),
            const SizedBox(height: 16),
            Text(
              mode.displayName,
              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              mode.description,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 14, color: Colors.grey, height: 1.4),
            ),
            const SizedBox(height: 20),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppColors.primary.withOpacity(0.08),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Text(
                "💬 Say anything on your mind. You are in a safe, judgment-free space.",
                style: TextStyle(fontSize: 13, color: AppColors.primaryDark),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMessageBubble(ChatMessage msg, bool isDark) {
    final isUser = msg.role == 'user';

    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 6),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.82),
        decoration: BoxDecoration(
          color: isUser
              ? AppColors.primary
              : (isDark ? AppColors.cardDark : Colors.white),
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(18),
            topRight: const Radius.circular(18),
            bottomLeft: Radius.circular(isUser ? 18 : 4),
            bottomRight: Radius.circular(isUser ? 4 : 18),
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.04),
              blurRadius: 6,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
          children: [
            Text(
              msg.content,
              style: TextStyle(
                fontSize: 15,
                height: 1.45,
                color: isUser ? Colors.white : (isDark ? Colors.white : AppColors.textPrimaryLight),
              ),
            ),
            const SizedBox(height: 4),
            Text(
              DateFormat('hh:mm a').format(msg.timestamp),
              style: TextStyle(
                fontSize: 10,
                color: isUser ? Colors.white70 : Colors.grey,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCrisisAlertBanner(SafetyAssessmentModel safety, ChatProvider provider) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppColors.crisisBannerBg,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppColors.crisisBannerBorder),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.favorite, color: AppColors.crisisRed, size: 20),
              const SizedBox(width: 8),
              const Expanded(
                child: Text(
                  "Support is available right now",
                  style: TextStyle(fontWeight: FontWeight.bold, color: AppColors.crisisRed, fontSize: 14),
                ),
              ),
              IconButton(
                padding: EdgeInsets.zero,
                constraints: const BoxConstraints(),
                icon: const Icon(Icons.close, size: 18, color: Colors.grey),
                onPressed: () => provider.dismissSafetyBanner(),
              ),
            ],
          ),
          const SizedBox(height: 6),
          const Text(
            "You are not alone. Please reach out to someone who can help keep you safe:",
            style: TextStyle(fontSize: 13, color: Colors.black87),
          ),
          const SizedBox(height: 10),
          Wrap(
            spacing: 8,
            children: [
              ActionChip(
                avatar: const Icon(Icons.phone, size: 14, color: Colors.white),
                backgroundColor: AppColors.crisisRed,
                label: const Text("Call 988 (Lifeline)", style: TextStyle(color: Colors.white, fontSize: 12)),
                onPressed: () {},
              ),
              ActionChip(
                avatar: const Icon(Icons.sms, size: 14, color: AppColors.crisisRed),
                backgroundColor: Colors.white,
                label: const Text("Text 741741", style: TextStyle(color: AppColors.crisisRed, fontSize: 12)),
                onPressed: () {},
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildInputBar(bool isDark) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: isDark ? AppColors.surfaceDark : Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 4,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: SafeArea(
        child: Row(
          children: [
            Expanded(
              child: TextField(
                controller: _textController,
                textInputAction: TextInputAction.send,
                onSubmitted: (_) => _handleSend(),
                decoration: InputDecoration(
                  hintText: "Type what's on your mind...",
                  hintStyle: const TextStyle(fontSize: 14, color: Colors.grey),
                  filled: true,
                  fillColor: isDark ? AppColors.cardDark : AppColors.bgLight,
                  contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(24),
                    borderSide: BorderSide.none,
                  ),
                ),
              ),
            ),
            const SizedBox(width: 8),
            Container(
              decoration: const BoxDecoration(
                color: AppColors.primary,
                shape: BoxShape.circle,
              ),
              child: IconButton(
                icon: const Icon(Icons.arrow_upward, color: Colors.white, size: 20),
                onPressed: _handleSend,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

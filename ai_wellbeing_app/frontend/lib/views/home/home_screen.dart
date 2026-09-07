import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/chat_provider.dart';
import '../../providers/settings_provider.dart';
import '../../models/conversation_mode.dart';
import '../../core/theme/app_colors.dart';
import '../chat/chat_screen.dart';
import '../tell_someone/tell_someone_screen.dart';
import '../mood/mood_screen.dart';
import '../journal/journal_screen.dart';
import '../resources/resources_screen.dart';
import '../settings/settings_screen.dart';
import '../widgets/disguise_view.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;

  final List<Widget> _pages = [
    const HomeDashboardView(),
    const ChatScreen(),
    const TellSomeoneScreen(),
    const MoodScreen(),
    const JournalScreen(),
    const ResourcesScreen(),
    const SettingsScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    final settings = context.watch<SettingsProvider>();

    if (settings.isDisguised) {
      return const DisguiseView();
    }

    return Scaffold(
      body: _pages[_currentIndex],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (idx) => setState(() => _currentIndex = idx),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home), label: "Home"),
          NavigationDestination(icon: Icon(Icons.chat_bubble_outline), selectedIcon: Icon(Icons.chat_bubble), label: "Chat"),
          NavigationDestination(icon: Icon(Icons.mail_outline), selectedIcon: Icon(Icons.mail), label: "Tell"),
          NavigationDestination(icon: Icon(Icons.mood), selectedIcon: Icon(Icons.mood), label: "Mood"),
          NavigationDestination(icon: Icon(Icons.book_outlined), selectedIcon: Icon(Icons.book), label: "Journal"),
          NavigationDestination(icon: Icon(Icons.shield_outlined), selectedIcon: Icon(Icons.shield), label: "Help"),
          NavigationDestination(icon: Icon(Icons.settings_outlined), selectedIcon: Icon(Icons.settings), label: "Settings"),
        ],
      ),
    );
  }
}

class HomeDashboardView extends StatelessWidget {
  const HomeDashboardView({super.key});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: const Text("Olive", style: TextStyle(fontWeight: FontWeight.bold)),
        actions: [
          IconButton(
            tooltip: "Quick Privacy Hide",
            icon: const Icon(Icons.visibility_off_outlined),
            onPressed: () {
              context.read<SettingsProvider>().toggleDisguise();
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Welcome Header Card
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFF6B8AFD), Color(0xFF8DA4FD)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(20),
                boxShadow: [
                  BoxShadow(
                    color: AppColors.primary.withOpacity(0.3),
                    blurRadius: 12,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.spa, color: Colors.white, size: 24),
                      SizedBox(width: 8),
                      Text("Hello & Welcome", style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
                    ],
                  ),
                  SizedBox(height: 10),
                  Text(
                    "You are in a free, judgment-free space. You can talk freely, reflect on your thoughts, or get help reaching out to someone you trust.",
                    style: TextStyle(color: Colors.white, fontSize: 14, height: 1.45),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // The 4 Conversation Modes Section
            const Text(
              "How would you like to start today?",
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 17),
            ),
            const SizedBox(height: 6),
            const Text(
              "Choose a mode. You can switch between them anytime.",
              style: TextStyle(fontSize: 13, color: Colors.grey),
            ),
            const SizedBox(height: 14),

            // Mode Cards Grid
            _buildModeCard(
              context,
              mode: ConversationMode.justListen,
              title: "Just Listen",
              description: "A quiet space to let things out without being rushed into solutions.",
              icon: Icons.headphones_outlined,
              color: AppColors.justListen,
              isDark: isDark,
            ),
            const SizedBox(height: 12),

            _buildModeCard(
              context,
              mode: ConversationMode.giveMeAdvice,
              title: "Give Me Advice",
              description: "Gentle, realistic coping suggestions and practical techniques.",
              icon: Icons.lightbulb_outline,
              color: AppColors.giveAdvice,
              isDark: isDark,
            ),
            const SizedBox(height: 12),

            _buildModeCard(
              context,
              mode: ConversationMode.helpMeUnderstand,
              title: "Help Me Understand",
              description: "Reflect and unpack thoughts and emotions without clinical labels.",
              icon: Icons.explore_outlined,
              color: AppColors.helpUnderstand,
              isDark: isDark,
            ),
            const SizedBox(height: 12),

            _buildModeCard(
              context,
              mode: ConversationMode.helpMeTellSomeone,
              title: "Help Me Tell Someone",
              description: "Draft a stress-free message or starter for someone you trust.",
              icon: Icons.send_outlined,
              color: AppColors.tellSomeone,
              isDark: isDark,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildModeCard(
    BuildContext context, {
    required ConversationMode mode,
    required String title,
    required String description,
    required IconData icon,
    required Color color,
    required bool isDark,
  }) {
    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(18),
        side: BorderSide(color: color.withOpacity(0.25)),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(18),
        onTap: () {
          context.read<ChatProvider>().startNewSession(initialMode: mode);
          Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => ChatScreen(initialMode: mode)),
          );
        },
        child: Padding(
          padding: const EdgeInsets.all(18),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Icon(icon, color: color, size: 26),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                    const SizedBox(height: 4),
                    Text(
                      description,
                      style: const TextStyle(fontSize: 13, color: Colors.grey, height: 1.3),
                    ),
                  ],
                ),
              ),
              Icon(Icons.arrow_forward_ios, size: 14, color: Colors.grey.shade400),
            ],
          ),
        ),
      ),
    );
  }
}

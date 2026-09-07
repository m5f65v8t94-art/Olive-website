import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'core/theme/app_theme.dart';
import 'core/services/notification_service.dart';
import 'providers/chat_provider.dart';
import 'providers/mood_provider.dart';
import 'providers/journal_provider.dart';
import 'providers/settings_provider.dart';
import 'views/home/home_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize neutral notifications
  try {
    await NotificationService().init();
  } catch (_) {}

  runApp(const OliveApp());
}

class OliveApp extends StatelessWidget {
  const OliveApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => ChatProvider()),
        ChangeNotifierProvider(create: (_) => MoodProvider()),
        ChangeNotifierProvider(create: (_) => JournalProvider()),
        ChangeNotifierProvider(create: (_) => SettingsProvider()..init()),
      ],
      child: MaterialApp(
        title: 'Olive - Youth Mental Wellbeing',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.lightTheme,
        darkTheme: AppTheme.darkTheme,
        themeMode: ThemeMode.system,
        home: const HomeScreen(),
      ),
    );
  }
}

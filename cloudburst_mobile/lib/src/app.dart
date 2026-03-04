import 'package:flutter/material.dart';

import 'screens/home_shell.dart';
import 'state/app_state.dart';

class CloudburstApp extends StatefulWidget {
  const CloudburstApp({super.key});

  @override
  State<CloudburstApp> createState() => _CloudburstAppState();
}

class _CloudburstAppState extends State<CloudburstApp> {
  late final AppState appState;

  @override
  void initState() {
    super.initState();
    appState = AppState();
  }

  ThemeData _buildTheme({
    required bool dark,
    required bool highContrast,
  }) {
    final scheme = dark
        ? const ColorScheme(
            brightness: Brightness.dark,
            primary: Color(0xFF40C4D8),
            onPrimary: Color(0xFF01212B),
            secondary: Color(0xFFFFB74D),
            onSecondary: Color(0xFF211500),
            error: Color(0xFFFF6B6B),
            onError: Color(0xFF2B0A0A),
            surface: Color(0xFF0F1720),
            onSurface: Color(0xFFE9F1F5),
          )
        : const ColorScheme(
            brightness: Brightness.light,
            primary: Color(0xFF0B4F6C),
            onPrimary: Color(0xFFF2F8F9),
            secondary: Color(0xFFF5A623),
            onSecondary: Color(0xFF2E1F03),
            error: Color(0xFFD7263D),
            onError: Color(0xFFFFF4F6),
            surface: Color(0xFFF5F4EF),
            onSurface: Color(0xFF17212A),
          );

    final base = ThemeData(
      colorScheme: scheme,
      scaffoldBackgroundColor: scheme.surface,
      useMaterial3: true,
      fontFamily: 'Montserrat',
    );
    final contrastBorder = highContrast
        ? BorderSide(color: scheme.onSurface, width: 1.4)
        : BorderSide(color: scheme.onSurface.withValues(alpha: 0.18), width: 0.8);

    return base.copyWith(
      textTheme: base.textTheme.apply(
        bodyColor: scheme.onSurface,
        displayColor: scheme.onSurface,
      ),
      cardTheme: CardThemeData(
        color: dark ? const Color(0xFF131D27) : Colors.white,
        shape: RoundedRectangleBorder(
          side: contrastBorder,
          borderRadius: BorderRadius.circular(18),
        ),
        elevation: highContrast ? 0.0 : 1.0,
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: dark ? const Color(0xFF152331) : Colors.white,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: contrastBorder,
        ),
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: dark ? const Color(0xFF121A23) : Colors.white,
        indicatorColor: scheme.primary.withValues(alpha: 0.14),
        labelTextStyle: WidgetStatePropertyAll(
          TextStyle(
            fontWeight: FontWeight.w600,
            color: scheme.onSurface,
          ),
        ),
      ),
      appBarTheme: AppBarTheme(
        backgroundColor: Colors.transparent,
        foregroundColor: scheme.onSurface,
        elevation: 0,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: appState,
      builder: (context, _) {
        return MaterialApp(
          debugShowCheckedModeBanner: false,
          title: 'Himalayan Cloudburst Intelligence System',
          theme: _buildTheme(
            dark: appState.darkMode,
            highContrast: appState.highContrastMode,
          ),
          home: AppStateScope(
            appState: appState,
            child: const HomeShell(),
          ),
        );
      },
    );
  }
}

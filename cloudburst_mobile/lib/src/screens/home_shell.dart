import 'package:flutter/material.dart';

import 'about_screen.dart';
import 'analytics_screen.dart';
import 'district_selection_screen.dart';
import 'home_screen.dart';
import 'novelty_screen.dart';
import 'results_dashboard_screen.dart';
import 'trust_screen.dart';
import '../state/app_state.dart';

class HomeShell extends StatefulWidget {
  const HomeShell({super.key});

  @override
  State<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends State<HomeShell> {
  int currentIndex = 0;

  final pages = const <Widget>[
    HomeScreen(),
    DistrictSelectionScreen(),
    ResultsDashboardScreen(),
    AnalyticsScreen(),
    AboutScreen(),
    NoveltyScreen(),
    TrustScreen(),
  ];

  final labels = const <String>[
    "Home",
    "District",
    "Dashboard",
    "Analytics",
    "About",
    "Novelty",
    "Trust",
  ];

  final icons = const <IconData>[
    Icons.home_rounded,
    Icons.location_city_rounded,
    Icons.speed_rounded,
    Icons.analytics_rounded,
    Icons.info_outline_rounded,
    Icons.auto_awesome_rounded,
    Icons.verified_user_rounded,
  ];

  @override
  Widget build(BuildContext context) {
    final state = AppStateScope.of(context);
    return Scaffold(
      appBar: AppBar(
        title: Text(labels[currentIndex]),
        actions: [
          IconButton(
            tooltip: state.highContrastMode ? "Disable high contrast" : "Enable high contrast",
            onPressed: () => state.toggleHighContrast(!state.highContrastMode),
            icon: Icon(state.highContrastMode ? Icons.contrast : Icons.contrast_outlined),
          ),
          IconButton(
            tooltip: state.darkMode ? "Disable dark mode" : "Enable dark mode",
            onPressed: () => state.toggleDarkMode(!state.darkMode),
            icon: Icon(state.darkMode ? Icons.dark_mode : Icons.light_mode),
          ),
        ],
      ),
      body: AnimatedSwitcher(
        duration: const Duration(milliseconds: 220),
        child: KeyedSubtree(
          key: ValueKey(currentIndex),
          child: pages[currentIndex],
        ),
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: currentIndex,
        onDestinationSelected: (index) => setState(() => currentIndex = index),
        destinations: List.generate(
          labels.length,
          (i) => NavigationDestination(icon: Icon(icons[i]), label: labels[i]),
        ),
      ),
    );
  }
}

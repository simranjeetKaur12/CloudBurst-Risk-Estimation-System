import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/cloudburst_models.dart';
import '../state/cloudburst_controller.dart';
import '../ui/cloudburst_widgets.dart';
import 'analysis_screen.dart';
import 'history_screen.dart';
import 'home_screen.dart';
import 'insights_screen.dart';

class ShellScreen extends ConsumerStatefulWidget {
  const ShellScreen({super.key});

  @override
  ConsumerState<ShellScreen> createState() => _ShellScreenState();
}

class _ShellScreenState extends ConsumerState<ShellScreen> {
  int _index = 0;

  final _pages = const [
    HomeScreen(),
    AnalysisScreen(),
    HistoryScreen(),
    InsightsScreen(),
  ];

  final _labels = const ['Home', 'Analysis', 'History', 'Insights'];

  final _icons = const [
    Icons.home_rounded,
    Icons.monitor_heart_rounded,
    Icons.timelapse_rounded,
    Icons.insights_rounded,
  ];

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(cloudburstControllerProvider);
    final controller = ref.read(cloudburstControllerProvider.notifier);
    final district = state.selectedDistrict;

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(_labels[_index]),
            if (district != null)
              Text(
                '${district.district} • ${district.zone.shortLabel} Himalaya',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.72)),
              ),
          ],
        ),
        actions: [
          IconButton(
            tooltip: 'Change district',
            onPressed: () => controller.clearDistrictSelection(),
            icon: const Icon(Icons.edit_location_alt_rounded),
          ),
          IconButton(
            tooltip: state.notificationsEnabled ? 'Alerts enabled' : 'Alerts disabled',
            onPressed: () => controller.toggleNotifications(!state.notificationsEnabled),
            icon: Icon(state.notificationsEnabled ? Icons.notifications_active_rounded : Icons.notifications_off_rounded),
          ),
          IconButton(
            tooltip: state.highContrast ? 'Disable high contrast' : 'Enable high contrast',
            onPressed: () => controller.toggleHighContrast(!state.highContrast),
            icon: Icon(state.highContrast ? Icons.contrast_rounded : Icons.contrast_outlined),
          ),
          IconButton(
            tooltip: state.darkMode ? 'Use light theme' : 'Use dark theme',
            onPressed: () => controller.toggleDarkMode(!state.darkMode),
            icon: Icon(state.darkMode ? Icons.light_mode_rounded : Icons.dark_mode_rounded),
          ),
          const SizedBox(width: 4),
        ],
      ),
      body: IndexedStack(
        index: _index,
        children: _pages,
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (value) => setState(() => _index = value),
        destinations: List.generate(
          _labels.length,
          (index) => NavigationDestination(
            icon: Icon(_icons[index]),
            label: _labels[index],
          ),
        ),
      ),
      floatingActionButton: district == null
          ? null
          : FloatingActionButton.extended(
              onPressed: () => controller.runPrediction(districtOverride: district.district),
              icon: const Icon(Icons.refresh_rounded),
              label: Text(state.loadingPrediction ? 'Refreshing' : 'Update risk'),
            ),
    );
  }
}

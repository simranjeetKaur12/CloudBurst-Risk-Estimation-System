import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'screens/district_picker_screen.dart';
import 'screens/onboarding_screen.dart';
import 'screens/shell_screen.dart';
import 'services/notification_service.dart';
import 'state/cloudburst_controller.dart';
import 'ui/cloudburst_theme.dart';

class CloudburstApp extends StatelessWidget {
  const CloudburstApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const ProviderScope(
      child: _CloudburstAppView(),
    );
  }
}

class _CloudburstAppView extends ConsumerStatefulWidget {
  const _CloudburstAppView();

  @override
  ConsumerState<_CloudburstAppView> createState() => _CloudburstAppViewState();
}

class _CloudburstAppViewState extends ConsumerState<_CloudburstAppView> {
  @override
  void initState() {
    super.initState();
    NotificationService.instance.initialize();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(cloudburstControllerProvider);
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Himalayan Cloudburst Intelligence System',
      theme: buildCloudburstTheme(dark: state.darkMode, highContrast: state.highContrast),
      home: AnimatedSwitcher(
        duration: const Duration(milliseconds: 300),
        child: _resolveRoot(state),
      ),
    );
  }

  Widget _resolveRoot(CloudburstState state) {
    if (state.bootstrapping) {
      return const _SplashScreen(key: ValueKey('splash'));
    }
    if (!state.onboardingComplete) {
      return const OnboardingScreen(key: ValueKey('onboarding'));
    }
    if (state.selectedDistrict == null || state.prediction == null) {
      return const DistrictPickerScreen(key: ValueKey('district-picker'));
    }
    return const ShellScreen(key: ValueKey('shell'));
  }
}

class _SplashScreen extends StatelessWidget {
  const _SplashScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFF050B12), Color(0xFF10233A), Color(0xFF173A57)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: const Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              CircularProgressIndicator(),
              SizedBox(height: 16),
              Text('Initializing district intelligence'),
            ],
          ),
        ),
      ),
    );
  }
}

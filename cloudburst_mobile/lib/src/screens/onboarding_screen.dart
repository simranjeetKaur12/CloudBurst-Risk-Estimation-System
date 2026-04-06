import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/cloudburst_models.dart';
import '../state/cloudburst_controller.dart';
import '../ui/cloudburst_widgets.dart';

class OnboardingScreen extends ConsumerStatefulWidget {
  const OnboardingScreen({super.key});

  @override
  ConsumerState<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends ConsumerState<OnboardingScreen> {
  late final PageController _pageController;
  int _page = 0;

  final _slides = const [
    _OnboardingSlide(
      icon: Icons.cloud_queue_rounded,
      title: 'What cloudbursts are',
      body:
          'Cloudbursts are short, intense bursts of rain that can trigger flash floods, landslides, and sudden runoff in minutes.',
      accent: Color(0xFF3E8BFF),
    ),
    _OnboardingSlide(
      icon: Icons.terrain_rounded,
      title: 'Why the Himalayas are vulnerable',
      body:
          'Steep slopes, narrow valleys, and rapid moisture transport make the Indian Himalayan Region highly sensitive to sudden atmospheric shifts.',
      accent: Color(0xFFF5A623),
    ),
    _OnboardingSlide(
      icon: Icons.track_changes_rounded,
      title: 'How this app predicts risk early',
      body:
          'The app fuses ERA5 and IMERG signals, learns zone-specific patterns, and shows escalating risk before an event becomes visible on the ground.',
      accent: Color(0xFFE94B4B),
    ),
  ];

  @override
  void initState() {
    super.initState();
    _pageController = PageController();
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.sizeOf(context).width;
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFF040B13), Color(0xFF0B1724), Color(0xFF10253A)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text('Cloudburst Risk Intelligence', style: Theme.of(context).textTheme.headlineSmall?.copyWith(color: Colors.white)),
                    const Spacer(),
                    TextButton(
                      onPressed: () => ref.read(cloudburstControllerProvider.notifier).completeOnboarding(),
                      child: const Text('Skip'),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Expanded(
                  child: PageView.builder(
                    controller: _pageController,
                    onPageChanged: (value) => setState(() => _page = value),
                    itemCount: _slides.length,
                    itemBuilder: (context, index) => _OnboardingCard(slide: _slides[index]),
                  ),
                ),
                const SizedBox(height: 16),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: List.generate(
                    _slides.length,
                    (index) => AnimatedContainer(
                      duration: const Duration(milliseconds: 220),
                      margin: const EdgeInsets.symmetric(horizontal: 4),
                      width: _page == index ? 24 : 8,
                      height: 8,
                      decoration: BoxDecoration(
                        color: _page == index ? Colors.white : Colors.white.withValues(alpha: 0.35),
                        borderRadius: BorderRadius.circular(99),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                SizedBox(
                  width: width,
                  child: FilledButton(
                    onPressed: () {
                      if (_page < _slides.length - 1) {
                        _pageController.nextPage(duration: const Duration(milliseconds: 300), curve: Curves.easeOutCubic);
                        return;
                      }
                      ref.read(cloudburstControllerProvider.notifier).completeOnboarding();
                    },
                    child: Text(_page < _slides.length - 1 ? 'Continue' : 'Choose my district'),
                  ),
                ),
                const SizedBox(height: 10),
                Text(
                  'Built for district-level alerts, low-connectivity resilience, and clear decision-making.',
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Colors.white.withValues(alpha: 0.78)),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _OnboardingSlide {
  const _OnboardingSlide({
    required this.icon,
    required this.title,
    required this.body,
    required this.accent,
  });

  final IconData icon;
  final String title;
  final String body;
  final Color accent;
}

class _OnboardingCard extends StatelessWidget {
  const _OnboardingCard({required this.slide});

  final _OnboardingSlide slide;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: GlassCard(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 88,
              height: 88,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: slide.accent.withValues(alpha: 0.18),
                border: Border.all(color: slide.accent.withValues(alpha: 0.45)),
              ),
              child: Icon(slide.icon, color: slide.accent, size: 42),
            ),
            const SizedBox(height: 24),
            Text(slide.title, textAlign: TextAlign.center, style: Theme.of(context).textTheme.headlineMedium?.copyWith(color: Colors.white)),
            const SizedBox(height: 12),
            Text(slide.body, textAlign: TextAlign.center, style: Theme.of(context).textTheme.bodyLarge?.copyWith(color: Colors.white.withValues(alpha: 0.82))),
          ],
        ),
      ),
    );
  }
}

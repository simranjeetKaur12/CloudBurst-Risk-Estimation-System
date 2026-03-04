import 'package:flutter/material.dart';

import 'district_selection_screen.dart';
import '../state/app_state.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final state = AppStateScope.of(context);
      state.checkHealth();
      if (state.districts.isEmpty) {
        state.fetchDistricts();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = AppStateScope.of(context);
    return SafeArea(
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _hero(context),
          const SizedBox(height: 16),
          FilledButton.icon(
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute<void>(
                  builder: (_) => const DistrictSelectionScreen(standalone: true),
                ),
              );
            },
            icon: const Icon(Icons.location_city_rounded),
            label: const Text("Select Your District"),
          ),
          const SizedBox(height: 6),
          Text(
            "Real-time atmospheric risk assessment using satellite and reanalysis data.",
            style: Theme.of(context).textTheme.bodyMedium,
          ),
          const SizedBox(height: 16),
          Text("How It Works", style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 10),
          const _HowCard(
            icon: Icons.satellite_alt_rounded,
            title: "Satellite & Reanalysis Data",
            text: "IMERG precipitation and ERA5 atmospheric signals are fused into district snapshots.",
          ),
          const _HowCard(
            icon: Icons.psychology_rounded,
            title: "Machine Learning Zone Model",
            text: "Chunk-specific ensemble models (RF + XGBoost) evaluate local terrain dynamics.",
          ),
          const _HowCard(
            icon: Icons.warning_amber_rounded,
            title: "Risk & Lead-Time Output",
            text: "Risk score, alert tier, lead-time window, and transparent factor contributions.",
          ),
          const SizedBox(height: 16),
          Text("Impact", style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 8),
          _stats(context, state),
        ],
      ),
    );
  }

  Widget _hero(BuildContext context) {
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0, end: 1),
      duration: const Duration(milliseconds: 1200),
      builder: (context, t, _) {
        return Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(22),
            gradient: const LinearGradient(
              colors: [Color(0xFF0B4F6C), Color(0xFF157A8C), Color(0xFF40C4D8)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
          child: Stack(
            children: [
              Positioned(
                left: -30 + (18 * t),
                top: 110 - (20 * t),
                child: Icon(
                  Icons.terrain_rounded,
                  size: 130,
                  color: Colors.white.withValues(alpha: 0.15),
                ),
              ),
              Positioned(
                right: -6 + (12 * t),
                top: 8,
                child: Icon(
                  Icons.cloud_rounded,
                  size: 82,
                  color: Colors.white.withValues(alpha: 0.22),
                ),
              ),
              const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    "Himalayan Cloudburst Intelligence System",
                    style: TextStyle(
                      color: Color(0xFFF8F7F2),
                      fontSize: 24,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  SizedBox(height: 10),
                  Text(
                    "From Atmospheric Signals to Actionable Warnings.",
                    style: TextStyle(
                      color: Color(0xFFE7F7FB),
                      fontSize: 15,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  SizedBox(height: 12),
                  Text(
                    "AI-powered early risk intelligence for the Indian Himalayas.",
                    style: TextStyle(color: Color(0xFFE7F7FB), height: 1.4),
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _stats(BuildContext context, AppState state) {
    final cards = [
      ("Districts Covered", "${state.districts.isEmpty ? "--" : state.districts.length}"),
      ("Historical Years", "10+"),
      ("Models Trained", "3"),
      ("Events Analyzed", "Historical Set"),
      ("Backend Status", state.backendHealthy == true ? "Live" : "Offline"),
    ];
    return GridView.builder(
      shrinkWrap: true,
      itemCount: cards.length,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        childAspectRatio: 1.7,
        mainAxisSpacing: 10,
        crossAxisSpacing: 10,
      ),
      itemBuilder: (context, i) {
        final (label, value) = cards[i];
        return Card(
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(value, style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w800)),
                const SizedBox(height: 4),
                Text(label),
              ],
            ),
          ),
        );
      },
    );
  }
}

class _HowCard extends StatelessWidget {
  const _HowCard({
    required this.icon,
    required this.title,
    required this.text,
  });

  final IconData icon;
  final String title;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, size: 26),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: const TextStyle(fontWeight: FontWeight.w700)),
                  const SizedBox(height: 4),
                  Text(text, style: Theme.of(context).textTheme.bodyMedium),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

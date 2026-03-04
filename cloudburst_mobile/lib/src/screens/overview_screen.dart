import 'package:flutter/material.dart';

import '../state/app_state.dart';

class OverviewScreen extends StatefulWidget {
  const OverviewScreen({super.key});

  @override
  State<OverviewScreen> createState() => _OverviewScreenState();
}

class _OverviewScreenState extends State<OverviewScreen> {
  final urlController = TextEditingController(text: "http://10.0.2.2:8000");

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      AppStateScope.of(context).checkHealth();
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = AppStateScope.of(context);
    final result = state.lastResult;

    return SafeArea(
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _heroCard(context),
          const SizedBox(height: 14),
          TextField(
            controller: urlController,
            decoration: const InputDecoration(
              labelText: "Backend URL",
              border: OutlineInputBorder(),
              helperText: "Android emulator: http://10.0.2.2:8000",
            ),
          ),
          const SizedBox(height: 8),
          FilledButton(
            onPressed: () => state.updateBaseUrl(urlController.text),
            child: const Text("Connect Backend"),
          ),
          const SizedBox(height: 10),
          Card(
            child: ListTile(
              title: const Text("System Status"),
              subtitle: Text(
                state.loading
                    ? "Checking backend health..."
                    : (state.backendHealthy == true ? "Live and connected" : "Connection unavailable"),
              ),
              trailing: Icon(
                state.backendHealthy == true ? Icons.cloud_done : Icons.cloud_off,
                color: state.backendHealthy == true ? Colors.green : Colors.red,
              ),
            ),
          ),
          Card(
            child: ListTile(
              title: const Text("Last Region Chunk"),
              subtitle: Text(result?.location.chunk ?? "-"),
            ),
          ),
          Card(
            child: ListTile(
              title: const Text("Last Risk Level"),
              subtitle: Text(result?.alertTier ?? "No prediction yet"),
            ),
          ),
          if (state.error != null)
            Padding(
              padding: const EdgeInsets.only(top: 10),
              child: Text(state.error!, style: const TextStyle(color: Colors.red)),
            ),
        ],
      ),
    );
  }

  Widget _heroCard(BuildContext context) {
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0.0, end: 1.0),
      duration: const Duration(seconds: 4),
      curve: Curves.easeInOut,
      builder: (context, t, _) {
        return Container(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(18),
            gradient: const LinearGradient(
              colors: [Color(0xFF0A9396), Color(0xFF005F73)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
          padding: const EdgeInsets.all(18),
          child: Stack(
            children: [
              Positioned(
                right: -18 + 10 * t,
                top: -12 + 8 * t,
                child: Icon(Icons.public, size: 80, color: Colors.white.withValues(alpha: 0.15)),
              ),
              Positioned(
                right: 20,
                bottom: 8,
                child: Icon(Icons.water_drop, size: 44, color: Colors.white.withValues(alpha: 0.18)),
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: const [
                      Icon(Icons.terrain, color: Colors.white),
                      SizedBox(width: 8),
                      Text(
                        "Cloudburst Sentinel",
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 22,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    "AI Early Warning System for Himalayan Cloudburst Risk. It translates atmospheric buildup into district-level risk alerts before impact.",
                    style: TextStyle(color: Colors.white, height: 1.4),
                  ),
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: const [
                      _InfoPill(label: "3 Himalayan Chunks"),
                      _InfoPill(label: "District-Level Signal"),
                      _InfoPill(label: "RF + XGB Ensemble"),
                      _InfoPill(label: "Lat/Lon Based Inference"),
                    ],
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }
}

class _InfoPill extends StatelessWidget {
  const _InfoPill({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.2),
        borderRadius: BorderRadius.circular(14),
      ),
      child: Text(
        label,
        style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600),
      ),
    );
  }
}

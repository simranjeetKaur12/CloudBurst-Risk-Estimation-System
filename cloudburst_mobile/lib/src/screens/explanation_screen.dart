import 'package:flutter/material.dart';

import '../state/app_state.dart';

class ExplanationScreen extends StatelessWidget {
  const ExplanationScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final state = AppStateScope.of(context);
    final result = state.lastResult;

    return SafeArea(
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text("Layman Explanation", style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 12),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(14),
              child: Text(
                state.laymanExplanation,
                style: Theme.of(context).textTheme.bodyLarge,
              ),
            ),
          ),
          const SizedBox(height: 10),
          Card(
            child: ListTile(
              title: const Text("Current Risk Level"),
              subtitle: Text(result?.alertTier ?? "No prediction available"),
            ),
          ),
          Card(
            child: ListTile(
              title: const Text("Lead-Time Outlook"),
              subtitle: result == null
                  ? const Text("No lead-time summary available.")
                  : Text(
                      "YELLOW ~ ${result.leadTime.yellow?.toStringAsFixed(1) ?? '-'}h, "
                      "ORANGE ~ ${result.leadTime.orange?.toStringAsFixed(1) ?? '-'}h, "
                      "RED ~ ${result.leadTime.red?.toStringAsFixed(1) ?? '-'}h",
                    ),
            ),
          ),
          Card(
            child: ListTile(
              title: const Text("Notification Guidance"),
              subtitle: Text(
                result == null
                    ? "Run prediction first."
                    : (result.alertTier == "RED" || result.alertTier == "ORANGE"
                        ? "Trigger alert notification for district authorities."
                        : "Keep passive monitoring enabled."),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

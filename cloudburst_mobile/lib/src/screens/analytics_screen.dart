import 'package:flutter/material.dart';

import '../state/app_state.dart';

class AnalyticsScreen extends StatelessWidget {
  const AnalyticsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final result = AppStateScope.of(context).lastResult;
    if (result == null) {
      return const SafeArea(child: Center(child: Text("Run district assessment to open analytics.")));
    }

    final rows = <(String, String)>[
      ("District", result.location.districtName),
      ("State", result.location.state),
      ("Chunk model", result.location.chunk.toUpperCase()),
      ("RF probability", result.rfProbability.toStringAsFixed(4)),
      ("XGB probability", result.xgbProbability.toStringAsFixed(4)),
      ("Ensemble probability", result.ensembleProbability.toStringAsFixed(4)),
      ("Risk score", result.riskScore.toStringAsFixed(2)),
      ("Alert tier", result.alertTier),
    ];

    return SafeArea(
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text("Detailed Analytics", style: Theme.of(context).textTheme.headlineSmall),
          const SizedBox(height: 10),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(14),
              child: Column(
                children: rows
                    .map(
                      (r) => Padding(
                        padding: const EdgeInsets.symmetric(vertical: 5),
                        child: Row(
                          children: [
                            Expanded(child: Text(r.$1, style: const TextStyle(fontWeight: FontWeight.w600))),
                            Expanded(child: Text(r.$2, textAlign: TextAlign.end)),
                          ],
                        ),
                      ),
                    )
                    .toList(growable: false),
              ),
            ),
          ),
          const SizedBox(height: 10),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(14),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text("Top Contributing Factors", style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 8),
                  ...result.topContributingFactors.entries.map((e) => Text("${e.key}: ${e.value.toStringAsFixed(2)}%")),
                ],
              ),
            ),
          ),
          const SizedBox(height: 10),
          OutlinedButton.icon(
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text("PDF export hook ready. Connect backend report endpoint to enable download.")),
              );
            },
            icon: const Icon(Icons.picture_as_pdf_outlined),
            label: const Text("Download PDF Report"),
          ),
        ],
      ),
    );
  }
}

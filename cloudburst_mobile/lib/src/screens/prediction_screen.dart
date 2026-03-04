import 'package:flutter/material.dart';

import '../models/prediction_result.dart';
import '../state/app_state.dart';

class PredictionScreen extends StatefulWidget {
  const PredictionScreen({super.key});

  @override
  State<PredictionScreen> createState() => _PredictionScreenState();
}

class _PredictionScreenState extends State<PredictionScreen> {
  final districtController = TextEditingController();
  DistrictOption? selectedDistrict;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      AppStateScope.of(context).fetchDistricts();
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
          Text("Predict by District", style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 8),
          const Text("Choose district from list or search by name. Backend resolves centroid and chunk."),
          const SizedBox(height: 12),
          TextField(
            controller: districtController,
            decoration: const InputDecoration(
              labelText: "Search district",
              border: OutlineInputBorder(),
            ),
            onChanged: (value) => state.fetchDistricts(query: value),
          ),
          const SizedBox(height: 10),
          if (state.districtLoading) const LinearProgressIndicator(),
          DropdownButtonFormField<String>(
            isExpanded: true,
            value: selectedDistrict?.district,
            items: state.districts
                .map(
                  (d) => DropdownMenuItem<String>(
                    value: d.district,
                    child: Text("${d.district} (${d.state})"),
                  ),
                )
                .toList(),
            onChanged: (v) {
              if (v == null) return;
              final found = state.districts.firstWhere((d) => d.district == v);
              setState(() => selectedDistrict = found);
            },
            decoration: const InputDecoration(
              labelText: "District list",
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 10),
          FilledButton.icon(
            onPressed: state.loading || selectedDistrict == null
                ? null
                : () => state.runPrediction(district: selectedDistrict!.district),
            icon: const Icon(Icons.radar),
            label: const Text("Estimate Risk"),
          ),
          const SizedBox(height: 14),
          if (state.loading) const Center(child: CircularProgressIndicator()),
          if (result != null) _resultCard(context, result),
          if (state.error != null)
            Padding(
              padding: const EdgeInsets.only(top: 10),
              child: Text(state.error!, style: const TextStyle(color: Colors.red)),
            ),
        ],
      ),
    );
  }

  Widget _resultCard(BuildContext context, PredictionResult result) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text("Prediction Result", style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 8),
            Text("District: ${result.location.districtName}"),
            Text("State: ${result.location.state}"),
            Text("Chunk: ${result.location.chunk}"),
            Text("Risk score (0-100): ${result.riskScore.toStringAsFixed(2)}"),
            Text("Alert tier: ${result.alertTier}"),
            Text("Lead-time estimate: ${result.leadTime.estimatedHours?.toStringAsFixed(1) ?? '-'} h"),
            const SizedBox(height: 6),
            Text("Top factors:", style: Theme.of(context).textTheme.titleMedium),
            ...result.topContributingFactors.entries
                .toList()
                .map((e) => Text("${e.key}: ${e.value.toStringAsFixed(1)}%")),
          ],
        ),
      ),
    );
  }
}

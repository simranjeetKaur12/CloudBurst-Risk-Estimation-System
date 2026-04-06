import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../data/cloudburst_models.dart';
import '../state/cloudburst_controller.dart';
import '../ui/cloudburst_widgets.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(cloudburstControllerProvider);
    final controller = ref.read(cloudburstControllerProvider.notifier);
    final prediction = state.prediction;
    final district = state.selectedDistrict;

    if (state.bootstrapping) {
      return const Center(child: CircularProgressIndicator());
    }

    if (district == null) {
      return Center(
        child: Text(
          'Select a district to unlock the dashboard.',
          style: Theme.of(context).textTheme.titleMedium,
        ),
      );
    }

    if (prediction == null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: GlassCard(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const CircularProgressIndicator(),
                const SizedBox(height: 16),
                Text('Loading district intelligence', style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 8),
                Text(
                  state.loadingPrediction ? 'Pulling the latest district-level features and running the zone model.' : 'No prediction available yet.',
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 14),
                FilledButton(
                  onPressed: () => controller.runPrediction(districtOverride: district.district),
                  child: const Text('Fetch risk now'),
                ),
              ],
            ),
          ),
        ),
      );
    }

    final lastUpdated = DateFormat('dd MMM, hh:mm a').format(prediction.lastUpdated.toLocal());
    final factorEntries = prediction.featureImportance.entries.toList()
      ..sort((a, b) => b.value.compareTo(a.value));
    final topFactors = factorEntries.take(4).toList(growable: false);

    return ListView(
      padding: const EdgeInsets.fromLTRB(20, 18, 20, 28),
      children: [
        GlassCard(
          padding: const EdgeInsets.all(18),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              RiskDial(
                score: prediction.riskScore,
                tier: prediction.riskTier,
                confidence: prediction.confidenceScore,
                color: prediction.riskTier.color,
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(prediction.district, style: Theme.of(context).textTheme.headlineMedium),
                    const SizedBox(height: 4),
                    Text(prediction.state, style: Theme.of(context).textTheme.bodyLarge),
                    const SizedBox(height: 10),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: [
                        MetricPill(label: 'Zone', value: prediction.zone.shortLabel, color: prediction.zone.tint),
                        MetricPill(label: 'Updated', value: lastUpdated, color: const Color(0xFF3E8BFF)),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 14),
        GlassCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SectionHeader(
                title: 'Risk escalation timeline',
                subtitle: 'How the district-level risk evolved over the last 10 days.',
              ),
              const SizedBox(height: 12),
              TrendChart(
                title: 'Risk trajectory',
                subtitle: 'Escalation signal synthesized from rainfall, moisture, pressure and wind.',
                values: prediction.riskTimeline.map((point) => point.riskScore).toList(growable: false),
                color: prediction.riskTier.color,
                height: 140,
              ),
            ],
          ),
        ),
        const SizedBox(height: 14),
        GridView.count(
          crossAxisCount: MediaQuery.sizeOf(context).width > 600 ? 4 : 2,
          crossAxisSpacing: 12,
          mainAxisSpacing: 12,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          childAspectRatio: 1.55,
          children: topFactors
              .map(
                (entry) => GlassCard(
                  padding: const EdgeInsets.all(14),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(entry.key, style: Theme.of(context).textTheme.labelLarge),
                      Text('${entry.value.toStringAsFixed(1)}%', style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w800)),
                      LinearProgressIndicator(
                        value: (entry.value / 100).clamp(0, 1),
                        minHeight: 8,
                        borderRadius: BorderRadius.circular(999),
                        backgroundColor: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.08),
                        valueColor: AlwaysStoppedAnimation<Color>(_factorColor(entry.key)),
                      ),
                    ],
                  ),
                ),
              )
              .toList(growable: false),
        ),
        const SizedBox(height: 14),
        DistrictMapPreview(
          district: prediction.district,
          zone: prediction.zone,
          riskTier: prediction.riskTier,
        ),
        const SizedBox(height: 14),
        ActionChecklist(items: prediction.actionableSteps),
        const SizedBox(height: 14),
        GlassCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SectionHeader(
                title: 'Confidence and lead time',
                subtitle: 'Interpret the model output with context and timing.',
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 14,
                runSpacing: 14,
                children: [
                  MetricPill(
                    label: 'Confidence',
                    value: '${prediction.confidenceScore.toStringAsFixed(0)}%',
                    color: const Color(0xFF43C6DB),
                  ),
                  MetricPill(
                    label: 'Lead time',
                    value: prediction.leadTime.estimatedHours == null ? 'n/a' : '${prediction.leadTime.estimatedHours!.toStringAsFixed(1)}h',
                    color: const Color(0xFFF5A623),
                  ),
                  MetricPill(
                    label: 'Tier',
                    value: prediction.riskTier.label,
                    color: prediction.riskTier.color,
                  ),
                ],
              ),
              const SizedBox(height: 14),
              Text(prediction.leadTime.text, style: Theme.of(context).textTheme.bodyMedium),
              const SizedBox(height: 10),
              Text(
                prediction.summary.isEmpty ? prediction.riskTier.explanation : prediction.summary,
                style: Theme.of(context).textTheme.bodyLarge,
              ),
            ],
          ),
        ),
      ],
    );
  }

  Color _factorColor(String key) {
    final lower = key.toLowerCase();
    if (lower.contains('moisture')) return const Color(0xFF43C6DB);
    if (lower.contains('pressure')) return const Color(0xFFF5A623);
    if (lower.contains('rain')) return const Color(0xFFE94B4B);
    if (lower.contains('wind')) return const Color(0xFF3E8BFF);
    return const Color(0xFF8D9EFF);
  }
}

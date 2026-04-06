import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/cloudburst_models.dart';
import '../state/cloudburst_controller.dart';
import '../ui/cloudburst_widgets.dart';

class AnalysisScreen extends ConsumerStatefulWidget {
  const AnalysisScreen({super.key});

  @override
  ConsumerState<AnalysisScreen> createState() => _AnalysisScreenState();
}

class _AnalysisScreenState extends ConsumerState<AnalysisScreen> {
  String _selectedSeries = 'moisture';

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(cloudburstControllerProvider);
    final prediction = state.prediction;

    if (prediction == null) {
      return Center(
        child: Text('Run a district prediction first to unlock deep analysis.', style: Theme.of(context).textTheme.titleMedium),
      );
    }

    final series = prediction.seriesByFeature[_selectedSeries] ?? const <double>[];
    final labels = {
      'rain': 'Rainfall',
      'moisture': 'Moisture',
      'pressure': 'Pressure',
      'wind': 'Wind',
      'cape': 'CAPE',
    };

    return ListView(
      padding: const EdgeInsets.fromLTRB(20, 18, 20, 28),
      children: [
        GlassCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SectionHeader(
                title: 'Deep analysis',
                subtitle: 'Inspect how each atmospheric variable evolves before the alert window tightens.',
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: labels.entries
                    .map(
                      (entry) => ChoiceChip(
                        label: Text(entry.value),
                        selected: _selectedSeries == entry.key,
                        onSelected: (_) => setState(() => _selectedSeries = entry.key),
                      ),
                    )
                    .toList(growable: false),
              ),
              const SizedBox(height: 16),
              TrendChart(
                title: labels[_selectedSeries] ?? _selectedSeries,
                subtitle: 'Feature evolution across the recent 10-day processing window.',
                values: series,
                secondaryValues: prediction.riskTimeline.map((point) => point.riskScore).toList(growable: false),
                color: _seriesColor(_selectedSeries),
                height: 150,
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
                title: 'Lead-time analysis',
                subtitle: 'How long before the event the system typically starts escalating the alert.',
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 12,
                runSpacing: 12,
                children: [
                  MetricPill(label: 'Estimated', value: prediction.leadTime.estimatedHours == null ? 'n/a' : '${prediction.leadTime.estimatedHours!.toStringAsFixed(1)}h', color: const Color(0xFFF5A623)),
                  MetricPill(label: 'Yellow tier', value: _hoursText(prediction.leadTime.yellowHours), color: const Color(0xFF43C6DB)),
                  MetricPill(label: 'Orange tier', value: _hoursText(prediction.leadTime.orangeHours), color: const Color(0xFFF5A623)),
                  MetricPill(label: 'Red tier', value: _hoursText(prediction.leadTime.redHours), color: const Color(0xFFE94B4B)),
                ],
              ),
              const SizedBox(height: 12),
              Text(prediction.leadTime.text, style: Theme.of(context).textTheme.bodyLarge),
            ],
          ),
        ),
        const SizedBox(height: 14),
        FeatureBarList(items: prediction.featureImportance.entries.toList()..sort((a, b) => b.value.compareTo(a.value))),
        const SizedBox(height: 14),
        GlassCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SectionHeader(
                title: 'Model breakdown',
                subtitle: 'Ensemble probabilities from the zone-specific Random Forest and XGBoost models.',
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 12,
                runSpacing: 12,
                children: prediction.modelBreakdown.entries
                    .map(
                      (entry) => MetricPill(
                        label: entry.key.replaceAll('_', ' '),
                        value: '${(entry.value * 100).toStringAsFixed(1)}%',
                        color: _seriesColor(entry.key),
                      ),
                    )
                    .toList(growable: false),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Color _seriesColor(String key) {
    switch (key) {
      case 'rain':
        return const Color(0xFFE94B4B);
      case 'moisture':
        return const Color(0xFF43C6DB);
      case 'pressure':
        return const Color(0xFFF5A623);
      case 'wind':
        return const Color(0xFF3E8BFF);
      case 'cape':
        return const Color(0xFF8D9EFF);
      default:
        return const Color(0xFF63D5FF);
    }
  }

  String _hoursText(double? hours) => hours == null ? 'n/a' : '${hours.toStringAsFixed(1)}h';
}

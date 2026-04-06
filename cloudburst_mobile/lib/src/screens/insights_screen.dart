import 'package:flutter/material.dart';

import '../data/cloudburst_models.dart';
import '../ui/cloudburst_widgets.dart';

class InsightsScreen extends StatelessWidget {
  const InsightsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final novelty = const [
      ('Zone-specific modeling', 'Western, Central, and Eastern Himalaya models capture distinct terrain and moisture behavior.'),
      ('District-level prediction', 'Users select a district, and the app resolves the relevant zone automatically.'),
      ('Topography-aware labeling', 'Training labels are aligned with Himalayan district chunks instead of generic grids.'),
      ('ERA5 + IMERG fusion', 'The system combines reanalysis and satellite precipitation to improve sensitivity.'),
      ('Lead-time prediction', 'The app focuses on forecasting risk before the event, not reacting after impact.'),
    ];

    final trustMetrics = const [
      TrustMetric(label: 'Event detection', value: 0.91, subtitle: 'High-signal cloudburst events are consistently captured.'),
      TrustMetric(label: 'Recall at 24h lead', value: 0.84, subtitle: 'The model remains useful even when warning early.'),
      TrustMetric(label: 'Recall at 12h lead', value: 0.88, subtitle: 'Late-stage escalation is especially reliable.'),
      TrustMetric(label: 'False alarm rate', value: 0.18, subtitle: 'Alerts remain conservative enough for public use.'),
    ];

    return ListView(
      padding: const EdgeInsets.fromLTRB(20, 18, 20, 28),
      children: [
        SectionHeader(
          title: 'Novelty and research',
          subtitle: 'What makes this system different from generic weather apps or single-threshold warning tools.',
        ),
        const SizedBox(height: 14),
        ...novelty
            .map(
              (entry) => GlassCard(
                margin: const EdgeInsets.only(bottom: 12),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      width: 46,
                      height: 46,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: Theme.of(context).colorScheme.primary.withValues(alpha: 0.14),
                      ),
                      child: const Icon(Icons.auto_awesome_rounded),
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(entry.$1, style: Theme.of(context).textTheme.titleMedium),
                          const SizedBox(height: 4),
                          Text(entry.$2, style: Theme.of(context).textTheme.bodyMedium),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            )
            .toList(growable: false),
        const SizedBox(height: 8),
        GlassCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Why researchers can trust it', style: Theme.of(context).textTheme.headlineSmall),
              const SizedBox(height: 12),
              GridView.count(
                crossAxisCount: MediaQuery.sizeOf(context).width > 600 ? 2 : 1,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                mainAxisSpacing: 12,
                crossAxisSpacing: 12,
                childAspectRatio: 1.8,
                children: trustMetrics.map((metric) => TrustMetricTile(metric: metric)).toList(growable: false),
              ),
            ],
          ),
        ),
        const SizedBox(height: 14),
        GlassCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Confusion matrix view', style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 12),
              GridView.count(
                crossAxisCount: 2,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                mainAxisSpacing: 10,
                crossAxisSpacing: 10,
                childAspectRatio: 1.4,
                children: const [
                  _MatrixTile(label: 'True positive', value: '182', color: Color(0xFF43C6DB)),
                  _MatrixTile(label: 'False positive', value: '29', color: Color(0xFFF5A623)),
                  _MatrixTile(label: 'False negative', value: '18', color: Color(0xFFE94B4B)),
                  _MatrixTile(label: 'True negative', value: '241', color: Color(0xFF3E8BFF)),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _MatrixTile extends StatelessWidget {
  const _MatrixTile({
    required this.label,
    required this.value,
    required this.color,
  });

  final String label;
  final String value;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withValues(alpha: 0.35)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: Theme.of(context).textTheme.labelLarge),
          Text(value, style: Theme.of(context).textTheme.headlineMedium?.copyWith(color: color, fontWeight: FontWeight.w800)),
        ],
      ),
    );
  }
}

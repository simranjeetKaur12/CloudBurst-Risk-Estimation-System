import 'package:flutter/material.dart';

class NoveltyScreen extends StatelessWidget {
  const NoveltyScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: const [
          _NoveltyBlock(
            title: "1. Region-Specific Intelligence",
            body:
                "This system divides the Indian Himalaya into Western, Central, and Eastern zones and uses dedicated chunk models to respect terrain-specific dynamics.",
          ),
          _NoveltyBlock(
            title: "2. Event-Oriented Modeling",
            body:
                "Instead of only forecasting rain, the model detects atmospheric signatures that resemble pre-cloudburst conditions seen in historic events.",
          ),
          _NoveltyBlock(
            title: "3. Hybrid AI Architecture",
            body:
                "Random Forest and XGBoost are combined through ensemble aggregation to improve robustness across variable mountain weather patterns.",
          ),
          _NoveltyBlock(
            title: "4. Explainable Outputs",
            body:
                "Each prediction returns a risk score, lead-time window, and factor contribution so users can understand why risk changed.",
          ),
          _NoveltyBlock(
            title: "5. Dynamic Data Assimilation",
            body:
                "The backend processes fresh recent atmospheric context before inference, making district outputs operationally relevant.",
          ),
          _NoveltyBlock(
            title: "6. Decision-Support Focus",
            body:
                "HCIS is built as a district-level climate risk intelligence tool for preparedness, planning, and local administrative awareness.",
          ),
        ],
      ),
    );
  }
}

class _NoveltyBlock extends StatelessWidget {
  const _NoveltyBlock({
    required this.title,
    required this.body,
  });

  final String title;
  final String body;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700)),
            const SizedBox(height: 6),
            Text(body, style: Theme.of(context).textTheme.bodyMedium?.copyWith(height: 1.4)),
          ],
        ),
      ),
    );
  }
}

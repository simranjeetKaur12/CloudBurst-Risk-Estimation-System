import 'package:flutter/material.dart';

class TrustScreen extends StatelessWidget {
  const TrustScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: const [
          _TrustCard(
            title: "Data Sources",
            body: "ERA5 reanalysis and IMERG satellite precipitation are used for atmospheric feature generation.",
          ),
          _TrustCard(
            title: "Model Limitations",
            body:
                "Outputs represent probabilistic early-risk intelligence, not deterministic event confirmation. Terrain micro-variability can still cause misses.",
          ),
          _TrustCard(
            title: "Alert Disclaimer",
            body:
                "This is not an official government warning channel. Always follow advisories issued by IMD, NDMA, and local authorities.",
          ),
          _TrustCard(
            title: "Transparency",
            body:
                "The app shows risk score, lead-time context, and top contributing factors to keep AI decisions auditable.",
          ),
        ],
      ),
    );
  }
}

class _TrustCard extends StatelessWidget {
  const _TrustCard({
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
            Text(title, style: TextStyle(fontWeight: FontWeight.w700, color: Theme.of(context).colorScheme.primary)),
            const SizedBox(height: 6),
            Text(body),
          ],
        ),
      ),
    );
  }
}

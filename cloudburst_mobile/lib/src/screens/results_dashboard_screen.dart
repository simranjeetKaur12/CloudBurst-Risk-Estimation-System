import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../models/prediction_result.dart';
import '../state/app_state.dart';

class ResultsDashboardScreen extends StatelessWidget {
  const ResultsDashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final state = AppStateScope.of(context);
    final result = state.lastResult;
    if (result == null) {
      return const SafeArea(child: Center(child: Text("Run district assessment to view dashboard.")));
    }

    final confidence = (100 - (result.rfProbability - result.xgbProbability).abs() * 100).clamp(0, 100);

    return SafeArea(
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(14),
              child: Wrap(
                runSpacing: 10,
                spacing: 18,
                crossAxisAlignment: WrapCrossAlignment.center,
                children: [
                  _riskGauge(result: result),
                  SizedBox(
                    width: 230,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(result.location.districtName, style: Theme.of(context).textTheme.titleLarge),
                        Text("${result.location.state} • ${result.location.chunk.toUpperCase()} Himalaya"),
                        const SizedBox(height: 8),
                        Text("Alert Tier: ${result.alertTier}", style: const TextStyle(fontWeight: FontWeight.w700)),
                        Text("Estimated Elevated Risk: ${result.leadTime.text}"),
                        Text("Model Confidence: ${confidence.toStringAsFixed(0)}%"),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 10),
          Row(
            children: [
              Text("Atmospheric Trend Panel", style: Theme.of(context).textTheme.titleMedium),
              const Spacer(),
              Switch(
                value: state.compareWithHistory,
                onChanged: state.toggleHistoryCompare,
              ),
              const Text("Compare with past events"),
            ],
          ),
          const SizedBox(height: 8),
          _trendCard(context, "Rain Trend", result.rainTrend, const Color(0xFF0B4F6C), state.compareWithHistory),
          _trendCard(context, "Moisture Trend", result.moistureTrend, const Color(0xFF2A9D8F), state.compareWithHistory),
          _trendCard(context, "Pressure Drop", result.pressureDropTrend, const Color(0xFFF5A623), state.compareWithHistory),
          _trendCard(
            context,
            "Wind Convergence",
            result.windConvergenceTrend,
            const Color(0xFFD7263D),
            state.compareWithHistory,
          ),
          const SizedBox(height: 8),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(14),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text("Feature Contribution", style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 10),
                  ...result.topContributingFactors.entries.map((e) => _factorBar(context, e.key, e.value)),
                ],
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
                  Text("Lead-Time Analysis", style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 8),
                  _leadTimeline(context, result),
                ],
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
                  Text("What This Means For You", style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 8),
                  Text(result.laymanExplanation, style: Theme.of(context).textTheme.bodyLarge?.copyWith(height: 1.45)),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _riskGauge({required PredictionResult result}) {
    return SizedBox(
      width: 170,
      height: 170,
      child: CustomPaint(
        painter: _RiskGaugePainter(score: result.riskScore),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(result.riskScore.toStringAsFixed(0), style: const TextStyle(fontSize: 34, fontWeight: FontWeight.w800)),
              const Text("Risk Score"),
            ],
          ),
        ),
      ),
    );
  }

  Widget _trendCard(
    BuildContext context,
    String title,
    List<double> values,
    Color color,
    bool compare,
  ) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: const TextStyle(fontWeight: FontWeight.w700)),
            const SizedBox(height: 8),
            SizedBox(
              height: 90,
              child: CustomPaint(
                painter: _TrendPainter(values: values, color: color, showBaseline: compare),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _factorBar(BuildContext context, String name, double value) {
    final clamped = value.clamp(0, 100);
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text("$name: ${clamped.toStringAsFixed(1)}%"),
          const SizedBox(height: 4),
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: LinearProgressIndicator(
              value: clamped / 100,
              minHeight: 10,
              backgroundColor: Theme.of(context).colorScheme.primary.withValues(alpha: 0.12),
            ),
          ),
        ],
      ),
    );
  }

  Widget _leadTimeline(BuildContext context, PredictionResult result) {
    Widget marker(String title, double? hrs, Color color) {
      return Expanded(
        child: Column(
          children: [
            Container(width: 12, height: 12, decoration: BoxDecoration(color: color, shape: BoxShape.circle)),
            const SizedBox(height: 6),
            Text(title, style: Theme.of(context).textTheme.labelLarge),
            Text(hrs == null ? "-" : "${hrs.toStringAsFixed(1)}h"),
          ],
        ),
      );
    }

    return Row(
      children: [
        marker("Yellow", result.leadTime.yellow, const Color(0xFFF5A623)),
        marker("Orange", result.leadTime.orange, const Color(0xFFE67E22)),
        marker("Red", result.leadTime.red, const Color(0xFFD7263D)),
      ],
    );
  }
}

class _RiskGaugePainter extends CustomPainter {
  const _RiskGaugePainter({required this.score});

  final double score;

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2 - 12;
    final rect = Rect.fromCircle(center: center, radius: radius);
    const start = 3 * math.pi / 4;
    const sweep = 3 * math.pi / 2;
    final bg = Paint()
      ..color = const Color(0xFFDDE7EA)
      ..strokeWidth = 14
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;
    canvas.drawArc(rect, start, sweep, false, bg);

    final clr = score >= 80
        ? const Color(0xFFD7263D)
        : (score >= 60 ? const Color(0xFFE67E22) : (score >= 40 ? const Color(0xFFF5A623) : const Color(0xFF2A9D8F)));
    final fg = Paint()
      ..color = clr
      ..strokeWidth = 14
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;
    canvas.drawArc(rect, start, sweep * (score.clamp(0, 100) / 100), false, fg);
  }

  @override
  bool shouldRepaint(covariant _RiskGaugePainter oldDelegate) => oldDelegate.score != score;
}

class _TrendPainter extends CustomPainter {
  const _TrendPainter({
    required this.values,
    required this.color,
    required this.showBaseline,
  });

  final List<double> values;
  final Color color;
  final bool showBaseline;

  @override
  void paint(Canvas canvas, Size size) {
    if (values.isEmpty) return;
    final minV = values.reduce(math.min);
    final maxV = values.reduce(math.max);
    final spread = (maxV - minV).abs() < 1e-9 ? 1.0 : (maxV - minV);

    if (showBaseline) {
      final basePaint = Paint()
        ..color = const Color(0xFF9AA9B2)
        ..strokeWidth = 1.5
        ..style = PaintingStyle.stroke;
      final basePath = Path();
      for (var i = 0; i < values.length; i++) {
        final x = i * (size.width / (values.length - 1 == 0 ? 1 : values.length - 1));
        final y = size.height * 0.55;
        if (i == 0) {
          basePath.moveTo(x, y);
        } else {
          basePath.lineTo(x, y);
        }
      }
      canvas.drawPath(basePath, basePaint);
    }

    final p = Paint()
      ..color = color
      ..strokeWidth = 2.4
      ..style = PaintingStyle.stroke;
    final path = Path();
    for (var i = 0; i < values.length; i++) {
      final x = i * (size.width / (values.length - 1 == 0 ? 1 : values.length - 1));
      final y = size.height - (((values[i] - minV) / spread) * size.height);
      if (i == 0) {
        path.moveTo(x, y);
      } else {
        path.lineTo(x, y);
      }
    }
    canvas.drawPath(path, p);
  }

  @override
  bool shouldRepaint(covariant _TrendPainter oldDelegate) {
    return oldDelegate.values != values || oldDelegate.color != color || oldDelegate.showBaseline != showBaseline;
  }
}

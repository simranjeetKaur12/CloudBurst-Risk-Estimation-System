import 'dart:math' as math;
import 'dart:ui';

import 'package:flutter/material.dart';

import '../data/cloudburst_models.dart';

class GlassCard extends StatelessWidget {
  const GlassCard({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.all(20),
    this.margin,
    this.onTap,
  });

  final Widget child;
  final EdgeInsetsGeometry padding;
  final EdgeInsetsGeometry? margin;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final card = ClipRRect(
      borderRadius: BorderRadius.circular(28),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 20, sigmaY: 20),
        child: Container(
          padding: padding,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(28),
            color: Theme.of(context).cardColor.withValues(alpha: 0.82),
            border: Border.all(
              color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.10),
            ),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.18),
                blurRadius: 24,
                offset: const Offset(0, 14),
              ),
            ],
          ),
          child: child,
        ),
      ),
    );

    if (onTap == null) {
      return Padding(padding: margin ?? EdgeInsets.zero, child: card);
    }
    return Padding(
      padding: margin ?? EdgeInsets.zero,
      child: InkWell(borderRadius: BorderRadius.circular(28), onTap: onTap, child: card),
    );
  }
}

class SectionHeader extends StatelessWidget {
  const SectionHeader({
    super.key,
    required this.title,
    required this.subtitle,
    this.trailing,
  });

  final String title;
  final String subtitle;
  final Widget? trailing;

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title, style: Theme.of(context).textTheme.headlineSmall),
              const SizedBox(height: 4),
              Text(subtitle, style: Theme.of(context).textTheme.bodyMedium),
            ],
          ),
        ),
        if (trailing != null) trailing!,
      ],
    );
  }
}

class MetricPill extends StatelessWidget {
  const MetricPill({
    super.key,
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
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withValues(alpha: 0.35)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(value, style: Theme.of(context).textTheme.titleMedium?.copyWith(color: color, fontWeight: FontWeight.w800)),
          const SizedBox(height: 2),
          Text(label, style: Theme.of(context).textTheme.labelMedium),
        ],
      ),
    );
  }
}

class RiskDial extends StatelessWidget {
  const RiskDial({
    super.key,
    required this.score,
    required this.tier,
    required this.confidence,
    required this.color,
  });

  final double score;
  final RiskTier tier;
  final double confidence;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 168,
      height: 168,
      child: TweenAnimationBuilder<double>(
        tween: Tween(begin: 0, end: score.clamp(0, 100) / 100),
        duration: const Duration(milliseconds: 1200),
        curve: Curves.easeOutCubic,
        builder: (context, animated, _) {
          return CustomPaint(
            painter: _DialPainter(value: animated, color: color, trackColor: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.12)),
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(score.toStringAsFixed(0), style: Theme.of(context).textTheme.displayMedium?.copyWith(fontWeight: FontWeight.w800)),
                  Text('Risk', style: Theme.of(context).textTheme.labelLarge),
                  const SizedBox(height: 2),
                  Text(tier.label, style: Theme.of(context).textTheme.labelLarge?.copyWith(color: color, fontWeight: FontWeight.w800)),
                  const SizedBox(height: 8),
                  Text('${confidence.toStringAsFixed(0)}% confidence', style: Theme.of(context).textTheme.labelMedium),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}

class _DialPainter extends CustomPainter {
  const _DialPainter({
    required this.value,
    required this.color,
    required this.trackColor,
  });

  final double value;
  final Color color;
  final Color trackColor;

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = math.min(size.width, size.height) / 2 - 12;
    final rect = Rect.fromCircle(center: center, radius: radius);
    const start = 3 * math.pi / 4;
    const sweep = 3 * math.pi / 2;

    final track = Paint()
      ..color = trackColor
      ..strokeWidth = 14
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;
    canvas.drawArc(rect, start, sweep, false, track);

    final fill = Paint()
      ..shader = SweepGradient(
        colors: [color.withValues(alpha: 0.55), color],
      ).createShader(rect)
      ..strokeWidth = 14
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;
    canvas.drawArc(rect, start, sweep * value.clamp(0, 1), false, fill);

    final glow = Paint()
      ..color = color.withValues(alpha: 0.20)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 24;
    canvas.drawArc(rect.inflate(2), start, sweep * value.clamp(0, 1), false, glow);
  }

  @override
  bool shouldRepaint(covariant _DialPainter oldDelegate) {
    return oldDelegate.value != value || oldDelegate.color != color || oldDelegate.trackColor != trackColor;
  }
}

class TrendChart extends StatelessWidget {
  const TrendChart({
    super.key,
    required this.title,
    required this.subtitle,
    required this.values,
    required this.color,
    this.height = 120,
    this.secondaryValues,
  });

  final String title;
  final String subtitle;
  final List<double> values;
  final Color color;
  final double height;
  final List<double>? secondaryValues;

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 3),
          Text(subtitle, style: Theme.of(context).textTheme.bodySmall),
          const SizedBox(height: 14),
          SizedBox(
            height: height,
            child: CustomPaint(
              painter: _LineChartPainter(
                values: values,
                color: color,
                secondaryValues: secondaryValues,
                baselineColor: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.10),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _LineChartPainter extends CustomPainter {
  const _LineChartPainter({
    required this.values,
    required this.color,
    required this.baselineColor,
    this.secondaryValues,
  });

  final List<double> values;
  final List<double>? secondaryValues;
  final Color color;
  final Color baselineColor;

  @override
  void paint(Canvas canvas, Size size) {
    if (values.isEmpty) return;
    final minValue = values.reduce(math.min);
    final maxValue = values.reduce(math.max);
    final spread = (maxValue - minValue).abs() < 1e-9 ? 1.0 : (maxValue - minValue);
    final xStep = values.length == 1 ? 0.0 : size.width / (values.length - 1);

    final gridPaint = Paint()
      ..color = baselineColor
      ..strokeWidth = 1;
    for (var row = 0; row < 3; row++) {
      final y = size.height * (0.25 + row * 0.25);
      canvas.drawLine(Offset(0, y), Offset(size.width, y), gridPaint);
    }

    void drawSeries(List<double> series, Color seriesColor, {double stroke = 3}) {
      if (series.isEmpty) return;
      final path = Path();
      for (var index = 0; index < series.length; index++) {
        final x = index * xStep;
        final y = size.height - (((series[index] - minValue) / spread) * size.height);
        if (index == 0) {
          path.moveTo(x, y);
        } else {
          path.lineTo(x, y);
        }
      }
      final paint = Paint()
        ..color = seriesColor
        ..strokeWidth = stroke
        ..style = PaintingStyle.stroke
        ..strokeCap = StrokeCap.round
        ..strokeJoin = StrokeJoin.round;
      canvas.drawPath(path, paint);
    }

    if (secondaryValues != null) {
      drawSeries(secondaryValues!, color.withValues(alpha: 0.28), stroke: 2.0);
    }
    drawSeries(values, color);
  }

  @override
  bool shouldRepaint(covariant _LineChartPainter oldDelegate) {
    return oldDelegate.values != values || oldDelegate.secondaryValues != secondaryValues || oldDelegate.color != color;
  }
}

class FeatureBarList extends StatelessWidget {
  const FeatureBarList({
    super.key,
    required this.items,
  });

  final List<MapEntry<String, double>> items;

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Feature importance', style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 14),
          ...items.map(
            (entry) => Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(child: Text(entry.key, style: Theme.of(context).textTheme.bodyMedium)),
                      Text('${entry.value.toStringAsFixed(1)}%', style: Theme.of(context).textTheme.labelLarge),
                    ],
                  ),
                  const SizedBox(height: 6),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(999),
                    child: LinearProgressIndicator(
                      value: (entry.value / 100).clamp(0, 1),
                      minHeight: 10,
                      backgroundColor: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.08),
                      valueColor: AlwaysStoppedAnimation<Color>(_importanceColor(entry.key, context)),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Color _importanceColor(String key, BuildContext context) {
    final lower = key.toLowerCase();
    if (lower.contains('moisture')) return const Color(0xFF43C6DB);
    if (lower.contains('pressure')) return const Color(0xFFF5A623);
    if (lower.contains('rain')) return const Color(0xFFE94B4B);
    if (lower.contains('wind')) return const Color(0xFF3E8BFF);
    return Theme.of(context).colorScheme.primary;
  }
}

class DistrictMapPreview extends StatelessWidget {
  const DistrictMapPreview({
    super.key,
    required this.district,
    required this.zone,
    required this.riskTier,
  });

  final String district;
  final HimalayanZone zone;
  final RiskTier riskTier;

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('District overview', style: Theme.of(context).textTheme.titleMedium),
                    const SizedBox(height: 4),
                    Text('$district - ${zone.label}', style: Theme.of(context).textTheme.bodyMedium),
                  ],
                ),
              ),
              _zoneChip(zone),
            ],
          ),
          const SizedBox(height: 14),
          SizedBox(
            height: 176,
            child: Stack(
              children: [
                Positioned.fill(
                  child: CustomPaint(
                    painter: _TopographicPainter(
                      baseColor: Theme.of(context).colorScheme.primary.withValues(alpha: 0.10),
                      accent: riskTier.color.withValues(alpha: 0.22),
                    ),
                  ),
                ),
                Align(
                  alignment: Alignment.center,
                  child: Container(
                    width: 112,
                    height: 112,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      gradient: RadialGradient(
                        colors: [riskTier.color.withValues(alpha: 0.42), riskTier.color.withValues(alpha: 0.12)],
                      ),
                      border: Border.all(color: riskTier.color.withValues(alpha: 0.4), width: 1.3),
                    ),
                    child: Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.place_rounded, color: riskTier.color, size: 30),
                          const SizedBox(height: 4),
                          Text(riskTier.label, style: Theme.of(context).textTheme.labelLarge?.copyWith(color: riskTier.color, fontWeight: FontWeight.w800)),
                        ],
                      ),
                    ),
                  ),
                ),
                Positioned(
                  left: 16,
                  bottom: 14,
                  child: _miniLegend(context, 'Terrain-aware', 'District-level'),
                ),
                Positioned(
                  right: 16,
                  top: 14,
                  child: _miniLegend(context, 'Zone', zone.shortLabel),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _zoneChip(HimalayanZone zone) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: zone.tint.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: zone.tint.withValues(alpha: 0.35)),
      ),
      child: Text(zone.shortLabel, style: TextStyle(color: zone.tint, fontWeight: FontWeight.w800)),
    );
  }

  Widget _miniLegend(BuildContext context, String title, String value) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface.withValues(alpha: 0.75),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: Theme.of(context).textTheme.labelSmall),
          Text(value, style: Theme.of(context).textTheme.labelLarge),
        ],
      ),
    );
  }
}

class _TopographicPainter extends CustomPainter {
  const _TopographicPainter({
    required this.baseColor,
    required this.accent,
  });

  final Color baseColor;
  final Color accent;

  @override
  void paint(Canvas canvas, Size size) {
    final linePaint = Paint()
      ..color = baseColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.4;
    final accentPaint = Paint()
      ..color = accent
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.6;

    for (var i = 0; i < 7; i++) {
      final path = Path();
      final y = size.height * (0.2 + i * 0.12);
      path.moveTo(0, y);
      path.cubicTo(size.width * 0.18, y - 10, size.width * 0.34, y + 10, size.width * 0.5, y);
      path.cubicTo(size.width * 0.62, y - 8, size.width * 0.78, y + 8, size.width, y - 4);
      canvas.drawPath(path, linePaint);
    }

    final ridge = Path()
      ..moveTo(size.width * 0.08, size.height * 0.78)
      ..cubicTo(size.width * 0.26, size.height * 0.28, size.width * 0.52, size.height * 0.26, size.width * 0.92, size.height * 0.72)
      ..lineTo(size.width * 0.08, size.height * 0.78);
    canvas.drawPath(ridge, accentPaint);
  }

  @override
  bool shouldRepaint(covariant _TopographicPainter oldDelegate) {
    return oldDelegate.baseColor != baseColor || oldDelegate.accent != accent;
  }
}

class ActionChecklist extends StatelessWidget {
  const ActionChecklist({
    super.key,
    required this.items,
  });

  final List<String> items;

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('What this means for you', style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 10),
          ...items.map(
            (item) => Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(Icons.check_circle_rounded, color: Theme.of(context).colorScheme.primary, size: 18),
                  const SizedBox(width: 8),
                  Expanded(child: Text(item, style: Theme.of(context).textTheme.bodyMedium)),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class TrustMetricTile extends StatelessWidget {
  const TrustMetricTile({
    super.key,
    required this.metric,
  });

  final TrustMetric metric;

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(metric.label, style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 8),
          LinearProgressIndicator(
            value: metric.value.clamp(0, 1),
            minHeight: 10,
            borderRadius: BorderRadius.circular(999),
          ),
          const SizedBox(height: 8),
          Text(metric.subtitle, style: Theme.of(context).textTheme.bodySmall),
        ],
      ),
    );
  }
}

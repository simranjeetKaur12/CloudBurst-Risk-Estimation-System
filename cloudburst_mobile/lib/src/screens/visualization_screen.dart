import 'package:flutter/material.dart';

import '../state/app_state.dart';

class VisualizationScreen extends StatelessWidget {
  const VisualizationScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final state = AppStateScope.of(context);
    final result = state.lastResult;
    if (result == null) {
      return const SafeArea(
        child: Center(child: Text("Run a location prediction to view trends.")),
      );
    }

    return SafeArea(
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text("Visualization", style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 10),
          _trendCard("Rain Trend", result.rainTrend, Colors.blue),
          _trendCard("Moisture Trend", result.moistureTrend, Colors.teal),
          _trendCard("Pressure Drop Trend", result.pressureDropTrend, Colors.deepOrange),
          _trendCard("Wind Convergence Trend", result.windConvergenceTrend, Colors.purple),
        ],
      ),
    );
  }

  Widget _trendCard(String title, List<double> values, Color color) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            SizedBox(
              height: 80,
              child: CustomPaint(
                painter: _MiniLinePainter(values: values, color: color),
                child: Container(),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _MiniLinePainter extends CustomPainter {
  const _MiniLinePainter({required this.values, required this.color});

  final List<double> values;
  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    if (values.isEmpty) return;
    final minV = values.reduce((a, b) => a < b ? a : b);
    final maxV = values.reduce((a, b) => a > b ? a : b);
    final spread = (maxV - minV).abs() < 1e-9 ? 1.0 : (maxV - minV);

    final p = Paint()
      ..color = color
      ..strokeWidth = 2.2
      ..style = PaintingStyle.stroke;
    final path = Path();
    for (var i = 0; i < values.length; i++) {
      final x = (i / (values.length - 1 == 0 ? 1 : values.length - 1)) * size.width;
      final y = size.height - ((values[i] - minV) / spread) * size.height;
      if (i == 0) {
        path.moveTo(x, y);
      } else {
        path.lineTo(x, y);
      }
    }
    canvas.drawPath(path, p);
  }

  @override
  bool shouldRepaint(covariant _MiniLinePainter oldDelegate) {
    return oldDelegate.values != values || oldDelegate.color != color;
  }
}

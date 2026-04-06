import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/cloudburst_models.dart';
import '../state/cloudburst_controller.dart';
import '../ui/cloudburst_widgets.dart';

class HistoryScreen extends ConsumerStatefulWidget {
  const HistoryScreen({super.key});

  @override
  ConsumerState<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends ConsumerState<HistoryScreen> {
  Timer? _timer;
  double _progress = 0;

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(cloudburstControllerProvider);
    final controller = ref.read(cloudburstControllerProvider.notifier);
    final events = HistoricalEventReplay.samples();
    final index = state.historyReplayIndex.clamp(0, events.length - 1);
    final event = events[index];

    return ListView(
      padding: const EdgeInsets.fromLTRB(20, 18, 20, 28),
      children: [
        SectionHeader(
          title: 'Historical events explorer',
          subtitle: 'Replay past cloudburst conditions to understand how precursors build before an event.',
        ),
        const SizedBox(height: 14),
        SizedBox(
          height: 230,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: events.length,
            separatorBuilder: (_, __) => const SizedBox(width: 12),
            itemBuilder: (context, i) {
              final item = events[i];
              final selected = i == index;
              return SizedBox(
                width: 270,
                child: GlassCard(
                  onTap: () => controller.selectReplayIndex(i),
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 220),
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(28),
                      border: Border.all(color: selected ? item.zone.tint : Colors.transparent, width: 1.4),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Row(
                          children: [
                            MetricPill(label: 'Zone', value: item.zone.shortLabel, color: item.zone.tint),
                            const Spacer(),
                            Icon(Icons.history_rounded, color: item.zone.tint),
                          ],
                        ),
                        const SizedBox(height: 10),
                        Text(
                          item.title,
                          style: Theme.of(context).textTheme.titleMedium,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                        Text(
                          item.district,
                          style: Theme.of(context).textTheme.bodyMedium,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        Text(_date(item.eventDate), style: Theme.of(context).textTheme.labelMedium),
                      ],
                    ),
                  ),
                ),
              );
            },
          ),
        ),
        const SizedBox(height: 14),
        GlassCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SectionHeader(
                title: event.title,
                subtitle: '${event.district} • ${_date(event.eventDate)}',
                trailing: IconButton(
                  onPressed: _toggleReplay,
                  icon: Icon(_timer == null ? Icons.play_arrow_rounded : Icons.pause_rounded),
                ),
              ),
              const SizedBox(height: 8),
              Text(event.summary, style: Theme.of(context).textTheme.bodyLarge),
              const SizedBox(height: 14),
              TrendChart(
                title: 'Replay risk trajectory',
                subtitle: 'Watch the risk signal accelerate as atmospheric precursors strengthen.',
                values: _interpolate(event.riskTrajectory, _progress),
                color: event.zone.tint,
                height: 140,
              ),
              const SizedBox(height: 12),
              Slider(
                value: _progress,
                onChanged: (value) => setState(() => _progress = value),
              ),
              Text('Replay at ${(100 * _progress).toStringAsFixed(0)}%', style: Theme.of(context).textTheme.labelLarge),
            ],
          ),
        ),
        const SizedBox(height: 14),
        GridView.count(
          crossAxisCount: MediaQuery.sizeOf(context).width > 600 ? 2 : 1,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          mainAxisSpacing: 12,
          crossAxisSpacing: 12,
          childAspectRatio: 1.75,
          children: [
            TrendChart(
              title: 'Rainfall',
              subtitle: 'How the precipitation pulse evolved.',
              values: _interpolate(event.seriesFor('rain'), _progress),
              color: const Color(0xFFE94B4B),
              height: 110,
            ),
            TrendChart(
              title: 'Moisture / Pressure',
              subtitle: 'Humidity buildup and pressure fall are the key triggers.',
              values: _interpolate(event.seriesFor('moisture'), _progress),
              secondaryValues: _interpolate(event.seriesFor('pressure'), _progress),
              color: const Color(0xFF43C6DB),
              height: 110,
            ),
          ],
        ),
        const SizedBox(height: 14),
        GlassCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Atmospheric replay', style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 12),
              Text(_replayNarrative(event, _progress), style: Theme.of(context).textTheme.bodyMedium),
            ],
          ),
        ),
      ],
    );
  }

  void _toggleReplay() {
    if (_timer != null) {
      _timer?.cancel();
      setState(() => _timer = null);
      return;
    }
    _timer = Timer.periodic(const Duration(milliseconds: 220), (timer) {
      setState(() {
        _progress += 0.02;
        if (_progress >= 1) {
          _progress = 1;
          timer.cancel();
          _timer = null;
        }
      });
    });
  }

  List<double> _interpolate(List<double> values, double progress) {
    if (values.isEmpty) return values;
    final count = (values.length * (0.35 + progress * 0.65)).ceil().clamp(2, values.length);
    return values.sublist(0, count);
  }

  String _replayNarrative(HistoricalEventReplay event, double progress) {
    final point = ((progress * (event.riskTrajectory.length - 1)).round().clamp(0, event.riskTrajectory.length - 1)) as int;
    final risk = event.riskTrajectory[point];
    final rainSeries = event.seriesFor('rain');
    final moistureSeries = event.seriesFor('moisture');
    final pressureSeries = event.seriesFor('pressure');
    final rain = rainSeries.isEmpty ? 0 : rainSeries[point.clamp(0, rainSeries.length - 1) as int];
    final moisture = moistureSeries.isEmpty ? 0 : moistureSeries[point.clamp(0, moistureSeries.length - 1) as int];
    final pressure = pressureSeries.isEmpty ? 0 : pressureSeries[point.clamp(0, pressureSeries.length - 1) as int];
    return 'At this point in the replay, risk is ${risk.toStringAsFixed(0)}%, rainfall sits near ${rain.toStringAsFixed(0)}, moisture is ${moisture.toStringAsFixed(0)}, and pressure has dropped to ${pressure.toStringAsFixed(0)}. The model would already start escalating attention here.';
  }

  String _date(DateTime value) => '${value.day.toString().padLeft(2, '0')} ${_month(value.month)} ${value.year}';

  String _month(int month) {
    const months = [
      'Jan',
      'Feb',
      'Mar',
      'Apr',
      'May',
      'Jun',
      'Jul',
      'Aug',
      'Sep',
      'Oct',
      'Nov',
      'Dec',
    ];
    return months[month - 1];
  }
}

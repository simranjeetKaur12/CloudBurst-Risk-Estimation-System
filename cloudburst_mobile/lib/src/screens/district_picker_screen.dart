import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/cloudburst_models.dart';
import '../state/cloudburst_controller.dart';
import '../ui/cloudburst_widgets.dart';

class DistrictPickerScreen extends ConsumerStatefulWidget {
  const DistrictPickerScreen({super.key});

  @override
  ConsumerState<DistrictPickerScreen> createState() => _DistrictPickerScreenState();
}

class _DistrictPickerScreenState extends ConsumerState<DistrictPickerScreen> {
  final TextEditingController _searchController = TextEditingController();

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(cloudburstControllerProvider);
    final controller = ref.read(cloudburstControllerProvider.notifier);
    final districts = _filteredDistricts(state.districts, state.districtQuery);
    final grouped = _groupByState(districts);

    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFF07111B), Color(0xFF091723), Color(0xFF0E2131)],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        child: SafeArea(
          child: ListView(
            padding: const EdgeInsets.all(20),
            children: [
              Text('Select your district', style: Theme.of(context).textTheme.displaySmall?.copyWith(color: Colors.white)),
              const SizedBox(height: 8),
              Text(
                'Search by district name. The app will automatically map it to a Himalayan zone and store it for future sessions.',
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(color: Colors.white.withValues(alpha: 0.78)),
              ),
              const SizedBox(height: 18),
              GlassCard(
                child: TextField(
                  controller: _searchController,
                  onChanged: (value) {
                    controller.loadDistricts(query: value);
                  },
                  style: Theme.of(context).textTheme.bodyLarge,
                  decoration: const InputDecoration(
                    prefixIcon: Icon(Icons.search_rounded),
                    hintText: 'Search district',
                  ),
                ),
              ),
              const SizedBox(height: 16),
              if (state.loadingDistricts) const LinearProgressIndicator(minHeight: 2),
              const SizedBox(height: 14),
              if (state.selectedDistrict != null) _selectedDistrictCard(context, state.selectedDistrict!),
              if (state.selectedDistrict != null) const SizedBox(height: 14),
              ...grouped.entries.map((entry) => _stateGroup(context, controller, state, entry.key, entry.value)),
              const SizedBox(height: 18),
              FilledButton.icon(
                onPressed: state.selectedDistrict == null || state.loadingPrediction
                    ? null
                    : () async {
                        await controller.runPrediction(districtOverride: state.selectedDistrict!.district);
                      },
                icon: state.loadingPrediction
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(strokeWidth: 2.2),
                      )
                    : const Icon(Icons.bolt_rounded),
                label: Text(state.loadingPrediction ? 'Loading district intelligence' : 'Continue to dashboard'),
              ),
              const SizedBox(height: 10),
              Text(
                state.selectedDistrict == null
                    ? 'Select one district to unlock the zone-specific dashboard.'
                    : '${state.selectedDistrict!.district} is mapped to the ${state.selectedDistrict!.zone.shortLabel} Himalaya.',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Colors.white.withValues(alpha: 0.75)),
              ),
              if (state.error != null) ...[
                const SizedBox(height: 12),
                Text(state.error!, style: const TextStyle(color: Color(0xFFFF8A80))),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _selectedDistrictCard(BuildContext context, DistrictOption district) {
    return GlassCard(
      child: Row(
        children: [
          Container(
            width: 54,
            height: 54,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: district.zone.tint.withValues(alpha: 0.16),
              border: Border.all(color: district.zone.tint.withValues(alpha: 0.45)),
            ),
            child: Icon(Icons.place_rounded, color: district.zone.tint),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(district.district, style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 2),
                Text('${district.state} • ${district.zone.label}', style: Theme.of(context).textTheme.bodyMedium),
              ],
            ),
          ),
          MetricPill(label: 'Zone', value: district.zone.shortLabel, color: district.zone.tint),
        ],
      ),
    );
  }

  Widget _stateGroup(
    BuildContext context,
    CloudburstController controller,
    CloudburstState state,
    String groupName,
    List<DistrictOption> options,
  ) {
    return GlassCard(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(14),
      child: ExpansionTile(
        tilePadding: EdgeInsets.zero,
        childrenPadding: EdgeInsets.zero,
        collapsedIconColor: Colors.white70,
        iconColor: Colors.white,
        title: Text(groupName, style: Theme.of(context).textTheme.titleMedium?.copyWith(color: Colors.white)),
        subtitle: Text('${options.length} districts', style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Colors.white.withValues(alpha: 0.7))),
        children: options
            .map(
              (district) => ListTile(
                contentPadding: EdgeInsets.zero,
                leading: CircleAvatar(
                  backgroundColor: district.zone.tint.withValues(alpha: 0.18),
                  child: Icon(Icons.map_rounded, color: district.zone.tint, size: 18),
                ),
                title: Text(district.district),
                subtitle: Text(district.zone.label),
                trailing: AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  width: 88,
                  alignment: Alignment.center,
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  decoration: BoxDecoration(
                    color: state.selectedDistrict?.district == district.district
                        ? district.zone.tint.withValues(alpha: 0.18)
                        : Colors.transparent,
                    borderRadius: BorderRadius.circular(999),
                    border: Border.all(color: district.zone.tint.withValues(alpha: 0.35)),
                  ),
                  child: Text(district.zone.shortLabel, style: TextStyle(color: district.zone.tint, fontWeight: FontWeight.w700)),
                ),
                onTap: () => controller.selectDistrict(district),
              ),
            )
            .toList(growable: false),
      ),
    );
  }

  Map<String, List<DistrictOption>> _groupByState(List<DistrictOption> options) {
    final grouped = <String, List<DistrictOption>>{};
    for (final district in options) {
      grouped.putIfAbsent(district.state, () => <DistrictOption>[]).add(district);
    }
    return Map.fromEntries(grouped.entries.toList()..sort((a, b) => a.key.compareTo(b.key)));
  }

  List<DistrictOption> _filteredDistricts(List<DistrictOption> districts, String query) {
    final clean = query.trim().toLowerCase();
    if (clean.isEmpty) return districts;
    return districts.where((district) => district.district.toLowerCase().contains(clean) || district.state.toLowerCase().contains(clean)).toList(growable: false);
  }
}

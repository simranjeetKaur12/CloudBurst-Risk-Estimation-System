import 'package:flutter/material.dart';

import '../models/prediction_result.dart';
import '../state/app_state.dart';

class DistrictSelectionScreen extends StatefulWidget {
  const DistrictSelectionScreen({
    super.key,
    this.standalone = false,
  });

  final bool standalone;

  @override
  State<DistrictSelectionScreen> createState() => _DistrictSelectionScreenState();
}

class _DistrictSelectionScreenState extends State<DistrictSelectionScreen> {
  final searchController = TextEditingController();
  DistrictOption? selected;
  String query = "";

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      AppStateScope.of(context).fetchDistricts();
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = AppStateScope.of(context);
    final filtered = _filteredDistricts(state.districts, query);
    final grouped = _groupByState(filtered);

    return SafeArea(
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text("Select District", style: Theme.of(context).textTheme.headlineSmall),
          const SizedBox(height: 6),
          const Text("Search, type, or pick from Himalayan district list."),
          const SizedBox(height: 12),
          TextField(
            controller: searchController,
            decoration: const InputDecoration(
              labelText: "District name",
              prefixIcon: Icon(Icons.search_rounded),
            ),
            onChanged: (value) {
              setState(() => query = value.trim());
              state.fetchDistricts(query: value);
            },
          ),
          const SizedBox(height: 10),
          if (state.recentDistricts.isNotEmpty) _chipRow(context, "Recent", state.recentDistricts),
          if (state.favoriteDistricts.isNotEmpty) _chipRow(context, "Favorites", state.favoriteDistricts.toList()),
          if (state.districtLoading) const LinearProgressIndicator(),
          const SizedBox(height: 8),
          ...grouped.entries.map((entry) => _statePanel(context, state, entry.key, entry.value)),
          const SizedBox(height: 12),
          FilledButton.icon(
            onPressed: state.loading || selected == null
                ? null
                : () async {
                    await state.runPrediction(district: selected!.district);
                    if (!context.mounted) return;
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text("${selected!.chunk.toUpperCase()} Himalaya zone detected."),
                      ),
                    );
                    if (widget.standalone) {
                      Navigator.of(context).pop();
                    }
                  },
            icon: const Icon(Icons.bolt_rounded),
            label: const Text("Run 10-Day Risk Assessment"),
          ),
          const SizedBox(height: 10),
          if (state.loading) _pipelineCard(context, state),
          if (state.error != null)
            Padding(
              padding: const EdgeInsets.only(top: 10),
              child: Text(state.error!, style: const TextStyle(color: Color(0xFFD7263D))),
            ),
        ],
      ),
    );
  }

  Widget _pipelineCard(BuildContext context, AppState state) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text("Data Pipeline", style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            ...state.pipelineStages.map(
              (step) => Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Row(
                  children: [
                    Icon(
                      step.completed
                          ? Icons.check_circle_rounded
                          : (step.active ? Icons.more_horiz_rounded : Icons.radio_button_unchecked_rounded),
                      size: 18,
                      color: step.completed
                          ? Colors.teal
                          : (step.active ? Theme.of(context).colorScheme.secondary : null),
                    ),
                    const SizedBox(width: 8),
                    Expanded(child: Text(step.label)),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _statePanel(
    BuildContext context,
    AppState state,
    String stateName,
    List<DistrictOption> options,
  ) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ExpansionTile(
        title: Text(stateName),
        subtitle: Text("${options.length} districts"),
        children: options
            .map(
              (d) => ListTile(
                title: Text(d.district),
                subtitle: Text("${d.chunk.toUpperCase()} Himalaya"),
                trailing: IconButton(
                  icon: Icon(
                    state.favoriteDistricts.contains(d.district) ? Icons.star_rounded : Icons.star_border_rounded,
                  ),
                  onPressed: () => state.toggleFavorite(d.district),
                ),
                selected: selected?.district == d.district,
                onTap: () => setState(() => selected = d),
              ),
            )
            .toList(growable: false),
      ),
    );
  }

  Widget _chipRow(BuildContext context, String title, List<String> values) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: Theme.of(context).textTheme.titleSmall),
          const SizedBox(height: 6),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: values
                .map(
                  (d) => ActionChip(
                    label: Text(d),
                    onPressed: () {
                      searchController.text = d;
                      setState(() => query = d);
                    },
                  ),
                )
                .toList(growable: false),
          ),
        ],
      ),
    );
  }

  List<DistrictOption> _filteredDistricts(List<DistrictOption> all, String q) {
    final clean = q.trim().toLowerCase();
    if (clean.isEmpty) return all;
    return all.where((d) {
      final n = d.district.toLowerCase();
      return n.contains(clean) || _fuzzyContains(n, clean);
    }).toList(growable: false);
  }

  bool _fuzzyContains(String text, String pattern) {
    var idx = 0;
    for (final rune in text.runes) {
      if (idx < pattern.length && String.fromCharCode(rune) == pattern[idx]) {
        idx += 1;
      }
    }
    return idx == pattern.length;
  }

  Map<String, List<DistrictOption>> _groupByState(List<DistrictOption> items) {
    final map = <String, List<DistrictOption>>{};
    for (final d in items) {
      map.putIfAbsent(d.state, () => <DistrictOption>[]).add(d);
    }
    final entries = map.entries.toList()
      ..sort((a, b) => a.key.compareTo(b.key));
    return Map.fromEntries(entries);
  }
}

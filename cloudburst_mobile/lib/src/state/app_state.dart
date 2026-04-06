import 'package:flutter/material.dart';

import '../models/prediction_result.dart';
import '../services/api_service.dart';

class PipelineStage {
  const PipelineStage({
    required this.label,
    required this.completed,
    required this.active,
  });

  final String label;
  final bool completed;
  final bool active;
}

class AppState extends ChangeNotifier {
  String baseUrl = const String.fromEnvironment(
    "CLOUDBURST_API_BASE_URL",
    defaultValue: "https://hcis-api.onrender.com",
  );
  bool? backendHealthy;
  bool loading = false;
  bool districtLoading = false;
  String? error;
  PredictionResult? lastResult;
  List<DistrictOption> districts = const [];
  bool darkMode = false;
  bool highContrastMode = false;
  bool compareWithHistory = false;
  List<String> recentDistricts = const [];
  Set<String> favoriteDistricts = <String>{};
  List<PipelineStage> pipelineStages = const [];

  ApiService get _api => ApiService(baseUrl: baseUrl);

  static const _stageLabels = <String>[
    "Locating District Geometry",
    "Retrieving Atmospheric Data (Last 10 Days)",
    "Feature Engineering",
    "Loading Regional AI Model",
    "Computing Risk & Lead Time",
    "Generating Explanation",
  ];

  Future<void> updateBaseUrl(String newBaseUrl) async {
    baseUrl = newBaseUrl.trim();
    notifyListeners();
    await checkHealth();
  }

  Future<void> checkHealth() async {
    loading = true;
    error = null;
    notifyListeners();
    try {
      backendHealthy = await _api.health();
    } catch (e) {
      backendHealthy = false;
      error = e.toString();
    } finally {
      loading = false;
      notifyListeners();
    }
  }

  Future<void> runPrediction({required String district}) async {
    loading = true;
    error = null;
    _resetPipeline();
    notifyListeners();
    try {
      _setStageActive(0);
      await Future<void>.delayed(const Duration(milliseconds: 150));
      _setStageDone(0);
      _setStageActive(1);
      lastResult = await _api.predictByDistrict(district: district);
      _setStageDone(1);
      _setStageActive(2);
      await Future<void>.delayed(const Duration(milliseconds: 120));
      _setStageDone(2);
      _setStageActive(3);
      await Future<void>.delayed(const Duration(milliseconds: 120));
      _setStageDone(3);
      _setStageActive(4);
      await Future<void>.delayed(const Duration(milliseconds: 140));
      _setStageDone(4);
      _setStageActive(5);
      await Future<void>.delayed(const Duration(milliseconds: 120));
      _setStageDone(5);
      _addRecentDistrict(district);
    } catch (e) {
      error = e.toString();
      pipelineStages = const [];
    } finally {
      loading = false;
      notifyListeners();
    }
  }

  String get laymanExplanation {
    final result = lastResult;
    if (result == null) {
      return "Select a district to get chunk-specific cloudburst risk and plain-language explanation.";
    }
    return result.laymanExplanation;
  }

  Future<void> fetchDistricts({String? query}) async {
    districtLoading = true;
    notifyListeners();
    try {
      districts = await _api.listDistricts(query: query);
    } catch (e) {
      error = e.toString();
    } finally {
      districtLoading = false;
      notifyListeners();
    }
  }

  void toggleDarkMode(bool enabled) {
    darkMode = enabled;
    notifyListeners();
  }

  void toggleHighContrast(bool enabled) {
    highContrastMode = enabled;
    notifyListeners();
  }

  void toggleHistoryCompare(bool enabled) {
    compareWithHistory = enabled;
    notifyListeners();
  }

  void toggleFavorite(String district) {
    if (favoriteDistricts.contains(district)) {
      favoriteDistricts.remove(district);
    } else {
      favoriteDistricts.add(district);
    }
    notifyListeners();
  }

  void _addRecentDistrict(String district) {
    final updated = [district, ...recentDistricts.where((d) => d != district)];
    recentDistricts = updated.take(5).toList(growable: false);
  }

  void _resetPipeline() {
    pipelineStages = _stageLabels
        .map(
          (label) =>
              PipelineStage(label: label, completed: false, active: false),
        )
        .toList(growable: false);
  }

  void _setStageActive(int idx) {
    pipelineStages = pipelineStages
        .asMap()
        .entries
        .map(
          (entry) => PipelineStage(
            label: entry.value.label,
            completed: entry.value.completed,
            active: entry.key == idx,
          ),
        )
        .toList(growable: false);
    notifyListeners();
  }

  void _setStageDone(int idx) {
    pipelineStages = pipelineStages
        .asMap()
        .entries
        .map(
          (entry) => PipelineStage(
            label: entry.value.label,
            completed: entry.key == idx ? true : entry.value.completed,
            active: false,
          ),
        )
        .toList(growable: false);
    notifyListeners();
  }
}

class AppStateScope extends InheritedNotifier<AppState> {
  const AppStateScope({
    super.key,
    required AppState appState,
    required super.child,
  }) : super(notifier: appState);

  static AppState of(BuildContext context) {
    final scope = context.dependOnInheritedWidgetOfExactType<AppStateScope>();
    if (scope == null || scope.notifier == null) {
      throw StateError("AppStateScope not found in widget tree.");
    }
    return scope.notifier!;
  }
}

import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/cloudburst_models.dart';
import '../data/cloudburst_providers.dart';
import '../data/cloudburst_repository.dart';
import '../services/notification_service.dart';

class CloudburstState {
  const CloudburstState({
    required this.userId,
    required this.bootstrapping,
    required this.onboardingComplete,
    required this.notificationsEnabled,
    required this.darkMode,
    required this.highContrast,
    required this.loadingDistricts,
    required this.loadingPrediction,
    required this.error,
    required this.districtQuery,
    required this.districts,
    required this.selectedDistrict,
    required this.prediction,
    required this.recentPredictions,
    required this.historyReplayIndex,
  });

  final String userId;
  final bool bootstrapping;
  final bool onboardingComplete;
  final bool notificationsEnabled;
  final bool darkMode;
  final bool highContrast;
  final bool loadingDistricts;
  final bool loadingPrediction;
  final String? error;
  final String districtQuery;
  final List<DistrictOption> districts;
  final DistrictOption? selectedDistrict;
  final PredictionSnapshot? prediction;
  final List<PredictionSnapshot> recentPredictions;
  final int historyReplayIndex;

  factory CloudburstState.initial() {
    return const CloudburstState(
      userId: '',
      bootstrapping: true,
      onboardingComplete: false,
      notificationsEnabled: true,
      darkMode: true,
      highContrast: false,
      loadingDistricts: false,
      loadingPrediction: false,
      error: null,
      districtQuery: '',
      districts: <DistrictOption>[],
      selectedDistrict: null,
      prediction: null,
      recentPredictions: <PredictionSnapshot>[],
      historyReplayIndex: 0,
    );
  }

  CloudburstState copyWith({
    String? userId,
    bool? bootstrapping,
    bool? onboardingComplete,
    bool? notificationsEnabled,
    bool? darkMode,
    bool? highContrast,
    bool? loadingDistricts,
    bool? loadingPrediction,
    String? error,
    bool clearError = false,
    String? districtQuery,
    List<DistrictOption>? districts,
    DistrictOption? selectedDistrict,
    bool clearSelectedDistrict = false,
    PredictionSnapshot? prediction,
    bool clearPrediction = false,
    List<PredictionSnapshot>? recentPredictions,
    int? historyReplayIndex,
  }) {
    return CloudburstState(
      userId: userId ?? this.userId,
      bootstrapping: bootstrapping ?? this.bootstrapping,
      onboardingComplete: onboardingComplete ?? this.onboardingComplete,
      notificationsEnabled: notificationsEnabled ?? this.notificationsEnabled,
      darkMode: darkMode ?? this.darkMode,
      highContrast: highContrast ?? this.highContrast,
      loadingDistricts: loadingDistricts ?? this.loadingDistricts,
      loadingPrediction: loadingPrediction ?? this.loadingPrediction,
      error: clearError ? null : (error ?? this.error),
      districtQuery: districtQuery ?? this.districtQuery,
      districts: districts ?? this.districts,
      selectedDistrict: clearSelectedDistrict ? null : (selectedDistrict ?? this.selectedDistrict),
      prediction: clearPrediction ? null : (prediction ?? this.prediction),
      recentPredictions: recentPredictions ?? this.recentPredictions,
      historyReplayIndex: historyReplayIndex ?? this.historyReplayIndex,
    );
  }
}

class CloudburstController extends Notifier<CloudburstState> {
  late final CloudburstRepository _repository;

  @override
  CloudburstState build() {
    _repository = ref.read(cloudburstRepositoryProvider);
    Future.microtask(_bootstrap);
    return CloudburstState.initial();
  }

  Future<void> _bootstrap() async {
    state = state.copyWith(bootstrapping: true, clearError: true);
    try {
      final bootstrap = await _repository.loadBootstrapData();
      await loadDistricts(query: bootstrap.selectedDistrict?.district ?? '');

      final serverPreferred = await _repository.fetchUserPreferredDistrict(bootstrap.userId);
      final preferredDistrict = serverPreferred ?? bootstrap.selectedDistrict;

      state = state.copyWith(
        userId: bootstrap.userId,
        onboardingComplete: bootstrap.onboardingComplete,
        notificationsEnabled: bootstrap.notificationsEnabled,
        darkMode: bootstrap.darkMode,
        highContrast: bootstrap.highContrast,
        selectedDistrict: preferredDistrict,
        prediction: bootstrap.cachedPrediction,
        recentPredictions: bootstrap.cachedPrediction == null
            ? state.recentPredictions
            : <PredictionSnapshot>[bootstrap.cachedPrediction!],
      );

      if (preferredDistrict != null && bootstrap.cachedPrediction == null) {
        await runPrediction(districtOverride: preferredDistrict.district, userIdOverride: bootstrap.userId);
      }

      state = state.copyWith(bootstrapping: false);
    } catch (error) {
      state = state.copyWith(bootstrapping: false, error: error.toString());
      await loadDistricts();
    }
  }

  Future<void> completeOnboarding() async {
    await _repository.saveOnboardingComplete(true);
    state = state.copyWith(onboardingComplete: true);
  }

  Future<void> loadDistricts({String query = ''}) async {
    state = state.copyWith(loadingDistricts: true, districtQuery: query, clearError: true);
    try {
      final districts = await _repository.listDistricts(query: query);
      state = state.copyWith(loadingDistricts: false, districts: districts, districtQuery: query);
    } catch (error) {
      state = state.copyWith(loadingDistricts: false, error: error.toString());
    }
  }

  Future<void> selectDistrict(DistrictOption district) async {
    await _repository.saveSelectedDistrict(district);
    if (state.userId.isNotEmpty) {
      unawaited(_repository.saveUserPreferredDistrict(userId: state.userId, district: district.district));
    }
    state = state.copyWith(
      selectedDistrict: district,
      districtQuery: district.district,
      clearError: true,
    );
  }

  Future<void> runPrediction({String? districtOverride, String? userIdOverride}) async {
    final district = districtOverride ?? state.selectedDistrict?.district;
    final userId = userIdOverride ?? state.userId;
    if (district == null || district.trim().isEmpty) {
      state = state.copyWith(error: 'Select a district before running a prediction.');
      return;
    }

    state = state.copyWith(loadingPrediction: true, clearError: true);
    try {
      final prediction = await _repository.fetchPredictionForUser(
        district: district.trim(),
        userId: userId.isEmpty ? null : userId,
      );
      final updatedHistory = [prediction, ...state.recentPredictions.where((entry) => entry.district != prediction.district)];
      state = state.copyWith(
        loadingPrediction: false,
        prediction: prediction,
        recentPredictions: updatedHistory.take(5).toList(growable: false),
      );
      await _repository.savePrediction(prediction);

      if (state.notificationsEnabled && prediction.riskTier == RiskTier.high) {
        await NotificationService.instance.showHighRiskAlert(
          district: prediction.district,
          probability: prediction.riskScore / 100,
        );
      }
    } catch (error) {
      final fallback = state.prediction;
      if (fallback != null) {
        state = state.copyWith(
          loadingPrediction: false,
          error: '${error.toString()} Using cached prediction.',
        );
        return;
      }
      state = state.copyWith(loadingPrediction: false, error: error.toString());
    }
  }

  Future<void> toggleDarkMode(bool value) async {
    await _repository.saveDarkMode(value);
    state = state.copyWith(darkMode: value);
  }

  Future<void> toggleHighContrast(bool value) async {
    await _repository.saveHighContrast(value);
    state = state.copyWith(highContrast: value);
  }

  Future<void> toggleNotifications(bool value) async {
    await _repository.saveNotificationPreference(value);
    state = state.copyWith(notificationsEnabled: value);
  }

  Future<void> clearDistrictSelection() async {
    await _repository.clearSelectedDistrict();
    await _repository.clearPrediction();
    state = state.copyWith(
      clearSelectedDistrict: true,
      clearPrediction: true,
    );
  }

  void selectReplayIndex(int index) {
    state = state.copyWith(historyReplayIndex: index);
  }

  void clearError() {
    state = state.copyWith(clearError: true);
  }
}

final cloudburstControllerProvider = NotifierProvider<CloudburstController, CloudburstState>(CloudburstController.new);

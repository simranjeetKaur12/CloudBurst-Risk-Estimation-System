import 'dart:async';
import 'dart:convert';
import 'dart:math';

import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import 'cloudburst_models.dart';

class AppBootstrapData {
  const AppBootstrapData({
    required this.userId,
    required this.onboardingComplete,
    required this.notificationsEnabled,
    required this.darkMode,
    required this.highContrast,
    required this.selectedDistrict,
    required this.cachedPrediction,
  });

  final String userId;
  final bool onboardingComplete;
  final bool notificationsEnabled;
  final bool darkMode;
  final bool highContrast;
  final DistrictOption? selectedDistrict;
  final PredictionSnapshot? cachedPrediction;
}

class CloudburstRepository {
  CloudburstRepository({
    required this.baseUrl,
    http.Client? client,
  }) : _client = client ?? http.Client();

  final String baseUrl;
  final http.Client _client;
  static const int _maxRetries = 1;

  static const _selectedDistrictKey = 'cloudburst.selected_district';
  static const _cachedPredictionKey = 'cloudburst.cached_prediction';
  static const _onboardingKey = 'cloudburst.onboarding_complete';
  static const _notificationsKey = 'cloudburst.notifications_enabled';
  static const _darkModeKey = 'cloudburst.dark_mode';
  static const _highContrastKey = 'cloudburst.high_contrast';
  static const _userIdKey = 'cloudburst.user_id';

  Future<bool> health() async {
    try {
      final response = await _client.get(Uri.parse('$baseUrl/health')).timeout(const Duration(seconds: 10));
      return response.statusCode == 200;
    } on TimeoutException {
      throw Exception(_timeoutMessage('health check', 10));
    }
  }

  Future<List<DistrictOption>> listDistricts({String query = ''}) async {
    final cleanQuery = query.trim();
    final uri = cleanQuery.isEmpty
        ? Uri.parse('$baseUrl/districts')
        : Uri.parse('$baseUrl/districts?q=${Uri.encodeQueryComponent(cleanQuery)}');
    try {
      final response = await _withRetry(() => _client.get(uri).timeout(const Duration(seconds: 15)));
      if (response.statusCode != 200) {
        throw Exception('District list failed (${response.statusCode}).');
      }
      final json = jsonDecode(response.body) as Map<String, dynamic>;
      final districts = (json['districts'] as List<dynamic>? ?? const <dynamic>[]);
      return districts.map((item) => DistrictOption.fromJson(item as Map<String, dynamic>)).toList(growable: false);
    } on TimeoutException {
      throw Exception(_timeoutMessage('district fetch', 15));
    }
  }

  Future<PredictionSnapshot> fetchPrediction(String district) async {
    return fetchPredictionForUser(district: district);
  }

  Future<PredictionSnapshot> fetchPredictionForUser({
    required String district,
    String? userId,
  }) async {
    try {
      final predictUri = Uri.parse(
        '$baseUrl/predict?district=${Uri.encodeQueryComponent(district)}${userId == null ? '' : '&user_id=${Uri.encodeQueryComponent(userId)}'}',
      );
      final response = await _withRetry(() => _client.get(predictUri).timeout(const Duration(seconds: 20)));
      if (response.statusCode == 200) {
        return PredictionSnapshot.fromBackend(jsonDecode(response.body) as Map<String, dynamic>);
      }

      final legacyResponse = await _withRetry(
        () => _client
            .post(
              Uri.parse('$baseUrl/predict-district'),
              headers: const {'Content-Type': 'application/json'},
              body: jsonEncode({'district': district}),
            )
            .timeout(const Duration(seconds: 20)),
      );
      if (legacyResponse.statusCode != 200) {
        throw Exception('Prediction failed (${legacyResponse.statusCode}).');
      }
      return PredictionSnapshot.fromBackend(jsonDecode(legacyResponse.body) as Map<String, dynamic>);
    } on TimeoutException {
      throw Exception(_timeoutMessage('prediction request', 20));
    }
  }

  Future<AppBootstrapData> loadBootstrapData() async {
    final prefs = await SharedPreferences.getInstance();
    final userId = await _ensureUserId(prefs);
    final selectedJson = prefs.getString(_selectedDistrictKey);
    final predictionJson = prefs.getString(_cachedPredictionKey);
    return AppBootstrapData(
      userId: userId,
      onboardingComplete: prefs.getBool(_onboardingKey) ?? false,
      notificationsEnabled: prefs.getBool(_notificationsKey) ?? true,
      darkMode: prefs.getBool(_darkModeKey) ?? true,
      highContrast: prefs.getBool(_highContrastKey) ?? false,
      selectedDistrict: selectedJson == null ? null : DistrictOption.fromJson(jsonDecode(selectedJson) as Map<String, dynamic>),
      cachedPrediction: predictionJson == null ? null : PredictionSnapshot.fromCache(jsonDecode(predictionJson) as Map<String, dynamic>),
    );
  }

  Future<DistrictOption?> fetchUserPreferredDistrict(String userId) async {
    try {
      final uri = Uri.parse('$baseUrl/user-profile?user_id=${Uri.encodeQueryComponent(userId)}');
      final response = await _withRetry(() => _client.get(uri).timeout(const Duration(seconds: 10)));
      if (response.statusCode != 200) {
        return null;
      }
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      final preferred = data['preferred_district'] as Map<String, dynamic>?;
      if (preferred == null) {
        return null;
      }
      return DistrictOption(
        district: (preferred['district'] ?? '').toString(),
        state: (preferred['state'] ?? 'Unknown').toString(),
        chunk: (preferred['chunk'] ?? '').toString(),
      );
    } catch (_) {
      return null;
    }
  }

  Future<void> saveUserPreferredDistrict({
    required String userId,
    required String district,
  }) async {
    final uri = Uri.parse('$baseUrl/user-profile/select-district');
    await _withRetry(
      () => _client
          .post(
            uri,
            headers: const {'Content-Type': 'application/json'},
            body: jsonEncode({'user_id': userId, 'district': district}),
          )
          .timeout(const Duration(seconds: 10)),
    );
  }

  Future<void> saveOnboardingComplete(bool value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_onboardingKey, value);
  }

  Future<void> saveNotificationPreference(bool value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_notificationsKey, value);
  }

  Future<void> saveDarkMode(bool value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_darkModeKey, value);
  }

  Future<void> saveHighContrast(bool value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_highContrastKey, value);
  }

  Future<void> saveSelectedDistrict(DistrictOption value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_selectedDistrictKey, jsonEncode(value.toJson()));
  }

  Future<void> clearSelectedDistrict() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_selectedDistrictKey);
  }

  Future<void> savePrediction(PredictionSnapshot value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_cachedPredictionKey, jsonEncode(value.toCacheJson()));
  }

  Future<void> clearPrediction() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_cachedPredictionKey);
  }

  Future<http.Response> _withRetry(Future<http.Response> Function() task) async {
    Object? lastError;
    for (var attempt = 0; attempt <= _maxRetries; attempt++) {
      try {
        return await task();
      } catch (error) {
        lastError = error;
        if (attempt == _maxRetries) {
          rethrow;
        }
      }
    }
    throw Exception(lastError ?? 'Request failed');
  }

  String _timeoutMessage(String operation, int seconds) {
    return 'Timeout while performing $operation after ${seconds}s. Confirm backend is running at $baseUrl and reachable from this device. You can override base URL with --dart-define=CLOUDBURST_API_BASE_URL=http://<host-ip>:8000';
  }

  Future<String> _ensureUserId(SharedPreferences prefs) async {
    final existing = prefs.getString(_userIdKey);
    if (existing != null && existing.trim().isNotEmpty) {
      return existing;
    }
    final random = Random();
    final generated = 'cb-${DateTime.now().microsecondsSinceEpoch.toRadixString(16)}-${random.nextInt(1 << 32).toRadixString(16)}';
    await prefs.setString(_userIdKey, generated);
    return generated;
  }
}

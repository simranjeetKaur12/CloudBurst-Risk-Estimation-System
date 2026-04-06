import 'dart:io' show Platform;

import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'cloudburst_repository.dart';

final cloudburstRepositoryProvider = Provider<CloudburstRepository>((ref) {
  const configuredBaseUrl = String.fromEnvironment(
    'CLOUDBURST_API_BASE_URL',
    defaultValue: '',
  );
  final baseUrl = configuredBaseUrl.isNotEmpty ? configuredBaseUrl : _defaultApiBaseUrl();
  return CloudburstRepository(baseUrl: baseUrl);
});

String _defaultApiBaseUrl() {
  if (kIsWeb) {
    return 'https://hcis-api.onrender.com';
  }
  if (Platform.isAndroid) {
    return 'https://hcis-api.onrender.com';
  }
  return 'https://hcis-api.onrender.com';
}

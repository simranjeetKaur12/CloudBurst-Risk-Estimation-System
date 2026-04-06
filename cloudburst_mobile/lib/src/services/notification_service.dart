import 'package:flutter_local_notifications/flutter_local_notifications.dart';

class NotificationService {
  NotificationService._();

  static final NotificationService instance = NotificationService._();

  final FlutterLocalNotificationsPlugin _plugin = FlutterLocalNotificationsPlugin();
  bool _initialized = false;

  Future<void> initialize() async {
    if (_initialized) return;

    const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
    const settings = InitializationSettings(android: androidSettings);

    await _plugin.initialize(settings);

    final androidPlugin = _plugin.resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>();
    await androidPlugin?.requestNotificationsPermission();

    _initialized = true;
  }

  Future<void> showHighRiskAlert({
    required String district,
    required double probability,
  }) async {
    if (!_initialized) {
      await initialize();
    }

    const androidDetails = AndroidNotificationDetails(
      'cloudburst_high_risk',
      'High Risk Alerts',
      channelDescription: 'Urgent cloudburst warning notifications for high risk conditions',
      importance: Importance.max,
      priority: Priority.high,
      ticker: 'Cloudburst warning',
    );

    const notificationDetails = NotificationDetails(android: androidDetails);

    final percentage = (probability * 100).clamp(0, 100).toStringAsFixed(0);
    await _plugin.show(
      1001,
      'High Cloudburst Risk in $district',
      'Risk probability is $percentage%. Stay alert and follow local advisories immediately.',
      notificationDetails,
    );
  }
}

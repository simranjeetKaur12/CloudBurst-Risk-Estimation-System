import 'dart:math' as math;

import 'package:flutter/material.dart';

enum HimalayanZone { western, central, eastern }

extension HimalayanZoneX on HimalayanZone {
  String get label => switch (this) {
        HimalayanZone.western => 'Western Himalaya',
        HimalayanZone.central => 'Central Himalaya',
        HimalayanZone.eastern => 'Eastern Himalaya',
      };

  String get shortLabel => switch (this) {
        HimalayanZone.western => 'Western',
        HimalayanZone.central => 'Central',
        HimalayanZone.eastern => 'Eastern',
      };

  Color get tint => switch (this) {
        HimalayanZone.western => const Color(0xFF43C6DB),
        HimalayanZone.central => const Color(0xFFF5A623),
        HimalayanZone.eastern => const Color(0xFFFF6B6B),
      };

  static HimalayanZone fromChunk(String value) {
    final normalized = value.trim().toLowerCase();
    if (normalized.contains('western')) return HimalayanZone.western;
    if (normalized.contains('central')) return HimalayanZone.central;
    return HimalayanZone.eastern;
  }
}

enum RiskTier { low, moderate, high }

extension RiskTierX on RiskTier {
  String get label => switch (this) {
        RiskTier.low => 'LOW',
        RiskTier.moderate => 'MODERATE',
        RiskTier.high => 'HIGH',
      };

  Color get color => switch (this) {
        RiskTier.low => const Color(0xFF38B48B),
        RiskTier.moderate => const Color(0xFFF5A623),
        RiskTier.high => const Color(0xFFE94B4B),
      };

  String get explanation => switch (this) {
        RiskTier.low => 'Atmospheric conditions are currently stable.',
        RiskTier.moderate => 'Signals are strengthening and merit close monitoring.',
        RiskTier.high => 'Conditions are aligned with cloudburst precursors.',
      };
}

class DistrictOption {
  const DistrictOption({
    required this.district,
    required this.state,
    required this.chunk,
  });

  final String district;
  final String state;
  final String chunk;

  HimalayanZone get zone => HimalayanZoneX.fromChunk(chunk);

  factory DistrictOption.fromJson(Map<String, dynamic> json) {
    return DistrictOption(
      district: (json['district'] ?? '').toString(),
      state: (json['state'] ?? '').toString(),
      chunk: (json['chunk'] ?? '').toString(),
    );
  }

  Map<String, dynamic> toJson() => {
        'district': district,
        'state': state,
        'chunk': chunk,
      };
}

class RiskTimelinePoint {
  const RiskTimelinePoint({
    required this.label,
    required this.riskScore,
    required this.moisture,
    required this.rainfall,
    required this.pressureDrop,
    required this.wind,
  });

  final String label;
  final double riskScore;
  final double moisture;
  final double rainfall;
  final double pressureDrop;
  final double wind;
}

class LeadTimeSummary {
  const LeadTimeSummary({
    required this.estimatedHours,
    required this.text,
    required this.yellowHours,
    required this.orangeHours,
    required this.redHours,
  });

  final double? estimatedHours;
  final String text;
  final double? yellowHours;
  final double? orangeHours;
  final double? redHours;

  factory LeadTimeSummary.fromJson(Map<String, dynamic> json) {
    return LeadTimeSummary(
      estimatedHours: (json['estimated_hours'] as num?)?.toDouble(),
      text: (json['text'] ?? '').toString(),
      yellowHours: (json['yellow_hr'] as num?)?.toDouble(),
      orangeHours: (json['orange_hr'] as num?)?.toDouble(),
      redHours: (json['red_hr'] as num?)?.toDouble(),
    );
  }
}

class TrustMetric {
  const TrustMetric({
    required this.label,
    required this.value,
    required this.subtitle,
  });

  final String label;
  final double value;
  final String subtitle;
}

class HistoricalEventReplay {
  const HistoricalEventReplay({
    required this.title,
    required this.district,
    required this.zone,
    required this.eventDate,
    required this.summary,
    required this.seriesByFeature,
    required this.riskTrajectory,
  });

  final String title;
  final String district;
  final HimalayanZone zone;
  final DateTime eventDate;
  final String summary;
  final Map<String, List<double>> seriesByFeature;
  final List<double> riskTrajectory;

  List<double> seriesFor(String key) => seriesByFeature[key] ?? const <double>[];

  static List<HistoricalEventReplay> samples() {
    return [
      HistoricalEventReplay(
        title: 'Pre-monsoon surge in Uttarkashi',
        district: 'Uttarkashi',
        zone: HimalayanZone.western,
        eventDate: DateTime(2023, 7, 12),
        summary: 'Rapid moisture accumulation and pressure fall preceded the burst by almost a day.',
        seriesByFeature: const {
          'rain': [2, 3, 5, 8, 12, 18, 24, 31],
          'moisture': [42, 44, 47, 50, 58, 67, 74, 81],
          'pressure': [1006, 1005, 1004, 1003, 1001, 999, 997, 994],
          'wind': [4, 5, 6, 7, 8, 9, 11, 13],
          'cape': [820, 870, 900, 940, 980, 1010, 1030, 1080],
        },
        riskTrajectory: const [18, 22, 27, 33, 48, 61, 76, 89],
      ),
      HistoricalEventReplay(
        title: 'Moisture break over Chamoli',
        district: 'Chamoli',
        zone: HimalayanZone.central,
        eventDate: DateTime(2022, 8, 4),
        summary: 'A pressure trough and strong convective energy build-up formed a high-risk window.',
        seriesByFeature: const {
          'rain': [1, 2, 3, 6, 10, 14, 20, 26],
          'moisture': [39, 41, 45, 51, 56, 60, 68, 75],
          'pressure': [1007, 1006, 1006, 1004, 1002, 1000, 998, 995],
          'wind': [5, 5, 6, 7, 9, 10, 12, 14],
          'cape': [780, 790, 830, 870, 920, 960, 1000, 1060],
        },
        riskTrajectory: const [14, 18, 24, 31, 43, 58, 71, 83],
      ),
      HistoricalEventReplay(
        title: 'Eastern slope trigger in Sikkim',
        district: 'Gangtok',
        zone: HimalayanZone.eastern,
        eventDate: DateTime(2021, 10, 9),
        summary: 'Rainfall pulses intensified after moisture transport from the Bay of Bengal.',
        seriesByFeature: const {
          'rain': [1, 2, 4, 5, 9, 13, 19, 29],
          'moisture': [40, 43, 46, 49, 57, 63, 72, 80],
          'pressure': [1008, 1007, 1005, 1004, 1002, 1000, 998, 996],
          'wind': [4, 5, 5, 6, 8, 10, 12, 13],
          'cape': [760, 800, 840, 880, 930, 970, 1015, 1070],
        },
        riskTrajectory: const [12, 17, 21, 29, 45, 59, 75, 86],
      ),
    ];
  }
}

class PredictionSnapshot {
  const PredictionSnapshot({
    required this.district,
    required this.state,
    required this.zone,
    required this.latitude,
    required this.longitude,
    required this.riskScore,
    required this.riskTier,
    required this.confidenceScore,
    required this.lastUpdated,
    required this.riskTimeline,
    required this.seriesByFeature,
    required this.featureImportance,
    required this.modelBreakdown,
    required this.leadTime,
    required this.summary,
    required this.actionableSteps,
  });

  final String district;
  final String state;
  final HimalayanZone zone;
  final double latitude;
  final double longitude;
  final double riskScore;
  final RiskTier riskTier;
  final double confidenceScore;
  final DateTime lastUpdated;
  final List<RiskTimelinePoint> riskTimeline;
  final Map<String, List<double>> seriesByFeature;
  final Map<String, double> featureImportance;
  final Map<String, double> modelBreakdown;
  final LeadTimeSummary leadTime;
  final String summary;
  final List<String> actionableSteps;

  factory PredictionSnapshot.fromBackend(Map<String, dynamic> json) {
    final resolved = (json['resolved_location'] as Map<String, dynamic>? ?? const {});
    final viz = (json['visualization'] as Map<String, dynamic>? ?? const {});
    final timeline = (json['timeline'] as List<dynamic>? ?? const <dynamic>[]);
    final timelineViz = _vizFromTimeline(timeline);
    final effectiveViz = viz.isNotEmpty ? viz : timelineViz;
    final model = (json['model_breakdown'] as Map<String, dynamic>? ?? const {});
    final factors = (json['top_contributing_factors'] as Map<String, dynamic>? ?? const {});
    final leadTime = LeadTimeSummary.fromJson((json['lead_time_analysis'] as Map<String, dynamic>? ?? const {}));

    final probability = (json['probability'] as num?)?.toDouble();
    final riskScore = (json['risk_score'] as num?)?.toDouble() ?? ((probability ?? 0) * 100);
    final riskTimeline = _buildRiskTimeline(effectiveViz, riskScore);

    final zoneFromContract = (json['zone'] ?? '').toString().trim().toLowerCase();
    final zoneFromChunk = (resolved['chunk'] ?? '').toString();
    final zone = zoneFromContract.isNotEmpty
        ? HimalayanZoneX.fromChunk(zoneFromContract)
        : HimalayanZoneX.fromChunk(zoneFromChunk);

    final confidence = (json['confidence'] as num?)?.toDouble() != null
        ? ((json['confidence'] as num).toDouble() * 100).clamp(0, 100).toDouble()
        : _confidenceFromBreakdown(model);

    final tierContract = (json['risk_tier'] ?? '').toString().trim().toUpperCase();
    final tier = switch (tierContract) {
      'LOW' => RiskTier.low,
      'MODERATE' => RiskTier.moderate,
      'HIGH' => RiskTier.high,
      _ => _riskTierFromScore(riskScore),
    };

    final district = (json['district'] ?? resolved['district'] ?? '').toString();
    final state = (resolved['state'] ?? '').toString();
    final precursors = (json['precursors'] as Map<String, dynamic>? ?? const {});
    final contractInsights = (json['insights'] as List<dynamic>? ?? const <dynamic>[]).map((e) => e.toString()).toList(growable: false);

    final featureImportance = factors.isNotEmpty
        ? factors.map((key, value) => MapEntry(key.toString(), (value as num?)?.toDouble() ?? 0))
        : _importanceFromPrecursors(precursors);

    final summary = (json['layman_explanation'] ?? '').toString().isNotEmpty
        ? (json['layman_explanation'] ?? '').toString()
        : (contractInsights.isNotEmpty ? contractInsights.join(' ') : tier.explanation);

    return PredictionSnapshot(
      district: district,
      state: state,
      zone: zone,
      latitude: (resolved['lat'] as num?)?.toDouble() ?? 0,
      longitude: (resolved['lon'] as num?)?.toDouble() ?? 0,
      riskScore: riskScore,
      riskTier: tier,
      confidenceScore: confidence,
      lastUpdated: DateTime.tryParse((json['last_updated'] ?? '').toString()) ?? _latestTimestamp(effectiveViz) ?? DateTime.now(),
      riskTimeline: riskTimeline,
      seriesByFeature: {
        'rain': _doubleList(effectiveViz['rain_trend']),
        'moisture': _doubleList(effectiveViz['moisture_trend']),
        'pressure': _doubleList(effectiveViz['pressure_drop_trend']),
        'wind': _doubleList(effectiveViz['wind_convergence_trend']),
        'cape': _syntheticCapeSeries(effectiveViz),
      },
      featureImportance: featureImportance,
      modelBreakdown: model.map((key, value) => MapEntry(key.toString(), (value as num?)?.toDouble() ?? 0)),
      leadTime: leadTime,
      summary: summary,
      actionableSteps: contractInsights.isNotEmpty ? contractInsights : _actionableSteps(tier),
    );
  }

  Map<String, dynamic> toCacheJson() {
    return {
      'district': district,
      'state': state,
      'zone': zone.name,
      'latitude': latitude,
      'longitude': longitude,
      'riskScore': riskScore,
      'riskTier': riskTier.name,
      'confidenceScore': confidenceScore,
      'lastUpdated': lastUpdated.toIso8601String(),
      'timeline': riskTimeline
          .map(
            (point) => {
              'label': point.label,
              'riskScore': point.riskScore,
              'moisture': point.moisture,
              'rainfall': point.rainfall,
              'pressureDrop': point.pressureDrop,
              'wind': point.wind,
            },
          )
          .toList(growable: false),
      'seriesByFeature': seriesByFeature,
      'featureImportance': featureImportance,
      'modelBreakdown': modelBreakdown,
      'leadTime': {
        'estimatedHours': leadTime.estimatedHours,
        'text': leadTime.text,
        'yellowHours': leadTime.yellowHours,
        'orangeHours': leadTime.orangeHours,
        'redHours': leadTime.redHours,
      },
      'summary': summary,
      'actionableSteps': actionableSteps,
    };
  }

  factory PredictionSnapshot.fromCache(Map<String, dynamic> json) {
    return PredictionSnapshot(
      district: (json['district'] ?? '').toString(),
      state: (json['state'] ?? '').toString(),
      zone: HimalayanZone.values.firstWhere(
        (value) => value.name == (json['zone'] ?? '').toString(),
        orElse: () => HimalayanZone.western,
      ),
      latitude: (json['latitude'] as num?)?.toDouble() ?? 0,
      longitude: (json['longitude'] as num?)?.toDouble() ?? 0,
      riskScore: (json['riskScore'] as num?)?.toDouble() ?? 0,
      riskTier: RiskTier.values.firstWhere(
        (value) => value.name == (json['riskTier'] ?? '').toString(),
        orElse: () => _riskTierFromScore((json['riskScore'] as num?)?.toDouble() ?? 0),
      ),
      confidenceScore: (json['confidenceScore'] as num?)?.toDouble() ?? 0,
      lastUpdated: DateTime.tryParse((json['lastUpdated'] ?? '').toString()) ?? DateTime.now(),
      riskTimeline: (json['timeline'] as List<dynamic>? ?? const <dynamic>[])
          .map(
            (item) => RiskTimelinePoint(
              label: (item as Map<String, dynamic>)['label'].toString(),
              riskScore: (item['riskScore'] as num?)?.toDouble() ?? 0,
              moisture: (item['moisture'] as num?)?.toDouble() ?? 0,
              rainfall: (item['rainfall'] as num?)?.toDouble() ?? 0,
              pressureDrop: (item['pressureDrop'] as num?)?.toDouble() ?? 0,
              wind: (item['wind'] as num?)?.toDouble() ?? 0,
            ),
          )
          .toList(growable: false),
      seriesByFeature: _mapOfSeries((json['seriesByFeature'] as Map<String, dynamic>? ?? const {})),
      featureImportance: _mapOfDouble(json['featureImportance'] as Map<String, dynamic>? ?? const {}),
      modelBreakdown: _mapOfDouble(json['modelBreakdown'] as Map<String, dynamic>? ?? const {}),
      leadTime: LeadTimeSummary.fromJson((json['leadTime'] as Map<String, dynamic>? ?? const {})),
      summary: (json['summary'] ?? '').toString(),
      actionableSteps: (json['actionableSteps'] as List<dynamic>? ?? const <dynamic>[]).map((e) => e.toString()).toList(growable: false),
    );
  }

  static RiskTier _riskTierFromScore(double value) {
    if (value < 40) return RiskTier.low;
    if (value < 70) return RiskTier.moderate;
    return RiskTier.high;
  }

  static double _confidenceFromBreakdown(Map<String, dynamic> breakdown) {
    final rf = (breakdown['rf_probability'] as num?)?.toDouble() ?? 0;
    final xgb = (breakdown['xgb_probability'] as num?)?.toDouble() ?? 0;
    return ((100 - ((rf - xgb).abs() * 100)).clamp(0, 100)).toDouble();
  }

  static List<RiskTimelinePoint> _buildRiskTimeline(Map<String, dynamic> viz, double riskScore) {
    final timestamps = (viz['timestamps'] as List<dynamic>? ?? const <dynamic>[]).map((value) => value.toString()).toList(growable: false);
    final rain = _doubleList(viz['rain_trend']);
    final moisture = _doubleList(viz['moisture_trend']);
    final pressure = _doubleList(viz['pressure_drop_trend']);
    final wind = _doubleList(viz['wind_convergence_trend']);
    final length = math.max(timestamps.length, math.max(rain.length, math.max(moisture.length, math.max(pressure.length, wind.length))));
    if (length == 0) return const <RiskTimelinePoint>[];

    return List<RiskTimelinePoint>.generate(length, (index) {
      final rainValue = _safeAt(rain, index);
      final moistureValue = _safeAt(moisture, index);
      final pressureValue = _safeAt(pressure, index);
      final windValue = _safeAt(wind, index);
      final normalized = _normalize(rainValue, moistureValue, pressureValue, windValue, riskScore);
      return RiskTimelinePoint(
        label: index < timestamps.length ? timestamps[index] : 'T${index + 1}',
        riskScore: normalized,
        moisture: moistureValue,
        rainfall: rainValue,
        pressureDrop: pressureValue,
        wind: windValue,
      );
    }, growable: false);
  }

  static double _normalize(double rain, double moisture, double pressure, double wind, double riskScore) {
    final pressurePenalty = pressure.abs() * 1.2;
    final weatherSum = rain * 1.6 + moisture * 0.35 + wind * 1.1 + pressurePenalty;
    return (riskScore * 0.22 + weatherSum).clamp(0, 100).toDouble();
  }

  static DateTime? _latestTimestamp(Map<String, dynamic> viz) {
    final timestamps = viz['timestamps'] as List<dynamic>?;
    if (timestamps == null || timestamps.isEmpty) return null;
    return DateTime.tryParse(timestamps.last.toString());
  }

  static double _safeAt(List<double> values, int index) {
    if (values.isEmpty) return 0;
    return index < values.length ? values[index] : values.last;
  }

  static List<double> _doubleList(dynamic value) {
    final list = value as List<dynamic>? ?? const <dynamic>[];
    return list.map((item) => (item as num?)?.toDouble() ?? 0).toList(growable: false);
  }

  static List<double> _syntheticCapeSeries(Map<String, dynamic> viz) {
    final rain = _doubleList(viz['rain_trend']);
    final moisture = _doubleList(viz['moisture_trend']);
    final length = math.max(rain.length, moisture.length);
    if (length == 0) return const <double>[];
    return List<double>.generate(length, (index) {
      final base = 700 + (_safeAt(rain, index) * 4.0) + (_safeAt(moisture, index) * 6.0);
      return base.clamp(0, 1800).toDouble();
    }, growable: false);
  }

  static Map<String, List<double>> _mapOfSeries(Map<String, dynamic> json) {
    return json.map((key, value) {
      final list = value as List<dynamic>? ?? const <dynamic>[];
      return MapEntry(key, list.map((item) => (item as num?)?.toDouble() ?? 0).toList(growable: false));
    });
  }

  static Map<String, double> _mapOfDouble(Map<String, dynamic> json) {
    return json.map((key, value) => MapEntry(key, (value as num?)?.toDouble() ?? 0));
  }

  static Map<String, dynamic> _vizFromTimeline(List<dynamic> timeline) {
    if (timeline.isEmpty) {
      return const {};
    }
    final rows = timeline
        .whereType<Map>()
        .map((row) => row.map((key, value) => MapEntry(key.toString(), value)))
        .toList(growable: false);
    if (rows.isEmpty) {
      return const {};
    }
    return {
      'timestamps': rows.map((row) => (row['timestamp'] ?? '').toString()).toList(growable: false),
      'rain_trend': rows.map((row) => (row['rainfall'] as num?)?.toDouble() ?? 0).toList(growable: false),
      'moisture_trend': rows.map((row) => (row['moisture'] as num?)?.toDouble() ?? 0).toList(growable: false),
      'pressure_drop_trend': rows.map((row) => (row['pressure_drop'] as num?)?.toDouble() ?? 0).toList(growable: false),
      'wind_convergence_trend': rows.map((row) => (row['wind'] as num?)?.toDouble() ?? 0).toList(growable: false),
    };
  }

  static Map<String, double> _importanceFromPrecursors(Map<String, dynamic> precursors) {
    const map = {
      'rainfall_spike': 'Rainfall spike',
      'moisture_surge': 'Moisture surge',
      'cape_high': 'High CAPE',
    };
    final result = <String, double>{};
    for (final entry in map.entries) {
      final active = (precursors[entry.key] as bool?) ?? false;
      result[entry.value] = active ? 33.3 : 5.0;
    }
    return result;
  }

  static List<String> _actionableSteps(RiskTier tier) {
    return switch (tier) {
      RiskTier.low => const [
          'Routine monitoring is enough for now.',
          'Keep an eye on weather alerts before travel.',
          'Use the analysis tab if conditions change quickly.',
        ],
      RiskTier.moderate => const [
          'Track rainfall and local drainage closely today.',
          'Avoid unnecessary exposure near streams or slopes.',
          'Check for stronger alerts again within a few hours.',
        ],
      RiskTier.high => const [
          'Treat this as an active early-warning condition.',
          'Pause travel in vulnerable valleys and road cuts.',
          'Prepare evacuation readiness and follow official advisories.',
        ],
    };
  }
}

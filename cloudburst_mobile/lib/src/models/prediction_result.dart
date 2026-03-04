class DistrictInfo {
  const DistrictInfo({
    required this.districtName,
    required this.state,
    required this.chunk,
    required this.lat,
    required this.lon,
  });

  final String districtName;
  final String state;
  final String chunk;
  final double lat;
  final double lon;

  factory DistrictInfo.fromResolved(Map<String, dynamic> json) {
    return DistrictInfo(
      districtName: (json["district"] ?? "").toString(),
      state: (json["state"] ?? "").toString(),
      chunk: (json["chunk"] ?? "").toString(),
      lat: (json["lat"] as num?)?.toDouble() ?? 0.0,
      lon: (json["lon"] as num?)?.toDouble() ?? 0.0,
    );
  }
}

class LeadTimeSummary {
  const LeadTimeSummary({
    required this.estimatedHours,
    required this.text,
    required this.yellow,
    required this.orange,
    required this.red,
  });

  final double? estimatedHours;
  final String text;
  final double? yellow;
  final double? orange;
  final double? red;

  factory LeadTimeSummary.fromJson(Map<String, dynamic> json) {
    return LeadTimeSummary(
      estimatedHours: (json["estimated_hours"] as num?)?.toDouble(),
      text: (json["text"] ?? "").toString(),
      yellow: (json["yellow_hr"] as num?)?.toDouble(),
      orange: (json["orange_hr"] as num?)?.toDouble(),
      red: (json["red_hr"] as num?)?.toDouble(),
    );
  }
}

class PredictionResult {
  const PredictionResult({
    required this.location,
    required this.riskScore,
    required this.riskLevel,
    required this.alertTier,
    required this.rfProbability,
    required this.xgbProbability,
    required this.ensembleProbability,
    required this.rainTrend,
    required this.moistureTrend,
    required this.pressureDropTrend,
    required this.windConvergenceTrend,
    required this.laymanExplanation,
    required this.leadTime,
    required this.topContributingFactors,
  });

  final DistrictInfo location;
  final double riskScore;
  final String riskLevel;
  final String alertTier;
  final double rfProbability;
  final double xgbProbability;
  final double ensembleProbability;
  final List<double> rainTrend;
  final List<double> moistureTrend;
  final List<double> pressureDropTrend;
  final List<double> windConvergenceTrend;
  final String laymanExplanation;
  final LeadTimeSummary leadTime;
  final Map<String, double> topContributingFactors;

  factory PredictionResult.fromJson(Map<String, dynamic> json) {
    List<double> listNum(Map<String, dynamic> src, String key) {
      final list = src[key] as List<dynamic>? ?? const <dynamic>[];
      return list.map((e) => (e as num?)?.toDouble() ?? 0.0).toList();
    }

    final location = DistrictInfo.fromResolved(
      (json["resolved_location"] as Map<String, dynamic>? ?? {}),
    );
    final model = (json["model_breakdown"] as Map<String, dynamic>? ?? {});
    final viz = (json["visualization"] as Map<String, dynamic>? ?? {});
    final contrib = (json["top_contributing_factors"] as Map<String, dynamic>? ?? {});

    return PredictionResult(
      location: location,
      riskScore: (json["risk_score"] as num?)?.toDouble() ?? 0.0,
      riskLevel: (json["risk_level"] ?? "").toString().toUpperCase(),
      alertTier: (json["alert_tier"] ?? "").toString().toUpperCase(),
      rfProbability: (model["rf_probability"] as num?)?.toDouble() ?? 0.0,
      xgbProbability: (model["xgb_probability"] as num?)?.toDouble() ?? 0.0,
      ensembleProbability: (model["ensemble_probability"] as num?)?.toDouble() ?? 0.0,
      rainTrend: listNum(viz, "rain_trend"),
      moistureTrend: listNum(viz, "moisture_trend"),
      pressureDropTrend: listNum(viz, "pressure_drop_trend"),
      windConvergenceTrend: listNum(viz, "wind_convergence_trend"),
      laymanExplanation: (json["layman_explanation"] ?? "").toString(),
      leadTime: LeadTimeSummary.fromJson((json["lead_time_analysis"] as Map<String, dynamic>? ?? {})),
      topContributingFactors: contrib.map((k, v) => MapEntry(k, (v as num?)?.toDouble() ?? 0.0)),
    );
  }
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

  factory DistrictOption.fromJson(Map<String, dynamic> json) {
    return DistrictOption(
      district: (json["district"] ?? "").toString(),
      state: (json["state"] ?? "").toString(),
      chunk: (json["chunk"] ?? "").toString(),
    );
  }
}

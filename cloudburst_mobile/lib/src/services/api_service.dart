import 'dart:convert';
import 'package:http/http.dart' as http;

import '../models/prediction_result.dart';

class ApiService {
  ApiService({required this.baseUrl});

  final String baseUrl;

  Future<bool> health() async {
    final response = await http.get(Uri.parse("$baseUrl/health"));
    return response.statusCode == 200;
  }

  Future<List<DistrictOption>> listDistricts({String? query}) async {
    final url = query == null || query.trim().isEmpty
        ? "$baseUrl/districts"
        : "$baseUrl/districts?q=${Uri.encodeQueryComponent(query.trim())}";
    final response = await http.get(Uri.parse(url));
    if (response.statusCode != 200) {
      throw Exception("District list failed (${response.statusCode}): ${response.body}");
    }
    final data = jsonDecode(response.body) as Map<String, dynamic>;
    final list = (data["districts"] as List<dynamic>? ?? const <dynamic>[]);
    return list.map((e) => DistrictOption.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<PredictionResult> predictByDistrict({required String district}) async {
    final response = await http.post(
      Uri.parse("$baseUrl/predict-district"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"district": district}),
    );
    if (response.statusCode != 200) {
      throw Exception("Prediction failed (${response.statusCode}): ${response.body}");
    }
    return PredictionResult.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }
}

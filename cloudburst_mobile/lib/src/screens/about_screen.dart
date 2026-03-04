import 'package:flutter/material.dart';

class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(16),
              gradient: const LinearGradient(
                colors: [Color(0xFF0B4F6C), Color(0xFF2A9D8F)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
            ),
            child: const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  "About HCIS",
                  style: TextStyle(color: Colors.white, fontWeight: FontWeight.w700, fontSize: 22),
                ),
                SizedBox(height: 10),
                Text(
                  "Turning Satellite Data Into Early Warnings for Himalayan Communities.",
                  style: TextStyle(color: Colors.white, fontSize: 15, height: 1.4),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),
          const Card(
            child: Padding(
              padding: EdgeInsets.all(14),
              child: Text(
                "Himalayan Cloudburst Intelligence System (HCIS) is an AI-supported district-level climate risk tool. "
                "For each request, it resolves district geography, identifies the Himalayan chunk, evaluates recent "
                "atmospheric behavior, and produces an explainable risk score with lead-time context. "
                "\n\nHCIS is designed for preparedness and decision support. It focuses on signatures that precede "
                "extreme localized rain bursts, not just generic rainfall forecasting.",
              ),
            ),
          ),
          const SizedBox(height: 10),
          const Card(
            child: Padding(
              padding: EdgeInsets.all(14),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text("System Philosophy", style: TextStyle(fontWeight: FontWeight.w700)),
                  SizedBox(height: 6),
                  Text("Scientific credibility • Calm but urgent UX • Data transparency • Citizen-friendly interpretation"),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

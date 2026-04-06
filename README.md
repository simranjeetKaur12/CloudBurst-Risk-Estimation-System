# Himalayan Cloudburst Intelligence System (HCIS)

District-level cloudburst early-risk intelligence for the Indian Himalayas using ERA5 + IMERG data, chunk-specific ML models, and explainable API outputs.

## Overview

HCIS is designed as an operational decision-support system, not a generic weather app. It converts atmospheric signals into actionable risk intelligence:

- District-first inference (`district -> centroid -> Himalayan chunk -> model`)
- Region-aware modeling across 3 Himalayan chunks (Western, Central, Eastern)
- Ensemble prediction (Random Forest + XGBoost)
- Explainable outputs (risk score, alert tier, lead-time, contributing factors, layman summary)
- Mobile-ready delivery through Flutter + FastAPI

## Current Capabilities

- Multi-region data pipeline for ERA5 and IMERG ingestion/preprocessing
- Feature engineering + cloudburst labeling + model training workflow
- Chunk-specific model loading at inference time
- District search endpoint and district prediction endpoint
- District-to-zone geospatial boundary intelligence endpoint
- Pipeline execution endpoint for latest 10-day operational context
- Visualization payload for rain/moisture/pressure/wind trends
- Historical events API with replay timeline support
- Optional token-based authentication for deeper analytics
- Flutter mobile app with district selection and risk dashboard UX

## Repository Structure

```text
backend/                  FastAPI inference service
cloudburst_mobile/        Flutter mobile app
src/                      Data, feature, labeling, model, visualization pipelines
models/                   Trained model artifacts (.pkl)
data/                     Raw/processed data + shapefiles
results/                  Evaluation outputs and summaries
run_pipeline.py           End-to-end model pipeline orchestrator
```

## System Architecture

```text
ERA5 + IMERG -> preprocessing -> merged dataset -> feature engineering
-> cloudburst labeling -> train/test split -> model training/evaluation
-> chunk models (.pkl) -> FastAPI inference -> Flutter app
```

## Regions and Chunks

HCIS uses zone-specific logic for Himalayan terrain behavior:

- Western Himalaya: Jammu & Kashmir, Ladakh, Himachal Pradesh
- Central Himalaya: Uttarakhand
- Eastern Himalaya: Sikkim, Arunachal Pradesh

At runtime, district geometry determines chunk membership and model routing.

## Model Approach

- Base learners: `RandomForestClassifier`, `XGBoost`
- Inference score: simple ensemble average of class-1 probabilities
- Output mapping:
  - `0-40`: Low (Green)
  - `40-60`: Yellow
  - `60-80`: Orange
  - `80-100`: Red

## Performance Snapshot

From `results/model_performance.csv` and `results/chunk_ensemble_performance.csv`:

- Random Forest: AUC `0.8897`, Recall `0.7598`, Precision `0.1721`
- XGBoost: AUC `0.8914`, Recall `0.6048`, Precision `0.2144`
- Ensemble: AUC `0.8929`, Recall `0.6550`, Precision `0.1929`

Interpretation:
- Strong discrimination (AUC ~0.89)
- Expected precision-recall tradeoff for rare-event early warning
- System is tuned toward event sensitivity, with moderate false-alert burden

## API (FastAPI)

### Health

- `GET /health`
- Returns service, shapefile, and model readiness metadata

### District List

- `GET /districts?q=<optional>&limit=<optional>`
- Returns searchable district list with `district`, `state`, `chunk`

### District Prediction

- `POST /predict-district`

Request:

```json
{
  "district": "Dehradun"
}
```

Response includes:
- `risk_score`, `alert_tier`, `lead_time_analysis`
- `model_breakdown` (rf/xgb/ensemble probabilities)
- `top_contributing_factors`
- `visualization` trend arrays
- `layman_explanation`

### Backward-Compatible Location Prediction

- `POST /predict-location` with `lat/lon` or `latitude/longitude`
- Internally resolves nearest/containing district and reuses district inference

### Production API Surface (Web + Mobile)

- `POST /inference/district` district-first inference with explainability payload
- `POST /pipeline/run` run/resolve latest 10-day processed context
- `GET /districts/{district_name}/zone` district boundary + zone metadata
- `GET /zones` available zone-level district counts
- `GET /model-insights?detailed=<bool>` model metrics and event detection summaries
- `GET /historical-events` searchable historical cloudburst catalog
- `GET /historical-events/replay?event_id=<id>` replay atmospheric progression
- `GET /metrics` runtime request/cache counters
- `POST /auth/token` optional bearer token for restricted advanced analytics

## Quick Start

### 1) Python Environment

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

### 2) Run Backend

```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

Local checks:
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

### 3) Run Web Frontend (Streamlit)

```bash
streamlit run frontend/app.py
```

Then open the app and navigate to:

- Home (immersive live map intro)
- Risk Dashboard (district-first inference + explainability)
- Novelty and Research
- Model Insights
- Historical Events (replay mode)

## Flutter Mobile App

### Run in development

```bash
cd cloudburst_mobile
flutter pub get
flutter run
```

### Build release APK

```bash
cd cloudburst_mobile
flutter build apk --release
```

APK path:

```text
cloudburst_mobile/build/app/outputs/flutter-apk/app-release.apk
```

For physical devices, set backend URL in app to your laptop LAN IP (example: `http://192.168.1.25:8000`), not `10.0.2.2`.

## End-to-End Training Pipeline

`run_pipeline.py` orchestrates full workflow:

1. ERA5 download/extract/preprocess
2. IMERG download/preprocess/aggregate
3. Merge ERA5 + IMERG
4. Feature engineering
5. Label creation
6. Train/test split
7. Model training
8. Risk-tier evaluation and lead-time analysis
9. Alert-signal generation

Example:

```bash
python run_pipeline.py --start_year 2018 --end_year 2020 --regions himalayan_west uttarakhand sikkim
```

## Required Runtime Assets

- Shapefile (district boundaries), e.g. `data/shapefiles/geoBoundaries-IND-ADM2.shp`
- Chunk model artifacts:
  - `models/western_model.pkl`
  - `models/central_model.pkl`
  - `models/eastern_model.pkl`
- Chunk timeseries CSVs used by inference:
  - `data/processed/labeled_cloudburst_district_western.csv`
  - `data/processed/labeled_cloudburst_district_central.csv`
  - `data/processed/labeled_cloudburst_district_eastern.csv`

## Known Limitations

- `POST /predict-district` currently uses cached processed chunk data for inference context.
- Live "fetch last 10 days ERA5+IMERG on every request" is not yet executed in the API path (placeholder exists in backend).
- Some shapefiles may not contain explicit district/state attributes; fallback labeling can occur.
- Region-wise metrics may be optimistic when trained on replicated placeholder datasets.

## Research and Governance Notes

- Outputs are probabilistic risk intelligence, not deterministic event confirmation.
- Not an official government warning system.
- Always follow IMD/NDMA/local authority advisories for public safety action.

## Roadmap

- True on-request 10-day data assimilation in backend inference path
- Stronger district-level validation by chunk with non-replicated training corpora
- PDF report generation endpoint for analytics export
- Production deployment hardening (auth, rate-limits, monitoring)

## License

MIT (see `LICENSE`).

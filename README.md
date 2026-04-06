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
- Primary strict prediction contract: `GET /predict?district=<name>`
- User profile persistence: save/retrieve preferred district by `user_id`
- Visualization payload for rain/moisture/pressure/wind trends
- Flutter mobile app with district selection, caching, and risk dashboard UX

## Repository Structure

```text
backend/                  FastAPI inference service
cloudburst_mobile/        Flutter mobile app
.github/workflows/        Scheduled offline batch automation
src/                      Data, feature, labeling, model, visualization pipelines
src/pipelines/offline/    Daily offline pipeline scripts (download->latest features)
models/                   Trained model artifacts (.pkl)
data/                     Raw/processed data + shapefiles
results/                  Evaluation outputs and summaries
run_pipeline.py           End-to-end model pipeline orchestrator
```

## Production Architecture (Offline vs Online)

```text
OFFLINE (GitHub Actions daily)
ERA5 + IMERG (last 10 days) -> preprocess -> merge -> feature engineering
-> compact latest feature tables (per chunk) -> commit/upload artifacts

ONLINE (Render FastAPI)
Client request -> district->chunk routing -> load cached model + cached latest features
-> inference + explainability payload -> response (<1s target)
```

## Data Flow Diagram

```text
             +----------------------------+
             | GitHub Actions (daily)     |
             | .github/workflows/pipeline |
             +-------------+--------------+
                           |
                           v
   +----------------------+------------------------+
   | Offline Pipeline (src/pipelines/offline)     |
   | download/preprocess/merge/feature scripts    |
   +----------------------+------------------------+
                           |
                           v
      data/processed/latest_features_{chunk}.csv
                           |
                           v
                  +--------+--------+
                  | Render FastAPI  |
                  | backend/app.py  |
                  +--------+--------+
                           |
                           v
                  Flutter + Streamlit clients
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

### District Prediction (Primary Contract)

- `GET /predict?district=<district_name>&user_id=<optional>`
- If `district` is omitted and `user_id` is provided, backend uses saved preferred district.

Example:

```http
GET /predict?district=Dehradun&user_id=demo-user-001
```

Response includes:
- `district`, `zone`, `risk_tier`, `probability`, `confidence`
- `timeline`, `precursors`, `insights`
- `risk_score`, `alert_tier`, `lead_time_analysis`
- `model_breakdown`, `top_contributing_factors`, `visualization`
- `layman_explanation`

### District Prediction (Backward-Compatible)

- `POST /predict-district`

Request:

```json
{
  "district": "Dehradun"
}
```

### User Profile Endpoints

- `GET /user-profile?user_id=<id>`
  - Returns saved preferred district for the user (if exists)
- `POST /user-profile/select-district`

Request:

```json
{
  "user_id": "demo-user-001",
  "district": "Dehradun"
}
```

This stores the district selection in SQLite (`data/app_users.db`) and enables auto-selection for subsequent sessions.

## Quick Start

### 1) Python Environment

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

### 2) Run Backend (Online Inference Only)

```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

Local checks:
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/districts?q=dehra`
- `http://127.0.0.1:8000/predict?district=Dehradun`

The backend never runs raw data download, full preprocessing, or training during request handling.

### 3) Run Web Frontend (Streamlit)

```bash
streamlit run frontend/app.py
```

Then open the app and use district-first risk estimation flows.

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

For local physical-device testing, pass your LAN API URL via `--dart-define`.

Default mobile URL behavior:
- Android/web/desktop default: `https://hcis-api.onrender.com`
- Can be overridden with `CLOUDBURST_API_BASE_URL`

Example override for local backend:

```bash
flutter run --dart-define=CLOUDBURST_API_BASE_URL=http://192.168.1.25:8000
```

## Daily Offline Pipeline (GitHub Actions)

Workflow file: `.github/workflows/pipeline.yml`

Schedule:
- Runs daily via cron
- Can be triggered manually via `workflow_dispatch`

Pipeline scripts:
- `src/pipelines/offline/download_era5.py`
- `src/pipelines/offline/download_imerg.py`
- `src/pipelines/offline/preprocess_era5.py`
- `src/pipelines/offline/preprocess_imerg.py`
- `src/pipelines/offline/merge_era5_imerg.py`
- `src/pipelines/offline/generate_latest_features.py`
- `src/pipelines/offline/run_daily_pipeline.py`

Outputs:
- `data/processed/latest_features_western.csv`
- `data/processed/latest_features_central.csv`
- `data/processed/latest_features_eastern.csv`

Workflow behavior:
- Uploads latest features as build artifacts
- Optionally commits refreshed latest feature CSVs back to the repo
- Keeps model `.pkl` artifacts static (no daily retraining)

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
- Precomputed lightweight latest feature CSVs used by online inference:
  - `data/processed/latest_features_western.csv`
  - `data/processed/latest_features_central.csv`
  - `data/processed/latest_features_eastern.csv`

Optional offline source files (for daily feature refresh):
- `data/processed/labeled_cloudburst_district_western.csv`
- `data/processed/labeled_cloudburst_district_central.csv`
- `data/processed/labeled_cloudburst_district_eastern.csv`

## Research and Governance Notes

- Outputs are probabilistic risk intelligence, not deterministic event confirmation.
- Not an official government warning system.
- Always follow IMD/NDMA/local authority advisories for public safety action.

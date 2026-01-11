# 🌧️ Cloudburst Risk Estimation using ERA5 & GPM-IMERG

> **A production-oriented, data-driven system for estimating cloudburst risk in the Himalayan region using multi-source atmospheric reanalysis and satellite precipitation data.**

---

## Why This Project Matters

Cloudbursts are short-lived, highly localized extreme rainfall events that frequently trigger flash floods and landslides in mountainous regions.  
Despite advances in numerical weather prediction, **cloudbursts remain extremely difficult to forecast** due to their rapid onset, small spatial scale, and complex terrain interactions.

Most existing approaches rely on:
- Fixed rainfall thresholds
- Post-event detection
- Rainfall-only analysis

This project instead focuses on **cloudburst risk estimation**, enabling **early warning signals** by combining atmospheric precursors with observed precipitation.

---

## Key Contributions 

✔ Risk **estimation** instead of binary “event / no-event” prediction  
✔ Fusion of **physical atmospheric precursors (ERA5)** with **satellite rainfall (GPM-IMERG)**  
✔ **Percentile-based extreme event labeling** (region-adaptive, data-driven)  
✔ **Strict time-based train/test split** (no temporal leakage)  
✔ Incremental, **storage-aware data pipeline**  
✔ End-to-end system: ingestion → features → labels → modeling → validation  

---

## Problem Definition

- **Objective:** Estimate cloudburst risk during Indian monsoon season  
- **Region:** Uttarakhand, India (28°–31.5°N, 77°–81°E)  
- **Temporal Resolution:** Hourly  
- **Output:** Cloudburst risk score (0–1)  

The system is designed for **decision support**, not deterministic forecasting.

---

## Data Sources

### ERA5 Atmospheric Reanalysis (ECMWF)

ERA5 is used to capture **large-scale atmospheric precursors** associated with extreme rainfall:

- Near-surface temperature (t2m)
- Wind components (u10, v10)
- Surface pressure (sp)
- Total column water vapor (tcwv)

ERA5 provides **physically consistent pre-event signals** that are not observable from rainfall alone.

---

### GPM IMERG Satellite Precipitation (NASA)

IMERG Final Run data is used for **high-resolution rainfall observation**:

- Half-hourly precipitation rate
- Converted to rainfall amount
- Aggregated to hourly resolution
- Spatially averaged over study region

IMERG enables **objective identification of extreme rainfall** events.

---

## Cloudburst Labeling Strategy

Cloudbursts are labeled using **percentile-based thresholds**, avoiding fixed heuristics:

- 1-hour rainfall ≥ 99th percentile  
- 3-hour rainfall ≥ 99th percentile  
- 6-hour rainfall ≥ 99th percentile  

This ensures:
- Regional adaptability  
- Robustness across years  
- Reduced labeling bias  

Labels represent **extreme rainfall conditions**, not post-disaster outcomes.

---

## Feature Engineering

Physically interpretable features are derived from ERA5 and IMERG:

### Rainfall Dynamics
- 1h, 3h, 6h accumulated rainfall
- Peak rainfall in last 3 hours
- Rainfall lags (t-1, t-2)

### Atmospheric Conditions
- Wind speed = √(u² + v²)
- 3h / 6h rolling TCWV
- Surface pressure drop over 3 hours
- Near-surface temperature gradient

These features capture **moisture availability, convergence, persistence, and instability**.

---

## System Architecture

Raw ERA5 Data ──┐
                ├── Feature Engineering ──┐
Raw IMERG Data ─┘                         │
                                          ├── Cloudburst Labeling
                                          │
                                Train/Test Split (Time-based)
                                          │
                                 ML Risk Estimation Model
                                          │
                                Historical Event Validation

---

## Tech Stack

### Core
- Python 3.10+
- NumPy, Pandas
- Xarray (NetCDF / HDF5 processing)

### Data Access
- EarthAccess (NASA GES DISC)
- ERA5 Reanalysis
- GPM IMERG

### Machine Learning
- Scikit-learn
- Class imbalance handling
- Time-aware evaluation

### Visualization
- Matplotlib
- GeoPandas 

---

## Project Structure

Cloudburst_project/
│
├── data/
│   ├── raw/
│   │   ├── era5/
│   │   └── imerg/
│   └── processed/
│       ├── imerg_halfhourly_uttarakhand.csv
│       ├── imerg_hourly_uttarakhand.csv
│       ├── era5_features_uttarakhand.csv
│       ├── era5_imerg_merged_2005_2015.csv
│       └── imerg_processed_days.csv
│
├── src/
│   ├── data/
│   │   ├── era5/
│   │   │   ├── download_era5.py
│   │   │   └── preprocess_era5.py
│   │   └── imerg/
│   │       ├── download_imerg.py
│   │       ├── preprocess_imerg.py
│   │       ├── aggregate_imerg.py
│   │       └── merge_era5_imerg.py
│   │
│   ├── labels/
│   │   └── create_cloudburst_labels.py
│   │
│   ├── models/
│   │   └── train_test_split.py
│   │
├── figures/
│   ├── fig1_study_area.py
│   ├── fig2_architecture.py
│   ├── ...
│
├── README.md
└── requirements.txt

---

## Incremental & Fault-Tolerant Design

Due to storage constraints, the pipeline supports **year-wise execution**:

1. Download IMERG for selected years
2. Preprocess → update `imerg_processed_days.csv`
3. Aggregate → merge → label
4. Safely delete raw files
5. Resume anytime without duplication

---

## Evaluation & Validation

- Time-aware train/test split
- Event-wise risk escalation analysis
- Comparison with historical cloudburst records

The objective is **early risk signal**, not perfect classification accuracy.

---

## Author Note

This project demonstrates:

- End-to-end ML system design
- Climate + ML domain understanding
- Production-aware data engineering
- Research-grade methodology

---
## Project Status

🚧 **Active Development**

- Data processing completed for rolling windows:
  - 2005–2015
  - 2006–2016
  - 2007–2017
- Remaining years are being processed incrementally due to storage constraints
- Model training and evaluation to be added after full data consolidation
- CI/CD integration planned

This repository reflects a real-world, iterative research workflow.

---

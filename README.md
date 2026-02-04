# 🌧️ Cloudburst Risk Estimation using ERA5 & GPM-IMERG

> **A data-driven system for estimating cloudburst risk in the Himalayan region using atmospheric reanalysis and satellite precipitation data.**

---

## Project Overview

Cloudbursts are short-duration, highly localized extreme rainfall events that frequently trigger flash floods and landslides in mountainous regions such as the Western Himalayas. Due to their rapid onset, fine spatial scale, and strong terrain dependence, cloudbursts remain difficult to capture using conventional numerical weather prediction (NWP) models.

This project presents a **data-driven cloudburst risk estimation framework** that integrates:
- **ERA5 atmospheric reanalysis** for large-scale precursors
- **GPM-IMERG satellite precipitation** for high-resolution rainfall dynamics

Instead of deterministic rainfall prediction, the system focuses on **probabilistic risk estimation and early warning**, enabling actionable alerts with quantifiable lead time.

---

## What Has Been Implemented So Far

This repository implements the **complete machine learning core** of the cloudburst early-warning system.

### ✔ Implemented
- ERA5 + IMERG data preprocessing and alignment  
- Physically interpretable feature engineering  
- Event-based cloudburst labeling  
- Leakage-free time-based train/test split  
- Training of multiple ML models  
- Risk probability estimation  
- Risk tier generation (Yellow / Orange / Red)  
- Lead-time vs detection tradeoff analysis  
- Research-grade visualizations  

### 🚧 Upcoming (Next Phase)
- Backend API (FastAPI)
- Frontend dashboard (Streamlit)
- Real-time inference pipeline

---

## Problem Definition

- **Objective:** Estimate cloudburst *risk* for early warning  
- **Region:** Uttarakhand, India (28°–31.5°N, 77°–81°E)  
- **Temporal Resolution:** Hourly  
- **Output:** Probabilistic cloudburst risk score + alert tier  

The framework is designed for **decision support**, not post-event analysis.

---

## Data Sources

### ERA5 Atmospheric Reanalysis (ECMWF)
Used to capture large-scale atmospheric precursors:
- 2m temperature (t2m)
- Surface pressure (sp)
- Wind components (u10, v10)
- Total column water vapour (tcwv)

### GPM-IMERG Satellite Precipitation (NASA)
Used for localized rainfall characterization:
- Half-hourly precipitation
- Aggregated to hourly, 3-hourly, and 6-hourly rainfall
- Spatially averaged over the study region

---


## Cloudburst Labeling Strategy

Cloudburst events are labeled using **percentile-based extreme rainfall thresholds**:

- 1-hour rainfall ≥ 99th percentile  
- 3-hour rainfall ≥ 99th percentile  
- 6-hour rainfall ≥ 99th percentile  

This adaptive approach:
- Avoids hard-coded heuristics
- Preserves regional climatology
- Reduces labeling bias

Labels represent **extreme rainfall risk**, not disaster impact.

---

## Feature Engineering

### Atmospheric Features (ERA5)
- Wind speed (derived from u10, v10)
- Rolling TCWV (3h, 6h)
- Surface pressure drop (3h)
- Near-surface temperature gradients

### Rainfall Features (IMERG)
- 1h, 3h, 6h accumulated rainfall
- Short-term rainfall persistence

All features are **physically interpretable** and time-aligned.

---

## Machine Learning Models

The following supervised models are trained and evaluated:

- **Logistic Regression** (baseline, interpretable)
- **Random Forest** (nonlinear ensemble)
- **XGBoost** (optimized for extreme-event sensitivity)

Class imbalance is handled using:
- Class weighting (LR, RF)
- `scale_pos_weight` (XGBoost)

---

## Current System Architecture

```
Raw ERA5 Data ──┐
                ├── Data Cleaning & Alignment
Raw IMERG Data ─┘             │
                      Feature Engineering
                              │
                      Cloudburst Labeling
                              │
                  Time-based Train / Test Split
                              │
                    ML Modeling (In Progress)
                              │
                   Historical Event Validation
```


---

## Tech Stack

### Core
- Python 3.10+
- NumPy, Pandas
- Xarray (NetCDF / HDF5)

### Data Access
- EarthAccess (NASA GES DISC)
- ERA5 Reanalysis
- GPM IMERG

### Machine Learning (Planned)
- Scikit-learn
- Time-aware evaluation
- Class imbalance handling

### Visualization
- Matplotlib
- GeoPandas

---

## Incremental & Fault-Tolerant Design

Due to storage constraints, the pipeline supports **year-wise execution**:

1. Download IMERG for selected years
2. Preprocess and update processed-days tracker
3. Aggregate and merge datasets
4. Safely remove raw files
5. Resume processing without duplication

---

## Author Note

This project is developed with an emphasis on:
- Physical interpretability
- Reproducible data pipelines
- Time-consistent evaluation
- Applied Climate + Machine Learning research


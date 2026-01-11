# 🌧️ Cloudburst Risk Estimation using ERA5 & GPM-IMERG

> **A data-driven system for estimating cloudburst risk in the Himalayan region using atmospheric reanalysis and satellite precipitation data.**

---

## Project Overview

Cloudbursts are short-duration, highly localized extreme rainfall events that frequently trigger flash floods and landslides in mountainous regions.  
Due to their rapid onset, small spatial scale, and strong terrain dependence, **cloudbursts remain difficult to forecast using conventional numerical models**.

This project focuses on **cloudburst risk estimation** by integrating:
- Large-scale atmospheric precursors
- High-resolution satellite rainfall observations

The objective is to **identify elevated risk conditions**, not deterministic event prediction.

---

## What Has Been Implemented So Far

✔ Robust data ingestion pipeline for ERA5 and GPM-IMERG  
✔ Region-specific preprocessing for Uttarakhand (India)  
✔ Fault-tolerant, incremental IMERG processing (storage-aware)  
✔ Hourly rainfall aggregation from half-hourly satellite data  
✔ Physically interpretable feature engineering  
✔ Percentile-based extreme rainfall labeling  
✔ Time-consistent train/test data preparation  

This repository currently emphasizes **data engineering, feature construction, and labeling**, which form the foundation of the modeling stage.

---

## Problem Definition

- **Objective:** Estimate cloudburst risk during Indian monsoon season  
- **Region:** Uttarakhand, India (28°–31.5°N, 77°–81°E)  
- **Temporal Resolution:** Hourly  
- **Output:** Cloudburst risk indicator (to be modeled)

The system is intended for **decision support and early risk awareness**.

---

## Data Sources

### ERA5 Atmospheric Reanalysis (ECMWF)

ERA5 is used to capture **large-scale atmospheric conditions preceding extreme rainfall**, including:

- Near-surface temperature (t2m)
- Wind components (u10, v10)
- Surface pressure (sp)
- Total column water vapor (tcwv)

These variables provide **physically consistent precursors** that rainfall data alone cannot represent.

---

### GPM IMERG Satellite Precipitation (NASA)

IMERG Final Run data is used for **high-resolution rainfall observation**:

- Half-hourly precipitation rate
- Converted to rainfall amount
- Aggregated to hourly resolution
- Spatially averaged over the study region

IMERG enables **objective identification of statistically extreme rainfall periods**.

---

## Cloudburst Labeling Strategy

Extreme rainfall conditions are labeled using **percentile-based thresholds**:

- 1-hour rainfall ≥ 99th percentile  
- 3-hour rainfall ≥ 99th percentile  
- 6-hour rainfall ≥ 99th percentile  

This approach avoids fixed heuristics and ensures:
- Regional adaptability  
- Consistency across years  
- Reduced labeling bias  

Labels represent **extreme rainfall risk**, not disaster outcomes.

---

## Feature Engineering

Physically interpretable features derived from ERA5 and IMERG include:

### Rainfall Dynamics
- 1h, 3h, 6h accumulated rainfall
- Peak rainfall in recent hours
- Rainfall lag features (t-1, t-2)

### Atmospheric Conditions
- Wind speed (√(u² + v²))
- Rolling TCWV (3h / 6h)
- Surface pressure tendency
- Near-surface temperature gradients

These features capture **moisture availability, persistence, and atmospheric instability**.

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

## Project Status

🚧 **Active Development**

### Completed
- Data ingestion and preprocessing
- Feature engineering
- Extreme rainfall labeling
- Rolling-window dataset creation:
  - 2005–2015
  - 2006–2016
  - 2007–2017

### In Progress
- Full multi-year dataset consolidation
- Model training and evaluation
- Result visualization
- CI/CD automation

---

## Author Note

This project is developed with an emphasis on:
- Physical interpretability
- Reproducible data pipelines
- Time-consistent evaluation
- Applied Climate + Machine Learning research

The repository will continue to evolve as modeling and validation stages are completed.

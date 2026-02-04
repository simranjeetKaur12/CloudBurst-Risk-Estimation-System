"""
Cloudburst Risk Estimation Pipeline
=================================

This script orchestrates the complete end-to-end workflow:
1. ERA5 data download & preprocessing
2. GPM-IMERG data download, preprocessing & aggregation
3. ERA5–IMERG feature merging
4. Feature engineering
5. Cloudburst labeling
6. Time-aware train/test split
7. Model training
8. Risk tier evaluation
9. Lead-time analysis
10. Visualization generation

Run:
    python run_pipeline.py

Optional:
    Comment/uncomment stages as needed.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(script_path: str):
    """Utility to run a python script with logging"""
    print(f"\n▶ Running: {script_path}")
    result = subprocess.run(
        [sys.executable, script_path],
        cwd=ROOT
    )
    if result.returncode != 0:
        raise RuntimeError(f"❌ Failed at {script_path}")
    print(f"✔ Completed: {script_path}")


def main():

    print("\n==============================")
    print(" CLOUD BURST ML PIPELINE START ")
    print("==============================")

    # -----------------------------
    # 1. ERA5 DATA PIPELINE
    # -----------------------------
    run("src/data/era5/download_era5.py")
    run("src/data/era5/unzip_era5.py")
    run("src/data/era5/preprocess_era5.py")

    # -----------------------------
    # 2. IMERG DATA PIPELINE
    # -----------------------------
    run("src/data/imerg/download_imerg.py")
    run("src/data/imerg/preprocess_imerg.py")
    run("src/data/imerg/aggregate_imerg.py")

    # -----------------------------
    # 3. MERGE ERA5 + IMERG
    # -----------------------------
    run("src/data/imerg/merge_era5_imerg.py")

    # -----------------------------
    # 4. FEATURE ENGINEERING
    # -----------------------------
    run("src/features/build_features.py")

    # -----------------------------
    # 5. CLOUD BURST LABELING
    # -----------------------------
    run("src/labels/create_cloudburst_labels.py")

    # -----------------------------
    # 6. TRAIN / TEST SPLIT (TIME-AWARE)
    # -----------------------------
    run("src/models/train_test_split.py")

    # -----------------------------
    # 7. MODEL TRAINING
    # -----------------------------
    run("src/models/train_models.py")

    # -----------------------------
    # 8. RISK TIER EVALUATION
    # -----------------------------
    run("src/models/risk_tier_evaluation.py")

    # -----------------------------
    # 9. LEAD-TIME ANALYSIS
    # -----------------------------
    run("src/models/lead_time_analysis.py")

    # -----------------------------
    # 10. VISUALIZATIONS
    # -----------------------------
    run("src/visualization/study_area.py")
    run("src/visualization/rainfall_extremes.py")
    run("src/visualization/atmospheric_precursors.py")
    run("src/visualization/feature_contribution.py")
    run("src/visualization/roc_curves.py")
    run("src/visualization/confusion_matrix.py")
    run("src/visualization/recall_comparison.py")
    run("src/visualization/leadtime_tradeoff.py")
    run("src/visualization/plot_risk_escalation.py")
    run("src/visualization/models_comparison.py")

    print("\n==============================")
    print(" PIPELINE COMPLETED SUCCESSFULLY ")
    print("==============================\n")


if __name__ == "__main__":
    main()

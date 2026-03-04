from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

MODEL_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data" / "processed"

XGB_MODEL = MODEL_DIR / "xgb_early_warning.pkl"
RF_MODEL  = MODEL_DIR / "rf_early_warning.pkl"
LR_MODEL  = MODEL_DIR / "lr_early_warning.pkl"

YELLOW_TH = 0.30
ORANGE_TH = 0.60
RED_TH    = 0.85

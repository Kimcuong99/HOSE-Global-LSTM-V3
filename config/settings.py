"""Central configuration for HOSE Global LSTM V3."""
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_NAME = "HOSE Global LSTM V3"
APP_VERSION = "3.0.0"
DEFAULT_LANGUAGE = "Tiếng Việt"
SUPPORTED_LANGUAGES = ("Tiếng Việt", "English", "简体中文")
RANDOM_SEED = 2027
START_DATE = "2020-01-01"
END_DATE = "2025-12-31"
EXPECTED_TICKERS = 160
DATA_TYPE = "SYNTHETIC"
DATA_SOURCE = "SIMULATED_NOT_MARKET_DATA"
SIMULATION_RAW_DIR = PROJECT_ROOT / "data" / "simulation" / "raw"
SIMULATION_PROCESSED_DIR = PROJECT_ROOT / "data" / "simulation" / "processed"
REAL_RAW_DIR = PROJECT_ROOT / "data" / "real" / "raw"
REAL_PROCESSED_DIR = PROJECT_ROOT / "data" / "real" / "processed"
MODEL_SIMULATION_DIR = PROJECT_ROOT / "models" / "simulation"
MODEL_REAL_DIR = PROJECT_ROOT / "models" / "real"
OUTPUT_SIMULATION_DIR = PROJECT_ROOT / "outputs" / "simulation"
OUTPUT_REAL_DIR = PROJECT_ROOT / "outputs" / "real"
for path in (SIMULATION_RAW_DIR, SIMULATION_PROCESSED_DIR, REAL_RAW_DIR, REAL_PROCESSED_DIR, MODEL_SIMULATION_DIR, MODEL_REAL_DIR, OUTPUT_SIMULATION_DIR, OUTPUT_REAL_DIR):
    path.mkdir(parents=True, exist_ok=True)

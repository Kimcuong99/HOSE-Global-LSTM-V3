"""
Prepare synthetic HOSE panel data for Global LSTM.
- Keeps each ticker's sequence isolated.
- Uses chronological date splits.
- Fits feature scaler on training dates only.
- Saves arrays and metadata for model training.
All input market values must be synthetic or clearly labeled real.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import joblib

ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "data" / "simulation" / "processed" / "hose_model_ready.csv"
OUTPUT_DIR = ROOT / "data" / "simulation" / "processed"
LOOKBACK = 60
FEATURES = [
    "open_rel", "high_rel", "low_rel", "close_rel",
    "adjusted_close_rel", "volume_log_change", "market_return"
]
TARGET = "next_day_return"
TRAIN_END = "2022-12-31"
VAL_END = "2024-12-31"

def load_data():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Missing {INPUT_FILE}. Run scripts/generate_hose_simulation.py first."
        )
    df = pd.read_csv(INPUT_FILE, parse_dates=["date"])
    required = {"date", "ticker", "open", "high", "low", "close",
                "adjusted_close", "volume", "market_return", TARGET}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Input is missing columns: {sorted(missing)}")
    if df["ticker"].nunique() != 160:
        raise ValueError(f"Expected 160 tickers, found {df['ticker'].nunique()}")
    return df.sort_values(["ticker", "date"]).reset_index(drop=True)

def add_features(df):
    parts = []
    for ticker, g in df.groupby("ticker", sort=False):
        g = g.sort_values("date").copy()
        base = g["close"].replace(0, np.nan)
        g["open_rel"] = g["open"] / base - 1
        g["high_rel"] = g["high"] / base - 1
        g["low_rel"] = g["low"] / base - 1
        g["close_rel"] = g["close"] / base - 1
        g["adjusted_close_rel"] = g["adjusted_close"] / base - 1
        g["volume_log_change"] = np.log1p(g["volume"]).diff()
        parts.append(g)
    result = pd.concat(parts, ignore_index=True)
    result.replace([np.inf, -np.inf], np.nan, inplace=True)
    result.dropna(subset=FEATURES + [TARGET], inplace=True)
    return result.sort_values(["ticker", "date"]).reset_index(drop=True)

def make_sequences(df, scaler):
    buckets = {"train": [], "validation": [], "test": []}
    targets = {"train": [], "validation": [], "test": []}
    metadata = {"train": [], "validation": [], "test": []}
    train_end = pd.Timestamp(TRAIN_END)
    val_end = pd.Timestamp(VAL_END)

    for ticker, g in df.groupby("ticker", sort=False):
        g = g.sort_values("date").reset_index(drop=True)
        x = scaler.transform(g[FEATURES].to_numpy(dtype=np.float32))
        y = g[TARGET].to_numpy(dtype=np.float32)
        dates = pd.to_datetime(g["date"]).to_numpy()

        for end in range(LOOKBACK, len(g)):
            target_date = pd.Timestamp(dates[end])
            start = end - LOOKBACK
            if target_date <= train_end:
                split = "train"
            elif target_date <= val_end:
                split = "validation"
            else:
                split = "test"
            buckets[split].append(x[start:end])
            targets[split].append(y[end])
            metadata[split].append((ticker, str(target_date.date())))
    return buckets, targets, metadata

def main():
    df = add_features(load_data())
    dates = pd.to_datetime(df["date"])
    train_mask = dates <= pd.Timestamp(TRAIN_END)
    if not train_mask.any():
        raise ValueError("No training observations before TRAIN_END.")
    scaler = StandardScaler()
    scaler.fit(df.loc[train_mask, FEATURES].to_numpy(dtype=np.float32))

    x_parts, y_parts, meta = make_sequences(df, scaler)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for split in ("train", "validation", "test"):
        if not x_parts[split]:
            raise ValueError(f"No {split} sequences. Check date range and LOOKBACK.")
        X = np.asarray(x_parts[split], dtype=np.float32)
        y = np.asarray(y_parts[split], dtype=np.float32)
        np.savez_compressed(OUTPUT_DIR / f"{split}_sequences.npz", X=X, y=y)
        pd.DataFrame(meta[split], columns=["ticker", "target_date"]).to_csv(
            OUTPUT_DIR / f"{split}_metadata.csv", index=False
        )
        print(f"{split}: X={X.shape}, y={y.shape}")

    joblib.dump(scaler, OUTPUT_DIR / "feature_scaler.joblib")
    (OUTPUT_DIR / "feature_config.json").write_text(
        json.dumps({
            "lookback": LOOKBACK,
            "features": FEATURES,
            "target": TARGET,
            "train_end": TRAIN_END,
            "validation_end": VAL_END,
            "test_start": "2025-01-01",
            "data_type": "SYNTHETIC",
            "note": "Synthetic prototype data; not actual HOSE market observations."
        }, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print("Preprocessing complete. Scaler was fitted using training dates only.")

if __name__ == "__main__":
    main()

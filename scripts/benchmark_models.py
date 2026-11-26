"""
Benchmark models for HOSE Global LSTM V3.
Reads train/validation/test sequence arrays produced by prepare_data.py.
Models: Historical Mean, Naive (zero return), Linear Regression, Random Forest.
Features are summarized from each 60-day window to keep training practical.
All reported metrics are for synthetic prototype data, not real HOSE performance.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "simulation" / "processed"
OUTPUT_DIR = ROOT / "outputs" / "simulation"
MODEL_DIR = ROOT / "models" / "simulation"

def load_split(name):
    path = DATA_DIR / f"{name}_sequences.npz"
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path}. Run generate_hose_simulation.py and prepare_data.py first."
        )
    with np.load(path) as z:
        return z["X"], z["y"]

def summarize_windows(X):
    # X: samples x lookback x features
    last = X[:, -1, :]
    mean = X.mean(axis=1)
    std = X.std(axis=1)
    slope = (X[:, -1, :] - X[:, 0, :]) / max(X.shape[1] - 1, 1)
    return np.concatenate([last, mean, std, slope], axis=1).astype(np.float32)

def metrics(y_true, y_pred):
    return {
        "MAE_Return": float(mean_absolute_error(y_true, y_pred)),
        "RMSE_Return": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "Directional_Accuracy_pct": float(
            np.mean(np.sign(y_true) == np.sign(y_pred)) * 100
        ),
    }

def main():
    X_train, y_train = load_split("train")
    X_val, y_val = load_split("validation")
    X_test, y_test = load_split("test")

    # Validation is retained for model-development diagnostics; final metrics
    # below are calculated only on the chronological test set.
    F_train = summarize_windows(X_train)
    F_val = summarize_windows(X_val)
    F_test = summarize_windows(X_test)

    historical_mean = float(np.mean(y_train))
    predictions = {
        "Historical Mean": np.full(len(y_test), historical_mean, dtype=np.float32),
        "Naive (Zero Return)": np.zeros(len(y_test), dtype=np.float32),
    }

    linear = LinearRegression()
    linear.fit(F_train, y_train)
    predictions["Linear Regression"] = linear.predict(F_test).astype(np.float32)

    forest = RandomForestRegressor(
        n_estimators=120,
        max_depth=14,
        min_samples_leaf=5,
        max_features=0.7,
        n_jobs=-1,
        random_state=2027,
    )
    forest.fit(F_train, y_train)
    predictions["Random Forest"] = forest.predict(F_test).astype(np.float32)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    metric_rows, prediction_frames = [], []
    for name, pred in predictions.items():
        metric_rows.append({"Model": name, **metrics(y_test, pred)})
        prediction_frames.append(pd.DataFrame({
            "observation": np.arange(len(y_test)),
            "actual_return": y_test,
            "predicted_return": pred,
            "model": name,
        }))
    pd.DataFrame(metric_rows).to_csv(
        OUTPUT_DIR / "benchmark_metrics.csv", index=False, encoding="utf-8-sig"
    )
    pd.concat(prediction_frames, ignore_index=True).to_csv(
        OUTPUT_DIR / "benchmark_predictions.csv", index=False, encoding="utf-8-sig"
    )
    joblib.dump(linear, MODEL_DIR / "linear_regression.joblib")
    joblib.dump(forest, MODEL_DIR / "random_forest.joblib")

    print("BENCHMARK TRAINING COMPLETE")
    print(pd.DataFrame(metric_rows).to_string(index=False))
    print(f"Metrics: {OUTPUT_DIR / 'benchmark_metrics.csv'}")
    print("Note: test metrics describe synthetic prototype data only.")

if __name__ == "__main__":
    main()

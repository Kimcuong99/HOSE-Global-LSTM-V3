"""
Global LSTM training for HOSE Global LSTM V3.
Input: train_sequences.npz, validation_sequences.npz, test_sequences.npz
created by prepare_data.py.
Target: next-day log return.
IMPORTANT: all metrics from the included simulated dataset are illustrative only.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "simulation" / "processed"
MODEL_DIR = ROOT / "models" / "simulation"
OUTPUT_DIR = ROOT / "outputs" / "simulation"
SEED = 2027
EPOCHS = 35
BATCH_SIZE = 512

def load_split(name):
    path = DATA_DIR / f"{name}_sequences.npz"
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path}. Run generate_hose_simulation.py and prepare_data.py first."
        )
    with np.load(path) as data:
        return data["X"].astype("float32"), data["y"].astype("float32")

def build_model(input_shape):
    try:
        import tensorflow as tf
    except ImportError as exc:
        raise SystemExit(
            "TensorFlow is not installed. Use Python 3.12 and run: "
            "pip install tensorflow==2.18.0"
        ) from exc

    tf.keras.utils.set_random_seed(SEED)
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=input_shape),
        tf.keras.layers.LSTM(64, return_sequences=True),
        tf.keras.layers.Dropout(0.20),
        tf.keras.layers.LSTM(32),
        tf.keras.layers.Dropout(0.15),
        tf.keras.layers.Dense(16, activation="relu"),
        tf.keras.layers.Dense(1, name="predicted_next_day_log_return"),
    ])
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss="mse",
        metrics=[tf.keras.metrics.MeanAbsoluteError(name="mae")],
    )
    return model

def main():
    import tensorflow as tf
    tf.keras.utils.set_random_seed(SEED)

    X_train, y_train = load_split("train")
    X_val, y_val = load_split("validation")
    X_test, y_test = load_split("test")

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    model = build_model(X_train.shape[1:])
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=6, restore_best_weights=True
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=3, min_lr=1e-5
        ),
        tf.keras.callbacks.ModelCheckpoint(
            str(MODEL_DIR / "global_lstm_best.keras"),
            monitor="val_loss", save_best_only=True
        ),
    ]

    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        shuffle=True,
        callbacks=callbacks,
        verbose=1,
    )

    test_loss, test_mae = model.evaluate(X_test, y_test, verbose=0)
    pred = model.predict(X_test, batch_size=BATCH_SIZE, verbose=0).reshape(-1)
    rmse = float(np.sqrt(np.mean((y_test - pred) ** 2)))
    directional = float(np.mean(np.sign(y_test) == np.sign(pred)) * 100)

    model.save(MODEL_DIR / "global_lstm_final.keras")
    pd.DataFrame(history.history).to_csv(
        OUTPUT_DIR / "global_lstm_training_history.csv",
        index=False, encoding="utf-8-sig"
    )
    pd.DataFrame({
        "observation": np.arange(len(y_test)),
        "actual_return": y_test,
        "predicted_return": pred,
        "model": "Global LSTM",
    }).to_csv(
        OUTPUT_DIR / "global_lstm_predictions.csv",
        index=False, encoding="utf-8-sig"
    )

    result = {
        "model": "Global LSTM",
        "target": "next_day_return (log return)",
        "test_mae_return": float(test_mae),
        "test_rmse_return": rmse,
        "directional_accuracy_pct": directional,
        "test_loss_mse": float(test_loss),
        "epochs_completed": len(history.history.get("loss", [])),
        "data_type": "SYNTHETIC",
        "warning": "Metrics are from simulated prototype data, not real HOSE performance."
    }
    (OUTPUT_DIR / "global_lstm_metrics.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print("\nGLOBAL LSTM TRAINING COMPLETE")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("Model saved:", MODEL_DIR / "global_lstm_final.keras")

if __name__ == "__main__":
    main()

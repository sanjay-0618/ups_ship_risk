"""
ML Training Script — trains a RandomForestClassifier on historical shipments.
Uses temporal train/test split to avoid data leakage.

Run: python -m app.ml.train_model
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

import sys

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "generated"
MODEL_DIR = Path(__file__).resolve().parent.parent / "models"

FEATURE_COLUMNS = [
    "distance_km",
    "planned_duration_minutes",
    "weather_exposure",
    "traffic_exposure",
    "congestion_exposure",
    "transport_delay_minutes",
    "external_event_exposure",
    "historical_route_delay_rate",
    "number_of_stops",
    "number_of_handoffs",
    "weight_kg",
    "priority_encoded",
]
TARGET_COLUMN = "sla_breached"
PRIORITY_MAP = {"Low": 0, "Normal": 1, "High": 2, "Critical": 3}


def train():
    # ── Load data ─────────────────────────────────────────────────
    hist_path = DATA_DIR / "historical_shipments.csv"
    if not hist_path.exists():
        print("❌ historical_shipments.csv not found. Run: python -m app.data.generate_dataset first.")
        return

    print(f"📂 Loading {hist_path} ...")
    df = pd.read_csv(hist_path, low_memory=False)
    print(f"   Loaded {len(df):,} rows")

    # ── Feature engineering ───────────────────────────────────────
    df["priority_encoded"] = df["priority"].map(PRIORITY_MAP).fillna(1).astype(int)
    df["sla_breached"] = df["sla_breached"].astype(int)

    # Ensure all feature columns exist with defaults
    for col in FEATURE_COLUMNS:
        if col not in df.columns:
            df[col] = 0.0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df = df.dropna(subset=FEATURE_COLUMNS + [TARGET_COLUMN])
    print(f"   {len(df):,} rows after cleaning  |  SLA breach rate: {df[TARGET_COLUMN].mean():.1%}")

    # ── Temporal train/test split ─────────────────────────────────
    if "planned_date" in df.columns:
        df["planned_date"] = pd.to_datetime(df["planned_date"], errors="coerce")
        df = df.sort_values("planned_date")
        split_date = "2026-01-01"
        train_df = df[df["planned_date"] < split_date]
        test_df = df[df["planned_date"] >= split_date]
    else:
        # Fall back to 80/20 split
        split_idx = int(len(df) * 0.8)
        train_df = df.iloc[:split_idx]
        test_df = df.iloc[split_idx:]

    X_train = train_df[FEATURE_COLUMNS].values
    y_train = train_df[TARGET_COLUMN].values
    X_test = test_df[FEATURE_COLUMNS].values
    y_test = test_df[TARGET_COLUMN].values

    print(f"   Train: {len(X_train):,}  |  Test: {len(X_test):,}")

    # ── Train RandomForestClassifier ──────────────────────────────
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
    import joblib

    print("🌲 Training RandomForestClassifier ...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=12,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    # ── Evaluate ──────────────────────────────────────────────────
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    auc = roc_auc_score(y_test, y_prob) if len(set(y_test)) > 1 else 0.5

    print(f"\n📊 Model Metrics:")
    print(f"   Accuracy:  {acc:.4f}")
    print(f"   Precision: {prec:.4f}")
    print(f"   Recall:    {rec:.4f}")
    print(f"   F1 Score:  {f1:.4f}")
    print(f"   ROC-AUC:   {auc:.4f}")

    # Feature importances
    importances = sorted(zip(FEATURE_COLUMNS, model.feature_importances_), key=lambda x: -x[1])
    print(f"\n🔍 Top Feature Importances:")
    for feat, imp in importances[:5]:
        print(f"   {feat}: {imp:.3f}")

    # ── Save model and metrics ────────────────────────────────────
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODEL_DIR / "sla_model.joblib"
    joblib.dump(model, model_path)
    print(f"\n💾 Model saved → {model_path}")

    metrics = {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1, 4),
        "roc_auc": round(auc, 4),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "feature_columns": FEATURE_COLUMNS,
        "feature_importances": {f: round(float(i), 4) for f, i in importances},
    }
    metrics_path = MODEL_DIR / "model_metrics.json"
    with open(metrics_path, "w") as mf:
        json.dump(metrics, mf, indent=2)
    print(f"📈 Metrics saved → {metrics_path}")
    print("\n✅ Training complete!")
    return metrics


if __name__ == "__main__":
    train()

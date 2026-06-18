from pathlib import Path

import joblib
import numpy as np
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier

from app.core.db import Sample, SessionLocal


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "backend" / "app" / "models" / "dynamic_classifier.joblib"


def main() -> None:
    db = SessionLocal()
    rows = db.query(Sample).filter(Sample.mode == "dynamic").all()
    db.close()
    if not rows:
        raise SystemExit("No dynamic samples found. Collect data before training.")

    labels = sorted({row.label for row in rows})
    label_to_idx = {label: idx for idx, label in enumerate(labels)}
    x = np.asarray([np.asarray(row.feature, dtype=np.float32).reshape(-1) for row in rows])
    y = np.asarray([label_to_idx[row.label] for row in rows], dtype=np.int64)

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, stratify=y, random_state=42)
    model = MLPClassifier(hidden_layer_sizes=(256, 128), max_iter=500, random_state=42)
    model.fit(x_train, y_train)
    pred = model.predict(x_test)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "labels": labels}, OUT)
    print("accuracy:", accuracy_score(y_test, pred))
    print(classification_report(y_test, pred, target_names=labels))
    print("saved:", OUT)


if __name__ == "__main__":
    main()

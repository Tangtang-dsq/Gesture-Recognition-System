from pathlib import Path

import joblib
import numpy as np
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier

from app.core.config import settings
from app.core.dataset_files import load_static_feature_csv
from app.core.db import Sample, SessionLocal


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "backend" / "app" / "models" / "static_classifier.joblib"


def main() -> None:
    db = SessionLocal()
    rows = db.query(Sample).filter(Sample.mode == "static").all()
    db.close()
    if rows:
        labels = sorted({row.label for row in rows})
        label_to_idx = {label: idx for idx, label in enumerate(labels)}
        x = np.asarray([row.feature for row in rows], dtype=np.float32)
        y = np.asarray([label_to_idx[row.label] for row in rows], dtype=np.int64)
    else:
        loaded = load_static_feature_csv(settings.dataset_root)
        if loaded is None:
            raise SystemExit(
                "No static samples found. Collect data or set DATASET_ROOT to a folder containing "
                "features/static/gesture_data.csv."
            )
        x, y, labels = loaded

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, stratify=y, random_state=42)
    model = MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=500, random_state=42)
    model.fit(x_train, y_train)
    pred = model.predict(x_test)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "labels": labels}, OUT)
    print("accuracy:", accuracy_score(y_test, pred))
    print(classification_report(y_test, pred, target_names=labels))
    print("saved:", OUT)


if __name__ == "__main__":
    main()

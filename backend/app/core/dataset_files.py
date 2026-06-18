from pathlib import Path

import numpy as np


def load_static_feature_csv(dataset_root: Path) -> tuple[np.ndarray, np.ndarray, list[str]] | None:
    csv_path = dataset_root / "features" / "static" / "gesture_data.csv"
    if not csv_path.exists():
        return None

    rows = np.genfromtxt(csv_path, delimiter=",", dtype=str, encoding="utf-8", skip_header=1)
    if rows.size == 0:
        return None
    if rows.ndim == 1:
        rows = rows.reshape(1, -1)

    raw_labels = rows[:, 0]
    labels = sorted(set(raw_labels.tolist()))
    label_to_idx = {label: idx for idx, label in enumerate(labels)}
    x = rows[:, 1:].astype(np.float32)
    y = np.asarray([label_to_idx[label] for label in raw_labels], dtype=np.int64)
    return x, y, labels


def load_dynamic_feature_dirs(dataset_root: Path) -> tuple[np.ndarray, np.ndarray, list[str]] | None:
    base_dir = dataset_root / "features" / "dynamic"
    if not base_dir.exists():
        return None

    samples: list[np.ndarray] = []
    raw_labels: list[str] = []
    for label_dir in sorted(path for path in base_dir.iterdir() if path.is_dir()):
        for npy_path in sorted(label_dir.glob("*.npy")):
            seq = np.load(npy_path).astype(np.float32)
            samples.append(seq.reshape(-1))
            raw_labels.append(label_dir.name)

    if not samples:
        return None

    labels = sorted(set(raw_labels))
    label_to_idx = {label: idx for idx, label in enumerate(labels)}
    x = np.asarray(samples, dtype=np.float32)
    y = np.asarray([label_to_idx[label] for label in raw_labels], dtype=np.int64)
    return x, y, labels

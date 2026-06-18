from pathlib import Path

import joblib
import numpy as np

from app.core.config import settings


class StaticClassifier:
    def __init__(self, labels: tuple[str, ...], model=None) -> None:
        self.labels = labels
        self.model = model

    @classmethod
    def load(cls, path: Path | None = None) -> "StaticClassifier":
        model_path = path or settings.static_model_path
        if model_path.exists():
            payload = joblib.load(model_path)
            return cls(tuple(payload["labels"]), payload["model"])
        return cls(settings.static_labels)

    def predict(self, feature: np.ndarray) -> tuple[str, float]:
        if self.model is not None:
            probs = self.model.predict_proba(feature.reshape(1, -1))[0]
            idx = int(np.argmax(probs))
            return self.labels[idx], float(probs[idx])
        return self._rule_predict(feature)

    def _rule_predict(self, feature: np.ndarray) -> tuple[str, float]:
        points = feature.reshape(21, 3)
        wrist = points[0]
        tips = points[[4, 8, 12, 16, 20]]
        bases = points[[2, 5, 9, 13, 17]]
        extended = np.linalg.norm(tips[:, :2] - wrist[:2], axis=1) > np.linalg.norm(
            bases[:, :2] - wrist[:2], axis=1
        ) * 1.35
        count = int(extended.sum())

        if count >= 5:
            return "palm", 0.72
        if count == 0:
            return "fist", 0.72
        if extended[1] and extended[2] and not extended[3] and not extended[4]:
            return "peace", 0.7
        if extended[1] and count == 1:
            return "point", 0.68
        if extended[0] and count == 1:
            return "thumbs_up", 0.66
        return "unknown", 0.35

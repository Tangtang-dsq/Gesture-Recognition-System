from collections import deque
from dataclasses import dataclass, field
from pathlib import Path

import joblib
import numpy as np

from app.core.config import settings


@dataclass
class SessionContext:
    seq_len: int = settings.seq_len
    buffer: deque[np.ndarray] = field(default_factory=lambda: deque(maxlen=settings.seq_len))

    def reset(self) -> None:
        self.buffer.clear()


class DynamicClassifier:
    def __init__(self, labels: tuple[str, ...], model=None) -> None:
        self.labels = labels
        self.model = model

    @classmethod
    def load(cls, path: Path | None = None) -> "DynamicClassifier":
        model_path = path or settings.dynamic_model_path
        if model_path.exists():
            payload = joblib.load(model_path)
            return cls(tuple(payload["labels"]), payload["model"])
        return cls(settings.dynamic_labels)

    def update(self, ctx: SessionContext, feature: np.ndarray) -> tuple[str, float] | None:
        ctx.buffer.append(feature)
        if len(ctx.buffer) < ctx.seq_len:
            return None

        seq = np.stack(ctx.buffer)
        if self.model is not None:
            probs = self.model.predict_proba(seq.reshape(1, -1))[0]
            idx = int(np.argmax(probs))
            return self.labels[idx], float(probs[idx])
        return self._rule_predict(seq)

    def _rule_predict(self, seq: np.ndarray) -> tuple[str, float]:
        wrist_x = seq[:, 0]
        wrist_y = seq[:, 1]
        dx = float(wrist_x[-1] - wrist_x[0])
        dy = float(wrist_y[-1] - wrist_y[0])

        if abs(dx) > 1.2 and abs(dx) > abs(dy) * 1.4:
            return ("swipe_right" if dx > 0 else "swipe_left"), 0.7
        if abs(dy) > 1.2 and abs(dy) > abs(dx) * 1.4:
            return ("swipe_down" if dy > 0 else "swipe_up"), 0.7
        return "none", 0.7

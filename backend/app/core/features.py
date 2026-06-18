import numpy as np


def validate_feature(feature: list[float] | np.ndarray) -> np.ndarray:
    arr = np.asarray(feature, dtype=np.float32)
    if arr.shape != (63,):
        raise ValueError("feature must contain exactly 63 numeric values")
    if not np.isfinite(arr).all():
        raise ValueError("feature contains non-finite values")
    return arr


def normalize_landmarks(landmarks: list[dict[str, float]]) -> list[float]:
    if len(landmarks) != 21:
        raise ValueError("landmarks must contain exactly 21 points")

    wrist = landmarks[0]
    middle_base = landmarks[9]
    base = (
        (middle_base["x"] - wrist["x"]) ** 2
        + (middle_base["y"] - wrist["y"]) ** 2
        + (middle_base.get("z", 0.0) - wrist.get("z", 0.0)) ** 2
    ) ** 0.5
    base = base or 1e-6

    out: list[float] = []
    for point in landmarks:
        out.extend(
            [
                (point["x"] - wrist["x"]) / base,
                (point["y"] - wrist["y"]) / base,
                (point.get("z", 0.0) - wrist.get("z", 0.0)) / base,
            ]
        )
    return out

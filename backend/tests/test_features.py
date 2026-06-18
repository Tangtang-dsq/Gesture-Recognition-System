import pytest

from app.core.features import normalize_landmarks, validate_feature


def test_validate_feature_accepts_63_values():
    assert validate_feature([0.0] * 63).shape == (63,)


def test_validate_feature_rejects_wrong_length():
    with pytest.raises(ValueError):
        validate_feature([0.0] * 62)


def test_normalize_landmarks_is_scale_and_translation_invariant():
    landmarks = [{"x": float(i), "y": float(i % 5), "z": 0.1 * i} for i in range(21)]
    shifted_scaled = [
        {"x": point["x"] * 3 + 10, "y": point["y"] * 3 - 7, "z": point["z"] * 3 + 2}
        for point in landmarks
    ]

    assert normalize_landmarks(landmarks) == pytest.approx(normalize_landmarks(shifted_scaled))

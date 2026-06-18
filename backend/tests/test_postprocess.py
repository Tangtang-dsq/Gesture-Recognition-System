from app.core.postprocess import Stabilizer


def test_stabilizer_requires_votes():
    stabilizer = Stabilizer(threshold=0.5, vote_n=3, vote_min=2, cooldown_seconds=0)
    assert stabilizer.stabilize("palm", 0.8) is None
    assert stabilizer.stabilize("palm", 0.8) == "palm"


def test_stabilizer_filters_low_confidence():
    stabilizer = Stabilizer(threshold=0.7, vote_n=3, vote_min=1, cooldown_seconds=0)
    assert stabilizer.stabilize("palm", 0.6) is None

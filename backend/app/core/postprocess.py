import time
from collections import Counter, deque


class Stabilizer:
    def __init__(
        self,
        threshold: float,
        vote_n: int,
        vote_min: int,
        cooldown_seconds: float,
    ) -> None:
        self.threshold = threshold
        self.vote_min = vote_min
        self.votes: deque[str] = deque(maxlen=vote_n)
        self.cooldown_seconds = cooldown_seconds
        self.last_label: str | None = None
        self.last_triggered_at = 0.0

    def stabilize(self, label: str | None, confidence: float) -> str | None:
        if not label or label == "unknown" or confidence < self.threshold:
            self.votes.clear()
            return None

        self.votes.append(label)
        winner, count = Counter(self.votes).most_common(1)[0]
        if count < self.vote_min:
            return None

        now = time.monotonic()
        if winner == self.last_label and now - self.last_triggered_at < self.cooldown_seconds:
            return None

        self.last_label = winner
        self.last_triggered_at = now
        return winner


class StaticStabilizer:
    def __init__(self, threshold: float, vote_n: int, vote_min: int) -> None:
        self.threshold = threshold
        self.vote_min = vote_min
        self.votes: deque[str] = deque(maxlen=vote_n)

    def stabilize(self, label: str | None, confidence: float) -> str | None:
        if not label or label == "unknown" or confidence < self.threshold:
            self.votes.clear()
            return None

        self.votes.append(label)
        winner, count = Counter(self.votes).most_common(1)[0]
        if count < self.vote_min:
            return None
        return winner

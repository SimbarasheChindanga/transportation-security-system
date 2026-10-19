"""Threshold-based driver behaviour analysis for synthetic or supplied telemetry."""
from __future__ import annotations

import pandas as pd


class BehaviorAnalyzer:
    """Detect speeding, harsh braking and cornering using documented units."""

    def __init__(self, speed_limit: float = 60, braking_threshold: float = -3.0, cornering_threshold: float = 2.0):
        if speed_limit <= 0:
            raise ValueError("speed_limit must be positive")
        if braking_threshold >= 0:
            raise ValueError("braking_threshold must be negative (m/s²)")
        if cornering_threshold <= 0:
            raise ValueError("cornering_threshold must be positive")
        self.speed_limit = float(speed_limit)
        self.braking_threshold = float(braking_threshold)
        self.cornering_threshold = float(cornering_threshold)

    def detect_speeding(self, speed: float) -> tuple[bool, float]:
        over_limit = float(speed) - self.speed_limit
        return (True, over_limit) if speed > self.speed_limit * 1.1 else (False, 0.0)

    def detect_harsh_braking(self, acceleration: float) -> tuple[bool, float]:
        return (True, abs(float(acceleration))) if acceleration < self.braking_threshold else (False, 0.0)

    def detect_harsh_cornering(self, lateral_accel: float) -> tuple[bool, float]:
        return (True, abs(float(lateral_accel))) if abs(lateral_accel) > self.cornering_threshold else (False, 0.0)

    @staticmethod
    def calculate_driver_score(speed_violations: int, braking_violations: int, cornering_violations: int) -> int:
        if min(speed_violations, braking_violations, cornering_violations) < 0:
            raise ValueError("Violation counts cannot be negative")
        return max(0, min(100, 100 - speed_violations * 5 - braking_violations * 3 - cornering_violations * 2))

    @staticmethod
    def get_score_rating(score: float) -> tuple[str, str]:
        if score >= 90: return "⭐ Excellent", "green"
        if score >= 70: return "👍 Good", "blue"
        if score >= 50: return "⚠️ Needs Improvement", "orange"
        return "🚨 Unsafe", "red"

    def analyze_driver(self, df: pd.DataFrame) -> dict:
        required = {"speed", "acceleration"}
        missing = required.difference(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
        if not ("lateral_accel" in df.columns or "harsh_cornering" in df.columns):
            raise ValueError("DataFrame must contain lateral_accel or harsh_cornering")
        if df.empty:
            raise ValueError("Cannot analyze an empty DataFrame")

        speeding = sum(self.detect_speeding(v)[0] for v in df["speed"].fillna(0))
        braking = sum(self.detect_harsh_braking(v)[0] for v in df["acceleration"].fillna(0))
        if "lateral_accel" in df.columns:
            cornering = sum(self.detect_harsh_cornering(v)[0] for v in df["lateral_accel"].fillna(0))
        else:
            cornering = sum(float(v) > self.cornering_threshold for v in df["harsh_cornering"].fillna(0))
        score = self.calculate_driver_score(speeding, braking, cornering)
        rating, color = self.get_score_rating(score)
        return {"speeding_events": int(speeding), "braking_events": int(braking), "cornering_events": int(cornering),
                "total_violations": int(speeding + braking + cornering), "score": score, "rating": rating, "color": color}

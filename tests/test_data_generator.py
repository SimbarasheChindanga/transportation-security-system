from pathlib import Path

import pandas as pd
import pytest

from src.data_collection.data_generator import generate_gps_data, generate_driver_data, save_driver_data, load_driver_data
from src.behavior_analysis.behavior_analyzer import BehaviorAnalyzer


def test_gps_generation_is_reproducible_and_has_expected_columns():
    a = generate_gps_data(50, seed=7)
    b = generate_gps_data(50, seed=7)
    pd.testing.assert_frame_equal(a, b)
    assert len(a) == 50
    assert {"timestamp", "speed", "latitude", "longitude", "acceleration", "braking"}.issubset(a.columns)
    assert a["speed"].between(0, 120).all()


def test_gps_generation_rejects_invalid_size():
    with pytest.raises(ValueError):
        generate_gps_data(0)


@pytest.mark.parametrize("style", ["safe", "normal", "aggressive", "unsafe"])
def test_driver_generation_schema_and_units(style):
    df = generate_driver_data(3, style, 100, seed=11)
    assert len(df) == 100
    assert df["driving_style"].eq(style).all()
    assert df["speed"].between(0, 95).all()
    assert df["acceleration"].notna().all()
    assert "lateral_accel" in df.columns
    assert (df["harsh_braking"] >= 0).all()


def test_driver_generation_rejects_unknown_style():
    with pytest.raises(ValueError):
        generate_driver_data(1, "reckless", 10)


def test_save_and_load_round_trip(tmp_path):
    original = generate_driver_data(2, "normal", 10, seed=1)
    saved = save_driver_data(original, "sample.csv", output_dir=tmp_path)
    assert saved.exists()
    loaded = load_driver_data("sample.csv", input_dir=tmp_path)
    assert len(loaded) == len(original)
    assert list(loaded.columns) == list(original.columns)


def test_speeding_braking_cornering_thresholds():
    analyzer = BehaviorAnalyzer()
    assert analyzer.detect_speeding(67)[0] is True
    assert analyzer.detect_speeding(66)[0] is False
    assert analyzer.detect_harsh_braking(-3.1)[0] is True
    assert analyzer.detect_harsh_braking(-3.0)[0] is False
    assert analyzer.detect_harsh_cornering(-2.1)[0] is True
    assert analyzer.detect_harsh_cornering(2.0)[0] is False


def test_score_formula_and_rating():
    analyzer = BehaviorAnalyzer()
    assert analyzer.calculate_driver_score(2, 1, 2) == 83
    assert analyzer.calculate_driver_score(100, 100, 100) == 0
    assert analyzer.get_score_rating(95)[0] == "⭐ Excellent"
    assert analyzer.get_score_rating(30)[0] == "🚨 Unsafe"


def test_analyze_driver_counts_events_and_score():
    df = pd.DataFrame({
        "speed": [70, 60, 80],
        "acceleration": [-4, -1, -3.5],
        "lateral_accel": [0.5, 2.5, -3.0],
    })
    result = BehaviorAnalyzer().analyze_driver(df)
    assert result["speeding_events"] == 2
    assert result["braking_events"] == 2
    assert result["cornering_events"] == 2
    assert result["total_violations"] == 6
    assert result["score"] == 80


def test_analyzer_rejects_missing_columns():
    with pytest.raises(ValueError, match="Missing required columns"):
        BehaviorAnalyzer().analyze_driver(pd.DataFrame({"speed": [10]}))

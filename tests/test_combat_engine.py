"""
Tests for the pure combat probability engine.

The engine has no real-world ground truth, so these tests assert the
*invariants the design promises* (every probability stays in range, no
function crashes on edge inputs, advantages move the odds the right way)
rather than exact magic numbers.
"""

import math

import pytest

import combat_engine as ce


# ---------------------------------------------------------------------------
# Fixtures: two representative airframes on the same numeric scales the GUI
# feeds the engine (radar ~0-10, missile/ew/maneuver/stealth in [0, 1]).
# ---------------------------------------------------------------------------
STEALTH_JET = {
    "name": "Test Raptor",
    "rcs": 0.001,
    "radar": 9.0,
    "missile": 0.9,
    "ew": 0.85,
    "maneuver": 0.9,
    "stealth": 0.95,
    "range": 1800.0,
    "speed": 2600.0,
    "ceiling": 20000.0,
}

LEGACY_JET = {
    "name": "Test Fishbed",
    "rcs": 5.0,
    "radar": 4.0,
    "missile": 0.4,
    "ew": 0.3,
    "maneuver": 0.45,
    "stealth": 0.15,
    "range": 900.0,
    "speed": 2100.0,
    "ceiling": 15000.0,
}

MISSIONS_VS_DEFENDER = [
    ce.p_bvr,
    ce.p_air_combat,
    ce.p_air_defense,
    ce.p_interception,
    ce.p_electronic_warfare,
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def test_logistic_is_overflow_safe_at_extremes():
    # Regression: math.exp used to OverflowError on large-magnitude inputs.
    for x in (-1000, 1000):
        y = ce.logistic(x)
        assert 0.0 <= y <= 1.0


def test_logistic_open_interval_for_moderate_inputs():
    for x in (-5, -1, 0, 1, 5):
        y = ce.logistic(x)
        assert 0.0 < y < 1.0


def test_logistic_is_monotonic_increasing():
    assert ce.logistic(-1) < ce.logistic(0) < ce.logistic(1)


def test_logistic_midpoint_is_half():
    assert ce.logistic(0.0, midpoint=0.0) == pytest.approx(0.5)


@pytest.mark.parametrize(
    "raw, expected",
    [("4", 4.0), ("5", 5.0), ("4.5", 4.5), ("4+", 4.33), ("4++", 4.66)],
)
def test_parse_generation(raw, expected):
    assert ce.parse_generation(raw) == pytest.approx(expected)


def test_detection_range_factor_grows_with_rcs():
    assert ce.detection_range_factor(0.001) < ce.detection_range_factor(5.0)


def test_detection_range_factor_handles_zero_rcs():
    # Clamped to 1e-6 internally; must not raise or return 0.
    assert ce.detection_range_factor(0.0) > 0.0


# ---------------------------------------------------------------------------
# Sub-probabilities stay in [0, 1]
# ---------------------------------------------------------------------------
def test_sub_probabilities_in_unit_interval():
    assert 0.0 <= ce.p_detect_first(STEALTH_JET, LEGACY_JET) <= 1.0
    assert 0.0 <= ce.p_valid_shot(STEALTH_JET, 150) <= 1.0
    assert 0.0 <= ce.p_hit(STEALTH_JET) <= 1.0
    assert 0.0 <= ce.p_survive(STEALTH_JET, LEGACY_JET) <= 1.0


def test_stealth_jet_detects_legacy_first():
    """A low-RCS, strong-radar jet should win the first-look more often."""
    atk = ce.p_detect_first(STEALTH_JET, LEGACY_JET)
    defn = ce.p_detect_first(LEGACY_JET, STEALTH_JET)
    assert atk > defn


# ---------------------------------------------------------------------------
# Mission models: result contract (final + sub-factors all in 0..100)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("mission_fn", MISSIONS_VS_DEFENDER)
def test_mission_results_in_percent_range(mission_fn):
    result = mission_fn(STEALTH_JET, LEGACY_JET)
    assert "final" in result
    for key, value in result.items():
        assert 0.0 <= value <= 100.0, f"{mission_fn.__name__}[{key}] = {value}"


def test_recon_result_in_percent_range():
    result = ce.p_recon(STEALTH_JET)
    assert "final" in result
    for value in result.values():
        assert 0.0 <= value <= 100.0


@pytest.mark.parametrize("mission_fn", MISSIONS_VS_DEFENDER)
@pytest.mark.parametrize("distance", ["Short", "Medium", "Long", "Unknown"])
def test_missions_handle_any_distance_without_crashing(mission_fn, distance):
    """Regression: p_interception used to KeyError on unexpected distances."""
    result = mission_fn(STEALTH_JET, LEGACY_JET, distance=distance)
    assert 0.0 <= result["final"] <= 100.0


@pytest.mark.parametrize("weather", ["Clear", "Cloudy", "Rain", "Hurricane"])
def test_unknown_weather_defaults_to_clear_multiplier(weather):
    result = ce.p_bvr(STEALTH_JET, LEGACY_JET, weather=weather)
    assert 0.0 <= result["final"] <= 100.0


def test_bad_weather_never_helps():
    clear = ce.p_bvr(STEALTH_JET, LEGACY_JET, weather="Clear")["final"]
    rain = ce.p_bvr(STEALTH_JET, LEGACY_JET, weather="Rain")["final"]
    assert rain <= clear

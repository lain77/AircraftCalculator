"""
Physics-based combat probability engine for the Air Combat Simulator.

Design principles
-----------------
1. Detection follows the radar range equation: R_detect ~ (RCS)^0.25.
   A 10,000x smaller RCS shrinks detection range only ~10x, not to zero.
2. Every sub-probability is bounded to [0, 1] by a logistic function,
   so a single weak stat never collapses the whole result to 0%.
3. Mission outcome = chain of INDEPENDENT probabilities (detect first,
   valid shot, hit, survive), combined multiplicatively only AFTER each
   term is a well-behaved probability in (0, 1).
"""

import math


# ===========================================================================
# CALIBRATION KNOBS  — tune these against your own domain knowledge.
# You built the dataset; you know these matchups better than any formula.
# Each `steepness` controls how sharply an advantage tips the odds;
# each `midpoint` sets where the 50/50 line sits.
# ---------------------------------------------------------------------------
DETECT_STEEPNESS = 2.2     # higher = first-look advantage matters more
HIT_MIDPOINT = 0.5         # missile+EW quality needed for 50% hit chance
HIT_STEEPNESS = 6.0
SURVIVE_MIDPOINT = -0.2    # negative = defender slightly favored by default
SURVIVE_STEEPNESS = 3.0
RECON_STEALTH_MIDPOINT = 0.45   # stealth score for 50% recon survivability
RECON_STEALTH_STEEPNESS = 8.0
# ===========================================================================


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def logistic(x, midpoint=0.0, steepness=1.0):
    """Maps any real number to (0, 1). Never returns exactly 0 or 1."""
    return 1.0 / (1.0 + math.exp(-steepness * (x - midpoint)))


def parse_generation(value):
    """'4++' -> 4.66, '4+' -> 4.33, '4.5' -> 4.5, '5' -> 5.0."""
    s = str(value).strip()
    if s.endswith("++"):
        return float(s[:-2]) + 0.66
    if s.endswith("+"):
        return float(s[:-1]) + 0.33
    return float(s)


def detection_range_factor(rcs):
    """
    Relative detection range from the radar range equation: R ~ RCS^(1/4).
    Returns a value normalized so a 1 m^2 reference target = 1.0.
    Stealth aircraft (RCS << 1) get a small factor; large RCS gets a big one.
    """
    rcs = max(rcs, 1e-6)
    return rcs ** 0.25


# ---------------------------------------------------------------------------
# Sub-probabilities (each in 0..1)
# ---------------------------------------------------------------------------
def p_detect_first(attacker, defender):
    """
    Probability the attacker detects the defender before being detected.

    Radar range equation: a radar of quality Q detects a target of signature
    RCS at range ~ Q * RCS^(1/4). The attacker detects first when its
    detection range on the defender exceeds the defender's detection range
    on the attacker.
    """
    # Range at which attacker sees defender (high = attacker detects far away)
    atk_sees = attacker["radar"] * detection_range_factor(defender["rcs"])
    # Range at which defender sees attacker (high = bad for attacker)
    def_sees = defender["radar"] * detection_range_factor(attacker["rcs"])

    # Log ratio: positive => attacker has the first-look advantage
    advantage = math.log10((atk_sees + 1e-9) / (def_sees + 1e-9))
    return logistic(advantage, midpoint=0.0, steepness=DETECT_STEEPNESS)


def p_valid_shot(attacker, distance_km):
    """Probability the engagement geometry allows a valid missile shot."""
    # Use combat radius as a proxy for reach/persistence; longer-legged
    # jets sustain favorable geometry better.
    reach = attacker["range"] / 1500.0  # ~1500 km is a typical reference
    geom = reach - (distance_km / 150.0)  # 150 km reference BVR distance
    return logistic(geom, midpoint=0.0, steepness=1.2)


def p_hit(attacker):
    """Probability a launched missile hits, from missile quality + EW edge."""
    quality = attacker["missile"] * 0.7 + attacker["ew"] * 0.3
    return logistic(quality, midpoint=HIT_MIDPOINT, steepness=HIT_STEEPNESS)


def p_survive(attacker, defender):
    """Probability of surviving the counter-engagement."""
    edge = (
        (attacker["maneuver"] - defender["maneuver"]) * 0.5
        + (attacker["stealth"] - defender["stealth"]) * 0.5
        + (attacker["ew"] - defender["ew"]) * 0.3
    )
    return logistic(edge, midpoint=SURVIVE_MIDPOINT, steepness=SURVIVE_STEEPNESS)


# ---------------------------------------------------------------------------
# Mission models
# ---------------------------------------------------------------------------
def p_bvr(attacker, defender, weather="Clear", distance="Long"):
    """BVR engagement: chain of independent probabilities."""
    distance_km = {"Short": 30, "Medium": 80, "Long": 150}.get(distance, 150)
    weather_mult = {"Clear": 1.0, "Cloudy": 0.95, "Rain": 0.88}.get(weather, 1.0)

    detect = p_detect_first(attacker, defender)
    shot = p_valid_shot(attacker, distance_km)
    hit = p_hit(attacker)
    survive = p_survive(attacker, defender)

    kill = detect * shot * hit * survive * weather_mult
    return {
        "final": round(kill * 100, 1),
        "detect_first": round(detect * 100, 1),
        "valid_shot": round(shot * 100, 1),
        "hit": round(hit * 100, 1),
        "survive": round(survive * 100, 1),
    }


def p_air_combat(attacker, defender, weather="Clear", distance="Medium"):
    """WVR/merge-leaning combat: maneuver and survivability weighted higher."""
    weather_mult = {"Clear": 1.0, "Cloudy": 0.96, "Rain": 0.9}.get(weather, 1.0)
    detect = p_detect_first(attacker, defender)
    survive = p_survive(attacker, defender)
    maneuver_edge = logistic(
        attacker["maneuver"] - defender["maneuver"], midpoint=0.0, steepness=4.0
    )
    hit = p_hit(attacker)
    kill = (0.25 * detect + 0.75 * maneuver_edge) * hit * survive * weather_mult
    return {
        "final": round(kill * 100, 1),
        "detect_first": round(detect * 100, 1),
        "maneuver_edge": round(maneuver_edge * 100, 1),
        "hit": round(hit * 100, 1),
        "survive": round(survive * 100, 1),
    }


def p_interception(attacker, defender, weather="Clear", distance="Long"):
    """Interception: speed + ceiling + radar reach dominate."""
    weather_mult = {"Clear": 1.0, "Cloudy": 0.95, "Rain": 0.9}.get(weather, 1.0)
    speed_edge = logistic(
        (attacker["speed"] - 2200) / 400.0, midpoint=0.0, steepness=2.0
    )
    reach = p_detect_first(attacker, defender)
    shot = p_valid_shot(attacker, {"Short": 30, "Medium": 80, "Long": 150}[distance])
    kill = (0.4 * speed_edge + 0.6 * reach) * shot * weather_mult
    return {
        "final": round(kill * 100, 1),
        "speed_edge": round(speed_edge * 100, 1),
        "detect_first": round(reach * 100, 1),
        "valid_shot": round(shot * 100, 1),
    }


def p_recon(attacker, weather="Clear", distance="Long"):
    """
    Strategic recon (single-platform survivability + coverage).
    Bounded so low stealth still yields a non-zero, low number
    instead of collapsing to 0.
    """
    weather_mult = {"Clear": 1.0, "Cloudy": 0.9, "Rain": 0.8}.get(weather, 1.0)
    # Survivability over hostile airspace: stealth is the dominant gate,
    # ceiling and speed only help if you can avoid detection in the first place.
    stealth_term = logistic(attacker["stealth"], midpoint=RECON_STEALTH_MIDPOINT, steepness=RECON_STEALTH_STEEPNESS)
    ceiling_term = logistic(
        (attacker["ceiling"] - 16000) / 2500.0, midpoint=0.0, steepness=2.0
    )
    coverage = logistic((attacker["range"] - 1500) / 800.0, midpoint=0.0, steepness=1.5)

    # Stealth gates survivability multiplicatively; a non-stealth jet over
    # defended airspace is attrited regardless of how high it flies.
    survive = (stealth_term ** 1.5) * (0.6 + 0.4 * ceiling_term)
    success = survive * coverage * weather_mult
    return {
        "final": round(success * 100, 1),
        "stealth_survive": round(stealth_term * 100, 1),
        "ceiling": round(ceiling_term * 100, 1),
        "coverage": round(coverage * 100, 1),
    }


def p_air_defense(attacker, defender, weather="Clear", distance="Medium"):
    """Defensive CAP: blend of BVR detection and survivability."""
    bvr = p_bvr(attacker, defender, weather, distance)
    survive = p_survive(attacker, defender)
    final = 0.6 * (bvr["final"] / 100.0) + 0.4 * survive
    return {
        "final": round(final * 100, 1),
        "detect_first": bvr["detect_first"],
        "hit": bvr["hit"],
        "survive": round(survive * 100, 1),
    }


def p_electronic_warfare(attacker, defender, weather="Clear", distance="Long"):
    """EW mission: EW score vs defender radar/EW."""
    weather_mult = {"Clear": 1.0, "Cloudy": 0.97, "Rain": 0.95}.get(weather, 1.0)
    jam_edge = logistic(
        attacker["ew"] - (defender["radar"] / 10.0) * 0.5, midpoint=0.3, steepness=4.0
    )
    survive = p_survive(attacker, defender)
    final = jam_edge * survive * weather_mult
    return {
        "final": round(final * 100, 1),
        "jam_edge": round(jam_edge * 100, 1),
        "survive": round(survive * 100, 1),
    }
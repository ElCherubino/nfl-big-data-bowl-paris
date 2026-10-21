import math

import pytest

from rb_lifeline.config import merged_parameters
from rb_lifeline.metrics import evaluate_play, normalize_play_direction, rb_checks_at


PEOPLE = [{"nflId": "q", "officialPosition": "QB", "pff_role": "Pass"},
          {"nflId": "b", "officialPosition": "RB", "pff_role": " Pass   Route "},
          {"nflId": "d", "officialPosition": "CB", "pff_role": "Coverage"}]


def rows(end_event="pass_forward", pressure=True):
    result = []
    for frame in range(1, 5):
        for i, x, y, o in [("q", 40, 20, 90), ("b", 43, 20, 270),
                           ("d", 42 if pressure and frame >= 3 else 50, 20, 0),
                           (None, 40, 20, None)]:
            result.append({"nflId": i, "frameId": frame, "team": "football" if i is None else "A",
                           "x": x, "y": y, "o": o, "playDirection": "right",
                           "event": "ball_snap" if frame == 1 else end_event if frame == 4 else "None"})
    return result


def evaluate(tracking=None, people=None, **params):
    return evaluate_play({"playId": 7, "passResult": "C"}, PEOPLE if people is None else people,
                         rows() if tracking is None else tracking, params)


def checks(rb=(43, 20, 270), qb=(40, 20, 90), defender=(48, 20, 0), los=40, role="route"):
    return rb_checks_at("b", role, {"b": rb, "q": qb, "d": defender}, "q", ["d"], los, merged_parameters())


def test_fixed_pressure_matches_replay_and_defender_coverage_counts():
    result = evaluate()
    assert result["events"]["pressureFrameId"] == 3
    assert result["pressure"]["distanceYd"] == 2
    assert result["pressure"]["timeS"] == .2
    observation = result["observations"][0]
    state = result["frames"][2]["rbStates"][0]
    assert observation["status"] == state["status"] == "unavailable"
    assert observation["checks"] == state["checks"]
    assert observation["counted"]


@pytest.mark.parametrize("distance,passed", [(2.5, False), (2.50001, True), (2.49999, False)])
def test_open_strict_boundary(distance, passed):
    assert checks(defender=(43 + distance, 20, 0))["checks"]["open"]["passed"] is passed


@pytest.mark.parametrize("distance,passed", [(15, False), (14.99999, True), (15.00001, False)])
def test_qb_range_strict_boundary(distance, passed):
    assert checks(qb=(43 - distance, 20, 0))["checks"]["inRange"]["passed"] is passed


@pytest.mark.parametrize("progress,passed", [(-1, True), (-1.00001, False), (-.99999, True)])
def test_los_inclusive_boundary(progress, passed):
    assert checks(los=43 - progress)["checks"]["pastLine"]["passed"] is passed


@pytest.mark.parametrize("orientation,passed", [(180, False), (180.00001, True), (179.99999, False)])
def test_facing_strict_boundary(orientation, passed):
    assert checks(rb=(43, 20, orientation))["checks"]["facingQb"]["passed"] is passed


def test_angle_wrap_and_missing_orientation_never_uses_dir():
    bearing = math.radians(1)
    state = checks(rb=(43, 20, 359), qb=(43 + math.sin(bearing), 20 + math.cos(bearing), 0))
    assert state["checks"]["facingQb"]["value"] == pytest.approx(2)
    assert checks(rb=(43, 20, None))["status"] == "unknown"
    assert checks(rb=(43, 20, None), defender=(44, 20, 0))["status"] == "unavailable"


def test_rotation_preserves_all_measurements_and_verdict():
    original = rows()
    left = [{**row, "x": 120 - row["x"], "y": 53.3 - row["y"],
             "o": (row["o"] + 180) % 360 if row["o"] is not None else None,
             "playDirection": "left"} for row in original]
    a, b = evaluate(original), evaluate(left)
    assert a["observations"] == b["observations"]
    assert normalize_play_direction({"x": 10, "y": 5, "o": 359, "playDirection": "left"}) == (110, 48.3, 179)


@pytest.mark.parametrize("event,kind", [("autoevent_passforward", "throw"), ("qb_sack", "sack"),
                                       ("qb_strip_sack", "sack"), ("run", "scramble")])
def test_ending_aliases(event, kind):
    assert evaluate(rows(end_event=event))["events"]["endKind"] == kind


def test_pressure_after_throw_excluded_and_no_pressure_still_replays():
    tracking = rows(pressure=False)
    tracking.extend({**r, "frameId": 5, "event": "None", "x": 41 if r["nflId"] == "d" else r["x"]}
                    for r in rows()[-4:])
    result = evaluate(tracking)
    assert result["pressure"]["status"] == "none"
    assert result["collectiveVerdict"] == "not_applicable"
    assert len(result["frames"]) == 4
    assert result["frames"][1]["rbStates"]
    assert not result["observations"][0]["counted"]


@pytest.mark.parametrize("gap", ["frame", "defender", "qb"])
def test_gap_before_observed_pressure_is_not_counted(gap):
    tracking = [r for r in rows() if not (r["frameId"] == 2 and
                (gap == "frame" or r["nflId"] == {"defender": "d", "qb": "q"}.get(gap)))]
    result = evaluate(tracking)
    assert result["pressure"]["status"] == "detected"
    assert "incomplete_first_pressure_tracking" in result["quality"]["reasons"]
    assert not result["observations"][0]["counted"]


def test_absent_snap_end_ball_and_defenders_are_explicit():
    for tracking, people, reason in [
        ([{**r, "event": "None"} for r in rows()], PEOPLE, "missing_snap"),
        ([{**r, "event": "ball_snap" if r["frameId"] == 1 else "None"} for r in rows()], PEOPLE, "missing_end_event"),
        ([r for r in rows() if r["nflId"] is not None], PEOPLE, "missing_ball_at_snap"),
        (rows(), PEOPLE[:2], "missing_defenders"),
    ]:
        result = evaluate(tracking, people)
        assert reason in result["quality"]["reasons"]
        if reason != "missing_ball_at_snap":
            assert not result["quality"]["countable"]


def test_blocking_back_is_gray_and_multiple_routes_collective_once():
    people = PEOPLE + [{"nflId": "b2", "officialPosition": "FB", "pff_role": "Pass Block"}]
    result = evaluate(people=people)
    assert result["observations"][1]["status"] == "blocking"
    assert not result["observations"][1]["counted"]
    assert all(f["rbStates"][1]["status"] == "blocking" for f in result["frames"])
    people[-1]["pff_role"] = "Pass Route"
    tracking = rows() + [{**r, "nflId": "b2", "x": 45, "y": 25, "o": 225}
                         for r in rows() if r["nflId"] == "b"]
    result = evaluate(tracking, people)
    assert len(result["observations"]) == 2
    assert result["collectiveVerdict"] == "available"


def test_precision_not_rounded_before_threshold_check():
    tracking = rows()
    for r in tracking:
        if r["nflId"] == "d":
            r["x"] = 42.000001
    result = evaluate(tracking)
    assert result["frames"][0]["entities"][2]["x"] == 42
    assert result["pressure"]["status"] == "none"


def test_pandas_inputs_supported():
    pd = pytest.importorskip("pandas")
    assert evaluate_play({"playId": "7"}, pd.DataFrame(PEOPLE), pd.DataFrame(rows()))["events"]["pressureFrameId"] == 3

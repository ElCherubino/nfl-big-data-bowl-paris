"""One precise evaluator for replay colours and fixed first-pressure verdicts.

Inputs are raw source records (or pandas tables); no interpolation is performed.
Only rendered coordinates are rounded. All football checks use source precision.
"""
from collections import defaultdict
import math

from .config import merged_parameters


def _records(value):
    return value.to_dict("records") if hasattr(value, "to_dict") else list(value)


def _number(value):
    try:
        number = float(value)
        return number if math.isfinite(number) else None
    except (ValueError, TypeError):
        return None


def _id(value):
    if value is None or str(value).lower() in {"nan", "na", "none", ""}:
        return None
    text = str(value)
    return text[:-2] if text.endswith(".0") else text


def normalize_role(value):
    key = " ".join(str(value or "").lower().replace("_", " ").split())
    return {"pass": "passer", "passer": "passer", "pass route": "route",
            "route": "route", "pass block": "blocking", "blocking": "blocking",
            "pass rush": "rusher", "rusher": "rusher", "coverage": "coverage"}.get(key, "unknown")


def normalize_play_direction(row, direction=None):
    """Return normalized x/y/o without rounding or substituting movement dir."""
    x, y, o = (_number(row.get(key)) for key in ("x", "y", "o"))
    if str(direction or row.get("playDirection", "")).lower() == "left":
        x = 120.0 - x if x is not None else None
        y = 53.3 - y if y is not None else None
        o = (o + 180.0) % 360 if o is not None else None
    elif o is not None:
        o %= 360
    return x, y, o


def _distance(a, b):
    if a is None or b is None or None in a[:2] or None in b[:2]:
        return None
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _check(value, passed=None, reason=None):
    return {"passed": passed, "value": value, "reason": reason}


def rb_checks_at(back_id, role, positions, qb_id, defender_ids, los_x, parameters):
    """Evaluate all checks once; used identically for every replay frame."""
    rb, qb = positions.get(back_id), positions.get(qb_id)
    ds = [_distance(rb, positions.get(i)) for i in defender_ids]
    known = [d for d in ds if d is not None]
    nearest = min(known) if known else None
    complete = bool(ds) and len(known) == len(ds)
    open_pass = None
    if nearest is not None and nearest <= parameters["openDistanceYd"]:
        open_pass = False
    elif complete:
        open_pass = True
    qb_distance = _distance(rb, qb)
    progress = rb[0] - los_x if rb and rb[0] is not None and los_x is not None else None
    angle = None
    if qb_distance is not None and rb[2] is not None:
        bearing = math.degrees(math.atan2(qb[0] - rb[0], qb[1] - rb[1])) % 360
        angle = abs((rb[2] - bearing + 180) % 360 - 180)
    route = True if role == "route" else False if role == "blocking" else None
    facing_limit = parameters["maxFacingAngleDeg"]
    checks = {
        "routeRunner": _check(route, route, "unknown_role" if route is None else None),
        "open": _check(nearest if complete or open_pass is False else None, open_pass,
                       None if complete else "incomplete_defender_tracking"),
        "inRange": _check(qb_distance, qb_distance < parameters["maxQbDistanceYd"] if qb_distance is not None else None,
                          "missing_qb_or_back_position" if qb_distance is None else None),
        "pastLine": _check(progress, progress >= parameters["minLosProgressYd"] if progress is not None else None,
                           "missing_ball_at_snap_or_back_position" if progress is None else None),
        "facingQb": _check(angle, True if facing_limit is None else angle < facing_limit if angle is not None else None,
                           "disabled_by_parameters" if facing_limit is None else "missing_orientation_or_position" if angle is None else None),
    }
    statuses = [check["passed"] for check in checks.values()]
    status = ("blocking" if role == "blocking" else "unavailable" if False in statuses
              else "available" if all(value is True for value in statuses) else "unknown")
    return {"nflId": back_id, "status": status, "checks": checks}


def evaluate_play(play, participants, frames, parameters=None, *, export_frames=True):
    """Return a complete CONTRACTS play, preserving even unreplayable dropbacks."""
    p = merged_parameters(parameters)
    participants, rows = _records(participants), _records(frames)
    people = {_id(row.get("nflId")): row for row in participants if _id(row.get("nflId"))}
    roles = {i: normalize_role(row.get("pff_role", row.get("role"))) for i, row in people.items()}
    qbs = [i for i, role in roles.items() if role == "passer"]
    qb_id = qbs[0] if len(qbs) == 1 else None
    defender_ids = [i for i, role in roles.items() if role in {"rusher", "coverage"}]
    backs = [i for i, row in people.items() if str(row.get("officialPosition", "")).upper().strip()
             in ({"RB", "FB"} if p["includeFb"] else {"RB"})]
    events, grouped = defaultdict(set), defaultdict(list)
    for row in rows:
        frame = _number(row.get("frameId"))
        if frame is None:
            continue
        frame = int(frame)
        grouped[frame].append(row)
        events[str(row.get("event", "")).strip().lower()].add(frame)
    snap_candidates = events["ball_snap"] | events["autoevent_ballsnap"]
    snap = min(snap_candidates) if snap_candidates else None
    end = None
    end_kind = "unknown"
    aliases = {"throw": {"pass_forward", "autoevent_passforward"},
               "sack": {"qb_sack", "qb_strip_sack", "autoevent_qbsack", "autoevent_qb_sack"},
               "scramble": {"run", "qb_scramble", "autoevent_run", "autoevent_qbscramble"}}
    if snap is not None:
        endings = [(f, kind) for kind, names in aliases.items() for name in names
                   for f in events[name] if f >= snap]
        if endings:
            end, end_kind = min(endings)
    reasons = []
    if snap is None:
        reasons.append("missing_snap")
    if end is None:
        reasons.append("missing_end_event")
    if qb_id is None:
        reasons.append("missing_or_ambiguous_passer")
    if not defender_ids:
        reasons.append("missing_defenders")
    direction = str(play.get("playDirection") or next((row.get("playDirection") for row in rows if row.get("playDirection")), "right"))
    normalized = {}
    for frame, frame_rows in grouped.items():
        normalized[frame] = {_id(row.get("nflId")): normalize_play_direction(row, direction)
                             for row in frame_rows}
    ball = normalized.get(snap, {}).get(None)
    los_x = ball[0] if ball else None
    if los_x is None:
        reasons.append("missing_ball_at_snap")
    pressure_frame = defender_id = pressure_distance = None
    defensive_team = play.get("defensiveTeam")
    unlabeled_defenders = {row.get("nflId") for row in rows
                           if defensive_team and row.get("team") == defensive_team
                           and _id(row.get("nflId")) not in defender_ids}
    uncertain = bool(unlabeled_defenders)
    if unlabeled_defenders:
        reasons.append("unknown_defender_roles")
    pressure_uncertain = False
    if snap is not None:
        limit = end if end is not None else max(grouped, default=snap)
        expected = snap + 1
        for frame in sorted(f for f in normalized if snap < f <= limit):
            positions = normalized[frame]
            distances = [(d, i) for i in defender_ids if (d := _distance(positions.get(qb_id), positions.get(i))) is not None]
            if frame != expected or len(distances) != len(defender_ids) or not defender_ids or qb_id is None:
                uncertain = True
            expected = frame + 1
            if distances:
                distance, defender = min(distances)
                if distance <= p["pressureRadiusYd"]:
                    pressure_frame, defender_id, pressure_distance = frame, defender, distance
                    pressure_uncertain = uncertain
                    break
        if pressure_frame is None and expected <= limit:
            uncertain = True
    if pressure_uncertain or (pressure_frame is None and uncertain):
        reasons.append("incomplete_first_pressure_tracking")
    pressure_status = "detected" if pressure_frame is not None else "unknown" if reasons and any(
        reason != "missing_ball_at_snap" for reason in reasons) else "none"
    pressure_reason = "incomplete_first_pressure_tracking" if pressure_uncertain else None
    if pressure_frame is None:
        pressure_reason = reasons[0] if pressure_status == "unknown" else "no_pressure_before_end"
    frame_results = []
    fixed = [rb_checks_at(i, roles[i], normalized[pressure_frame], qb_id, defender_ids, los_x, p)
             for i in backs] if pressure_frame is not None and end is not None else None
    if export_frames and snap is not None and end is not None:
        for frame in sorted(f for f in normalized if snap <= f <= end):
            positions = normalized[frame]
            states = [rb_checks_at(i, roles[i], positions, qb_id, defender_ids, los_x, p) for i in backs]
            entities = []
            for row in grouped[frame]:
                i = _id(row.get("nflId"))
                x, y, o = positions[i]
                if x is not None and y is not None:
                    entities.append({"nflId": i, "team": row.get("team", "football" if i is None else None),
                                     "x": round(x, 1), "y": round(y, 1), "o": o if i is not None else None})
            frame_results.append({"frameId": frame, "timeS": (frame - snap) / 10,
                                  "entities": entities, "rbStates": states})
            if frame == pressure_frame:
                fixed = states
    pressure_trusted = pressure_frame is not None and not pressure_uncertain and end is not None and qb_id is not None
    observations = []
    for i in backs:
        state = next((state for state in (fixed or []) if state["nflId"] == i), None)
        if state is None:
            state = rb_checks_at(i, roles[i], {}, qb_id, defender_ids, los_x, p)
            state["status"] = "blocking" if roles[i] == "blocking" else "unknown"
        counted = pressure_trusted and roles[i] == "route" and state["status"] in {"available", "unavailable"}
        exclusion = None if counted else "blocking" if roles[i] == "blocking" else "unknown_role" if roles[i] != "route" else pressure_reason or ("unknown_checks" if pressure_trusted else "missing_end_event")
        observations.append({**state, "counted": counted, "exclusionReason": exclusion,
                             "pressureFrameId": pressure_frame, "targetStatus": "unmatched",
                             "targeted": None, "completedWhenTargeted": None})
    eligible = [o for o in observations if roles[o["nflId"]] != "blocking"]
    if pressure_frame is None:
        collective = "not_applicable" if pressure_status == "none" else "unknown"
    elif not eligible:
        collective = "not_applicable"
    elif any(o["status"] == "available" and roles[o["nflId"]] == "route" for o in eligible):
        collective = "available"
    elif all(o["status"] == "unavailable" and roles[o["nflId"]] == "route" for o in eligible):
        collective = "unavailable"
    else:
        collective = "unknown"
    rushers = sum(role == "rusher" for role in roles.values())
    context = {"coverageFamily": play.get("pff_passCoverageType"), "coverageScheme": play.get("pff_passCoverage"),
               "blitz": True if rushers >= 5 else False if len(defender_ids) == 11 and not unlabeled_defenders else None,
               "passRusherCount": rushers if defender_ids and not unlabeled_defenders else None}
    result = {key: play.get(key) for key in ("possessionTeam", "defensiveTeam", "quarter", "gameClock", "down", "yardsToGo", "passResult", "playResult")}
    result.update({"playId": _id(play.get("playId")), "description": play.get("playDescription", play.get("description", "")),
                   "context": context, "participants": [{"nflId": i, "role": roles[i]} for i in people],
                   "events": {"snapFrameId": snap, "pressureFrameId": pressure_frame, "endFrameId": end, "endKind": end_kind},
                   "pressure": {"status": pressure_status, "timeS": (pressure_frame - snap) / 10 if pressure_frame is not None else None,
                                "defenderId": defender_id, "distanceYd": pressure_distance, "reason": pressure_reason},
                   "losX": los_x, "collectiveVerdict": collective, "target": {"status": "unmatched", "nflId": None, "reason": "not_yet_matched"},
                   "observations": observations, "frames": frame_results,
                   "routeBackCount": sum(roles[i] == "route" for i in backs),
                   "blockingBackCount": sum(roles[i] == "blocking" for i in backs),
                   "quality": {"replayable": bool(snap is not None and end is not None and normalized), "countable": bool(pressure_trusted and collective in {"available", "unavailable"}),
                               "reasons": list(dict.fromkeys(reasons))}})
    return result

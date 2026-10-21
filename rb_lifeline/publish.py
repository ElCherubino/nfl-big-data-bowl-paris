"""Validated, generation-scoped JSON publication with an atomic manifest swap."""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path, PurePosixPath
import shutil
import uuid

from jsonschema import Draft202012Validator

SCHEMA_VERSION = "1.0.0"
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "contracts" / "schema.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text())
RESOURCE_NAMES = {"games": "games.json", "seasonRb": "season_rb.json", "seasonTeam": "season_team.json", "analysis": "analysis.json", "quality": "quality.json"}


class PublicationError(ValueError):
    """A publication failed its contract or conservation checks."""


def _require(condition, message):
    if not condition:
        raise PublicationError(message)


def _schema(value, definition):
    schema = {"$ref": f"#/$defs/{definition}", "$defs": SCHEMA["$defs"]}
    error = next(Draft202012Validator(schema).iter_errors(value), None)
    if error:
        raise PublicationError(f"{definition}: {'.'.join(map(str, error.absolute_path))}: {error.message}")


def _metric_invariants(value):
    if isinstance(value, dict):
        if {"value", "numerator", "denominator", "unknownCount"} <= value.keys():
            n, d = value["numerator"], value["denominator"]
            _require(n <= d, "Metric numerator exceeds denominator")
            expected = n / d if d else None
            _require(value["value"] == expected or (expected is not None and isinstance(value["value"], (float, int)) and abs(value["value"] - expected) < 1e-10), "Metric value differs from its denominator")
        if {"pressuredRoutePlays", "evaluatedPlays", "excludedUnknownPlays", "availablePlays"} <= value.keys():
            _require(0 <= value["availablePlays"] <= value["evaluatedPlays"] <= value["pressuredRoutePlays"], "Counts are not ordered")
            _require(value["excludedUnknownPlays"] == value["pressuredRoutePlays"] - value["evaluatedPlays"], "Unknown count does not reconcile")
        for key, child in value.items():
            if key != "frames":
                _metric_invariants(child)
    elif isinstance(value, list):
        for child in value:
            _metric_invariants(child)


def _finite(value):
    if isinstance(value, float):
        _require(math.isfinite(value), "Non-finite JSON number")
    elif isinstance(value, dict):
        for child in value.values():
            _finite(child)
    elif isinstance(value, list):
        for child in value:
            _finite(child)


def _check_frame(frame, players):
    # This hot path validates millions of entities without JSON Schema's per-field
    # interpreter overhead. The equivalent portable schema lives in schema.json.
    _require({"frameId", "timeS", "entities", "rbStates"} <= frame.keys(), "Incomplete frame")
    _require(type(frame["frameId"]) is int and isinstance(frame["timeS"], (int, float)), "Invalid frame time/id")
    _require(isinstance(frame["entities"], list) and isinstance(frame["rbStates"], list), "Invalid frame arrays")
    seen = set()
    for entity in frame["entities"]:
        _require({"nflId", "team", "x", "y", "o"} <= entity.keys(), "Incomplete entity")
        pid = entity["nflId"]
        _require(pid is None and entity["team"] == "football" or isinstance(pid, str) and pid in players, "Unknown frame player")
        key = pid if pid is not None else "football"
        _require(key not in seen, "Duplicate entity in frame")
        seen.add(key)
        _require(all(type(entity[k]) in (int, float) for k in ("x", "y")), "Invalid entity coordinates")
        _require(entity["o"] is None or type(entity["o"]) in (int, float) and 0 <= entity["o"] < 360, "Invalid entity orientation")
    state_ids = set()
    for state in frame["rbStates"]:
        _require({"nflId", "status", "checks"} <= state.keys(), "Incomplete RB state")
        _require(state["nflId"] in players and state["nflId"] not in state_ids, "Duplicate/unknown RB state")
        state_ids.add(state["nflId"])
        _require(state["status"] in {"available", "unavailable", "blocking", "unknown"}, "Invalid RB status")
        _require({"routeRunner", "open", "inRange", "pastLine", "facingQb"} <= state["checks"].keys(), "Missing spatial check")
        for check in state["checks"].values():
            _require({"passed", "value", "reason"} <= check.keys(), "Incomplete spatial check")
            _require(check["passed"] is None or type(check["passed"]) is bool, "Invalid check flag")
            _require(check["value"] is None or type(check["value"]) in (bool, int, float), "Invalid check value")
            _require(check["reason"] is None or isinstance(check["reason"], str), "Invalid check reason")


def validate_document(data, definition):
    """Validate a public data object, including replay and numeric invariants."""
    _finite(data)
    if definition != "game":
        _schema(data, definition)
    else:
        # Apply the documented schema to metadata; the hot frame path above
        # enforces the equivalent entity/check structure plus references.
        projected = {**data, "plays": [{**p, "frames": []} for p in data.get("plays", [])]}
        _schema(projected, "game")
        players = data["players"]
        ids = [p["playId"] for p in data["plays"]]
        _require(len(ids) == len(set(ids)), "Duplicate playId in game")
        for play in data["plays"]:
            frames = play["frames"]
            frame_ids = [f["frameId"] for f in frames]
            _require(frame_ids == sorted(set(frame_ids)), "Frames are not strictly increasing")
            for frame in frames:
                _check_frame(frame, players)
            for participant in play["participants"]:
                _require(isinstance(participant.get("nflId"), str) and participant["nflId"] in players, "Unknown participant")
            events = play["events"]
            pressure = events.get("pressureFrameId")
            if play["pressure"].get("status") == "detected":
                _require(pressure is not None and events.get("snapFrameId") is not None, "Detected pressure lacks snap/pressure frame")
                _require(events["snapFrameId"] <= pressure, "Pressure precedes snap")
                if events.get("endFrameId") is not None:
                    _require(pressure <= events["endFrameId"], "Pressure after end")
                if play["quality"]["replayable"] or play["quality"]["countable"]:
                    _require(events.get("endFrameId") is not None, "Usable pressure lacks end frame")
                    pressure_frame = next((f for f in frames if f["frameId"] == pressure), None)
                    _require(pressure_frame is not None and abs(pressure_frame["timeS"] - play["pressure"]["timeS"]) < 1e-8, "Pressure time/frame mismatch")
                else:
                    _require(bool(play["quality"]["reasons"]), "Unusable pressure lacks quality diagnostic")
            for observation in play["observations"]:
                _require(observation["nflId"] in players, "Unknown observed player")
                if observation["counted"]:
                    _require(observation["status"] in {"available", "unavailable"} and observation["pressureFrameId"] == pressure, "Counted observation lacks pressure/verdict")
                    frame = next((f for f in frames if f["frameId"] == pressure), None)
                    state = next((s for s in (frame or {}).get("rbStates", []) if s["nflId"] == observation["nflId"]), None)
                    _require(state is not None and state["status"] == observation["status"] and state["checks"] == observation["checks"], "Pressure flag and fixed observation disagree")
                else:
                    _require(bool(observation.get("exclusionReason")), "Excluded observation lacks reason")
    _metric_invariants(data)
    if definition in {"seasonRb", "seasonTeam"}:
        key = "nflId" if definition == "seasonRb" else "team"
        ids = [r[key] for r in data["rows"]]
        _require(len(ids) == len(set(ids)), f"Duplicate {definition} identity")
        for row in data["rows"]:
            _require(row["eligible"] or row["rank"] is None, "Ineligible row has a rank")


def _write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
        stream.write("\n")


def _load(path):
    try:
        return json.loads(path.read_text(), parse_constant=lambda val: (_ for _ in ()).throw(PublicationError(f"Non-finite JSON number: {val}")))
    except (OSError, json.JSONDecodeError) as exc:
        raise PublicationError(f"Cannot read {path}: {exc}") from exc


def _path(root, relative):
    parsed = PurePosixPath(relative)
    _require(isinstance(relative, str) and not parsed.is_absolute() and ".." not in parsed.parts and ":" not in relative and "\\" not in relative, "Unsafe resource path")
    candidate = (root / relative).resolve()
    _require(candidate.is_relative_to(root.resolve()), "Resource leaves publication root")
    return candidate


COUNT_FIELDS = ("pressuredRoutePlays", "evaluatedPlays", "excludedUnknownPlays", "availablePlays")


def publish(publication, output_dir):
    """Publish a complete generation; gameBundles may be a one-pass iterator.

    The existing manifest stays usable on any validation or write failure. Old
    generations are retained because already-open browsers may still use them.
    """
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    gid = uuid.uuid4().hex
    stage = output / f".staging-{gid}"
    stage.mkdir()
    counts = Counter(gameCount=0, playCount=0, replayablePlayCount=0, pressuredPlayCount=0, rbObservationCount=0, excludedObservationCount=0)
    games = [dict(g) for g in publication["games"]]
    by_id = {g["gameId"]: g for g in games}
    _require(len(by_id) == len(games), "Duplicate catalogue gameId")
    resources = {key: f"generations/{gid}/{name}" for key, name in RESOURCE_NAMES.items()}
    manifest = {**publication["manifest"], "schemaVersion": SCHEMA_VERSION, "generationId": gid, "generatedAt": datetime.now(timezone.utc).isoformat(), "resources": resources}
    def envelope(data):
        return {"schemaVersion": SCHEMA_VERSION, "generationId": gid, "data": data}
    try:
        seen = set()
        for bundle in publication["gameBundles"]:
            game_id = bundle["gameId"]
            _require(isinstance(game_id, str) and game_id.isdigit(), "Unsafe game identifier")
            _require(game_id in by_id and game_id not in seen, "Unknown/duplicate game bundle")
            seen.add(game_id)
            validate_document(bundle, "game")
            game = by_id[game_id]
            game["gameResource"] = f"generations/{gid}/game_{game_id}.json"
            game["playCount"] = len(bundle["plays"])
            game["pressuredRoutePlayCount"] = sum(any(o["checks"]["routeRunner"]["passed"] is True for o in p["observations"]) and p["pressure"]["status"] == "detected" for p in bundle["plays"])
            counts["gameCount"] += 1
            counts["playCount"] += len(bundle["plays"])
            for play in bundle["plays"]:
                counts["replayablePlayCount"] += bool(play["quality"]["replayable"])
                counts["pressuredPlayCount"] += play["pressure"]["status"] == "detected"
                counts["rbObservationCount"] += len(play["observations"])
                counts["excludedObservationCount"] += sum(not o["counted"] for o in play["observations"])
            _write(stage / f"game_{game_id}.json", envelope(bundle))
        _require(seen == set(by_id), "Missing game bundles")
        for key in RESOURCE_NAMES:
            data = games if key == "games" else publication[key]
            validate_document(data, key)
            _write(stage / RESOURCE_NAMES[key], envelope(data))
        manifest["counts"] = dict(counts)
        _schema(manifest, "manifest")
        # Validate conservation before making any new generation discoverable.
        _validate_conservation(stage, games, publication["seasonRb"], publication["seasonTeam"], counts)
        destination = output / "generations" / gid
        destination.parent.mkdir(exist_ok=True)
        stage.rename(destination)
        temporary_manifest = output / f".manifest-{gid}.json"
        _write(temporary_manifest, manifest)
        os.replace(temporary_manifest, output / "manifest.json")
        return manifest
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def _validate_conservation(directory, games, rb, teams, counts):
    from .aggregates import counts_for_plays, is_pressured_route_observation
    from .game_counts import summarize_game

    accumulated = defaultdict(Counter)
    player_games, player_teams = defaultdict(set), defaultdict(set)
    team_plays = defaultdict(list)
    play_count = 0
    metrics = ("availability", "targetedWhenAvailable", "completionWhenTargeted")

    def compare_counts(expected, observed, identity):
        for field in COUNT_FIELDS:
            _require(expected[field] == observed[field],
                     f"Conservation failed {identity}/{field}: expected {expected[field]}, observed {observed[field]}")
        for metric in metrics:
            for field in ("numerator", "denominator", "unknownCount"):
                _require(expected[metric][field] == observed[metric][field],
                         f"Conservation failed {identity}/{metric}.{field}: expected {expected[metric][field]}, observed {observed[metric][field]}")

    for game in games:
        data = _load(directory / f"game_{game['gameId']}.json")["data"]
        gid = data["gameId"]
        _require(gid == game["gameId"], "Game identity mismatch")
        _require(len(data["plays"]) == game["playCount"], "Catalogue play count mismatch")
        play_count += len(data["plays"])
        expected_rows = {(r["team"], r["nflId"]): r for r in summarize_game(data)}
        actual_rows = {(r["team"], r["nflId"]): r for r in data["rbSummary"]}
        _require(len(actual_rows) == len(data["rbSummary"]), f"Duplicate match summary identity {gid}")
        _require(expected_rows.keys() == actual_rows.keys(), f"Match summary identities differ {gid}")
        for key, expected in expected_rows.items():
            row = actual_rows[key]
            _require(not ({"rank", "shrunkRate", "percentile", "interval"} & row.keys()),
                     f"Match summary contains ranking or uncertainty fields {gid}/{key}")
            _require(row["nflId"] in data["players"], "Unresolved match summary player")
            _require(sorted(row["playIds"]) == expected["playIds"], f"Match summary play references differ {gid}/{key}")
            compare_counts(expected["counts"], row["counts"], f"game {gid}/{key}")
            identifier = row["nflId"]
            player_games[identifier].add(gid)
            player_teams[identifier].add(row["team"])
            for field in COUNT_FIELDS:
                accumulated[identifier][field] += row["counts"][field]
            for metric in metrics:
                for field in ("numerator", "denominator", "unknownCount"):
                    accumulated[identifier][f"{metric}.{field}"] += row["counts"][metric][field]
        for play in data["plays"]:
            team_plays[play["possessionTeam"]].append({**play, "gameId": gid})
    _require(play_count == counts["playCount"] and len(games) == counts["gameCount"], "Manifest count mismatch")
    _require(set(accumulated) == {r["nflId"] for r in rb["rows"]}, "Match/season player identities differ")
    for row in rb["rows"]:
        identifier = row["nflId"]
        expected = {field: accumulated[identifier][field] for field in COUNT_FIELDS}
        expected.update({metric: {field: accumulated[identifier][f"{metric}.{field}"]
                         for field in ("numerator", "denominator", "unknownCount")} for metric in metrics})
        compare_counts(expected, row["counts"], f"player {identifier}")
        _require(set(row["gameIds"]) == player_games[identifier], f"Player game identities differ {identifier}")
        _require(set(row["teams"]) == player_teams[identifier], f"Player team identities differ {identifier}")
    expected_teams = {team: counts_for_plays(plays) for team, plays in team_plays.items()}
    expected_teams = {team: value for team, value in expected_teams.items() if value["pressuredRoutePlays"]}
    _require(set(expected_teams) == {r["team"] for r in teams["rows"]}, "Match/season team identities differ")
    for row in teams["rows"]:
        team = row["team"]
        compare_counts(expected_teams[team], row["counts"], f"team {team}")
        game_ids = {p["gameId"] for p in team_plays[team] if any(
            is_pressured_route_observation(p, o) for o in p.get("observations", []))}
        _require(set(row["gameIds"]) == game_ids, f"Team game identities differ {team}")


def validate_publication(output_dir):
    """Read an existing publication one bundle at a time and reject corruption."""
    output = Path(output_dir)
    manifest = _load(output / "manifest.json")
    _schema(manifest, "manifest")
    generation = manifest["generationId"]
    loaded = {}
    def read(relative, kind):
        document = _load(_path(output, relative))
        _schema(document, "envelope")
        _require(document["generationId"] == generation, "Resource generation mismatch")
        validate_document(document["data"], kind)
        return document["data"]
    for key, relative in manifest["resources"].items():
        _require(relative.startswith(f"generations/{generation}/"), "Resource outside selected generation")
        loaded[key] = read(relative, key)
    observed = Counter(gameCount=len(loaded["games"]), playCount=0, replayablePlayCount=0, pressuredPlayCount=0, rbObservationCount=0, excludedObservationCount=0)
    for game in loaded["games"]:
        relative = game["gameResource"]
        _require(relative == f"generations/{generation}/game_{game['gameId']}.json", "Invalid game resource")
        data = read(relative, "game")
        for play in data["plays"]:
            observed["playCount"] += 1
            observed["replayablePlayCount"] += bool(play["quality"]["replayable"])
            observed["pressuredPlayCount"] += play["pressure"]["status"] == "detected"
            observed["rbObservationCount"] += len(play["observations"])
            observed["excludedObservationCount"] += sum(not o["counted"] for o in play["observations"])
    _require(dict(observed) == manifest["counts"], "Manifest counts differ from bundles")
    _validate_conservation(output / "generations" / generation, loaded["games"], loaded["seasonRb"], loaded["seasonTeam"], observed)
    return {"valid": True, "generationId": generation, "counts": dict(observed)}

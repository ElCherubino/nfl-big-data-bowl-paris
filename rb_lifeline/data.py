"""Read original NFL tables without lossy joins or fabricated replacements.

Metadata is loaded once. Tracking is opened one match at a time. Returned rows
retain source field names and source coordinates; metrics owns normalization.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass, field
import hashlib
from pathlib import Path
from typing import Any, Iterator


class DataError(ValueError):
    """Input cannot be safely joined or interpreted."""


REQUIRED = {
    "games": {"gameId", "season", "week", "homeTeamAbbr", "visitorTeamAbbr"},
    "plays": {"gameId", "playId", "possessionTeam", "defensiveTeam", "passResult"},
    "players": {"nflId", "displayName", "officialPosition"},
    "scouting": {"gameId", "playId", "nflId", "pff_role"},
    "tracking": {"gameId", "playId", "nflId", "frameId", "team", "playDirection", "x", "y", "o", "event"},
}
FILENAMES = {"games": "games.csv", "plays": "plays.csv", "players": "players.csv", "scouting": "pffScoutingData.csv"}
KEYS = {"games": ("gameId",), "plays": ("gameId", "playId"), "players": ("nflId",), "scouting": ("gameId", "playId", "nflId"), "tracking": ("gameId", "playId", "nflId", "frameId", "team")}
IDS = {"gameId", "playId", "nflId", "pff_nflIdBlockedPlayer", "foulNFLId1", "foulNFLId2", "foulNFLId3"}
INTS = {"season", "week", "quarter", "down", "yardsToGo", "yardlineNumber", "preSnapHomeScore", "preSnapVisitorScore", "penaltyYards", "prePenaltyPlayResult", "playResult", "absoluteYardlineNumber", "frameId", "jerseyNumber", "weight"}
FLOATS = {"x", "y", "s", "a", "dis", "o", "dir", "defendersInBox"}


def _value(key: str, value: str | None) -> Any:
    if value is None or value.strip() in {"", "NA", "NaN", "nan", "null"}:
        return None
    value = value.strip()
    if key in IDS:
        # Some CSV writers encode integer identifiers as decimal numbers.
        return value[:-2] if value.endswith(".0") else value
    if key in INTS:
        return int(float(value))
    if key in FLOATS or (key.startswith("pff_") and key not in {"pff_role", "pff_positionLinedUp", "pff_nflIdBlockedPlayer", "pff_blockType", "pff_passCoverage", "pff_passCoverageType"}):
        try:
            return float(value)
        except ValueError:
            return value
    return value


def _read(path: Path, table: str) -> list[dict]:
    if not path.is_file():
        raise DataError(f"Missing {path}. Initialize sources with git submodule update --init --recursive, or set --data-dir to the supplied data directory.")
    rows, seen = [], set()
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        missing = REQUIRED[table] - set(reader.fieldnames or [])
        if missing:
            raise DataError(f"{path.name}: missing required columns: {', '.join(sorted(missing))}")
        for line, source in enumerate(reader, 2):
            try:
                row = {key: _value(key, val) for key, val in source.items()}
            except (TypeError, ValueError) as exc:
                raise DataError(f"{path.name}:{line}: invalid numeric value") from exc
            key = tuple(row.get(k) for k in KEYS[table])
            if table == "tracking":
                if row["nflId"] is None and row["team"] != "football":
                    raise DataError(f"{path.name}:{line}: missing nflId on a non-ball row")
            elif any(item is None for item in key):
                raise DataError(f"{path.name}:{line}: missing key {KEYS[table]}")
            if key in seen:
                raise DataError(f"{path.name}:{line}: duplicate {table} key {key}; input was not deduplicated")
            seen.add(key)
            rows.append(row)
    return rows


@dataclass
class Sources:
    data_dir: Path
    games: list[dict]
    plays: list[dict]
    players: list[dict]
    scouting: list[dict]
    fingerprint: str
    diagnostics: list[dict] = field(default_factory=list)

    @property
    def input_counts(self) -> dict:
        return {"games": len(self.games), "plays": len(self.plays), "players": len(self.players), "scouting": len(self.scouting)}

    def load_tracking(self, game_id: str) -> list[dict]:
        path = self.data_dir / "tracking" / f"tracking_{game_id}.csv"
        if not path.exists():
            return []  # A missing match is a reported quality limitation, not a dropped play.
        rows = _read(path, "tracking")
        play_ids = {p["playId"] for p in self.plays if p["gameId"] == str(game_id)}
        for row in rows:
            if row["gameId"] != str(game_id) or row["playId"] not in play_ids:
                raise DataError(f"{path.name}: tracking references an unknown game/play {row['gameId']}/{row['playId']}")
        return rows

    def iter_games(self, game_ids=None) -> Iterator[dict]:
        selected = None if game_ids is None else {str(g) for g in game_ids}
        players = {p["nflId"]: p for p in self.players}
        for game in self.games:
            gid = game["gameId"]
            if selected is not None and gid not in selected:
                continue
            plays = [p for p in self.plays if p["gameId"] == gid]
            participants, tracking = defaultdict(list), defaultdict(list)
            for row in self.scouting:
                if row["gameId"] == gid:
                    participants[row["playId"]].append({**players.get(row["nflId"], {"displayName": None, "officialPosition": None}), **row})
            for row in self.load_tracking(gid):
                tracking[row["playId"]].append(row)
            yield {"game": game, "plays": plays, "participantsByPlay": dict(participants), "trackingByPlay": dict(tracking)}


def load_sources(data_dir: str | Path) -> Sources:
    directory = Path(data_dir)
    tables = {name: _read(directory / filename, name) for name, filename in FILENAMES.items()}
    game_ids = {r["gameId"] for r in tables["games"]}
    play_keys = {(r["gameId"], r["playId"]) for r in tables["plays"]}
    player_ids = {r["nflId"] for r in tables["players"]}
    diagnostics = []
    for play in tables["plays"]:
        if play["gameId"] not in game_ids:
            raise DataError(f"plays.csv: unknown gameId {play['gameId']}")
    for row in tables["scouting"]:
        if (row["gameId"], row["playId"]) not in play_keys:
            raise DataError(f"pffScoutingData.csv: unknown play {row['gameId']}/{row['playId']}")
        if row["nflId"] not in player_ids:
            diagnostics.append({"reason": "player_not_found", "gameId": row["gameId"], "playId": row["playId"], "nflId": row["nflId"]})
    for game in tables["games"]:
        if not (directory / "tracking" / f"tracking_{game['gameId']}.csv").exists():
            diagnostics.append({"reason": "tracking_file_missing", "gameId": game["gameId"]})
    if len(tables["games"]) != 122 or len(tables["plays"]) != 8557:
        diagnostics.append({"reason": "source_scope_differs_from_documentation", "expectedGames": 122, "actualGames": len(tables["games"]), "expectedPlays": 8557, "actualPlays": len(tables["plays"]), "explanation": "Configured source scope differs from the announced full event dataset."})
    fingerprint = hashlib.sha256()
    paths = [directory / filename for filename in FILENAMES.values()] + sorted((directory / "tracking").glob("tracking_*.csv"))
    for path in paths:
        fingerprint.update(str(path.relative_to(directory)).encode())
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                fingerprint.update(chunk)
    return Sources(directory, **tables, fingerprint=fingerprint.hexdigest(), diagnostics=diagnostics)

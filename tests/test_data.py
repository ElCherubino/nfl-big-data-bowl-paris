import csv

import pytest

from rb_lifeline.data import DataError, load_sources


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture
def sources_dir(tmp_path):
    games = [{"gameId": gid, "season": "2021", "week": "1", "homeTeamAbbr": "A", "visitorTeamAbbr": "B"} for gid in ("1", "2")]
    plays = [{"gameId": gid, "playId": "7", "possessionTeam": "A", "defensiveTeam": "B", "passResult": "I"} for gid in ("1", "2")]
    write_csv(tmp_path / "games.csv", games)
    write_csv(tmp_path / "plays.csv", plays)
    write_csv(tmp_path / "players.csv", [{"nflId": "10", "displayName": "A Back", "officialPosition": "RB"}])
    write_csv(tmp_path / "pffScoutingData.csv", [{"gameId": "1", "playId": "7", "nflId": "10", "pff_role": "Pass route"}, {"gameId": "2", "playId": "7", "nflId": "99", "pff_role": "Pass"}])
    write_csv(tmp_path / "tracking" / "tracking_1.csv", [{"gameId": "1", "playId": "7", "nflId": "NA", "frameId": "1", "team": "football", "playDirection": "left", "x": "50.2", "y": "20.1", "o": "NA", "event": "ball_snap"}])
    return tmp_path


def test_composite_keys_ball_and_missing_tracking_remain_visible(sources_dir):
    sources = load_sources(sources_dir)
    games = list(sources.iter_games())
    assert len(sources.plays) == 2
    assert games[0]["trackingByPlay"]["7"][0]["nflId"] is None
    assert games[0]["trackingByPlay"]["7"][0]["x"] == 50.2
    assert games[0]["participantsByPlay"]["7"][0]["displayName"] == "A Back"
    assert games[1]["participantsByPlay"]["7"][0]["officialPosition"] is None
    assert len(games[1]["plays"]) == 1 and games[1]["trackingByPlay"] == {}
    assert {d["reason"] for d in sources.diagnostics} >= {"player_not_found", "tracking_file_missing"}
    assert len(sources.fingerprint) == 64


def test_missing_column_fails_before_join(sources_dir):
    write_csv(sources_dir / "players.csv", [{"nflId": "10", "displayName": "Missing position"}])
    with pytest.raises(DataError, match="officialPosition"):
        load_sources(sources_dir)


def test_conflicting_duplicate_is_never_silently_discarded(sources_dir):
    with (sources_dir / "plays.csv").open("a") as stream:
        stream.write("1,7,B,A,C\n")
    with pytest.raises(DataError, match="duplicate plays key"):
        load_sources(sources_dir)


def test_tracking_duplicate_and_unknown_join_are_rejected(sources_dir):
    with (sources_dir / "tracking" / "tracking_1.csv").open("a") as stream:
        stream.write("1,7,NA,1,football,left,50.2,20.1,NA,ball_snap\n")
    with pytest.raises(DataError, match="duplicate tracking key"):
        load_sources(sources_dir).load_tracking("1")


def test_missing_sources_gives_setup_instruction(tmp_path):
    with pytest.raises(DataError, match="git submodule update"):
        load_sources(tmp_path)


def test_fingerprint_tracks_content(sources_dir):
    before = load_sources(sources_dir).fingerprint
    path = sources_dir / "tracking" / "tracking_1.csv"
    path.write_text(path.read_text().replace("50.2", "50.3"))
    assert before != load_sources(sources_dir).fingerprint

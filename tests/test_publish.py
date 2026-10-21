from copy import deepcopy
import json

import pytest

from rb_lifeline.publish import PublicationError, publish, validate_document, validate_publication


def publication():
    period = {"season": 2021, "weeks": [1], "label": "Synthetic contract test only"}
    metric = {"value": None, "numerator": 0, "denominator": 0, "unknownCount": 0}
    return {
        "manifest": {"calculationVersion": "test", "sourceFingerprint": "synthetic", "period": period, "parameters": {"pressureRadiusYd": 2, "openDistanceYd": 2.5, "maxQbDistanceYd": 15, "minLosProgressYd": -1, "maxFacingAngleDeg": 90, "includeFb": True, "minSeasonN": 20, "shrinkageK": 20, "bootstrapReplicates": 20, "randomSeed": 1}},
        "games": [{"gameId": "1", "season": 2021, "week": 1, "gameDate": "2021-09-09", "homeTeam": "A", "awayTeam": "B", "score": None, "scoreReason": "final_score_not_supplied"}],
        "gameBundles": [{"gameId": "1", "players": {}, "plays": [], "rbSummary": []}],
        "seasonRb": {"period": period, "reference": {"metricUnit": "player_play", "leagueAvailability": None, "shrinkageK": 20, "minN": 20, "cohortSize": 0}, "rows": []},
        "seasonTeam": {"period": period, "reference": {"metricUnit": "team_play", "leagueAvailability": None, "shrinkageK": 20, "minN": 20, "cohortSize": 0}, "rows": []},
        "analysis": {"comparisonRows": [], "sensitivityRows": []},
        "quality": {"inputCounts": {"games": 1, "plays": 0}, "exclusions": [], "targetMatching": {"thrownPassCount": 0, "matchedCount": 0, "unmatchedCount": 0, "ambiguousCount": 0, "matchRate": metric}, "pressureProxy": {"evaluatedPlayCount": 0, "truePositive": 0, "falsePositive": 0, "trueNegative": 0, "falseNegative": 0, "precision": metric, "recall": metric, "medianTimeToPressureS": None}, "prototypeDifferences": []},
    }


def test_atomic_publication_and_generation_validation(tmp_path):
    first = publish(publication(), tmp_path)
    assert validate_publication(tmp_path)["valid"]
    game_path = tmp_path / f"generations/{first['generationId']}/game_1.json"
    assert json.loads(game_path.read_text())["generationId"] == first["generationId"]
    second = publication()
    second["gameBundles"] = iter([])
    with pytest.raises(PublicationError, match="Missing game bundles"):
        publish(second, tmp_path)
    assert json.loads((tmp_path / "manifest.json").read_text())["generationId"] == first["generationId"]
    assert not list(tmp_path.glob(".staging-*"))


def test_consumer_rejects_schema_generation_and_path_mismatch(tmp_path):
    manifest = publish(publication(), tmp_path)
    path = tmp_path / manifest["resources"]["games"]
    good = json.loads(path.read_text())
    bad = deepcopy(good)
    bad["schemaVersion"] = "2.0.0"
    path.write_text(json.dumps(bad))
    with pytest.raises(PublicationError, match="1.0.0"):
        validate_publication(tmp_path)
    bad = deepcopy(good)
    bad["generationId"] = "other"
    path.write_text(json.dumps(bad))
    with pytest.raises(PublicationError, match="generation mismatch"):
        validate_publication(tmp_path)
    path.write_text(json.dumps(good))
    manifest["resources"]["games"] = "../escape.json"
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(PublicationError):
        validate_publication(tmp_path)


def test_nonfinite_and_bad_metrics_rejected_before_manifest_changes(tmp_path):
    data = publication()
    data["quality"]["targetMatching"]["matchRate"]["value"] = float("nan")
    with pytest.raises(PublicationError, match="Non-finite"):
        publish(data, tmp_path)
    assert not (tmp_path / "manifest.json").exists()
    data = publication()
    data["quality"]["targetMatching"]["matchRate"].update(value=0.5, numerator=1, denominator=3)
    with pytest.raises(PublicationError, match="denominator"):
        publish(data, tmp_path)


def test_ranking_minimum_and_conservation(tmp_path):
    data = publication()
    metric = {"value": 1.0, "numerator": 1, "denominator": 1, "unknownCount": 0}
    row = {"nflId": "9", "displayName": "Synthetic", "position": "RB", "teams": ["A"], "counts": {"pressuredRoutePlays": 1, "evaluatedPlays": 1, "excludedUnknownPlays": 0, "availablePlays": 1, "availability": metric, "targetedWhenAvailable": metric, "completionWhenTargeted": metric}, "rawRate": 1.0, "shrunkRate": 1.0, "interval": None, "eligible": False, "rank": 1, "percentile": None, "gameIds": ["1"]}
    data["seasonRb"]["rows"] = [row]
    with pytest.raises(PublicationError, match="Ineligible"):
        publish(data, tmp_path)
    row["rank"] = None
    with pytest.raises(PublicationError, match="identities differ"):
        publish(data, tmp_path)

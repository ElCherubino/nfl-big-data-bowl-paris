"""Synthetic two-game public exports with exact, hand-counted opportunities."""
from copy import deepcopy

import pytest

from rb_lifeline.aggregates import aggregate_season
from rb_lifeline.game_counts import summarize_game
from rb_lifeline.publish import PublicationError, publish, validate_publication
from test_publish import publication


def observation(identifier, status='available', targeted=False, completed=None):
    checks = {name: {'passed': True, 'value': True if name == 'routeRunner' else 1, 'reason': None}
              for name in ('routeRunner', 'open', 'inRange', 'pastLine', 'facingQb')}
    return {'nflId': identifier, 'status': status, 'counted': status != 'unknown',
            'exclusionReason': 'unknown_geometry' if status == 'unknown' else None,
            'pressureFrameId': 2, 'checks': checks,
            'targetStatus': 'unmatched' if targeted is None else 'matched',
            'targeted': targeted, 'completedWhenTargeted': completed}


def play(identifier, team, observations, target='a', target_status='matched'):
    return {'playId': identifier, 'possessionTeam': team, 'defensiveTeam': 'B' if team == 'A' else 'A',
            'quarter': 1, 'gameClock': '10:00', 'down': 1, 'yardsToGo': 10,
            'description': 'Synthetic test only', 'passResult': 'C', 'playResult': 3,
            'context': {}, 'participants': [], 'events': {'snapFrameId': 1, 'pressureFrameId': 2, 'endFrameId': 3},
            'pressure': {'status': 'detected', 'timeS': .1}, 'losX': 20,
            'collectiveVerdict': 'available' if any(o['status'] == 'available' for o in observations) else 'unknown',
            'target': {'status': target_status, 'nflId': target}, 'observations': observations,
            'frames': [{'frameId': 2, 'timeS': .1, 'entities': [],
                        'rbStates': [{k: o[k] for k in ('nflId', 'status', 'checks')} for o in observations]}],
            'quality': {'replayable': True, 'countable': any(o['counted'] for o in observations), 'reasons': []}}


def fixture():
    first = {'gameId': '1', 'players': {
        'a': {'displayName': 'Zulu', 'officialPosition': 'RB', 'team': 'A'},
        'b': {'displayName': 'Alpha', 'officialPosition': 'FB', 'team': 'A'},
        'u': {'displayName': 'Unknown', 'officialPosition': 'RB', 'team': 'B'}},
        'plays': [play('1', 'A', [observation('a', targeted=True, completed=True), observation('b')]),
                  play('2', 'A', [observation('a', targeted=None)], target=None, target_status='unmatched'),
                  play('3', 'B', [observation('u', 'unknown', targeted=None)], target=None, target_status='unmatched')]}
    second = {'gameId': '2', 'players': {'a': {'displayName': 'Zulu', 'officialPosition': 'RB', 'team': 'B'}},
              'plays': [play('1', 'B', [observation('a')], target='other')]}
    bundles = [first, second]
    for bundle in bundles:
        bundle['rbSummary'] = summarize_game(bundle)
    data = publication()
    data['gameBundles'] = bundles
    second_catalogue = {**data['games'][0], 'gameId': '2'}
    data['games'].append(second_catalogue)
    season = aggregate_season(bundles)
    data.update(seasonRb=season['rb'], seasonTeam=season['teams'])
    return data


def test_two_games_multiback_unknowns_and_transfer_are_unranked(tmp_path):
    data = fixture()
    rows = data['gameBundles'][0]['rbSummary']
    assert [(r['team'], r['nflId']) for r in rows] == [('A', 'b'), ('A', 'a'), ('B', 'u')]
    assert all(set(row) == {'nflId', 'team', 'counts', 'playIds'} for row in rows)
    assert rows[1]['playIds'] == ['1', '2']
    assert rows[1]['counts']['targetedWhenAvailable'] == {'value': 1., 'numerator': 1, 'denominator': 1, 'unknownCount': 1}
    assert rows[2]['counts']['evaluatedPlays'] == 0
    assert rows[2]['counts']['availability']['value'] is None
    assert rows[2]['counts']['excludedUnknownPlays'] == 1
    player = next(r for r in data['seasonRb']['rows'] if r['nflId'] == 'a')
    assert player['teams'] == ['A', 'B'] and player['counts']['evaluatedPlays'] == 3
    team = next(r for r in data['seasonTeam']['rows'] if r['team'] == 'A')
    assert team['counts']['evaluatedPlays'] == 2  # Three player opportunities, two team plays.
    publish(data, tmp_path)
    assert validate_publication(tmp_path)['valid']


@pytest.mark.parametrize('location,field', [('team', 'targetedWhenAvailable'), ('player', 'completionWhenTargeted'), ('match', 'targetedWhenAvailable')])
@pytest.mark.parametrize('component', ['numerator', 'denominator', 'unknownCount'])
def test_injected_denominator_or_unknown_mismatch_blocks_publication(tmp_path, location, field, component):
    data = fixture()
    publish(data, tmp_path)
    old_manifest = (tmp_path / 'manifest.json').read_bytes()
    if location == 'match':
        counts = data['gameBundles'][0]['rbSummary'][1]['counts']
    else:
        table = data['seasonTeam'] if location == 'team' else data['seasonRb']
        counts = table['rows'][0]['counts']
    metric = counts[field]
    if component == 'numerator':
        metric['numerator'] = 0  # The fixture has one known target/completion.
    else:
        metric[component] += 1
    metric['value'] = metric['numerator'] / metric['denominator'] if metric['denominator'] else None
    with pytest.raises(PublicationError, match=f'Conservation failed .*{field}.{component}: expected .*observed'):
        publish(data, tmp_path)
    assert (tmp_path / 'manifest.json').read_bytes() == old_manifest


def test_summary_preserves_identical_duplicate_only_once_and_rejects_conflicts():
    bundle = fixture()['gameBundles'][0]
    before = summarize_game(bundle)
    bundle['plays'].append(deepcopy(bundle['plays'][0]))
    assert summarize_game(bundle) == before
    bundle['plays'][-1]['possessionTeam'] = 'B'
    with pytest.raises(ValueError, match='Conflicting duplicate'):
        summarize_game(bundle)

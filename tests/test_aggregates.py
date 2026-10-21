"""Known-count fixtures for season ranking and the shared counting contract."""
from copy import deepcopy

import pytest

from rb_lifeline.aggregates import aggregate_season, counts_for_observations, counts_for_plays


def observation(identifier='a', status='available', targeted=False, completed=None, target_status='matched'):
    return {'nflId': identifier, 'status': status, 'counted': status in {'available', 'unavailable'},
            'checks': {'routeRunner': {'passed': status != 'blocking'}},
            'targeted': targeted, 'completedWhenTargeted': completed, 'targetStatus': target_status}


def play(identifier, observations, team='A', target='a', target_status='matched', result='C', countable=True):
    return {'playId': str(identifier), 'possessionTeam': team, 'pressure': {'status': 'detected'},
            'quality': {'countable': countable}, 'observations': observations,
            'collectiveVerdict': 'available' if any(o['status'] == 'available' for o in observations) else
                'unknown' if any(o['status'] == 'unknown' for o in observations) else 'unavailable',
            'target': {'status': target_status, 'nflId': target}, 'passResult': result}


def game(identifier, plays):
    return {'gameId': str(identifier), 'plays': plays, 'players': {
        'a': {'displayName': 'Alpha', 'officialPosition': 'RB'},
        'b': {'displayName': 'Beta', 'officialPosition': 'FB'},
        'c': {'displayName': 'Charlie', 'officialPosition': 'RB'},
        'u': {'displayName': 'Unknown', 'officialPosition': 'RB'}}}


def test_individual_known_nonpasses_unknown_targets_and_completion_denominators():
    observations = [observation(targeted=True, completed=True), observation(targeted=True, completed=False),
                    observation(targeted=False), observation(targeted=False, target_status='not_applicable'),
                    observation(targeted=None, target_status='ambiguous'),
                    observation(status='unavailable', targeted=True, completed=True),
                    observation(status='unknown', targeted=None)]
    counts = counts_for_observations(observations)
    assert (counts['pressuredRoutePlays'], counts['evaluatedPlays'], counts['availablePlays']) == (7, 6, 5)
    assert counts['availability'] == {'value': 5/6, 'numerator': 5, 'denominator': 6, 'unknownCount': 1}
    assert counts['targetedWhenAvailable'] == {'value': .5, 'numerator': 2, 'denominator': 4, 'unknownCount': 1}
    assert counts['completionWhenTargeted'] == {'value': 2/3, 'numerator': 2, 'denominator': 3, 'unknownCount': 1}


def test_multiback_reference_multiteam_identity_and_unknown_only_player():
    one = play(1, [observation(), observation('b', 'unavailable', True, True)], target='b')
    two = play(1, [observation(status='unavailable'), observation('u', 'unknown', None)], team='B')
    games = [game('g1', [one]), game('g2', [two])]
    result = aggregate_season(games)
    rows = {r['nflId']: r for r in result['rb']['rows']}
    assert rows['a']['teams'] == ['A', 'B']
    assert rows['a']['counts']['evaluatedPlays'] == 2
    assert rows['a']['gameIds'] == ['g1', 'g2']
    assert result['rb']['reference']['leagueAvailability'] == 1/3
    assert result['teams']['reference']['leagueAvailability'] == 1
    assert rows['a']['shrunkRate'] == pytest.approx((1+20/3)/22)
    assert rows['u']['counts']['pressuredRoutePlays'] == 1
    assert rows['u']['rawRate'] is None
    assert rows['u']['rank'] is None and rows['u']['percentile'] is None
    assert rows['u']['interval'] is None
    team = result['teams']['rows'][0]
    assert team['counts']['targetedWhenAvailable']['numerator'] == 0
    assert team['counts']['completionWhenTargeted']['numerator'] == 1
    # Exact duplicate bundles/plays cannot double either counting unit.
    assert aggregate_season(games + games) == result
    bad = deepcopy(games[0]); bad['plays'][0]['passResult'] = 'I'
    with pytest.raises(ValueError, match='Conflicting duplicate'):
        aggregate_season([games[0], bad])


def test_rank_boundaries_ties_percentiles_and_published_variants():
    plays = []
    for identifier, n in [('a', 19), ('b', 20), ('c', 21)]:
        plays.extend(play(f'{identifier}{i}', [observation(identifier)]) for i in range(n))
    result = aggregate_season([game('g', plays)])['rb']
    rows = {r['nflId']: r for r in result['rows']}
    assert rows['a']['eligible'] is False and rows['a']['rank'] is None
    assert rows['b']['rank'] == 2 and rows['c']['rank'] == 1
    assert rows['b']['percentile'] == rows['c']['percentile'] == 50
    assert rows['b']['percentileTiedOtherCount'] == 1
    variants = {v['variantId']: v for v in result['rankingVariants']}
    assert variants['minN_15']['reference']['cohortSize'] == 3
    assert all(r['reason'] == 'insufficient_n' for r in variants['minN_30']['rows'])
    assert [r['nflId'] for r in variants['rb_only']['rows']] == ['a', 'c']
    # A row promoted by a variant must shed its baseline insufficient-n label.
    assert 'reason' not in variants['minN_15']['rows'][0]


def test_bootstrap_is_repeatable_on_raw_rate_and_singleton_percentile_absent():
    plays = [play(i, [observation(status='available' if i < 8 else 'unavailable')]) for i in range(20)]
    result = aggregate_season([game('g', plays)])['rb']
    assert result == aggregate_season([game('g', plays)])['rb']
    row = result['rows'][0]; interval = row['interval']
    assert row['rank'] == 1 and row['percentile'] is None
    assert interval['replicates'] == 2000 and interval['seed'] == 20261021
    assert interval['estimand'] == 'raw_availability_rate' and interval['denominator'] == 20
    assert interval['low'] <= .4 <= interval['high']
    assert interval['high'] > interval['low']


def test_team_unique_opportunities_quality_and_missing_targets():
    plays = [play(1, [observation(), observation('b')], target_status='unmatched'),
             play(2, [observation(status='unknown')], countable=False),
             play(3, [observation()], result='S', target=None, target_status='not_applicable')]
    counts = counts_for_plays(plays + [plays[0]])
    assert counts['pressuredRoutePlays'] == 3 and counts['evaluatedPlays'] == 2
    assert counts['availablePlays'] == 2 and counts['excludedUnknownPlays'] == 1
    assert counts['targetedWhenAvailable'] == {'value': 0, 'numerator': 0, 'denominator': 1, 'unknownCount': 1}
    assert counts['completionWhenTargeted']['value'] is None
    assert counts['completionWhenTargeted']['unknownCount'] == 1


def test_no_pressure_and_blocking_are_not_opportunities():
    no_pressure = play(1, [observation()]); no_pressure['pressure']['status'] = 'none'
    blocking = play(2, [observation(status='blocking')])
    result = aggregate_season([game('g', [no_pressure, blocking])])
    assert result['rb']['rows'] == result['teams']['rows'] == []
    assert result['rb']['reference']['leagueAvailability'] is None

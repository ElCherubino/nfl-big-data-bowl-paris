"""Auditable player-play and unique team-play season aggregates.

No coordinates or browser state enter these calculations. The counting helpers
are also the source of truth for per-game summaries and conservation checks.
"""
from collections import defaultdict
from copy import deepcopy

import numpy as np

from .config import merged_parameters

DEFAULT_PERIOD = {'season': 2021, 'weeks': list(range(1, 9)), 'label': '2021 · semaines 1–8'}


def _metric(numerator, denominator, unknown=0):
    result = {'value': numerator / denominator if denominator else None,
              'numerator': int(numerator), 'denominator': int(denominator),
              'unknownCount': int(unknown)}
    if not denominator:
        result['reason'] = 'empty_denominator'
    return result


def is_pressured_route_observation(play, observation):
    return (play.get('pressure', {}).get('status') == 'detected'
            and observation.get('checks', {}).get('routeRunner', {}).get('passed') is True)


def _counts(opportunities, evaluated, available, targeted, completed):
    return {'pressuredRoutePlays': opportunities, 'evaluatedPlays': evaluated,
            'excludedUnknownPlays': opportunities - evaluated, 'availablePlays': available,
            'availability': _metric(available, evaluated, opportunities - evaluated),
            'targetedWhenAvailable': _metric(*targeted),
            'completionWhenTargeted': _metric(*completed)}


def counts_for_observations(observations):
    """Count already selected, distinct pressured player-route observations.

    Keep unknown verdicts as opportunities. Callers select and deduplicate using
    gameId/playId/nflId before passing observations to this helper.
    """
    observations = list(observations)
    evaluated = [o for o in observations if o.get('counted') is True
                 and o.get('status') in {'available', 'unavailable'}]
    available = [o for o in evaluated if o['status'] == 'available']
    known = [o for o in available if isinstance(o.get('targeted'), bool)]
    targets = [o for o in evaluated if o.get('targeted') is True]
    completed = [o for o in targets if isinstance(o.get('completedWhenTargeted'), bool)]
    unknown_completion = sum(o.get('targeted') is None and o.get('targetStatus') != 'not_applicable'
                             for o in evaluated) + len(targets) - len(completed)
    return _counts(len(observations), len(evaluated), len(available),
                   (sum(o['targeted'] for o in known), len(known), len(available)-len(known)),
                   (sum(o['completedWhenTargeted'] for o in completed), len(completed), unknown_completion))


def _unique_plays(plays):
    result = {}
    for play in plays:
        key = (str(play.get('gameId', '')), str(play['playId']))
        if key in result and result[key] != play:
            raise ValueError(f'Conflicting duplicate play {key}')
        result[key] = play
    return list(result.values())


def _route_plays(plays):
    return [p for p in _unique_plays(plays) if any(is_pressured_route_observation(p, o)
            for o in p.get('observations', []))]


def counts_for_plays(plays):
    """Count collective opportunities once per (gameId, playId).

    Pass gameId on plays when combining games. Targeting when available means
    an available route back was targeted; completion covers all route backs.
    """
    opportunities = _route_plays(plays)
    evaluated = [p for p in opportunities if p.get('quality', {}).get('countable') is True
                 and p.get('collectiveVerdict') in {'available', 'unavailable'}]
    available = [p for p in evaluated if p['collectiveVerdict'] == 'available']
    known = [p for p in available if p.get('target', {}).get('status') in {'matched', 'not_applicable'}]
    targeted = sum(p.get('target', {}).get('status') == 'matched' and any(
        o.get('nflId') == p['target'].get('nflId') and o.get('counted') is True
        and o.get('status') == 'available' for o in p.get('observations', [])) for p in known)
    target_plays = [p for p in evaluated if p.get('target', {}).get('status') == 'matched'
                    and any(o.get('nflId') == p['target'].get('nflId')
                            and o.get('checks', {}).get('routeRunner', {}).get('passed') is True
                            for o in p.get('observations', []))]
    thrown_targets = [p for p in target_plays if p.get('passResult') in {'C', 'I', 'IN'}]
    unknown = sum(p.get('target', {}).get('status') in {'unmatched', 'ambiguous'}
                  and p.get('passResult') in {'C', 'I', 'IN'} for p in evaluated)
    return _counts(len(opportunities), len(evaluated), len(available),
                   (targeted, len(known), len(available)-len(known)),
                   (sum(p['passResult'] == 'C' for p in thrown_targets), len(thrown_targets), unknown))


def _interval(available, n, parameters):
    if not n or int(parameters['bootstrapReplicates']) <= 0:
        return None
    # For binary observations, a binomial draw is exactly the distribution of
    # resampling n original plays with replacement, without a giant index array.
    rng = np.random.default_rng(int(parameters['randomSeed']))
    samples = rng.binomial(n, available / n, size=int(parameters['bootstrapReplicates'])) / n
    low, high = np.percentile(samples, [2.5, 97.5])
    return {'low': float(low), 'high': float(high), 'level': .95,
            'method': 'bootstrap_percentile', 'replicates': len(samples),
            'seed': int(parameters['randomSeed']), 'denominator': n,
            'estimand': 'raw_availability_rate', 'samplingUnit': 'play'}


def _rank(rows, parameters, unit, minimum=None):
    minimum = int(parameters['minSeasonN'] if minimum is None else minimum)
    n = sum(r['counts']['evaluatedPlays'] for r in rows)
    available = sum(r['counts']['availablePlays'] for r in rows)
    league = available / n if n else None
    k = parameters['shrinkageK']
    for row in rows:
        row.pop('reason', None)
        counts = row['counts']; count = counts['evaluatedPlays']
        row.update(rawRate=counts['availability']['value'],
                   shrunkRate=(counts['availablePlays'] + k * league) / (count+k) if count and league is not None else None,
                   interval=_interval(counts['availablePlays'], count, parameters),
                   eligible=count >= minimum and count > 0, rank=None)
        if 'nflId' in row:
            row['percentile'] = None
        if not count:
            row['reason'] = 'no_evaluable_plays'
        elif count < minimum:
            row['reason'] = 'insufficient_n'
    eligible = sorted((r for r in rows if r['eligible']),
                      key=lambda r: (-r['shrunkRate'], -r['counts']['evaluatedPlays'], str(r.get('nflId', r.get('team')))))
    size = len(eligible)
    scores = [r['shrunkRate'] for r in eligible]
    for rank, row in enumerate(eligible, 1):
        row['rank'] = rank
        if 'nflId' in row:
            lower = sum(score < row['shrunkRate'] for score in scores)
            tied = sum(score == row['shrunkRate'] for score in scores) - 1
            row['percentile'] = 100 * (lower + .5*tied) / (size-1) if size > 1 else None
            row['percentileCohortSize'] = size
            row['percentileTiedOtherCount'] = tied
    return {'metricUnit': unit, 'leagueAvailability': league, 'shrinkageK': k,
            'minN': minimum, 'cohortSize': size, 'referenceEvaluatedPlays': n}


def aggregate_season(game_results, parameters=None, period=None):
    """Return contract data objects for season_rb and season_team."""
    parameters = merged_parameters(parameters)
    players, teams = {}, defaultdict(list)
    seen = {}
    for game in game_results:
        gid = str(game['gameId'])
        for source in game.get('plays', []):
            key = (gid, str(source['playId']))
            if key in seen:
                if seen[key] != source:
                    raise ValueError(f'Conflicting duplicate play {key}')
                continue
            seen[key] = source
            play = {**source, 'gameId': gid}
            if not any(is_pressured_route_observation(play, o) for o in play.get('observations', [])):
                continue
            teams[play['possessionTeam']].append(play)
            observed_ids = set()
            for observation in play.get('observations', []):
                if not is_pressured_route_observation(play, observation):
                    continue
                identifier = str(observation['nflId'])
                if identifier in observed_ids:
                    raise ValueError(f'Duplicate player observation {key}: {identifier}')
                observed_ids.add(identifier)
                identity = game.get('players', {}).get(identifier, {})
                position = identity.get('officialPosition')
                if position == 'FB' and not parameters['includeFb']:
                    continue
                row = players.setdefault(identifier, {'nflId': identifier,
                    'displayName': identity.get('displayName') or identifier,
                    'position': position, 'teams': set(), 'gameIds': set(), '_observations': []})
                row['teams'].add(play['possessionTeam']); row['gameIds'].add(gid)
                row['_observations'].append(observation)
    rb_rows = []
    for _, row in sorted(players.items()):
        row['counts'] = counts_for_observations(row.pop('_observations'))
        row['teams'] = sorted(row['teams']); row['gameIds'] = sorted(row['gameIds'])
        rb_rows.append(row)
    team_rows = [{'team': team, 'counts': counts_for_plays(plays),
                  'gameIds': sorted({p['gameId'] for p in plays})} for team, plays in sorted(teams.items())]
    period = deepcopy(period or DEFAULT_PERIOD)
    rb = {'period': period, 'reference': _rank(rb_rows, parameters, 'player_play'), 'rows': rb_rows}
    team_data = {'period': deepcopy(period), 'reference': _rank(team_rows, parameters, 'team_play'), 'rows': team_rows,
                 'targetedWhenAvailableDefinition': 'An available route back targeted among collectively available plays with known target'}
    variants = []
    for minimum in (15, 30):
        rows = deepcopy(rb_rows)
        variants.append({'variantId': f'minN_{minimum}', 'includeFb': parameters['includeFb'],
                         'reference': _rank(rows, parameters, 'player_play', minimum), 'rows': rows})
    rows = deepcopy([r for r in rb_rows if r['position'] == 'RB'])
    variants.append({'variantId': 'rb_only', 'includeFb': False,
                     'reference': _rank(rows, parameters, 'player_play'), 'rows': rows})
    rb['rankingVariants'] = variants
    return {'rb': rb, 'teams': team_data}

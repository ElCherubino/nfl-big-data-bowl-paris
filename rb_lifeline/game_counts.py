"""Unranked match counts, computed from the same opportunities as season data."""
from collections import defaultdict

from .aggregates import counts_for_observations, is_pressured_route_observation


def summarize_game(bundle):
    """Return neutral, auditable rows for every pressured route back.

    Unknown verdicts remain opportunities, even when a row has no evaluable
    plays. Team comes from the offensive play, so transfers are not rewritten
    using a current roster.
    """
    groups = defaultdict(dict)
    players = bundle.get('players', {})
    seen = {}
    for play in bundle.get('plays', []):
        play_id = str(play['playId'])
        if play_id in seen:
            if seen[play_id] != play:
                raise ValueError(f'Conflicting duplicate play {bundle["gameId"]}/{play_id}')
            continue
        seen[play_id] = play
        observation_ids = set()
        for observation in play.get('observations', []):
            if not is_pressured_route_observation(play, observation):
                continue
            identifier = str(observation['nflId'])
            if identifier in observation_ids:
                raise ValueError(f'Duplicate player observation {bundle["gameId"]}/{play_id}/{identifier}')
            observation_ids.add(identifier)
            groups[(play['possessionTeam'], identifier)][play_id] = observation
    rows = [{'nflId': identifier, 'team': team,
             'counts': counts_for_observations(observations.values()),
             'playIds': sorted(observations)}
            for (team, identifier), observations in groups.items()]
    return sorted(rows, key=lambda row: (row['team'],
                  players.get(row['nflId'], {}).get('displayName') or row['nflId'], row['nflId']))

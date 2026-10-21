"""Offline build orchestration; only one game's full tracking is retained."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import time

from .config import CALCULATION_VERSION, SCHEMA_VERSION, merged_parameters
from .data import load_sources
from .metrics import evaluate_play
from .publish import publish


DEFAULT_DATA_DIR = Path('nfl-data/nfl-big-data-bowl-regional-event-data/data')


def build(data_dir=DEFAULT_DATA_DIR, output='outputs/site', *, game_ids=None, parameters=None):
    from .targets import enrich_targets
    from .aggregates import aggregate_season
    from .game_counts import summarize_game
    from .analysis import build_analysis, build_quality, sensitivity_variants, summarize_variant

    params = merged_parameters(parameters)
    started = time.monotonic()
    print(f'Loading original source tables from {data_dir}', flush=True)
    sources = load_sources(data_dir)
    if game_ids:
        unknown = set(game_ids) - {g['gameId'] for g in sources.games}
        if unknown:
            raise ValueError(f'Unknown game identifiers: {sorted(unknown)}')
    period = {'season': 2021, 'weeks': list(range(1, 9)), 'label': '2021 · semaines 1–8'}
    light_games, catalog, all_players = [], [], {}
    variants = sensitivity_variants(params)
    variant_games = {v['variantId']: [] for v in variants}
    with tempfile.TemporaryDirectory(prefix='rb-lifeline-build-') as temporary:
        paths = []
        for number, source_game in enumerate(sources.iter_games(game_ids), 1):
            game = source_game['game']; gid = game['gameId']
            print(f'[{number}] Evaluating {gid} · {game["visitorTeamAbbr"]} @ {game["homeTeamAbbr"]}', flush=True)
            players, evaluated = {}, []
            per_variant = {v['variantId']: [] for v in variants}
            for play in source_game['plays']:
                pid = play['playId']
                participants = source_game['participantsByPlay'].get(pid, [])
                tracking = source_game['trackingByPlay'].get(pid, [])
                teams = {r['nflId']: r['team'] for r in tracking if r['nflId']}
                for person in participants:
                    role = str(person.get('pff_role') or '').lower()
                    team = teams.get(person['nflId']) or (play['defensiveTeam'] if role in {'coverage', 'pass rush'} else play['possessionTeam'])
                    players[person['nflId']] = {'displayName': person.get('displayName'), 'officialPosition': person.get('officialPosition'), 'team': team}
                result = evaluate_play(play, participants, tracking, params)
                enrich_targets(result, play, participants)
                # PFF validation is independent of RB eligibility and uses all defenders.
                defenders = [p for p in participants if str(p.get('pff_role') or '').lower() in {'coverage', 'pass rush'}]
                labels = [p.get(k) for p in defenders for k in ('pff_hit', 'pff_hurry', 'pff_sack')]
                result['pffPressure'] = True if any(v == 1 for v in labels) else (False if labels and all(v is not None for v in labels) else None)
                evaluated.append(result)
                for variant in variants:
                    alternative = summarize_variant(result, play, participants, tracking, params, variant)
                    per_variant[variant['variantId']].append(alternative)
            all_players.update(players)
            bundle = {'gameId': gid, 'players': players, 'plays': evaluated}
            bundle['rbSummary'] = summarize_game(bundle)
            path = Path(temporary) / f'{gid}.json'
            path.write_text(json.dumps(bundle, allow_nan=False, separators=(',', ':')))
            paths.append(path)
            light_games.append({**bundle, 'plays': [{**p, 'frames': []} for p in evaluated]})
            for variant in variants:
                variant_games[variant['variantId']].append({'gameId': gid, 'players': players, 'plays': per_variant[variant['variantId']]})
            catalog.append({'gameId': gid, 'season': game['season'], 'week': game['week'], 'gameDate': game.get('gameDate'), 'homeTeam': game['homeTeamAbbr'], 'awayTeam': game['visitorTeamAbbr'], 'score': None, 'scoreReason': 'Final score not provided by the source tables', 'playCount': len(evaluated), 'pressuredRoutePlayCount': sum(p['pressure']['status'] == 'detected' and any(o['checks']['routeRunner']['passed'] is True for o in p['observations']) for p in evaluated)})
        season = aggregate_season(light_games, params, period=period)
        analysis = build_analysis(light_games, params)
        analysis['sensitivityRows'] = [{**{k: v[k] for k in ('variantId', 'changedParameter', 'parameterValue')}, 'comparisonRows': build_analysis(variant_games[v['variantId']], params)['comparisonRows']} for v in variants]
        quality = build_quality(light_games, sources, params)
        publication = {'manifest': {'schemaVersion': SCHEMA_VERSION, 'generatedAt': datetime.now(timezone.utc).isoformat(), 'calculationVersion': CALCULATION_VERSION, 'sourceFingerprint': sources.fingerprint, 'period': period, 'parameters': params}, 'games': catalog, 'seasonRb': season['rb'], 'seasonTeam': season['teams'], 'analysis': analysis, 'quality': quality, 'gameBundles': (json.loads(p.read_text()) for p in paths)}
        manifest = publish(publication, output)
    print(f'Published {manifest["counts"]["gameCount"]} games to {output} in {time.monotonic() - started:.1f}s · generation {manifest["generationId"]}', flush=True)
    return manifest

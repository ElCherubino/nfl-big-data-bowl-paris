#!/usr/bin/env python3
"""Independently recompute five identified real examples from source coordinates.

This deliberately does not call the pipeline evaluator. It is a numerical audit;
browser screenshots and a human/agent visual review complement this evidence.
"""
import argparse
import csv
import json
import math
from pathlib import Path

CASES = [('available_completion', '4560'), ('unavailable_sack', '2279'),
         ('no_pressure', '97'), ('blocking', '349'), ('multi_back', '1368')]
GAME_ID = '2021090900'


def audit(publication, data_dir):
    manifest = json.loads((publication / 'manifest.json').read_text())
    catalog = json.loads((publication / manifest['resources']['games']).read_text())['data']
    entry = next(g for g in catalog if g['gameId'] == GAME_ID)
    bundle = json.loads((publication / entry['gameResource']).read_text())['data']
    with (data_dir / 'tracking' / f'tracking_{GAME_ID}.csv').open() as stream:
        tracking = list(csv.DictReader(stream))
    with (data_dir / 'pffScoutingData.csv').open() as stream:
        scouting = [r for r in csv.DictReader(stream) if r['gameId'] == GAME_ID]
    parameters = manifest['parameters']
    records = []
    for label, play_id in CASES:
        play = next(p for p in bundle['plays'] if p['playId'] == play_id)
        rows = [r for r in tracking if r['playId'] == play_id]
        roles = {r['nflId']: r['pff_role'].lower() for r in scouting if r['playId'] == play_id}
        qb_id = next(i for i, role in roles.items() if role == 'pass')
        defender_ids = {i for i, role in roles.items() if role in {'pass rush', 'coverage'}}
        snap = min(int(r['frameId']) for r in rows if r['event'] in {'ball_snap', 'autoevent_ballsnap'})
        endings = {'pass_forward', 'autoevent_passforward', 'qb_sack', 'qb_strip_sack', 'run', 'qb_scramble'}
        end = min(int(r['frameId']) for r in rows if r['event'] in endings and int(r['frameId']) >= snap)
        assert (snap, end) == (play['events']['snapFrameId'], play['events']['endFrameId'])
        positions = {}
        left = rows[0]['playDirection'] == 'left'
        for r in rows:
            identifier = None if r['nflId'] in {'NA', ''} else r['nflId']
            x, y = float(r['x']), float(r['y'])
            orientation = float(r['o']) if r['o'] not in {'NA', ''} else None
            if left:
                x, y = 120-x, 53.3-y
                orientation = (orientation+180) % 360 if orientation is not None else None
            positions.setdefault(int(r['frameId']), {})[identifier] = (x, y, orientation)
        first = None
        for frame_id in sorted(f for f in positions if snap < f <= end):
            points = positions[frame_id]; qb = points[qb_id]
            distance = min(math.dist(qb[:2], points[i][:2]) for i in defender_ids)
            if distance <= parameters['pressureRadiusYd']:
                first = frame_id; break
        assert first == play['events']['pressureFrameId']
        observed = first or snap
        points = positions[observed]
        exported = next(f for f in play['frames'] if f['frameId'] == observed)
        for entity in exported['entities']:
            original = points[entity['nflId']]
            assert entity['x'] == round(original[0], 1) and entity['y'] == round(original[1], 1)
            if entity['nflId'] is not None:
                assert entity['o'] == original[2]
        back_records = []
        for state in exported['rbStates']:
            identifier = state['nflId']; rb = points[identifier]; qb = points[qb_id]
            nearest = min(math.dist(rb[:2], points[i][:2]) for i in defender_ids)
            distance = math.dist(rb[:2], qb[:2]); progress = rb[0]-positions[snap][None][0]
            bearing = math.degrees(math.atan2(qb[0]-rb[0], qb[1]-rb[1])) % 360
            angle = abs((rb[2]-bearing+180) % 360-180)
            values = {'routeRunner': roles[identifier] == 'pass route', 'open': nearest,
                      'inRange': distance, 'pastLine': progress, 'facingQb': angle}
            passed = {'routeRunner': values['routeRunner'], 'open': nearest > parameters['openDistanceYd'],
                      'inRange': distance < parameters['maxQbDistanceYd'],
                      'pastLine': progress >= parameters['minLosProgressYd'],
                      'facingQb': angle < parameters['maxFacingAngleDeg']}
            for key, value in values.items():
                assert math.isclose(value, state['checks'][key]['value'], abs_tol=1e-10)
                assert passed[key] == state['checks'][key]['passed']
            expected = 'blocking' if roles[identifier] == 'pass block' else 'available' if all(passed.values()) else 'unavailable'
            assert state['status'] == expected
            if first:
                fixed = next(o for o in play['observations'] if o['nflId'] == identifier)
                assert fixed['status'] == state['status'] and fixed['checks'] == state['checks']
            back_records.append({'nflId': identifier, 'name': bundle['players'][identifier]['displayName'],
                                 'values': values, 'passed': passed, 'status': expected})
        records.append({'case': label, 'gameId': GAME_ID, 'playId': play_id,
                        'sourceDirection': 'left' if left else 'right', 'snapFrameId': snap,
                        'endFrameId': end, 'pressureFrameId': first, 'auditedFrameId': observed,
                        'collectiveVerdict': play['collectiveVerdict'], 'passResult': play['passResult'],
                        'target': play['target'], 'description': play['description'], 'backs': back_records})
    assert {'left', 'right'} <= {r['sourceDirection'] for r in records}
    return {'generationId': manifest['generationId'], 'sourceFingerprint': manifest['sourceFingerprint'],
            'method': 'Independent scalar source-coordinate and event recalculation; no evaluator imports',
            'numericalChecksPassed': True, 'visualReview': 'Record browser screenshot review separately', 'plays': records}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publication', type=Path, default=Path('outputs/site'))
    parser.add_argument('--data-dir', type=Path, default=Path('nfl-data/nfl-big-data-bowl-regional-event-data/data'))
    parser.add_argument('--output', type=Path, default=Path('outputs/validation/play-audit.json'))
    args = parser.parse_args()
    result = audit(args.publication, args.data_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n')
    print(f'Independent coordinate audit passed for {len(result["plays"])} real plays: {args.output}')

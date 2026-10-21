"""Play-level descriptive comparisons, reproducible uncertainty and sensitivity.

Bootstrap samples plays, keeping every RB observation in the same sampling unit.
Duplicate outcome vectors are compressed before multinomial sampling; this is
exactly equivalent to sampling the original plays with replacement.
"""
from collections import Counter, defaultdict
from copy import deepcopy
from statistics import median

import numpy as np

from .config import merged_parameters
from .metrics import evaluate_play, normalize_role
from .targets import THROWN, enrich_targets

METRICS = ('sackRate', 'rbTargetRate', 'rbCompletionRate')
POPULATION = 'Detected pressure, route RB/FB, determined collective availability; one row per play'


def metric(numerator, denominator, unknown=0):
    result = {'value': numerator / denominator if denominator else None,
              'numerator': int(numerator), 'denominator': int(denominator), 'unknownCount': int(unknown)}
    if not denominator:
        result['reason'] = 'empty_denominator'
    return result


def _eligible(play):
    return (play.get('pressure', {}).get('status') == 'detected'
            and play.get('quality', {}).get('countable', False)
            and play.get('collectiveVerdict') in {'available', 'unavailable'}
            and any(o.get('checks', {}).get('routeRunner', {}).get('passed') is True for o in play.get('observations', [])))


def _outcomes(play):
    """Each metric is represented by numerator, denominator, excluded unknown."""
    passed = play.get('passResult')
    target = play.get('target', {})
    known = target.get('status') in {'matched', 'not_applicable'}
    backs = {o['nflId'] for o in play.get('observations', [])
             if o.get('checks', {}).get('routeRunner', {}).get('passed') is True}
    rb_target = target.get('status') == 'matched' and target.get('nflId') in backs
    sack_known = passed in THROWN | {'S', 'R'}
    return ((int(passed == 'S'), int(sack_known), int(not sack_known)),
            (int(rb_target), int(known), int(not known)),
            (int(rb_target and passed == 'C'), int(rb_target and passed in THROWN), int(not known and passed in THROWN)))


def _interval(values, requested):
    values = values[np.isfinite(values)]
    if not len(values):
        return None
    low, high = np.percentile(values, [2.5, 97.5])
    return {'low': float(low), 'high': float(high), 'level': .95,
            'method': 'bootstrap_percentile', 'replicates': int(len(values))}


def _comparison(plays, params, identifier, family=None, blitz=None):
    groups = {'available': [], 'unavailable': []}
    vectors = []
    for play in plays:
        group = play['collectiveVerdict']
        outcomes = _outcomes(play)
        groups[group].append(outcomes)
        # Six numerator/denominator columns per group, sampling both groups jointly.
        vector = [0] * 12
        offset = 0 if group == 'available' else 6
        for i, (num, den, _) in enumerate(outcomes):
            vector[offset + i * 2:offset + i * 2 + 2] = [num, den]
        vectors.append(vector)
    row = {'id': identifier, 'scope': 'league' if identifier == 'league' else 'stratum',
           'coverageFamily': family, 'blitz': blitz, 'populationLabel': POPULATION,
           'differences': {}}
    totals = {}
    for name, outcomes in groups.items():
        result = {'playCount': len(outcomes)}
        for i, key in enumerate(METRICS):
            counts = [sum(o[i][j] for o in outcomes) for j in range(3)]
            result[key] = metric(*counts)
        row[name + 'Group'] = result
        totals[name] = result
    replicates = int(params['bootstrapReplicates'])
    samples = np.empty((0, 12))
    if vectors and replicates > 0:
        unique, frequencies = np.unique(np.asarray(vectors, dtype=np.int64), axis=0, return_counts=True)
        rng = np.random.default_rng(int(params['randomSeed']))
        weights = rng.multinomial(len(vectors), frequencies / len(vectors), size=replicates)
        samples = weights @ unique
    for i, key in enumerate(METRICS):
        available, unavailable = totals['available'][key], totals['unavailable'][key]
        value = None
        if available['value'] is not None and unavailable['value'] is not None:
            value = available['value'] - unavailable['value']
            if key == 'sackRate':
                value *= -1
        if len(samples):
            with np.errstate(divide='ignore', invalid='ignore'):
                a = samples[:, 2*i] / samples[:, 2*i+1]
                u = samples[:, 6+2*i] / samples[:, 7+2*i]
                differences = u-a if key == 'sackRate' else a-u
            interval = _interval(differences, replicates)
        else:
            interval = None
        large_enough = min(available['denominator'], unavailable['denominator']) >= 20
        excludes_zero = interval is not None and (interval['low'] > 0 or interval['high'] < 0)
        directional = large_enough and excludes_zero
        row['differences'][key] = {'value': value, 'interval': interval,
            'interpretation': 'directional' if directional else 'inconclusive',
            'reason': 'descriptive_association_not_causal' if directional else
                      'empty_or_degenerate_denominator' if interval is None else
                      'fewer_than_20_per_group' if not large_enough else 'interval_includes_zero'}
    return row


def _family(value):
    return value if value in {'Man', 'Zone'} else 'Unknown' if value is None or value == '' else 'Other'


def build_analysis(game_results, parameters=None):
    params = merged_parameters(parameters)
    plays = [p for game in game_results for p in game['plays'] if _eligible(p)]
    rows = [_comparison(plays, params, 'league')]
    # Publish every context cell, including unknown, so missing context never turns into non-blitz.
    for family in ('Man', 'Zone', 'Other', 'Unknown'):
        for blitz in (False, True, None):
            subset = [p for p in plays if _family(p.get('context', {}).get('coverageFamily')) == family
                      and p.get('context', {}).get('blitz') is blitz]
            rows.append(_comparison(subset, params, f'{family.lower()}_{"unknown" if blitz is None else "blitz" if blitz else "non_blitz"}', family, blitz))
    return {'comparisonRows': rows, 'sensitivityRows': []}


def sensitivity_variants(parameters=None):
    params = merged_parameters(parameters)
    variants = []
    for key, values in (('pressureRadiusYd', (1.5, 2., 2.5)),
                        ('openDistanceYd', (2., 2.5, 3.)),
                        ('maxQbDistanceYd', (12., 15., 18.)),
                        ('maxFacingAngleDeg', (90., 105., 120., 135., None))):
        for value in values:
            variants.append({'variantId': f'{key}_{"disabled" if value is None else value:g}' if value is not None else f'{key}_disabled',
                             'changedParameter': key, 'parameterValue': value,
                             'baseline': value == params[key]})
    return variants


def summarize_variant(result, source_play, participants, tracking, parameters, variant):
    key, value = variant['changedParameter'], variant['parameterValue']
    params = {**parameters, key: value}
    if value == parameters[key]:
        # Treat these immutable subobjects as shared; caller only serializes them.
        return {k: v for k, v in result.items() if k != 'frames'}
    incomplete_open = key == 'openDistanceYd' and any(
        o.get('checks', {}).get('open', {}).get('reason') == 'incomplete_defender_tracking'
        for o in result.get('observations', []))
    if key == 'pressureRadiusYd' or incomplete_open:
        output = evaluate_play(source_play, participants, tracking, params, export_frames=False)
        enrich_targets(output, source_play, participants)
        output['pffPressure'] = result.get('pffPressure')
        output['quality']['replayable'] = result.get('quality', {}).get('replayable', False)
        output.pop('frames', None)
        return output
    output = {k: v for k, v in result.items() if k not in {'frames', 'observations', 'quality'}}
    output['observations'] = deepcopy(result.get('observations', []))
    output['quality'] = deepcopy(result['quality'])
    check_key, operator = {'openDistanceYd': ('open', lambda x: x > value),
                           'maxQbDistanceYd': ('inRange', lambda x: x < value),
                           'maxFacingAngleDeg': ('facingQb', lambda x: True if value is None else x < value)}[key]
    trusted = (result.get('pressure', {}).get('status') == 'detected'
               and result.get('pressure', {}).get('reason') is None
               and result.get('events', {}).get('endFrameId') is not None)
    fixed_exists = result.get('events', {}).get('pressureFrameId') is not None and result.get('events', {}).get('endFrameId') is not None
    for observation in output['observations']:
        check = observation['checks'][check_key]
        precise = check.get('value')
        check['passed'] = True if key == 'maxFacingAngleDeg' and value is None else operator(precise) if precise is not None else None
        if key == 'openDistanceYd' and check.get('reason') == 'incomplete_defender_tracking' and check['passed'] is True:
            check['passed'] = None
        if key == 'maxFacingAngleDeg' and value is None:
            check['reason'] = 'disabled_by_parameters'
        role = observation['checks']['routeRunner']['passed']
        checks = [c['passed'] for c in observation['checks'].values()]
        observation['status'] = ('blocking' if role is False else 'unknown' if not fixed_exists else
                                 'unavailable' if False in checks else 'available' if all(c is True for c in checks) else 'unknown')
        observation['counted'] = trusted and role is True and observation['status'] in {'available', 'unavailable'}
        observation['exclusionReason'] = None if observation['counted'] else observation.get('exclusionReason') or 'unknown_checks'
    eligible = [o for o in output['observations'] if o['checks']['routeRunner']['passed'] is not False]
    if result['pressure']['status'] == 'detected':
        output['collectiveVerdict'] = ('not_applicable' if not eligible else
            'available' if any(o['status'] == 'available' and o['checks']['routeRunner']['passed'] is True for o in eligible) else
            'unavailable' if all(o['status'] == 'unavailable' and o['checks']['routeRunner']['passed'] is True for o in eligible) else 'unknown')
    output['quality']['countable'] = trusted and output['collectiveVerdict'] in {'available', 'unavailable'}
    return output


def build_quality(game_results, sources, parameters=None):
    plays = [p for game in game_results for p in game['plays']]
    exclusions = defaultdict(lambda: {'playCount': 0, 'observationCount': 0})
    for play in plays:
        reasons = set(play.get('quality', {}).get('reasons', []))
        if play.get('pressure', {}).get('status') == 'detected' and play.get('collectiveVerdict') == 'unknown':
            reasons.add('unknown_collective_verdict')
        observation_reasons = Counter(o.get('exclusionReason') or 'unknown_exclusion' for o in play.get('observations', []) if not o.get('counted'))
        for reason in reasons | set(observation_reasons):
            exclusions[reason]['playCount'] += 1
            exclusions[reason]['observationCount'] += observation_reasons.get(reason, 0)
    thrown = [p for p in plays if p.get('passResult') in THROWN]
    statuses = Counter(p.get('target', {}).get('status') for p in thrown)
    matched = statuses['matched']
    evaluated = [p for p in plays if p.get('pffPressure') is not None
                 and p.get('pressure', {}).get('status') in {'detected', 'none'}
                 and p.get('pressure', {}).get('reason') != 'incomplete_first_pressure_tracking'
                 and p.get('events', {}).get('snapFrameId') is not None
                 and p.get('events', {}).get('endFrameId') is not None]
    cells = Counter((p['pressure']['status'] == 'detected', bool(p['pffPressure'])) for p in evaluated)
    tp, fp, tn, fn = cells[True, True], cells[True, False], cells[False, False], cells[False, True]
    times = [p['pressure']['timeS'] for p in evaluated if p['pressure']['status'] == 'detected' and p['pressure'].get('timeS') is not None]
    observations = [o for p in plays for o in p.get('observations', []) if o.get('counted')]
    availability = sum(o['status'] == 'available' for o in observations) / len(observations) if observations else None
    return {'inputCounts': dict(sources.input_counts),
            'exclusions': [{'reason': r, **c} for r, c in sorted(exclusions.items())],
            'targetMatching': {'thrownPassCount': len(thrown), 'matchedCount': matched,
                'unmatchedCount': statuses['unmatched'], 'ambiguousCount': statuses['ambiguous'],
                'matchRate': metric(matched, len(thrown))},
            'pressureProxy': {'evaluatedPlayCount': len(evaluated), 'truePositive': tp, 'falsePositive': fp,
                'trueNegative': tn, 'falseNegative': fn, 'precision': metric(tp, tp+fp),
                'recall': metric(tp, tp+fn), 'medianTimeToPressureS': median(times) if times else None,
                'excludedUnknownPlayCount': len(plays)-len(evaluated),
                'populationLabel': 'All evaluable dropbacks, including plays without a route RB/FB'},
            'prototypeDifferences': [{'metric': 'playerPlayAvailability', 'referenceValue': .15,
                'recalculatedValue': availability,
                'explanation': 'Prototype 15% is a reference only. Recalculation uses precise first-pressure checks, conservative unknown exclusions and player-play units; exact attribution of the gap is not established.'}]}

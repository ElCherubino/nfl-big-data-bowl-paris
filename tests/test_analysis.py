from types import SimpleNamespace

from rb_lifeline.analysis import build_analysis, build_quality, sensitivity_variants, summarize_variant


def sample(group='available', result='C', target='1', target_status='matched', pressure=True, pff=True):
    return {'playId': '1', 'collectiveVerdict': group, 'passResult': result,
            'pressure': {'status': 'detected' if pressure else 'none', 'reason': None, 'timeS': 1.2},
            'target': {'status': target_status, 'nflId': target},
            'observations': [{'nflId': '1', 'counted': True, 'status': group, 'checks': {'routeRunner': {'passed': True}}}],
            'quality': {'countable': True, 'reasons': []}, 'context': {'coverageFamily': 'Man', 'blitz': None},
            'events': {'snapFrameId': 1, 'endFrameId': 20}, 'pffPressure': pff}


def analysis(plays, **params):
    return build_analysis([{'plays': plays}], {'bootstrapReplicates': 100, **params})


def test_unique_play_denominators_unknown_exclusions_and_difference_sign():
    complete = sample()
    complete['observations'].append({'nflId': '2', 'checks': {'routeRunner': {'passed': True}}})
    sack = sample('unavailable', 'S', None, 'not_applicable')
    unknown = sample(target_status='unmatched')
    row = analysis([complete, sack, unknown])['comparisonRows'][0]
    assert row['availableGroup']['playCount'] == 2
    assert row['availableGroup']['rbTargetRate'] == {'value': 1., 'numerator': 1, 'denominator': 1, 'unknownCount': 1}
    assert row['unavailableGroup']['rbTargetRate']['denominator'] == 1
    assert row['differences']['sackRate']['value'] == 1.
    assert row['differences']['rbTargetRate']['value'] == 1.
    assert row['availableGroup']['rbCompletionRate']['denominator'] == 1
    assert row['differences']['sackRate']['interpretation'] == 'inconclusive'


def test_bootstrap_reproducibility_and_twenty_play_guard():
    plays = [sample() for _ in range(20)] + [sample('unavailable', 'S', None, 'not_applicable') for _ in range(20)]
    first, second = analysis(plays), analysis(plays)
    assert first == second
    assert first['comparisonRows'][0]['differences']['sackRate']['interpretation'] == 'directional'
    assert analysis(plays[:-1])['comparisonRows'][0]['differences']['sackRate']['interpretation'] == 'inconclusive'
    empty = analysis([])['comparisonRows'][0]
    assert empty['differences']['sackRate']['interval'] is None
    assert empty['availableGroup']['sackRate']['value'] is None


def test_unknown_context_separate_from_non_blitz():
    rows = analysis([sample()])['comparisonRows']
    unknown = next(r for r in rows if r['id'] == 'man_unknown')
    no_blitz = next(r for r in rows if r['id'] == 'man_non_blitz')
    assert unknown['availableGroup']['playCount'] == 1
    assert no_blitz['availableGroup']['playCount'] == 0


def test_proxy_uses_no_rb_plays_and_omits_unknown_labels():
    plays = [sample(pressure=p, pff=f) for p, f in [(True, True), (True, False), (False, True), (False, False), (True, None)]]
    for p in plays:
        p['observations'] = []
    result = build_quality([{'plays': plays}], SimpleNamespace(input_counts={'plays': 5}))
    proxy = result['pressureProxy']
    assert proxy['evaluatedPlayCount'] == 4
    assert [proxy[k] for k in ('truePositive', 'falsePositive', 'trueNegative', 'falseNegative')] == [1, 1, 1, 1]
    assert proxy['precision']['value'] == .5
    assert proxy['recall']['value'] == .5


def test_variant_parameters_are_one_at_a_time_and_baseline_reused():
    variants = sensitivity_variants()
    assert len(variants) == 14
    assert any(v['parameterValue'] is None for v in variants)
    baseline = next(v for v in variants if v['changedParameter'] == 'pressureRadiusYd' and v['parameterValue'] == 2.)
    original = sample()
    original['frames'] = [1, 2]
    output = summarize_variant(original, {}, [], [], {'pressureRadiusYd': 2.}, baseline)
    assert 'frames' not in output
    assert output['target'] == original['target']


def test_fast_sensitivity_agrees_with_full_evaluation_including_missing_tracking():
    from rb_lifeline.metrics import evaluate_play
    from rb_lifeline.targets import enrich_targets
    from rb_lifeline.config import merged_parameters
    people = [{'nflId': 'q', 'officialPosition': 'QB', 'pff_role': 'Pass'},
              {'nflId': 'b', 'officialPosition': 'RB', 'pff_role': 'Pass Route', 'displayName': 'Joe Back'},
              {'nflId': 'd', 'officialPosition': 'CB', 'pff_role': 'Coverage'},
              {'nflId': 'd2', 'officialPosition': 'CB', 'pff_role': 'Coverage'}]
    source = {'playId': '1', 'passResult': 'C', 'playDescription': 'A.Qb pass to J.Back.'}
    tracking = []
    for f in range(1, 5):
        for i, x, y, orientation in [('q', 40, 20, 90), ('b', 43, 22, 235), ('d', 42 if f >= 3 else 50, 20, 0), ('d2', 50, 30, 0), (None, 40, 20, None)]:
            tracking.append({'nflId': i, 'frameId': f, 'x': x, 'y': y, 'o': orientation,
                             'event': 'ball_snap' if f == 1 else 'pass_forward' if f == 4 else '', 'team': 'football' if i is None else 'A'})
    cases = [tracking, [r for r in tracking if not (r['frameId'] == 3 and r['nflId'] == 'd2')],
             [{**r, 'o': None if r['nflId'] == 'b' else r['o']} for r in tracking],
             [r for r in tracking if r['frameId'] != 2]]
    params = merged_parameters()
    for rows in cases:
        baseline = evaluate_play(source, people, rows, params)
        enrich_targets(baseline, source, people)
        for variant in sensitivity_variants(params):
            actual = summarize_variant(baseline, source, people, rows, params, variant)
            expected = evaluate_play(source, people, rows, {**params, variant['changedParameter']: variant['parameterValue']}, export_frames=False)
            enrich_targets(expected, source, people)
            assert actual['collectiveVerdict'] == expected['collectiveVerdict'], variant
            assert actual['quality']['countable'] == expected['quality']['countable'], variant
            assert actual['observations'] == expected['observations'], variant

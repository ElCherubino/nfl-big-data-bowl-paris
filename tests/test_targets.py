from rb_lifeline.targets import enrich_targets, match_target


def person(nfl_id='1', name='Duke Johnson Jr.', role='Pass Route', **extra):
    return dict(nflId=nfl_id, displayName=name, pff_role=role, **extra)


def play(description='A.Qb pass short right to D.Johnson for 5 yards.', result='C'):
    return dict(playDescription=description, passResult=result, possessionTeam='BUF')


def test_suffix_prefix_and_offensive_identity():
    assert match_target(play(), [person()])['nflId'] == '1'
    assert match_target(play('A.Qb pass to Mi.Carter.'), [person(name='Michael Carter')])['nflId'] == '1'
    assert match_target(play(), [person(), person('2', role='Coverage')])['status'] == 'matched'
    assert match_target(play(), [person(team='NE')])['status'] == 'unmatched'


def test_ambiguous_and_unrecognized_receivers_are_unknown():
    assert match_target(play(), [person(), person('2', 'David Johnson')])['status'] == 'ambiguous'
    assert match_target(play('A.Qb pass incomplete. INTERCEPTED by D.Johnson.'), [person()])['status'] == 'unmatched'
    assert match_target(play('A.Qb pass intended for D.Johnson INTERCEPTED.', 'IN'), [person()])['nflId'] == '1'


def test_no_pass_is_known_zero_but_another_back_does_not_receive_credit():
    for result in ['S', 'R']:
        output = {'observations': [{'nflId': '1'}]}
        enrich_targets(output, play(result=result), [person()])
        assert output['target']['status'] == 'not_applicable'
        assert output['observations'][0]['targeted'] is False
    output = {'observations': [{'nflId': '1'}, {'nflId': '2'}]}
    enrich_targets(output, play(), [person(), person('2', 'James Cook')])
    assert output['observations'][0]['completedWhenTargeted'] is True
    assert output['observations'][1]['targeted'] is False
    assert output['observations'][1]['completedWhenTargeted'] is None

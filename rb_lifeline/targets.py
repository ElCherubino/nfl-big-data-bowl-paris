"""Conservative description-to-offensive-participant receiver matching."""
import re
import unicodedata

from .metrics import _id, normalize_role

THROWN = {'C', 'I', 'IN'}
_SUFFIX = re.compile(r'\b(jr|sr|ii|iii|iv|v)\b\.?', re.I)
_TOKEN = re.compile(r'(?:\bto|\bintended for)\s+([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ.\'’\-]*(?:\s+(?:Jr\.?|Sr\.?|II|III|IV))?)', re.I)


def _name(value):
    text = unicodedata.normalize('NFKD', str(value or ''))
    text = ''.join(c for c in text if not unicodedata.combining(c))
    return re.sub(r'[^a-z]', '', _SUFFIX.sub('', text.lower()))


def match_target(play, participants):
    if play.get('passResult') in {'S', 'R'}:
        return {'status': 'not_applicable', 'nflId': None, 'reason': 'no_thrown_pass'}
    if play.get('passResult') not in THROWN:
        return {'status': 'unmatched', 'nflId': None, 'reason': 'unknown_pass_result'}
    description = str(play.get('playDescription', play.get('description', '')) or '')
    # Only inspect the pass clause, never a later tackle/recovery/penalty clause.
    match = re.search(r'\bpass\b', description, re.I)
    clause = re.split(r'\b(?:INTERCEPTED|PENALTY)\b', description[match.end():], maxsplit=1, flags=re.I)[0] if match else ''
    token = _TOKEN.search(clause) if match else None
    if token is None:
        return {'status': 'unmatched', 'nflId': None, 'reason': 'receiver_not_in_description'}
    receiver = _name(token.group(1))
    candidates = set()
    for person in participants:
        role = normalize_role(person.get('pff_role', person.get('role')))
        if role not in {'route', 'blocking', 'passer'}:
            continue
        team = person.get('team')
        if team and team != play.get('possessionTeam'):
            continue
        full = str(person.get('displayName') or '')
        parts = _SUFFIX.sub('', full).strip().split()
        aliases = {_name(full)}
        if len(parts) >= 2:
            # Match first initial and complete last name, including hyphenated names.
            aliases.update(_name(parts[0][:length] + ''.join(parts[1:]))
                           for length in range(1, len(parts[0]) + 1))
        if receiver in aliases and _id(person.get('nflId')):
            candidates.add(_id(person['nflId']))
    if len(candidates) == 1:
        return {'status': 'matched', 'nflId': next(iter(candidates)), 'reason': None}
    return {'status': 'ambiguous' if candidates else 'unmatched', 'nflId': None,
            'reason': 'multiple_offensive_participants' if candidates else 'receiver_not_uniquely_identified'}


def enrich_targets(result, source_play, participants):
    target = match_target(source_play, participants)
    result['target'] = target
    known = target['status'] in {'matched', 'not_applicable'}
    for observation in result.get('observations', []):
        targeted = observation['nflId'] == target['nflId'] if known else None
        observation.update(targetStatus=target['status'], targeted=targeted,
                           completedWhenTargeted=(source_play.get('passResult') == 'C') if targeted else None)
    return result

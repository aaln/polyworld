"""Accepted-lineage suppression children with inward defense rendezvous."""
from copy import deepcopy
from pathlib import Path
from policy_ir import read, write, digest, refresh_grounding, bundle

C = Path('/Users/aaln/experiments/softmax/gota-autoresearch')
F = C / 'forks/fork_20260920_045449_29b23b'
STUDY = F / 'inward_rally'
REFERENCE = C / 'urgent-jordan-20260919/final-feedback'
VARIANTS = ('parent', 'suppression_reference', 'relay_all', 'relay_sentries')


def make(name):
    parent = read(C / 'snapshots/0000-b2693715459d/policy.ir.json')
    if name == 'parent':
        return parent
    reference = read(C / 'forks/fork_20260919_212453_e79df8/target_geometry/candidates/suppress_toward/policy.ir.json')
    if name == 'suppression_reference':
        return reference
    assert name in VARIANTS
    p = deepcopy(reference)
    plan = read(STUDY / 'prospective.json')
    p['id'] = 'autoresearch_20260920_' + name
    p['situation']['notes'] += ' An inherited defense refresh identifies a currently observed threatened anchor; positive-HP friendly structures are standing even when objectAlive is false. Inward structure geometry and own Manhattan distance are public observations, not route-time estimates.'
    for claim in p['belief']['claims'].values():
        claim['claim'] = 'Inherited evidence, not a measurement of ' + name + '. ' + claim['claim']
    p['belief']['claims']['B_inward_rally'] = {'status': 'untested', 'claim': plan['hypothesis'], 'evidence': [{'artifact': str(STUDY / 'prospective.json'), 'sha256': digest((STUDY / 'prospective.json').read_bytes())}]}
    p['goal']['G_defense']['preference'] += ' Test earlier arrival by remote responders at the nearest standing inward structure, preserving threat combat and alarm persistence. Closer integer coordinates do not guarantee arrival.'
    p['goal']['G_fort']['preference'] = plan['screen']['decision_rule'] + ' ' + plan['confirmation']['decision_rule']
    p['skill']['observe']['operator'] = 'lineup_inward_rally_v1'
    p['skill']['observe']['parameters']['relay_sentry_only'] = int(name == 'relay_sentries')
    for rule in p['strategy']:
        if rule['id'] == 'R1':
            rule['for'] = ['G_base', 'G_defense', 'G_fort', 'G_survival']
    p['execution']['game_version'] = '2026.9.16.5'
    p['update'].update(parent=digest(reference), revision=reference['update']['revision'] + 1, change='Observed inward defense rendezvous: ' + name, needs_review=['belief/B_inward_rally', 'goal/G_defense', 'goal/G_fort'])
    refresh_grounding(p)
    return p


if __name__ == '__main__':
    for name in VARIANTS:
        bundle(make(name), STUDY / 'candidates' / name)
        print(name, 'full compile / extraction parity passed', flush=True)

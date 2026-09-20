"""Two accepted-parent siblings; WeaponAll remains an unchanged failed reference."""
from copy import deepcopy
from pathlib import Path
from policy_ir import read, digest, refresh_grounding, bundle

C = Path('/Users/aaln/experiments/softmax/gota-autoresearch')
F = C / 'forks/fork_20260919_102345_6fb224'
STUDY = F / 'defense_phase'
VARIANTS = ('parent', 'weapon_reference', 'push_only', 'small_defense')


def make(name):
    parent = read(C / 'snapshots/0000-b2693715459d/policy.ir.json')
    if name == 'parent':
        return parent
    if name == 'weapon_reference':
        return read(F / 'weapon_dense/candidates/weapon_all/policy.ir.json')
    assert name in VARIANTS
    p = deepcopy(parent)
    p['id'] = 'autoresearch_20260919_defense_phase_' + name
    p['situation']['notes'] = ('Published2026.9.16.5. Use inherited current defActive '
        'and observed local defCount, never total hidden enemies. Physical-class dense '
        'post-hit recovery is suppressed during all active alarms for push_only; '
        'small_defense permits active alarms only with <=3 observed heroes, below '
        'the inherited4hero mass-raid threshold. Other physical eligibility, '
        'consecutive-hit guards, terrain check and homeward one-tile destination '
        'remain. No seed/opponent branch, collision assumption or hidden state.')
    for claim in p['belief']['claims'].values():
        claim['claim'] = 'Inherited evidence, not a measurement of ' + name + '. ' + claim['claim']
    p['belief']['claims']['B_defense_phase'] = {
        'status': 'untested', 'claim': read(STUDY / 'prospective.json')['hypothesis'],
        'evidence': [{'artifact': str(STUDY / 'prospective.json'),
                      'sha256': digest((STUDY / 'prospective.json').read_bytes())}]}
    p['goal']['G_cadence']['preference'] = ('Allow physical dense recovery only in the '
        'declared defense phase; resetting a swing or increasing hit count is not '
        'a fort-win verdict or proof of useful displacement.')
    p['goal']['G_defense']['preference'] = ('Preserve accepted-parent dense attack '
        'orders in the suppressed alarm context, while testing whether allowed '
        'recovery retains useful proactive and small-raid combat.')
    p['goal']['G_survival']['preference'] += ' Require complete actual team-death nonregression within the fixed local allowance; inspect every class.'
    p['goal']['G_fort']['preference'] = read(STUDY / 'prospective.json')['decision_rule']
    p['skill']['attack'] = {'operator': 'defense_phase_weapon_cadence_v1',
        'parameters': parent['skill']['attack']['parameters'] |
        {'weapon_melee': 1, 'dense_defense_ceiling': 0 if name == 'push_only' else 3}}
    for rule in p['strategy']:
        if rule['id'] == 'R2':
            rule['for'] = ['G_fort', 'G_defense', 'G_cadence', 'G_survival']
    p['execution']['game_version'] = '2026.9.16.5'
    p['update'].update(parent=digest(parent), revision=parent['update']['revision'] + 1,
        change='Physical dense recovery by observed defense phase: ' + name,
        needs_review=['belief/B_defense_phase', 'goal/G_defense', 'goal/G_cadence', 'goal/G_fort'])
    refresh_grounding(p)
    return p


if __name__ == '__main__':
    for name in VARIANTS:
        bundle(make(name), STUDY / 'candidates' / name)
        print(name, 'exact full IR roundtrip complete', flush=True)

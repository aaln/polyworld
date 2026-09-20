"""Two independent accepted-parent children testing the mana threshold gap."""
from copy import deepcopy
from pathlib import Path
from policy_ir import read, digest, refresh_grounding, bundle

C = Path('/Users/aaln/experiments/softmax/gota-autoresearch')
STUDY = C / 'forks/fork_20260919_022654_d61958/mana_alignment'
VARIANTS = ('parent', 'mana50', 'buy40')


def make(name):
    parent = read(C / 'snapshots/0000-b2693715459d/policy.ir.json')
    if name == 'parent':
        return parent
    assert name in VARIANTS
    p = deepcopy(parent)
    p['id'] = 'autoresearch_20260919_' + name
    if name == 'mana50':
        p['skill']['consume']['parameters'].update(mana_denominator=2, mana_numerator=1)
        change = 'Consume a held mana potion strictly below50%, aligned with unchanged buying below50%.'
    else:
        p['skill']['sustain']['operator'] = 'buy_mana_aligned_v1'
        change = 'Buy mana strictly below40%, aligned with unchanged consumption below40%.'
    p['situation']['notes'] = (
        'Published2026.9.16.5. Economy uses own starting mana/maxmana and gold, '
        'and live inventory queries. A held potion occupies a slot; missing '
        'equipment or observed high gold does not imply a purchase succeeded. '
        'Public class/team only; no rival identity or seed matching. ' + change)
    for claim in p['belief']['claims'].values():
        claim['claim'] = 'Inherited ancestor evidence, not a measurement of '+name+'. ' + claim['claim']
    p['belief']['claims']['B_mana_alignment'] = {
        'status': 'untested', 'claim': read(STUDY/'prospective.json')['hypothesis'],
        'evidence': [{'artifact':str(STUDY/'prospective.json'),
                      'sha256':digest((STUDY/'prospective.json').read_bytes())}]}
    p['goal']['G_capacity']['preference'] = (
        change+' Test whether fewer stranded potions allow existing class gear '
        'progression. Preserve emergency healing and measure allclass inventory, '
        'hero deaths and fortwins; no guaranteed resource gain.')
    p['goal']['G_survival']['preference'] += (
        ' Mana alignment must satisfy the prospective survival gate on both colors; '
        'earlier use can waste restoration and later buying can delay spells.')
    p['goal']['G_fort']['preference'] = (
        'Actual enemy fort destruction on both colors is the objective. Equipment '
        'counts, gold and kills are diagnostics. Require local cell nonregression '
        'and survival, then fresh hosted qualification and immutable acceptance gates.')
    for rule in p['strategy']:
        if rule['id'] in ('E0','E1','E2'):
            rule['for'] = list(dict.fromkeys(rule['for'] + ['G_capacity','G_survival','G_fort']))
    p['execution']['game_version'] = '2026.9.16.5'
    p['update'].update(parent=digest(parent), revision=parent['update']['revision']+1,
        change='Mana threshold alignment '+name+'. '+change,
        needs_review=['belief/B_mana_alignment','goal/G_capacity','goal/G_survival','goal/G_fort'])
    refresh_grounding(p)
    return p


if __name__ == '__main__':
    for name in VARIANTS:
        bundle(make(name), STUDY/'candidates'/name)
        print(name+' exact compile/reverse parity complete',flush=True)

"""Red pair-alarm candidates descended directly from the accepted fork."""
from copy import deepcopy
from binding import CONTRACTS
from policy_ir import read, digest, refresh_grounding, bundle
from autoresearch_wave_study import FORK

STUDY = FORK / 'damage_alarm'
VARIANTS = ('parent', 'damage150', 'damage350')


def make(name):
    parent = read(FORK / 'wave_followup/captured-parent/policy.ir.json')
    if name == 'parent': return parent
    assert name in VARIANTS
    p = deepcopy(parent)
    p['id'] = 'autoresearch_20260919_' + name
    old = p['skill']['observe']['parameters']
    operator = 'lineup_red_damage_v1'
    params = {k:old.get(k, v[0]) for k,v in CONTRACTS[operator].parameters.items()}
    params.update(redbranch_raid_damage=int(name[6:]), redbranch_raid_opening=7200)
    p['skill']['observe'] = {'operator': operator, 'parameters': params}
    p['situation']['notes'] += ' A living visible pair near a standing red lane tower with observed HP deficit is an additional raid situation. Absence remains unobserved.'
    p['belief']['claims']['B_damaged_pair'] = {'status':'untested',
        'claim':read(STUDY/'prospective.json')['hypothesis'],
        'evidence':[{'artifact':str(STUDY/'prospective.json'), 'sha256':digest((STUDY/'prospective.json').read_bytes())}]}
    p['goal']['G_defense']['preference'] += ' Before7200ticks, red also recalls for at leasttwo visible clustered living enemies near a standing lane tower missing'+name[6:]+'HP. Original commitment, targeting and navigation remain; measure stale recalls and forgone offense.'
    p['goal']['G_fort']['preference'] += ' Count damaged-tower raid response only if actual fort wins improve; tower preservation alone is diagnostic.'
    for rule in p['strategy']:
        if rule['id'] == 'R1': rule['for'] = list(dict.fromkeys(rule['for'] + ['G_fort']))
    p['execution']['game_version'] = '2026.9.16.5'
    p['update'].update(parent=digest(parent), revision=parent['update']['revision']+1,
        change='Red observed damaged-pair recall '+name,
        needs_review=['belief/B_damaged_pair','goal/G_defense','goal/G_fort'])
    refresh_grounding(p)
    return p


if __name__ == '__main__':
    for name in VARIANTS:
        bundle(make(name), STUDY/'candidates'/name)
        print(name, flush=True)

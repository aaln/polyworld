"""Direct accepted-parent fork combining damaged-pair recall and guarded release."""
from copy import deepcopy
from binding import CONTRACTS
from policy_ir import read, digest, refresh_grounding, bundle
from autoresearch_wave_study import FORK

STUDY = FORK / 'raid_wave'


def make(name):
    parent = read(FORK/'wave_followup/captured-parent/policy.ir.json')
    if name == 'parent': return parent
    if name == 'damage150': return read(STUDY/'candidates/damage150/policy.ir.json')
    assert name == 'raid_wave'
    p = deepcopy(parent)
    p['id'] = 'autoresearch_20260919_raid_wave_v2'
    operator = 'lineup_raid_wave_v2'
    old = p['skill']['observe']['parameters']
    params = {k:old.get(k,v[0]) for k,v in CONTRACTS[operator].parameters.items()}
    params.update(redbranch_raid_damage=150, redbranch_raid_opening=7200,
                  redbranch_split_quiet=360, redbranch_rear_radius=30)
    p['skill']['observe'] = {'operator':operator,'parameters':params}
    p['situation']['notes'] += ' Red recognizes observed paired raids near damaged standing lane towers, and separately observes quiet home pressure, assembled allies, core creeps and fort damage for release or recall. Missing enemies remain unknown.'
    p['belief']['claims']['B_raid_wave'] = {'status':'untested',
        'claim':read(STUDY/'prospective.json')['hypothesis'],
        'evidence':[{'artifact':str(STUDY/'prospective.json'),'sha256':digest((STUDY/'prospective.json').read_bytes())}]}
    p['goal']['G_defense']['preference'] = (
        'Before 7200 ticks, red also recalls for two visible clustered living enemies '
        'near a standing lane tower missing 150 HP. After an alarm, release after '
        '360 ticks with fewer than three visible enemies within 60 home, none within '
        '10 home, and three allies assembled within 28 home. Lich and Warlock '
        'cover current hero pressure within 30 home or recent core creeps; three '
        'returning heroes or observed fort damage recall the team. Safety is unproven.')
    p['goal']['G_wave']['preference'] = 'On guarded release use original wave escort and ordinary exposed structure selection, retaining local combat. Do not force center or discard outer structures.'
    p['goal']['G_fort']['preference'] += ' Judge the combined detection and release by actual fort wins and survival on both colors; draws count zero. Blue behavior remains the accepted implementation.'
    for rule in p['strategy']:
        if rule['id'] in ('R1','R4'):
            rule['for'] = list(dict.fromkeys(rule['for']+['G_wave','G_fort']))
    p['execution']['game_version'] = '2026.9.16.5'
    p['update'].update(parent=digest(parent), revision=parent['update']['revision']+1,
        change='Versioned coordinated damaged-pair recall and pressure-guarded wave release',
        needs_review=['belief/B_raid_wave','goal/G_defense','goal/G_wave','goal/G_fort'])
    refresh_grounding(p)
    return p


if __name__ == '__main__':
    bundle(make('raid_wave'),STUDY/'candidates/raid_wave')
    print('raid_wave bundle exact roundtrip complete',flush=True)

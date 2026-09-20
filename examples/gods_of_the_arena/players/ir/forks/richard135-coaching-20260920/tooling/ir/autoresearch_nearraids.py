"""Accepted-parent children for bounded-distance small-raid response."""
from copy import deepcopy
from binding import CONTRACTS
from policy_ir import read,digest,refresh_grounding,bundle
from autoresearch_wave_study import FORK

STUDY=FORK/'nearby_raid'
VARIANTS=('parent','near40','near64')


def make(name):
    parent=read(FORK/'wave_followup/captured-parent/policy.ir.json')
    if name=='parent':return parent
    assert name in VARIANTS
    p=deepcopy(parent);p['id']='autoresearch_20260919_'+name
    operator='lineup_red_nearraids_v1';old=p['skill']['observe']['parameters']
    params={k:old.get(k,v[0]) for k,v in CONTRACTS[operator].parameters.items()}
    radius=int(name[4:])
    params.update(redbranch_raid_damage=150,redbranch_raid_opening=7200,
        redbranch_raid_responders=2,redbranch_raid_hold=720,redbranch_raid_response=radius)
    p['skill']['observe']={'operator':operator,'parameters':params}
    p['situation']['notes']+=' Current shared living allied positions establish geometric response rank and distance to an observed damaged standing lane tower. Geometry does not establish route length or arrival; missing enemies remain unobserved.'
    p['belief']['claims']['B_nearby_raid']={'status':'untested','claim':read(STUDY/'prospective.json')['hypothesis'],
        'evidence':[{'artifact':str(STUDY/'prospective.json'),'sha256':digest((STUDY/'prospective.json').read_bytes())}]}
    p['goal']['G_defense']['preference']+=f' Before 7200 ticks, red additionally recruits at most two nearest living allies within {radius} coordinate tiles of a standing lane tower missing at least 150 HP and threatened by a visible clustered pair. This small-raid commitment and survivor refresh uses 720 ticks; a larger group restores original hold. Existing commitments are not canceled by the distance bound. Original larger-group alarms remain for every hero. Measure unavailable responders and lost defensive coverage.'
    p['goal']['G_wave']['preference']+=' Heroes outside the recruitment bound keep original local combat, wave escort and exposed structure selection, without forced center or outer routing.'
    p['goal']['G_fort']['preference']+=' Require actual fort-win gains and the prospectively fixed survival guard on both colors; shorter travel or fewer recalls alone is not success.'
    for rule in p['strategy']:
        if rule['id'] in ('R1','R4'):rule['for']=list(dict.fromkeys(rule['for']+['G_wave','G_fort']))
    p['execution']['game_version']='2026.9.16.5'
    p['update'].update(parent=digest(parent),revision=parent['update']['revision']+1,
        change='Versioned bounded-distance damaged-pair response '+name,
        needs_review=['belief/B_nearby_raid','goal/G_defense','goal/G_wave','goal/G_fort'])
    refresh_grounding(p);return p


if __name__=='__main__':
    for name in VARIANTS[1:]:
        bundle(make(name),STUDY/'candidates'/name);print(name+' exact roundtrip complete',flush=True)

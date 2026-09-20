"""Accepted-parent children for rank-limited small-raid response."""
from copy import deepcopy
from binding import CONTRACTS
from policy_ir import read, digest, refresh_grounding, bundle
from autoresearch_wave_study import FORK

STUDY=FORK/'ranked_raid'
VARIANTS=('parent','rank2','rank2short')


def make(name):
    parent=read(FORK/'wave_followup/captured-parent/policy.ir.json')
    if name=='parent':return parent
    assert name in VARIANTS
    p=deepcopy(parent);p['id']='autoresearch_20260919_'+name
    operator='lineup_red_rankraid_v1';old=p['skill']['observe']['parameters']
    params={k:old.get(k,v[0]) for k,v in CONTRACTS[operator].parameters.items()}
    hold=720 if name=='rank2short' else 0
    params.update(redbranch_raid_damage=150,redbranch_raid_opening=7200,
        redbranch_raid_responders=2,redbranch_raid_hold=hold)
    p['skill']['observe']={'operator':operator,'parameters':params}
    p['situation']['notes']+=' Current shared living allied positions establish geometric response rank for observed damaged-tower pair raids. Distance is not path length; absence is not death; no opponent identity enters the policy.'
    p['belief']['claims']['B_ranked_raid']={'status':'untested','claim':read(STUDY/'prospective.json')['hypothesis'],
        'evidence':[{'artifact':str(STUDY/'prospective.json'),'sha256':digest((STUDY/'prospective.json').read_bytes())}]}
    p['goal']['G_defense']['preference']+=' Red newly recalls only the two nearest living allies for a visible clustered pair near a standing lane tower missing150HP before7200ticks. All larger-group alarms remain. '+('A commitment initiated solely by this alarm and survivor refresh uses720ticks until expiry/reset or a larger-group alarm.' if hold else 'Original role-specific commitment durations remain.')+' More than two persistent defenders may accumulate after movement or deaths; measure actual assignments.'
    p['goal']['G_wave']['preference']+=' Unrecruited heroes retain original combat, wave escort and structure selection; no forced lane or center release.'
    p['goal']['G_fort']['preference']+=' Judge response allocation by actual fort wins on each color and survival, not rank activation, kills or gold.'
    for rule in p['strategy']:
        if rule['id'] in ('R1','R4'):rule['for']=list(dict.fromkeys(rule['for']+['G_wave','G_fort']))
    p['execution']['game_version']='2026.9.16.5'
    p['update'].update(parent=digest(parent),revision=parent['update']['revision']+1,
        change='Versioned rank-limited red pair raid '+name,
        needs_review=['belief/B_ranked_raid','goal/G_defense','goal/G_wave','goal/G_fort'])
    refresh_grounding(p);return p


if __name__=='__main__':
    for name in VARIANTS[1:]:
        bundle(make(name),STUDY/'candidates'/name);print(name+' exact roundtrip complete',flush=True)

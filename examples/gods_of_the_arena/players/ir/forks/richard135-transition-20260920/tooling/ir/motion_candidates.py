"""Build a multi-hypothesis IR campaign; behavior is compiled, never patched."""
from copy import deepcopy
from pathlib import Path
import sys
from binding import CONTRACTS
from policy_ir import HERE, ROOT, bundle, digest, read, refresh_grounding, write

VARIANTS = {
    'motion_all': {'motion': {'targeted':0}},
    'motion_targeted': {'motion': {}},
    'motion_bare': {'motion': {'targeted':0,'spells':0}},
    'early_pressure': {'motion': {'normal':0,'risk_hp':55}},
    'motion_pressure': {'motion': {'risk_hp':55}},
    'tower_route': {'tower': True},
    'ranged_weapon': {'weapon': True},
    'motion_weapon': {'motion': {'targeted':0}, 'weapon':True},
    'tower_weapon': {'tower':True,'weapon':True},
    'combined': {'motion': {'risk_hp':55}, 'tower':True,'weapon':True},
}


def make_policy(name, definition=None):
    definition = VARIANTS[name] if definition is None else definition
    parent = read(HERE/'waveguard_xp.evaluated.ir.json')
    p = deepcopy(parent)
    p['id'] = 'gota_motion_campaign_'+name
    p['belief']['claims']['B_candidate'] = {
        'claim':f"Test {name}: {definition}. Stable-destination separation feedback, earlier damage/attacker response, preventive tower routing and ranged starting damage are distinct hypotheses; combinations may interact. Competitive benefit is untested.",
        'status':'untested', 'evidence':[{'artifact':str((HERE/'replay-findings-20260915.json').relative_to(ROOT)),
                                       'sha256':digest((HERE/'replay-findings-20260915.json').read_bytes())}]}
    if 'motion' in definition:
        params = CONTRACTS['motion_feedback'].defaults() | definition['motion']
        p['skill']['attack'] = {'operator':'motion_feedback','parameters':params}
        for rule in p['strategy']:
            if rule['id']=='R2':rule.update(when='always', **{'for':['G_fort','G_survival','G_glory']})
            if rule['id']=='R4':rule['when']='no_candidate_no_motion'
    if definition.get('weapon'):
        p['skill']['equipment']={'operator':'ranged_weapon_start','parameters':{}}
    if definition.get('tower'):
        p['skill']['tower_route']={'operator':'tower_detour','parameters':CONTRACTS['tower_detour'].defaults()}
        p['strategy'].append({'id':'R5','when':'no_motion' if 'motion' in definition else 'always',
                              'skill':'tower_route','for':['G_wave','G_fort','G_survival']})
    p['update']={'revision':parent['update']['revision']+1,'parent':digest(parent),
                 'change':f'Multi-hypothesis campaign candidate {name}; no promotion from construction.',
                 'needs_review':['belief/B_candidate','goal/G_survival','goal/G_fort'], 'evidence':[]}
    refresh_grounding(p)
    return p


def main():
    directory=Path(sys.argv[1]);directory.mkdir(parents=True,exist_ok=True)
    for name in VARIANTS:
        manifest=bundle(make_policy(name),directory/name)
        print(name,manifest['source_sha256'])
    write(directory/'variants.json',VARIANTS)


if __name__=='__main__':main()

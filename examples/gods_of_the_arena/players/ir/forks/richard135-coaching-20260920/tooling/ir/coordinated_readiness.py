"""Combine qualified caster support with a frontline readiness decision."""
from copy import deepcopy
from anchored_support import make as anchored
from caster_binding_repair import make as caster
from policy_ir import digest,refresh_grounding
from release_workspace import RUN

STUDY=RUN/'coached-lanes/r5-coordinated-readiness'
VARIANTS=['deployed','pressure_parent','anchor_ready10','anchor_ready12','frontline_ready12']


def make(name):
    if name=='deployed':return caster('deployed')
    if name=='pressure_parent':return caster('bound_idle')
    if name not in VARIANTS[2:]:raise ValueError(name)
    parent=anchored('anchor' if name.startswith('anchor_') else 'frontline')
    p=deepcopy(parent);p['id']='gota_coordinated_'+name
    p['skill']['observe']['operator']='lineup_anchored_readiness'
    p['skill']['observe']['parameters']['redbranch_ready_tiles']=int(name[-2:])
    p['goal']['G_defense']['preference'] += (
        ' Before frontline initiation, require a nearby healthy ally close enough '
        'to the enemy or already targeting it. Otherwise use the existing rally '
        'until the enemy approaches, while preserving immediate tower/core defense. '
        'Once the frontline commits, qualified healthy idle casters support it. '
        'Evaluate this coordinated pair of decisions together; earlier orders '
        'alone did not save the first defender in observed Richard games.')
    evidence=STUDY/'diagnosis.json'
    p['belief']['claims']['B_coordinated_readiness']={'status':'untested','claim':(
        'Coaching gives two valid responses: engage with support or wait for the '
        'enemy to approach. Earlier caster support ran in actual Richard games '
        'but did not save the first DeathKnight; health-only support readiness '
        'also regressed hosted outcomes. Test enemy-distance10/12 readiness '
        'together with context-qualified caster support. Keep ordinary close '
        'defense, recall/rally, carry pressure and blue branch. Individual '
        'components need not improve on their own; no combined benefit assumed.'),
        'evidence':[{'artifact':str(evidence),'sha256':digest(evidence.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),
                       change='Coordinated initiate-or-hold defense: '+name)
    refresh_grounding(p);return p

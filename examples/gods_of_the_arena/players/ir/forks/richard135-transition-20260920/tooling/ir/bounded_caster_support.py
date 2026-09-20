"""Bridge the coached target gap without permitting distant support pursuit."""
from copy import deepcopy
from caster_binding_repair import make as caster
from policy_ir import digest, refresh_grounding
from release_workspace import RUN

STUDY=RUN/'coached-lanes/r5-bounded-caster-support'
VARIANTS=['deployed','pressure_parent','reach16','reach18']


def make(name):
    if name=='deployed':return caster('deployed')
    parent=caster('bound_idle')
    if name=='pressure_parent':return parent
    p=deepcopy(parent);p['id']='gota_caster_'+name
    p['skill']['observe']['parameters']['redbranch_assist_tiles']=int(name[5:])
    p['goal']['G_defense']['preference'] += (
        ' Bound caster support pursuit to nearby engagements. Bridge the original '
        '10tile eligibility gap without treating an ally chasing a distant enemy '
        'as sufficient reason to leave the base defense perimeter.')
    e=STUDY/'diagnosis.json'
    p['belief']['claims']['B_bounded_support']={'status':'untested','claim':(
        'Corrected idlecaster support22 wonRichard80/80 butJordan76/80; all4red '
        'losses share initial VM order1, which deployedG won4/4. CoachedRichard '
        'Lich assistance at5537 required squared distance242 (15.6tiles). Jordan '
        'loss has bothcasters joining at6721 with squared distance389 (19.7tiles). '
        'Hypothesis: reach16/18 preserves nearby support while excluding distant '
        'pursuit. This mechanism is plausible, not causal proof of the whole loss.'),
        'evidence':[{'artifact':str(e),'sha256':digest(e.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),
                       change='Bound source-correct caster assistance: '+name)
    refresh_grounding(p);return p

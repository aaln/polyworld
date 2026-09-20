"""Coaching: a lone visible attacker can decide a mixed-team game."""
from copy import deepcopy
from binding import CONTRACTS
from policy_ir import digest,read,refresh_grounding
from release_workspace import RUN
from rush_unblock_safe import make as parent_make

STUDY=RUN/'coached-lanes/r5-mixed-backdoor'
VARIANTS=['deployed_parent','fused_parent','solo_20','solo_40']


def make(name):
    if name=='deployed_parent':return parent_make(name)
    parent=parent_make('fused_core')
    if name=='fused_parent':return parent
    p=deepcopy(parent);p['id']='gota_mixed_backdoor_'+name
    p['skill']['observe']={'operator':'solo_base_defense','parameters':
        CONTRACTS['solo_base_defense'].defaults() | parent['skill']['observe']['parameters'] |
        {'backdoor_hold':int(name.split('_')[1])*24}}
    evidence=STUDY/'review.json'
    p['belief']['claims']['B_lone_base_attacker']={
        'claim':'User episode ereq_3b560872 on release.5: our Ranger(slot6) and Arcanist(slot7) '
                'lost against mixed opponents including Jordan186(Crossbowman,slot1). Jordan '
                'was visible attacking own guard31 by200seconds. Ranger stayed nearhome '
                'without engaging then left; Arcanist continued enemy siege. Both guards '
                'and own god fell by284.5seconds. Test a single visible hero targeting the '
                'god or either guard as an independent defense trigger, with explicit '
                'pursuit beyond old intercept radius. Use a short commitment after lone '
                'threats while keeping long group defense. This selected replay does not '
                'prove win improvement or that every return can arrive in time.',
        'status':'untested','evidence':[{'artifact':str(evidence),'sha256':digest(evidence.read_bytes())}]}
    p['goal']['G_defense']['preference']+=' A single observed attacker targeting the own god or either final guard takes priority over an ordinary siege; respond from any role and expire isolated-intruder duty promptly after pressure ends.'
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),
                       change='Lone core-structure attacker interrupts siege in mixed teams: '+name)
    refresh_grounding(p);return p

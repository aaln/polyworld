"""Do not downgrade an established large-rush commitment when its group shrinks."""
from copy import deepcopy
from binding import CONTRACTS
from policy_ir import digest,refresh_grounding
from mixed_backdoor import STUDY,make as base
from mixed_backdoor_assigned import make as assigned

VARIANTS=['deployed_parent','fused_parent','protected_all','protected_assigned4','protected_assigned8','protected_near']


def make(name):
    if name in ('deployed_parent','fused_parent'):return base(name)
    parent=assigned('assigned_'+name[-1]) if name.startswith('protected_assigned') else base('solo_20')
    p=deepcopy(parent);p['id']='gota_backdoor_'+name
    operator='protected_assigned_defense' if name.startswith('protected_assigned') else (
        'protected_near_defense' if name=='protected_near' else 'protected_solo_defense')
    p['skill']['observe']={'operator':operator,'parameters':CONTRACTS[operator].defaults()|parent['skill']['observe']['parameters']}
    evidence=STUDY/'screen-assigned/result.json'
    p['belief']['claims']['B_preserve_group_duty']={
        'claim':'Earlier solo-response experiments could cap an existing five-hero-rush '
                'commitment to20seconds when attackers dwindled. This violated the intended '
                'preservation of long group defense. Retain the established group deadline '
                'before considering a shorter solo duty. Test all-role, staggered-backup, '
                'and nearby-only scopes together. Prior local failures remain evidence, '
                'not successful candidates. Nearby-only cannot solve a fully unattended base.',
        'status':'untested','evidence':[{'artifact':str(evidence),'sha256':digest(evidence.read_bytes())}]}
    p['goal']['G_defense']['preference']+=' Surviving members of an observed full rush must not shorten the already-established defense commitment.'
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),change='Preserve group deadline while adding solo response: '+name)
    refresh_grounding(p);return p

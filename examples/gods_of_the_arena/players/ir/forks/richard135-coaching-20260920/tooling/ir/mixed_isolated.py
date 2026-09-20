"""Separate a backdoor intruder from a full rush before overriding targeting."""
from copy import deepcopy
from binding import CONTRACTS
from policy_ir import digest,refresh_grounding
from release_workspace import RUN
from mixed_backdoor_protected import make as parent_make
from mixed_backdoor import STUDY as PRIOR

STUDY=RUN/'coached-lanes/r5-mixed-isolated'
VARIANTS=['deployed_parent','fused_parent','isolated_all1','isolated_all2',
          'isolated_assigned4','isolated_assigned8','isolated_near1']


def make(name):
    if name in ('deployed_parent','fused_parent'):return parent_make(name)
    mode='assigned' if 'assigned' in name else 'near' if 'near' in name else 'all'
    parent=parent_make('protected_assigned'+name[-1] if mode=='assigned' else 'protected_'+mode)
    p=deepcopy(parent);p['id']='gota_'+name
    operator='isolated_solo_defense' if mode=='all' else 'isolated_'+mode+'_defense'
    p['skill']['observe']={'operator':operator,'parameters':CONTRACTS[operator].defaults() |
                          parent['skill']['observe']['parameters'] | {'isolated_max':2 if name.endswith('all2') else 1}}
    p['goal']['G_defense']['preference']=(
        'Keep existing group defense, three sentries, individual rally positions and nearby '
        'core interception. A visible isolated hero directly attacking a standing own god or '
        'guard must trigger an explicit defense response. Do not override group combat '
        'targeting with the solo rule when more than the declared isolated_max heroes cluster '
        'around the attacker. Preserve established group deadlines. Isolated duty lasts '
        '20seconds beyond the last qualifying attack. '+
        {'all':'Any of our living heroes may return from offense.',
         'assigned':'Nearby heroes respond now. Remote backups stagger by distance rank and return if no ally actually targets the attacker.',
         'near':'Only heroes already within28tiles of home gain this new response; fully unattended bases remain outside its scope.'}[mode])
    evidence=PRIOR/'local/comparison.json'
    p['belief']['claims']['B_isolate_target_override']={
        'claim':'The previous nearby response won51/60 versus deployed55/60 and fused58/60; '
                'it failed qualification. Code inspection found the lone-attacker target '
                'override also ran during full groups. Gate the complete added trigger by '
                'visible cluster size, retaining parent group targeting. Test global recall, '
                'assigned backup and nearby-only together. The suspected causal explanation '
                'requires combined evaluation, not code inspection alone.',
        'status':'untested','evidence':[{'artifact':str(evidence),'sha256':digest(evidence.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),
                       change='Restrict lone-base-attacker intervention to observed isolated groups: '+name)
    refresh_grounding(p);return p

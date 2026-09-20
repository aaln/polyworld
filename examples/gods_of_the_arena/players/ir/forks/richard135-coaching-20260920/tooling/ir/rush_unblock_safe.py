"""Version the one-pass defense repair after quarantining a VM-budget failure."""
from copy import deepcopy
from binding import CONTRACTS
from policy_ir import digest,read,refresh_grounding
from rush_unblock import STUDY


def make(name):
    if name in ('deployed_parent','spread'):
        return read(STUDY/'screen-refine/candidates'/name/'policy.ir.json')
    if name!='fused_core':raise ValueError(name)
    parent=make('spread');p=deepcopy(parent);p['id']='gota_defense_unblock_fused_core'
    p['skill']['observe']={'operator':'fused_core_defense','parameters':
                          CONTRACTS['fused_core_defense'].defaults() | parent['skill']['observe']['parameters']}
    evidence=STUDY/'local/games/near_core/762025/stderr.log'
    p['belief']['claims']['B_scan_budget']={
        'claim':'The first nearby-core repair exceeded the VM instruction budget in seed762025, '
                'slot9. It is invalid and cannot be uploaded. Fuse emergency detection into '
                'the existing active-defense enemy scan; inactive defense stays unchanged. '
                'Only visible god attackers/units within6tiles qualify, and only defenders '
                'within24tiles respond. Scope is stale sentries after an observed rush, '
                'not universal base recall. New whole-game confirmation remains required.',
        'status':'untested','evidence':[{'artifact':str(evidence),'sha256':digest(evidence.read_bytes())}]}
    p['goal']['G_defense']['preference']+=' During active defense, nearby sentries must respond to visible core attackers instead of holding an obsolete rally.'
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),
                       change='One-pass core protection during active defense, separate rally destinations')
    refresh_grounding(p);return p

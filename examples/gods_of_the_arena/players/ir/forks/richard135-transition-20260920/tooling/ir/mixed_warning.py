"""Remember a verified base attacker across its brief target switches."""
from copy import deepcopy
from binding import CONTRACTS
from policy_ir import digest,refresh_grounding
from release_workspace import RUN
from mixed_blue import make as previous

STUDY=RUN/'coached-lanes/r5-mixed-warning'


def make(name):
    if name in ('deployed_parent','fused_parent','blue_assigned'):return previous(name)
    if name!='blue_warning20':raise ValueError(name)
    parent=previous('blue_assigned');p=deepcopy(parent);p['id']='gota_blue_warning20'
    op='blue_warning_defense'
    p['skill']['observe']={'operator':op,'parameters':CONTRACTS[op].defaults()|parent['skill']['observe']['parameters']}
    evidence=RUN/'coached-lanes/r5-mixed-backdoor/target-switching.json'
    p['belief']['claims']['B_warning_starvation']={
        'claim':'Full tick replay trace confirms Jordan attacked blue guard31 in short '
                'bursts separated by gaps of5.8to6.7seconds around191to224seconds. The '
                'experimental assigned response forgets its warning after3seconds; a '
                'remote hero delayed by distance rank can repeatedly restart its warning '
                'clock. Retain warning history for20seconds while requiring a new current '
                'visible qualifying attack to act. This fixes synthetic clock starvation; '
                'actual hosted benefit is untested, and historical post-tick states are '
                'not a counterfactual policy rollout. Keep the preceding160game candidate frozen.',
        'status':'untested','evidence':[{'artifact':str(evidence),'sha256':digest(evidence.read_bytes())}]}
    p['goal']['G_defense']['preference']+=' Retain the same intruder warning for20seconds across target switches so a delayed remote backup can qualify; warning memory alone must not cause a recall.'
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),
                       change='Prevent transient target switches from starving blue backup assignment')
    refresh_grounding(p);return p

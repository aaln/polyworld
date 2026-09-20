"""Lineup-specific isolated base defense after red regressions in discovery."""
from copy import deepcopy
from binding import CONTRACTS
from policy_ir import digest,refresh_grounding
from release_workspace import RUN
from mixed_isolated import STUDY as PRIOR,make as previous

STUDY=RUN/'coached-lanes/r5-mixed-blue'


def make(name):
    if name in ('deployed_parent','fused_parent'):return previous(name)
    if name!='blue_assigned':raise ValueError(name)
    parent=previous('isolated_assigned4');p=deepcopy(parent);p['id']='gota_blue_assigned_backdoor'
    op='blue_isolated_assigned'
    p['skill']['observe']={'operator':op,'parameters':CONTRACTS[op].defaults()|parent['skill']['observe']['parameters']}
    p['goal']['G_defense']['preference']=(
        'Retain group sentries, class rally spacing and fused nearby core interception on '
        'both lineups. Add isolated-attacker response on blue only: if one visible enemy '
        'hero directly targets a standing own god or final guard within24tiles of home, '
        'nearby heroes within28tiles respond immediately. Remote backups wait4seconds '
        'per visible ally nearer home, then return if no ally actually targets the intruder. '
        'Keep20second isolated duty and preserve existing group deadlines. Red uses the '
        'fused parent with no new solo trigger. Do not override full-group combat targeting.')
    evidence=PRIOR/'screen/result.json'
    p['belief']['claims']['B_lineup_scope']={
        'claim':'In the isolated screen, assigned4and8 won10/12: blue6/6, red4/6; both parents '
                'won12/12. Red losses were against the center-rush proxy. Test blue-only '
                'assigned response and verify red action parity with the fused parent. '
                'This adaptation follows observed failures, not independent confirmation. '
                'The reported hosted episode had our Ranger and Arcanist on blue. Its '
                'mixed-roster improvement and unattended red defense remain unproven.',
        'status':'untested','evidence':[{'artifact':str(evidence),'sha256':digest(evidence.read_bytes())}]}
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),
                       change='Keep red parent behavior while testing blue assigned base response')
    refresh_grounding(p);return p

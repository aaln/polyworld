"""Avoid sacrificing every remote sieger to an isolated intrusion."""
from copy import deepcopy
from binding import CONTRACTS
from policy_ir import digest,refresh_grounding
from mixed_backdoor import STUDY,make as first_make

VARIANTS=['deployed_parent','fused_parent','assigned_4','assigned_8']


def make(name):
    if name in ('deployed_parent','fused_parent'):return first_make(name)
    parent=first_make('solo_20');p=deepcopy(parent);p['id']='gota_mixed_backdoor_'+name
    p['skill']['observe']={'operator':'assigned_solo_defense','parameters':
        CONTRACTS['assigned_solo_defense'].defaults()|parent['skill']['observe']['parameters']|
        {'response_stagger':int(name.split('_')[1])*24}}
    evidence=STUDY/'screen/result.json'
    p['belief']['claims']['B_assign_response']={
        'claim':'The first local screen rejected recalling all remote heroes: solo20won3/6 '
                'and solo40won4/6 versus both parents6/6. Keep the solo structure-attack '
                'detector, but prioritize nearby responders and stagger remote backups by '
                'distance rank. A remote hero stays on offense when another ally actually '
                'targets the intruder; an ignored threat eventually recalls a backup. '
                'Do not assume unrelated teammate policies will cooperate.',
        'status':'untested','evidence':[{'artifact':str(evidence),'sha256':digest(evidence.read_bytes())}]}
    p['goal']['G_defense']['preference']+=' Keep distant offensive pressure when an ally is demonstrably engaging the intruder; provide a delayed backup if allies ignore it.'
    p['update'].update(revision=parent['update']['revision']+1,parent=digest(parent),
                       change='Assign lone base defense with observable ally response and delayed backups: '+name)
    refresh_grounding(p);return p

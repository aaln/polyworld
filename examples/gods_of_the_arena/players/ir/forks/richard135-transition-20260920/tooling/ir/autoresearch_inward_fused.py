"""Source-equivalent scan repair for the promising sentry-rally policy."""
from copy import deepcopy
from pathlib import Path
from policy_ir import read, digest, refresh_grounding, bundle
from autoresearch_inward_rally import C, F, STUDY as RAW

STUDY = F/'inward_fused'
VARIANTS = ('parent','suppression_reference','relay_fused')


def make(name):
    if name in ('parent','suppression_reference'):
        return read(RAW/'candidates'/name/'policy.ir.json')
    assert name == 'relay_fused'
    original=read(RAW/'candidates/relay_sentries/policy.ir.json')
    p=deepcopy(original)
    p['id']='autoresearch_20260920_relay_fused'
    p['situation']['notes']+=' Wave selection is cached within the same decision from the same public object view. Zero-target validation cannot match positive object IDs. No public-object scan is truncated.'
    for claim in p['belief']['claims'].values():
        claim['claim']='Prior-source evidence; new executable requires separate equivalence and reacting validation. '+claim['claim']
    p['belief']['claims']['B_wave_work']={'status':'untested','claim':read(STUDY/'prospective.json')['hypothesis'],'evidence':[{'artifact':str(STUDY/'prospective.json'),'sha256':digest((STUDY/'prospective.json').read_bytes())}]}
    p['goal']['G_wave']['preference']+=' Preserve original nearest/retained escort semantics and stall history while avoiding duplicate traversals. Check actions, not only counts.'
    p['goal']['G_fort']['preference']=read(STUDY/'prospective.json')['confirmation']['decision_rule']
    p['skill']['observe']['operator']='lineup_inward_fused_work_v1'
    p['skill']['fallback']['operator']='lineup_fused_wave_route_v1'
    for rule in p['strategy']:
        if rule['id']=='R1' and 'G_wave' not in rule['for']:
            rule['for'].append('G_wave')
    p['execution']['game_version']='2026.9.16.5'
    p['update'].update(parent=digest(original),revision=original['update']['revision']+1,change='Same-decision wave cache and empty-target validation omission on sentry inward rallies',needs_review=['belief/B_wave_work','goal/G_wave','goal/G_fort'])
    refresh_grounding(p)
    return p


if __name__=='__main__':
    for name in VARIANTS:
        bundle(make(name),STUDY/'candidates'/name)
        print(name,'exact compile/reverse complete',flush=True)

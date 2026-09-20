"""V2 equivalent object-pass repair, with V1 native failures retained."""
from policy_ir import read, digest, refresh_grounding, bundle
from autoresearch_inward_fused import make as make_v1, C, F, RAW, VARIANTS

STUDY=F/'inward_fused_v2'


def make(name):
    p=make_v1(name)
    if name!='relay_fused':
        return p
    p['id']='autoresearch_20260920_relay_fused_v2'
    p['skill']['observe']['operator']='lineup_inward_fused_work_v2'
    p['situation']['notes']+=' Selected-object coordinates are cached at the winning public scan index; the next strategy rules see the same selected target.'
    p['belief']['claims']['B_wave_work']={'status':'untested','claim':read(STUDY/'prospective.json')['hypothesis'],'evidence':[{'artifact':str(STUDY/'prospective.json'),'sha256':digest((STUDY/'prospective.json').read_bytes())}]}
    p['update']['change']='V2 equivalent selected-object cache and unused-wave-work suppression; V1 failure retained'
    refresh_grounding(p)
    return p


if __name__=='__main__':
    for name in VARIANTS:
        bundle(make(name),STUDY/'candidates'/name)
        print(name,'exact compile/reverse complete',flush=True)

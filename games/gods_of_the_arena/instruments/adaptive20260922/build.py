"""Create a new portable candidate; never mutate a deployed IR/source pair."""
import argparse
import json
import pprint
import shutil
from pathlib import Path
import adaptive_binding as binding

ROOT, PARENT, HERE = binding.ROOT, binding.PARENT, binding.HERE
STUDY = ROOT.parent/'polyworld/tmp/gota-adaptive-score-20260922'


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2)+'\n')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--variant',choices=['spell-targeting','spell-pressure'],required=True);args=parser.parse_args()
    out=STUDY/args.variant
    assert not out.exists(), 'Preserve every candidate'
    p=json.loads((PARENT/'policy.ir.json').read_text())
    ir=binding.ir;parent_digest=ir.digest(p)
    specs=binding.configure()
    p['id']='gota_adaptive_'+args.variant.replace('-','_')
    p['execution']['binding']=binding.VERSION
    p['execution']['game_version']='2026.9.22.3'
    p['situation']['notes']+=' Independent public spell target; optional higher hero basic-target priority; no hidden player identity or lifetime-XP input. Own lifetime XP is not exposed by this host BASIC API.'
    p['goal']['Score']['preference']='Sole objective: maximize final individual max(0, lifetime XP*1440 -200*world_ticks)//1440. Hero kill150XP, shared creep pool15XP, building100XP, enemy god destruction500XP for every teammate. Prefer productive kills and farming; elapsed time always costs200/minute. Survival, items and portals matter only through their contribution to this objective.'
    p['goal']['Win']['preference']='No independent victory incentive. Enemy-god destruction supplies500 own XP and avoids later elapsed-time cost. Keep the baseline structure targeting in this experiment; do not idle merely to lengthen games.'
    p['skill']={k:{'operator':'adaptive_'+k,'parameters':v.defaults()} for k,v in specs.items()}
    p['skill']['observe']['parameters']['hero_priority_bonus']=480 if args.variant=='spell-pressure' else 80
    old={x['id'][2:]:x for x in p['strategy']}
    p['strategy']=[dict(old.get(k,{'id':'R_'+k,'when':'active','skill':k}), **{'for':['Score']}) for k in specs]
    p['belief']['claims']={
        'OpportunityMechanism':{'claim':'Independent public hero spell attempts produce legal damaging casts when the basic target is unreachable or is a creep, with fallback on rejection. Mana restore abilities are used when beneficial. Basic hero priority parameter is frozen per variant.','status':'requires_review','evidence':[{'artifact':'evidence/practice.json'}]},
        'PortalPreserved':{'claim':'The new target controller preserves the parent portal fixture behavior.','status':'requires_review','evidence':[{'artifact':'evidence/portals.json'}]},
        'CompetitiveGain':{'claim':'The new source improves aggregate individual score at least10% while retaining95% on each color versus fresh deployed-source controls.','status':'requires_review','evidence':[{'artifact':'evidence/screen-plan.json'}]}}
    p['update']={'revision':1,'parent':parent_digest,'change':{'origin':'User: keep improving individual points as opponents change; Richard167 and khors114. Current clean replay diagnosis and preserved failed f6a0dace bundle.'},'needs_review':['belief/'+k for k in p['belief']['claims']],'evidence':[{'artifact':'evidence/experiment.md'}]}
    ir.refresh_grounding(p);source=ir.compile_policy(p)
    assert ir.extract(source,p)==p
    out.mkdir(parents=True)
    for name,v in [('policy.ir.json',p),('extracted.ir.json',p),('semantics.json',ir.grounded(p))]:write(out/name,v)
    (out/'policy.py').write_text('POLICY = '+pprint.pformat(p,width=110,sort_dicts=False)+'\n')
    (out/'policy.bas').write_text(source)
    shutil.copytree(PARENT/'tooling',out/'tooling',ignore=shutil.ignore_patterns('__pycache__'))
    (out/'tooling/adaptive20260922').mkdir()
    shutil.copy2(HERE/'adaptive_binding.py',out/'tooling/adaptive20260922/adaptive_binding.py')
    converter=(PARENT/'convert.py').read_text().replace('tooling/portals20260922','tooling/adaptive20260922').replace('import portal_binding\nportal_binding.configure()\nir = portal_binding.ir','import adaptive_binding\nadaptive_binding.configure()\nir = adaptive_binding.ir')
    (out/'convert.py').write_text(converter)
    write(out/'manifest.json',{'source_sha256':ir.digest(source.encode()),'ir_sha256':ir.digest(p),'binding':binding.VERSION,'parent_source_sha256':ir.digest((PARENT/'policy.bas').read_bytes()),'engine_commit':'1b70894436b7ffdcd0d421b6b32c2415c9c8bfde','game_version':'2026.9.22.3','hosted_complete':False,'score_gate_passed':None})
    print(json.dumps({'out':str(out),**json.loads((out/'manifest.json').read_text())}))


if __name__=='__main__':main()

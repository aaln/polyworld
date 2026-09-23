"""Save reviewed IR with byte-identical tested policy; keep every input snapshot."""
from pathlib import Path
import json,shutil,hashlib,pprint,subprocess,sys
import blue_binding as b
ROOT,HERE=b.ROOT,b.HERE
STUDY=ROOT.parent/'polyworld/tmp/gota-blue-khors-20260923'
OUT=ROOT/'examples/gods_of_the_arena/players/ir/forks/blue-center20260923-hosted'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def main():
    report=read(STUDY/'trial/report.json');assert report['complete'] and report['games']==400
    assert not OUT.exists(),'Preserve existing capsule'
    OUT.mkdir(parents=True)
    evidence=OUT/'evidence';evidence.mkdir()
    for name in ['diagnosis-class.json','opening-samples.png','local-summary.json','native-plan.json','native-result.json','red-equivalence.json','runtime-provenance.json','start.json','conversion-proof.json','source-discovery.json','practice-provenance.json','skill-difference.json','prospective-experiment.md','baseline-practice.json']:
        shutil.copy2(STUDY/name,evidence/name)
    shutil.copy2(ROOT/'games/gods_of_the_arena/experiments/2026-09-23-blue-center.md',evidence/'experiment.md')
    for name in ['plan.json','result.json','report.json','field-changes.json','effects-plan.json','effects-summary.json','score-breakdown.png']:
        (evidence/'trial').mkdir(exist_ok=True);shutil.copy2(STUDY/'trial'/name,evidence/'trial'/name)
    for label in ['field-before','field-after']:
        (evidence/'trial'/label).mkdir()
        for name in ['snapshot.json','game.json','leaderboard.json']:shutil.copy2(STUDY/'trial'/label/name,evidence/'trial'/label/name)
    for arm in read(STUDY/'trial/plan.json')['arms']:
        src=STUDY/'trial'/arm['name']/str(arm['side']);dst=evidence/'trial'/arm['name']/str(arm['side']);dst.mkdir(parents=True)
        for name in ['arm.json','request.json','episodes.json','review.json']:shutil.copy2(src/name,dst/name)
        shutil.copy2(src/'batch/created.json',dst/'created.json')
    shutil.copytree(STUDY/'initial-r1/blue-center',OUT/'initial-r1',ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copy2(STUDY/'initial-r1/blue-center-portals.json',evidence/'initial-r1-portals.json')
    write(evidence/'initial-r1-verdict.json',{'status':'rejected_local','failed_portal_cases':2,'why':'Central outward movement persisted through the critical keep recovery throttle, escaping the keep then spending a scroll. Correct the coordinated recovery handoff before hosted evaluation.','hosted_games':0})
    parent=STUDY/'blue-center';dst=OUT/'blue-center';shutil.copytree(parent,dst,ignore=shutil.ignore_patterns('__pycache__'))
    b.configure();ir=b.ir;p=read(parent/'policy.ir.json');old=ir.digest(p);entry=report['candidates'][0]
    p['belief']['claims']['RouteMechanism'].update(status='supported',claim='All100 actual opening contexts pass across ten classes/two teams/five ordinals; two full native red command streams and terminal states match the parent. Only blue lead ranged advance and immediate critical keep recovery change. This proves bounded command semantics, not competitive strength.',evidence=[{'artifact':'evidence/practice.json'},{'artifact':'evidence/red-equivalence.json'}])
    p['belief']['claims']['InheritedMechanics'].update(status='supported',claim='All180 buyback,84portal,126broader host checks and8complete native games pass on the frozen engine. Route-only r1 failed2portal cases and is separately preserved; r2 fixes the recovery handoff. Native score does not qualify competitive deployment.',evidence=[{'artifact':'evidence/local-summary.json'}])
    p['belief']['claims']['CompetitiveGain'].update(status='supported' if report['deployment_qualified'] else 'contradicted' if not entry['score_gate_passed'] else 'requires_review',claim=f"400 fresh games: aggregate {entry['aggregate_gain_percent']:.3f}%, colors {entry['per_color_gain_percent']}, aggregate95%CI {entry['gain_ci95_percent']}, blue95%CI {entry['blue_gain_ci95_percent']}, blue mean gap to khors114 {entry['blue_mean_khors_gap']}. Original aggregate/red/blue/confidence and field qualification: {report['deployment_qualified']}. Fixed first-team-seat mixed roster; no permanent rank, later-draft or separate-component causality.",evidence=[{'artifact':'evidence/trial-report.json'}])
    p['update']={'revision':2,'parent':old,'change':{'origin':'Completed local and hosted evidence reflected into IR; frozen executable bytes unchanged','deployment_qualified':report['deployment_qualified']},'needs_review':['belief/CompetitiveGain'] if p['belief']['claims']['CompetitiveGain']['status']=='requires_review' else [],'evidence':[{'artifact':'evidence/trial-report.json'}]}
    ir.refresh_grounding(p);source=(parent/'policy.bas').read_text();assert ir.compile_policy(p)==source and ir.extract(source,p)==p
    for name,v in [('policy.ir.json',p),('extracted.ir.json',p),('semantics.json',ir.grounded(p))]:write(dst/name,v)
    (dst/'policy.py').write_text('POLICY = '+pprint.pformat(p,width=110,sort_dicts=False)+'\n')
    ev=dst/'evidence';ev.mkdir(exist_ok=True)
    for name in ['practice','buyback','portals','scenarios']:shutil.copy2(STUDY/('blue-center-'+name+'.json'),ev/(name+'.json'))
    for name in ['local-summary.json','red-equivalence.json']:shutil.copy2(STUDY/name,ev/name)
    shutil.copy2(STUDY/'trial/report.json',ev/'trial-report.json')
    write(ev/'parent-and-inputs.json',{'parent_pair':str(b.PARENT.relative_to(ROOT)),'parent_source_sha256':sha(b.PARENT/'policy.bas'),'initial_ir':read(parent/'policy.ir.json'),'raw_root':str(STUDY),'coaching_session':'/Users/aaln/Documents/Policy Loops/sessions/2026-09-22t16-43-56-076z862811','preserved_initial_route_failure':'../initial-r1','scope':'Original captures and initial source/IR remain unchanged; feedback revises semantic claims only.'})
    verifier='''from pathlib import Path
import json,hashlib,sys
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'tooling/bluekhors20260923'))
import blue_binding as b
b.configure();ir=b.ir
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(P/'manifest.json');p=read(P/'policy.ir.json');source=(P/'policy.bas').read_text()
assert ir.compile_policy(p)==source and ir.extract(source,p)==p
assert ir.digest(p)==m['ir_sha256'] and sha(P/'policy.bas')==m['source_sha256']
for path,digest in m['artifacts'].items():assert sha(P/path)==digest,path
for name in ['practice','buyback','portals']:assert all(r['passed'] for r in read(P/'evidence'/(name+'.json'))['rows'])
assert read(P/'evidence/scenarios.json')['passed']
print(json.dumps({'verified':True,'source_sha256':m['source_sha256'],'ir_sha256':m['ir_sha256'],'deployment_qualified':m['deployment_qualified']}))
'''
    (dst/'verify.py').write_text(verifier)
    (dst/'README.md').write_text(f"# Blue central route with immediate keep recovery\n\n400-game trial gain {entry['aggregate_gain_percent']:+.2f}%; blue gain {entry['per_color_gain_percent'][1]:+.2f}%. Deployment qualified: {report['deployment_qualified']}. Read evidence/trial-report.json for confidence and rival gaps.\n\nRun `python verify.py`; use `convert.py compile --out /new/path` or `convert.py extract --source policy.bas --out /new/path`. Changes to executable bytes invalidate the hosted evidence. Original IR and failed route-only source remain preserved.\n")
    manifest=read(parent/'manifest.json');manifest.update(ir_sha256=ir.digest(p),hosted_complete=True,score_gate_passed=entry['score_gate_passed'],deployment_qualified=report['deployment_qualified'])
    manifest['artifacts']={str(f.relative_to(dst)):sha(f) for f in dst.rglob('*') if f.is_file() and f.name!='manifest.json' and '__pycache__' not in f.parts};write(dst/'manifest.json',manifest)
    subprocess.run([sys.executable,str(dst/'verify.py')],check=True)
    write(evidence/'artifact-index.json',{'raw_root':str(STUDY),'artifacts':{str(f.relative_to(STUDY)):sha(f) for f in (STUDY/'trial').rglob('*') if f.is_file() and f.suffix not in ['.log','.tmp']}})
    write(OUT/'summary.json',{'trial':entry,'deployment_qualified':report['deployment_qualified'],'source_sha256':manifest['source_sha256'],'ir_sha256':manifest['ir_sha256']})
    print(OUT)
if __name__=='__main__':main()

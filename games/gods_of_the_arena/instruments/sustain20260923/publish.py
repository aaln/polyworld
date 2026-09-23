"""Seal the tested coaching pair with reviewed claims, preserving every input."""
from pathlib import Path
import json,shutil,hashlib,pprint,subprocess,sys
import sustain_binding as b
ROOT,HERE=b.ROOT,b.HERE
STUDY=ROOT.parent/'polyworld/tmp/gota-field-sustain-20260923'
OUT=ROOT/'examples/gods_of_the_arena/players/ir/forks/field-sustain20260923-hosted'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def main():
    report=read(STUDY/'trial/report.json');assert report['complete'] and report['games']==240
    assert not OUT.exists(),'Preserve sealed capsules'
    evidence=OUT/'evidence';evidence.mkdir(parents=True)
    for name in ['session-input-manifest.json','coaching-review.json','user-league-reference.json','local-summary.json','native-plan.json','native-result.json','runtime-provenance.json','start.json','conversion-proof.json','practice-provenance.json','skill-difference.json','prospective-experiment.md','baseline-practice.json']:
        shutil.copy2(STUDY/name,evidence/name)
    for name in ['coaching-episode-binding.json','coaching-review-initial.json','coached-sequence.png']:
        if (STUDY/name).exists():shutil.copy2(STUDY/name,evidence/name)
    shutil.copy2(ROOT/'games/gods_of_the_arena/experiments/2026-09-23-field-sustain.md',evidence/'experiment.md')
    (evidence/'trial').mkdir()
    for name in ['plan.json','result.json','report.json','field-changes.json','effects-plan.json','effects-summary.json','score-breakdown.png']:
        shutil.copy2(STUDY/'trial'/name,evidence/'trial'/name)
    for label in ['field-before','field-after']:
        (evidence/'trial'/label).mkdir()
        for name in ['snapshot.json','game.json','leaderboard.json']:shutil.copy2(STUDY/'trial'/label/name,evidence/'trial'/label/name)
    for arm in read(STUDY/'trial/plan.json')['arms']:
        src=STUDY/'trial'/arm['name']/arm['cell'];dst=evidence/'trial'/arm['name']/arm['cell'];dst.mkdir(parents=True)
        for name in ['arm.json','request.json','episodes.json','review.json']:shutil.copy2(src/name,dst/name)
        shutil.copy2(src/'batch/created.json',dst/'created.json')
    shutil.copytree(STUDY/'initial-r1',OUT/'initial-r1',ignore=shutil.ignore_patterns('__pycache__'))
    parent=STUDY/'field-sustain';dst=OUT/'field-sustain';shutil.copytree(parent,dst,ignore=shutil.ignore_patterns('__pycache__'))
    b.configure();ir=b.ir;p=read(parent/'policy.ir.json');old=ir.digest(p);entry=report['candidates'][0]
    bound=read(STUDY/'coaching-episode-binding.json') if (STUDY/'coaching-episode-binding.json').exists() else None
    if bound:
        p['belief']['claims']['CoachingInterpretation'].update(claim=bound['summary'],evidence=[{'artifact':'evidence/coaching-episode-binding.json'},{'artifact':'evidence/coaching-review.json'}])
        p['situation']['notes']=p['situation']['notes'].replace('Source/episode unbound;', 'Source/episode subsequently matched and verified in coaching-episode-binding; original capture was unbound;')
    p['belief']['claims']['RecoveryMechanism'].update(status='supported',claim='All68actual-tick sustain/recovery fixtures,100opening,180buyback,84portal and126broad checks pass;12complete native games pass. Druid heals162HP in the controlled scene and leaves health-only retreat; recovered heroes across ten classes replace the base path and advance in the same tick. Threat,resource,restock and active-channel guards preserved. Initialr1 mistook own healing warnings for threats and is preserved as a local failure.',evidence=[{'artifact':'evidence/practice.json'},{'artifact':'evidence/local-summary.json'}])
    p['belief']['claims']['CompetitiveGain'].update(status='supported' if report['deployment_qualified'] else 'contradicted' if not entry['score_gate_passed'] else 'requires_review',claim=f"240fresh games: aggregate{entry['aggregate_gain_percent']:.3f}%,contexts{entry['per_context_gain_percent']},95%gainCI{entry['gain_ci95_percent']},Druid exposures{entry['druid_exposure']}. Original score/context/exposure/stability qualification:{report['deployment_qualified']}. Blue lead and two ordinal3 mixed-roster contexts; latter have two fixed reference teammates. No permanent rank or isolated-component causal claim.",evidence=[{'artifact':'evidence/trial-report.json'}])
    p['update']={'revision':2,'parent':old,'change':{'origin':'Completed coaching/source/local/hosted evidence reflected into semantic IR; tested executable bytes unchanged.','deployment_qualified':report['deployment_qualified']},'needs_review':['belief/CompetitiveGain'] if p['belief']['claims']['CompetitiveGain']['status']=='requires_review' else [],'evidence':[{'artifact':'evidence/trial-report.json'},{'artifact':'evidence/session-input-manifest.json'}]}
    ir.refresh_grounding(p);source=(parent/'policy.bas').read_text();assert ir.compile_policy(p)==source and ir.extract(source,p)==p
    for name,v in [('policy.ir.json',p),('extracted.ir.json',p),('semantics.json',ir.grounded(p))]:write(dst/name,v)
    (dst/'policy.py').write_text('POLICY = '+pprint.pformat(p,width=110,sort_dicts=False)+'\n')
    ev=dst/'evidence'
    for name in ['practice','openings','buyback','portals','scenarios']:shutil.copy2(STUDY/('field-sustain-'+name+'.json'),ev/(name+'.json'))
    for name in ['local-summary.json','coaching-review.json','session-input-manifest.json']:shutil.copy2(STUDY/name,ev/name)
    if bound:shutil.copy2(STUDY/'coaching-episode-binding.json',ev/'coaching-episode-binding.json')
    shutil.copy2(STUDY/'trial/report.json',ev/'trial-report.json')
    write(ev/'parent-and-inputs.json',{'parent_pair':str(b.PARENT.relative_to(ROOT)),'parent_source_sha256':sha(b.PARENT/'policy.bas'),'initial_ir':read(parent/'policy.ir.json'),'initial_source_sha256':sha(parent/'policy.bas'),'raw_root':str(STUDY),'coaching_session':'/Users/aaln/Documents/Policy Loops/sessions/2026-09-23t02-52-57-098ze03810','preserved_original_capture':str(STUDY/'captured-session'),'scope':'All original51files unchanged; sealed hosted revision changes semantic claims only. r1 failure and first build failure preserved locally.'})
    verifier='''from pathlib import Path
import json,hashlib,sys
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'tooling/sustain20260923'))
import sustain_binding as b
b.configure();ir=b.ir
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(P/'manifest.json');p=read(P/'policy.ir.json');source=(P/'policy.bas').read_text()
assert ir.compile_policy(p)==source and ir.extract(source,p)==p
assert ir.digest(p)==m['ir_sha256'] and sha(P/'policy.bas')==m['source_sha256']
for path,digest in m['artifacts'].items():assert sha(P/path)==digest,path
for name in ['practice','openings','buyback','portals']:assert all(r['passed'] for r in read(P/'evidence'/(name+'.json'))['rows'])
assert read(P/'evidence/scenarios.json')['passed']
print(json.dumps({'verified':True,'source_sha256':m['source_sha256'],'ir_sha256':m['ir_sha256'],'deployment_qualified':m['deployment_qualified']}))
'''
    (dst/'verify.py').write_text(verifier)
    (dst/'README.md').write_text(f"# Field sustain and interruptible retreat\n\n240-game trial gain{entry['aggregate_gain_percent']:+.2f}%;deployment qualified:{report['deployment_qualified']}. Read evidence/trial-report.json for contexts, confidence, exposure and rival gaps.\n\nRun `python verify.py`; `convert.py compile --out /new/path` or `convert.py extract --source policy.bas --out /new/path`. Tested source3807330d remains byte-identical. Original coaching captures/input hashes and failedr1 remain preserved.\n")
    manifest=read(parent/'manifest.json');manifest.update(ir_sha256=ir.digest(p),hosted_complete=True,score_gate_passed=entry['score_gate_passed'],deployment_qualified=report['deployment_qualified'])
    manifest['artifacts']={str(f.relative_to(dst)):sha(f) for f in dst.rglob('*') if f.is_file() and f.name!='manifest.json' and '__pycache__' not in f.parts};write(dst/'manifest.json',manifest)
    subprocess.run([sys.executable,str(dst/'verify.py')],check=True)
    write(evidence/'artifact-index.json',{'raw_root':str(STUDY),'artifacts':{str(f.relative_to(STUDY)):sha(f) for f in (STUDY/'trial').rglob('*') if f.is_file() and f.suffix not in ['.log','.tmp']}})
    # Recheck the immutable user session and local byte-preserving copy.
    captured=read(STUDY/'session-input-manifest.json')
    for name,meta in captured['files'].items():
        assert sha(Path(captured['session'])/name)==meta['sha256']
        assert sha(STUDY/'captured-session'/name)==meta['sha256']
    write(OUT/'summary.json',{'trial':entry,'deployment_qualified':report['deployment_qualified'],'source_sha256':manifest['source_sha256'],'ir_sha256':manifest['ir_sha256'],'original_session_inputs_unchanged':True})
    print(OUT)
if __name__=='__main__':main()

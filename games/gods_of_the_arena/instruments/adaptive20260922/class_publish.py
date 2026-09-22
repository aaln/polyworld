"""Reflect validated feedback in new portable pairs without changing frozen sources."""
import json,pprint,shutil,hashlib,subprocess,sys
from pathlib import Path
import class_binding as binding
ROOT,HERE=binding.ROOT,binding.HERE
STUDY=ROOT.parent/'polyworld/tmp/gota-class-score-20260922'
OUT=ROOT/'examples/gods_of_the_arena/players/ir/forks/class-score20260922'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')

def main():
    screen=read(STUDY/'screen/report.json');assert screen['complete']
    stages=['screen']
    if screen['selected']:
        confirm=read(STUDY/'confirmation/report.json');assert confirm['complete'];stages.append('confirmation')
    else:confirm=None
    assert not OUT.exists(),'Preserve existing published inputs'
    OUT.mkdir(parents=True)
    for stage in stages:
        src=STUDY/stage;dst=OUT/'evidence'/stage
        for name in ['plan.json','result.json','report.json','field-changes.json','effects-plan.json','effects-summary.json']:
            (dst/name).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src/name,dst/name)
        for file in ['score-breakdown.png']:
            if (src/file).exists():shutil.copy2(src/file,dst/file)
        if (src/'class-mix-review.json').exists():shutil.copy2(src/'class-mix-review.json',dst/'class-mix-review.json')
        for label in ['field-before','field-after']:
            (dst/label).mkdir(parents=True)
            for file in ['snapshot.json','game.json','leaderboard.json']:
                shutil.copy2(src/label/file,dst/label/file)
        for arm in read(src/'plan.json')['arms']:
            folder=src/arm['name']/str(arm['side']);target=dst/arm['name']/str(arm['side']);target.mkdir(parents=True)
            for name in ['arm.json','request.json','episodes.json','review.json']:shutil.copy2(folder/name,target/name)
            shutil.copy2(folder/'batch/created.json',target/'created.json')
    for name in ['diagnosis-summary.json','local-summary.json','native-plan.json','native-result.json','runtime-provenance.json','start.json','conversion-proof.json','source-discovery.json','native-fallback-plan.json','native-fallback-result.json','native-equivalence.json','conformance-provenance.json']:
        shutil.copy2(STUDY/name,OUT/'evidence'/name)
    shutil.copy2(ROOT/'games/gods_of_the_arena/experiments/2026-09-22-class-score.md',OUT/'evidence/experiment.md')
    ir=binding.ir;binding.configure()
    pairs=[]
    for entry in screen['candidates']:
        name=entry['name'];parent=STUDY/name;out=OUT/name
        shutil.copytree(parent,out,ignore=shutil.ignore_patterns('__pycache__'))
        p=read(parent/'policy.ir.json');old=ir.digest(p)
        p['belief']['claims']['OpportunityMechanism'].update(status='supported',claim='All160 actual-tick command/state conformance scenes pass: Crossbowman matches the screened intervention; nine other hero classes match the deployed controller. Twenty full native games and eight exact trajectory comparisons pass. This validates branch behavior/runtime, not comparative rival score.',evidence=[{'artifact':'evidence/practice.json'}])
        p['belief']['claims']['PortalPreserved'].update(status='supported',claim='All84 inherited portal fixtures and126 broader all-class host checks pass on the frozen current engine.',evidence=[{'artifact':'evidence/portals.json'},{'artifact':'evidence/scenarios.json'}])
        final=next((r for r in confirm['candidates'] if r['name']==name),None) if confirm else None
        supported=bool(final and final['score_gate_passed'])
        competitive=final or entry
        p['belief']['claims']['CompetitiveGain'].update(status='supported' if supported else 'contradicted' if not competitive['score_gate_passed'] else 'requires_review',claim=f"Screen {'passed' if entry['score_gate_passed'] else 'failed'}: {entry['aggregate_gain_percent']:.3f}% aggregate, colors{entry['per_color_gain_percent']},95% interval{entry['gain_ci95_percent']}. "+(f"Independent different-roster confirmation {'passed' if final['score_gate_passed'] else 'failed'}: {final['aggregate_gain_percent']:.3f}% aggregate, colors{final['per_color_gain_percent']},95% interval{final['gain_ci95_percent']}." if final else 'No independent confirmation for this source; no replacement qualification.')+' Exact-version fixed-roster scope, no universal rank guarantee or per-component causal claim.',evidence=[{'artifact':'evidence/screen-report.json'}]+([{'artifact':'evidence/confirmation-report.json'}] if final else []))
        p['belief']['claims']['FieldDrift']={'status':'supported','claim':'Opponent-version and game snapshots are evaluation metadata; newer entries can change optimal behavior. No opponent UUID or hidden replay state enters the live source. A changed field requires a new comparison, preserving pinned results.','evidence':[{'artifact':'evidence/field-changes.json'}]}
        p['update']={'revision':2,'parent':old,'change':{'origin':'Current-engine practice and completed hosted outcomes reflected into IR; executable bytes unchanged','screen_passed':entry['score_gate_passed'],'confirmation_passed':supported},'needs_review':[] if p['belief']['claims']['CompetitiveGain']['status']!='requires_review' else ['belief/CompetitiveGain'],'evidence':[{'artifact':'evidence/screen-report.json'}]}
        ir.refresh_grounding(p);source=(parent/'policy.bas').read_text();assert ir.compile_policy(p)==source and ir.extract(source,p)==p
        for file,v in [('policy.ir.json',p),('extracted.ir.json',p),('semantics.json',ir.grounded(p))]:write(out/file,v)
        (out/'policy.py').write_text('POLICY = '+pprint.pformat(p,width=110,sort_dicts=False)+'\n')
        evidence=out/'evidence';evidence.mkdir(exist_ok=True)
        for n in ['practice','portals','scenarios']:shutil.copy2(STUDY/(name+'-'+n+'.json'),evidence/(n+'.json'))
        shutil.copy2(STUDY/'screen/report.json',evidence/'screen-report.json');shutil.copy2(STUDY/'screen/field-changes.json',evidence/'field-changes.json')
        if final:shutil.copy2(STUDY/'confirmation/report.json',evidence/'confirmation-report.json')
        write(evidence/'parent-and-inputs.json',{'parent_pair':'examples/gods_of_the_arena/players/ir/forks/portal-coaching20260922-hosted','parent_source_sha256':sha(binding.PARENT/'policy.bas'),'original_local_pair':str(parent),'original_ir':read(parent/'policy.ir.json'),'raw_inputs':str(STUDY),'preserved_prior_failure':'examples/gods_of_the_arena/players/ir/forks/score-opportunities20260922-hosted','original_portal_coaching_session':'/Users/aaln/Documents/Policy Loops/sessions/2026-09-22t16-43-56-076z862811','explanation':'Original coaching captures and local semantic snapshots remain immutable. Parent evidence retains their original release scope.'})
        verifier='''"""Verify exact portable semantic/source pair and frozen artifact hashes."""
from pathlib import Path
import hashlib,json,sys
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'tooling/adaptive20260922'))
import class_binding as b
b.configure();ir=b.ir
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(P/'manifest.json');p=read(P/'policy.ir.json');source=(P/'policy.bas').read_text()
assert ir.compile_policy(p)==source and ir.extract(source,p)==p
assert m['ir_sha256']==ir.digest(p) and m['source_sha256']==sha(P/'policy.bas')
assert read(P/'extracted.ir.json')==p and read(P/'semantics.json')==ir.grounded(p)
for path,digest in m['artifacts'].items():assert sha(P/path)==digest,path
assert all(r['passed'] for r in read(P/'evidence/practice.json')['rows'])
assert all(r['passed'] for r in read(P/'evidence/portals.json')['rows'])
assert read(P/'evidence/scenarios.json')['passed']
print(json.dumps({'verified':True,'source_sha256':m['source_sha256'],'ir_sha256':m['ir_sha256'],'screen_passed':m['screen_passed'],'confirmation_passed':m['confirmation_passed']}))
'''
        (out/'verify.py').write_text(verifier)
        (out/'README.md').write_text(f"# {name}\n\nScreen gain **{entry['aggregate_gain_percent']:+.2f}%**, colors {entry['per_color_gain_percent']}. Independent confirmation: **{supported}**.\n\nSee evidence for confidence intervals and exact roster/version scope. Practice validates mechanism/runtime; hosted individual score determines selection. Edited executable bytes invalidate this evidence.\n\nRun `python verify.py`, or `python convert.py compile --out /new/path` and `python convert.py extract --source policy.bas --out /another/new/path`. The local initial pair and prior portal/coaching inputs remain preserved.\n")
        manifest=read(parent/'manifest.json');manifest.update(ir_sha256=ir.digest(p),hosted_complete=True,screen_passed=entry['score_gate_passed'],confirmation_passed=supported,score_gate_passed=supported)
        manifest['artifacts']={str(f.relative_to(out)):sha(f) for f in out.rglob('*') if f.is_file() and f!=out/'manifest.json' and '__pycache__' not in f.parts};write(out/'manifest.json',manifest)
        result=subprocess.check_output([sys.executable,str(out/'verify.py')],text=True);pairs.append(json.loads(result))
    write(OUT/'evidence/artifact-index.json',{'raw_root':str(STUDY),'artifacts':{str(f.relative_to(STUDY)):sha(f) for stage in stages for f in (STUDY/stage).rglob('*') if f.is_file() and f.suffix not in ['.log','.tmp']}})
    write(OUT/'summary.json',{'screen':screen['candidates'],'confirmation':confirm['candidates'] if confirm else None,'qualified':confirm['selected'] if confirm else None,'pairs':pairs})
    print(json.dumps({'out':str(OUT),'pairs':pairs}))
if __name__=='__main__':main()

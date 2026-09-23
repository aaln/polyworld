"""Seal the generated pair and reflect practiced behavior without claiming score gain."""
import hashlib,json,pprint,shutil,subprocess,sys
from pathlib import Path
import blue_siege_binding as b
ROOT=b.ROOT;STUDY=ROOT.parent/'polyworld/tmp/gota-blue-druid-siege-20260923';OUT=ROOT/'examples/gods_of_the_arena/players/ir/forks/blue-druid-siege20260923-local'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def main():
 assert not OUT.exists(),'Preserve sealed pair'
 assert read(STUDY/'local-summary.json')['passed'] and read(STUDY/'native-result.json')['passed']
 src=STUDY/'blue-druid-siege';pair=OUT/'blue-druid-siege';shutil.copytree(src,pair,ignore=shutil.ignore_patterns('__pycache__'))
 ev=pair/'evidence'
 shutil.copy2(b.PARENT/'evidence/coaching-review.json',ev/'coaching-review.json')
 shutil.copy2(b.PARENT/'policy.ir.json',ev/'parent-reviewed.ir.json')
 # The source snapshot is immutable; add the independent explanatory review and verifier.
 for name in ['README.md','verify.py']:shutil.copy2(ROOT/'docs/opponents/richard-v174/source-audit-20260923'/name,ev/'opponent'/name)
 for name in ['local-summary.json','native-plan.json','native-result.json','runtime-provenance.json','conversion-proof.json','prospective-experiment.md','skill-difference.json','baseline-practice.json','preflight.json','equivalence.json','druid-native-plan.json','druid-native-result.json','reference-defer-druid.bas']:
  shutil.copy2(STUDY/name,ev/name)
 for label in ['practice','recovery','openings','buyback','portals','scenarios']:shutil.copy2(STUDY/f'blue-druid-siege-{label}.json',ev/f'{label}.json')
 shutil.copy2(STUDY/'trial/plan.json',ev/'hosted-plan.json')
 write(ev/'initial-ir.json',read(src/'policy.ir.json'))
 write(ev/'native-artifact-index.json',{'raw_root':str(STUDY),'artifacts':{str(p.relative_to(STUDY)):sha(p) for p in (STUDY/'native').rglob('*') if p.is_file()}})
 write(ev/'preserved-local-revisions.json',{'raw_root':str(STUDY),'artifacts':{str(p.relative_to(STUDY)):sha(p) for p in (STUDY/'local-revisions').rglob('*') if p.is_file() and '__pycache__' not in p.parts},'reason':'r1 used undefined Druid rather than host DruidWarden;80scene checks exposed the incorrect class scope. r2 fixes that enum. No hosted games used r1. Original16native matches did not expose a Druid subject;8additional matches explicitly provide Druid availability.'})
 write(ev/'practice-provenance.json',{'source_sha256':sha(ROOT/'games/gods_of_the_arena/instruments/bluesiege20260923/practice.nim'),'binary_sha256':sha(STUDY/'practice'),'effect_source_sha256':sha(ROOT/'games/gods_of_the_arena/instruments/bluesiege20260923/source_probe.nim'),'effect_binary_sha256':sha(STUDY/'effect-probe-r2')})
 b.configure();ir=b.ir;p=read(src/'policy.ir.json');initial=ir.digest(p)
 p['belief']['claims']['RecoveryMechanism'].update(status='supported',claim='The inherited Druid recovery component is byte-for-byte unchanged. Its92 actual-tick recovery cases pass on this complete new source; the previous Druid-only hosted result belongs to the parent pair. The coordinated siege skill is restricted to blue Druids. Ten unaffected full-match pairs, including red Druids, retain exact command tapes and terminal world state; these are tested contexts, not an exhaustive all-state proof.',evidence=[{'artifact':'evidence/recovery.json'},{'artifact':'evidence/parent-reviewed.ir.json'},{'artifact':'evidence/equivalence.json'}])
 p['belief']['claims']['RichardSourceTransfer'].update(status='supported',claim='Richard source identity and ordering are verified over82818commands in4Warlock games. Our broader retrospective diagnosis finds109 guarded tower opportunities. Scope and target selection pass80 actual-host scenes on four classes and both colors, together with582 inherited checks and24 complete native matches, including active blue Druids and10 unaffected command/world-equivalent pairs. Source identity, runtime and intended guarded choices are supported; competitive value of the coordinated transfer remains unvalidated.',evidence=[{'artifact':'evidence/opponent/richard_v174.source.ir.json'},{'artifact':'evidence/own-diagnosis.json'},{'artifact':'evidence/practice.json'},{'artifact':'evidence/local-summary.json'}])
 p['update']={'revision':2,'parent':initial,'change':{'origin':'Practiced coordinated behavior reflected into IR; frozen BASIC unchanged.'},'needs_review':['belief/CompetitiveGain'],'evidence':[{'artifact':'evidence/local-summary.json'},{'artifact':'evidence/hosted-plan.json'}]}
 ir.refresh_grounding(p);source=(src/'policy.bas').read_text();assert ir.compile_policy(p)==source and ir.extract(source,p)==p
 for name,value in [('policy.ir.json',p),('extracted.ir.json',p),('semantics.json',ir.grounded(p))]:write(pair/name,value)
 (pair/'policy.py').write_text('POLICY = '+pprint.pformat(p,width=110,sort_dicts=False)+'\n')
 (pair/'convert.py').write_text((pair/'convert.py').read_text().replace('draft-only current-game','current-game guarded siege'))
 verifier='''from pathlib import Path
import hashlib,json,sys
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'tooling/bluesiege20260923'))
import blue_siege_binding as b
b.configure();ir=b.ir
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(P/'manifest.json');p=read(P/'policy.ir.json');s=(P/'policy.bas').read_text()
assert ir.compile_policy(p)==s and ir.extract(s,p)==p
assert ir.digest(p)==m['ir_sha256'] and sha(P/'policy.bas')==m['source_sha256']
for path,digest in m['artifacts'].items():assert sha(P/path)==digest,path
for name in ['practice','recovery','openings','buyback','portals']:assert all(r['passed'] for r in read(P/'evidence'/(name+'.json'))['rows'])
assert read(P/'evidence/scenarios.json')['passed'] and read(P/'evidence/native-result.json')['passed'] and read(P/'evidence/druid-native-result.json')['passed'] and read(P/'evidence/equivalence.json')['passed']
print(json.dumps({'verified':True,'source_sha256':m['source_sha256'],'ir_sha256':m['ir_sha256'],'hosted_complete':m['hosted_complete'],'deployment_qualified':m['deployment_qualified']}))
'''
 (pair/'verify.py').write_text(verifier)
 manifest=read(src/'manifest.json');manifest.update(ir_sha256=ir.digest(p),local_validated=True,hosted_complete=False,deployment_qualified=False)
 manifest['artifacts']={str(f.relative_to(pair)):sha(f) for f in pair.rglob('*') if f.is_file() and f.name!='manifest.json' and '__pycache__' not in f.parts};write(pair/'manifest.json',manifest)
 subprocess.run([sys.executable,str(pair/'verify.py')],check=True)
 write(OUT/'summary.json',{'source_sha256':manifest['source_sha256'],'ir_sha256':manifest['ir_sha256'],'local':read(STUDY/'local-summary.json'),'hosted_complete':False,'deployment_qualified':False})
 print(OUT)
if __name__=='__main__':main()

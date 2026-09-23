from pathlib import Path
import sys,json,hashlib,pprint,subprocess
repo=Path(__file__).resolve().parents[4];sys.path.insert(0,str(repo/'games/gods_of_the_arena/instruments/controltactics20260923'))
import harvest_binding as b
b.configure();r=repo.parent/'polyworld/tmp/gota-harvest-value61-20260923';p=repo/'examples/gods_of_the_arena/players/ir/forks/harvest-value20260923-local/harvest-value';data=json.loads((r/'native-result.json').read_text());base={ (x['side'],x['ordinal'],x['seed']):x for x in data['rows'] if x['name']=='baseline'}
pairs=[]
for x in data['rows']:
 if x['name']=='baseline':continue
 a=base[x['side'],x['ordinal'],x['seed']];pairs.append({'side':x['side'],'ordinal':x['ordinal'],'seed':x['seed'],'class':x['subject']['class'],'baseline':a['subject']['score'],'candidate':x['subject']['score'],'delta':x['subject']['score']-a['subject']['score'],'baseline_xp':a['subject']['xp'],'candidate_xp':x['subject']['xp'],'baseline_ticks':a['ticks'],'candidate_ticks':x['ticks'],'baseline_replay_sha256':a['replay_sha256'],'candidate_replay_sha256':x['replay_sha256']})
result={'games':16,'fresh_native_games':8,'reused_exact_native_controls':8,'new_hosted_games':0,'runtime_valid':True,'pairs':pairs,'baseline_sum':sum(x['baseline'] for x in pairs),'candidate_sum':sum(x['candidate'] for x in pairs),'score_delta_sum':sum(x['delta'] for x in pairs),'by_side':{str(s):{'baseline':sum(x['baseline'] for x in pairs if x['side']==s),'candidate':sum(x['candidate'] for x in pairs if x['side']==s)} for s in range(2)},'deployment_qualified':False,'interpretation':'Pooled score nearly unchanged; three paired gains/five declines with opposite side results. Exploratory baseline-reference roster only, not a demonstrated improvement. Do not upload/promote unchanged based on this screen.'}
(r/'native-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
# Preserve initially prepared semantic inputs before annotating their local results.
cap=r/'captured-ir';cap.mkdir(exist_ok=True)
for f in ['policy.ir.json','policy.py','extracted.ir.json','semantics.json','manifest.json']:
 if not (cap/f).exists():(cap/f).write_bytes((p/f).read_bytes())
d=json.loads((p/'policy.ir.json').read_text());d['belief']['claims']['RewardWorkRanking'].update(status='requires_review',claim='The integer XP/work target ranking runs correctly but has no demonstrated score gain: eight matched native comparisons total19367to19376, red gains and blue losses. Preserve the fork for refinement, not deployment.',evidence=[{'artifact':'evidence/native-comparison.json'}]);d['belief']['claims']['ProxyLimitations']['status']='supported';d['update']['revision']=2;d['update']['needs_review']=['belief/RewardWorkRanking'];d['update']['evidence']=[{'artifact':'evidence/native-comparison.json'},{'artifact':'README.md'}];b.ir.refresh_grounding(d);assert b.ir.compile_policy(d).encode()==(p/'policy.bas').read_bytes();assert b.ir.extract((p/'policy.bas').read_text(),d)==d
for f,v in [('policy.ir.json',d),('extracted.ir.json',d),('semantics.json',b.ir.grounded(d))]:(p/f).write_text(json.dumps(v,indent=2)+'\n')
(p/'policy.py').write_text('POLICY = '+pprint.pformat(d,width=110,sort_dicts=False)+'\n');e=p/'evidence';e.mkdir(exist_ok=True)
for f in ['native-comparison.json','native-plan-with-hashes.json','native-result.json','objective.json']:(e/f).write_bytes((r/f).read_bytes())
(p/'README.md').write_text('''# XP-per-work harvesting candidate

This separate replay61 fork implements the user's score-only direction with
integer target-opportunity ranking. It preserves current control legality and
ranks visible attackable targets by reward divided by ceil(HP/basic damage) plus
travel tiles beyond reach. Rewards are hero150, structure100, exposed god500,
and creep15 as an upper bound before sharing. Current-target preference is5%.

It has no team-win utility. Survival, purchases and returning to lane remain
mechanisms for score. This prototype changes target selection; it does not
pretend to estimate full future opportunity cost. Obstacle paths, spells,
competing last hitters and shared XP still need calibration.

Eight complete responsive candidate games plus eight byte-exact reused controls
pass all ten VM limits, full replay hash/command/XP/score checks. Score totals are
**19,367 → 19,376 (+0.05%)**, with red gains and blue losses. This is not evidence
of a competitive improvement. No hosted games, uploads or league writes use this
candidate. Saved for refinement; do not promote it from these eight comparisons.

The reviewed semantic annotations compile/extract to the exact tested BASIC.
`evidence/native-comparison.json` contains every pair and replay digest;
`evidence/objective.json` records the user steering. Captured initial IR and full
replays remain in `polyworld/tmp/gota-harvest-value61-20260923`.
See `docs/guides/guide-gota-score-analysis.md` for the statistical method.

Run `python verify.py`, or use `convert.py compile --out <new-directory>` and
`convert.py extract --source policy.bas --out <new-directory>`.
''')
verify='''from pathlib import Path
import hashlib,json,runpy,sys
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'tooling/controltactics20260923'))
import harvest_binding as b
b.configure();ir=b.ir
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(P/'manifest.json');p=read(P/'policy.ir.json');s=(P/'policy.bas').read_text()
assert runpy.run_path(str(P/'policy.py'))['POLICY']==p
assert ir.compile_policy(p)==s and ir.extract(s,p)==p
assert read(P/'extracted.ir.json')==p and read(P/'semantics.json')==ir.grounded(p)
assert ir.digest(p)==m['ir_sha256'] and sha(P/'policy.bas')==m['source_sha256']
for path,digest in m['artifacts'].items():assert sha(P/path)==digest,path
assert read(P/'evidence/native-comparison.json')['runtime_valid']
assert not m['deployment_qualified'] and not m['hosted_complete']
print(json.dumps({'verified':True,'source_sha256':m['source_sha256'],'ir_sha256':m['ir_sha256']}))
'''
(p/'verify.py').write_text(verify)
m=json.loads((p/'manifest.json').read_text());m.update(ir_sha256=b.ir.digest(d),stage='Local runtime passed; pooled score nearly flat with mixed side effects. No competitive qualification.',local_validated=True,reviewed_ir_preserves_tested_source=True)
m['artifacts']={str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(p.rglob('*')) if f.is_file() and f.name!='manifest.json' and '__pycache__' not in f.parts};(p/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
subprocess.run([sys.executable,str(p/'verify.py')],check=True)
print(json.dumps(result,indent=2))

"""Seal the completed selective-finish result and reflect evidence into its semantic IR."""
from pathlib import Path
import json,hashlib,shutil,pprint,subprocess,sys
import finish_binding as b
ROOT=b.ROOT;RAW=ROOT.parent/'polyworld/tmp/gota-selective-finish59-20260923';OUT=ROOT/'examples/gods_of_the_arena/players/ir/forks/selective-finish20260923-hosted'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def main():
 report=read(RAW/'trial/report.json');effects=read(RAW/'trial/effects-summary.json');assert report['complete'] and report['games']==400 and len(effects['rows'])==32
 assert not OUT.exists(),'Preserve sealed capsules'
 pair=OUT/'selective-finish';shutil.copytree(RAW/'selective-finish',pair,ignore=shutil.ignore_patterns('__pycache__'))
 evidence=OUT/'evidence';evidence.mkdir()
 for n in ['local-summary.json','native-plan.json','native-result.json','runtime-provenance.json','conversion-proof.json','skill-difference.json','preflight.json','calibration-proof.json']:
  shutil.copy2(RAW/n,evidence/n)
 for n in ['collector-interruption.json']:
  if (RAW/n).exists():shutil.copy2(RAW/n,evidence/n)
 members=read(RAW/'trial/field-after/memberships.json')
 retained=[{'player':m['player']['name'],'player_id':m['player']['id'],'version':m['policy_version']['id'],'status':m['status'],'substatus':m['substatus'],'is_champion':m['is_champion']} for m in members if m['player']['id'] in ['ply_630a768f-d623-44b2-80fa-36968d6fa75a','ply_594ec24d-d7f3-4370-a000-468354ec41c9']]
 assert len(retained)==2 and all(m['status']=='competing' and m['substatus']=='active' and m['is_champion'] for m in retained)
 write(evidence/'retained-champions.json',{'captured_at':read(RAW/'trial/field-after/snapshot.json')['captured_at'],'champions':retained,'league_writes':0})
 shutil.copy2(ROOT/'games/gods_of_the_arena/budget-authorizations/2026-09-23-permanent-100000.json',evidence/'budget-authorization.json')
 missing_logs=[]
 for n in ['finish.json','practice.json','baseline-practice.json','recovery.json','openings.json','buyback.json','scenarios.json']:
  shutil.copy2(RAW/n,pair/'evidence'/n)
 for n in ['plan.json','result.json','report.json','field-changes.json','effects-plan.json','effects-summary.json']:
  shutil.copy2(RAW/'trial'/n,evidence/n)
 for label in ['field-before','field-after','field-submit']:
  (evidence/label).mkdir()
  for n in ['snapshot.json','game.json','leaderboard.json']:shutil.copy2(RAW/'trial'/label/n,evidence/label/n)
 for arm in read(RAW/'trial/plan.json')['arms']:
  src=RAW/'trial'/arm['name']/arm['cell'];dst=evidence/arm['name']/arm['cell'];dst.mkdir(parents=True)
  for n in ['arm.json','request.json','episodes.json','review.json']:shutil.copy2(src/n,dst/n)
  shutil.copy2(src/'batch/created.json',dst/'created.json')
  for receipt in sorted((src/'artifacts').glob('*/logs-unavailable.json')):
   row={'name':arm['name'],'cell':arm['cell'],'episode':receipt.parent.name,'receipt':read(receipt),'logs_present_at_seal':(receipt.parent/'game.log').exists()}
   missing_logs.append(row)
 write(evidence/'missing-log-receipts.json',{'episodes':missing_logs,'scope':'Ancillary text logs only; no game excluded or replaced. Exact source identities, player exits, replay states, XP and integer scores remain mandatory.'})
 for n,target in [('local-summary.json','local-summary.json'),('native-result.json','native-result.json'),('trial/report.json','trial-report.json'),('trial/effects-summary.json','effects-summary.json'),('canonical-game.json','release.json')]:shutil.copy2(RAW/n,pair/'evidence'/target)
 shutil.copy2(ROOT/'games/gods_of_the_arena/experiments/2026-09-23-selective-finish.md',pair/'evidence/experiment.md')
 b.configure();ir=b.ir;p=read(pair/'policy.ir.json');initial=ir.digest(p);entry=report['candidates'][0]
 write(evidence/'initial-ir.json',p)
 p['goal']['Win']['preference']='Permit a nearby two-hit god finish for500XP per teammate and a two-hit tower finish for100XP. Barracks require one hit because destruction removes future waves. Preserve lethal-unit priorities and measure opportunity cost after elapsed time.'
 p['belief']['claims']['RecoveryMechanism'].update(claim='The inherited Druid recovery behavior previously passed its own scoped study. For this target-selection source, 92 recovery, 100 opening, 180 buyback, 84 portal and 126 broader host checks pass again on replay59; 16 complete responsive native matches validate runtime. The separate 220 target/kill fixtures validate the new eligibility rule. Prior non-Druid command-equivalence claims describe the Druid parent change, not this all-class targeting intervention.',evidence=[{'artifact':'evidence/recovery.json'},{'artifact':'evidence/local-summary.json'},{'artifact':'evidence/native-result.json'}])
 building=effects['totals']['selective-finish']['building_attack_commands']
 counts=[r['hero']['counts'] for r in effects['rows'] if r['name']=='selective-finish']
 over=sum(c.get('structure_command_over_two_hits',0)+c.get('structure_command_BarracksBuilding_two_hits',0) for c in counts)
 p['belief']['claims']['SelectiveFinish'].update(status='supported' if building>0 and over==0 else 'requires_review',claim=f"All 220 target/kill fixtures plus582 inherited checks and16 native games pass on replay59. In the32-game preselected diagnostic subset, candidate building-target commands={building}; commands exceeding the pre-tick two-hit limit or the one-hit barracks limit={over}. Fixture kills yield100building or500god XP. Selection/acceptance evidence is distinct from competitive value.",evidence=[{'artifact':'evidence/local-summary.json'},{'artifact':'evidence/effects-summary.json'}])
 p['belief']['claims']['CompetitiveGain'].update(status='supported' if report['deployment_qualified'] else 'requires_review' if entry['score_gate_passed'] else 'contradicted',claim=f"Frozen400game qualification passed={report['deployment_qualified']}. Mean score{entry['baseline_score']:.3f}→{entry['candidate_score']:.3f}, gain{entry['aggregate_gain_percent']:.3f}%,95%gainCI{entry['gain_ci95_percent']}; context gains{entry['per_context_gain_percent']}. Productivity metrics and field drift recorded in trial-report. Fixedkhors180/Richard195/Jordan411 rosters; this is not a universal rank or certain population-effect claim.",evidence=[{'artifact':'evidence/trial-report.json'}])
 p['update']={'revision':2,'parent':initial,'change':{'origin':'Complete hosted and local evidence reflected into IR; tested BASIC bytes unchanged.','deployment_qualified':report['deployment_qualified']},'needs_review':['belief/CompetitiveGain'] if entry['score_gate_passed'] and not report['deployment_qualified'] else [],'evidence':[{'artifact':'evidence/trial-report.json'},{'artifact':'evidence/effects-summary.json'}]}
 ir.refresh_grounding(p);source=(pair/'policy.bas').read_text();assert ir.compile_policy(p)==source and ir.extract(source,p)==p
 for n,d in [('policy.ir.json',p),('extracted.ir.json',p),('semantics.json',ir.grounded(p))]:write(pair/n,d)
 (pair/'policy.py').write_text('POLICY = '+pprint.pformat(p,width=110,sort_dicts=False)+'\n')
 (pair/'verify.py').write_text('''from pathlib import Path
import json,hashlib,sys
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'tooling/productive20260923'))
import finish_binding as b
b.configure();ir=b.ir
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(P/'manifest.json');p=read(P/'policy.ir.json');source=(P/'policy.bas').read_text()
assert ir.compile_policy(p)==source and ir.extract(source,p)==p
assert ir.digest(p)==m['ir_sha256'] and sha(P/'policy.bas')==m['source_sha256']
for n,d in m['artifacts'].items():assert sha(P/n)==d,n
assert read(P/'evidence/local-summary.json')['passed']
assert read(P/'evidence/trial-report.json')['complete']
print(json.dumps({'verified':True,'source_sha256':m['source_sha256'],'ir_sha256':m['ir_sha256'],'deployment_qualified':m['deployment_qualified']}))
''')
 (pair/'README.md').write_text(f"# Selective short structure finishes\n\nFresh400-game comparison: mean score{entry['baseline_score']:.2f}→{entry['candidate_score']:.2f} ({entry['aggregate_gain_percent']:+.2f}%). Deployment qualified: {report['deployment_qualified']}. Read evidence/trial-report.json for intervals, frequencies, contexts and rival gaps.\n\nRun `python verify.py`. Compile with `python convert.py compile --out /new/path`; extract with `python convert.py extract --source policy.bas --out /new/path`. The exact tested source must remain unchanged.\n")
 manifest=read(pair/'manifest.json');manifest.update(ir_sha256=ir.digest(p),hosted_complete=True,score_gate_passed=entry['score_gate_passed'],deployment_qualified=report['deployment_qualified'],initial_ir_sha256=initial)
 manifest['artifacts']={str(f.relative_to(pair)):sha(f) for f in pair.rglob('*') if f.is_file() and f.name!='manifest.json' and '__pycache__' not in f.parts};write(pair/'manifest.json',manifest)
 write(evidence/'raw-input-manifest.json',{'raw_root':str(RAW),'artifacts':{str(f.relative_to(RAW)):sha(f) for f in (RAW/'trial').rglob('*') if f.is_file() and f.suffix not in ['.log','.tmp']}})
 write(OUT/'summary.json',{'trial':entry,'deployment_qualified':report['deployment_qualified'],'source_sha256':manifest['source_sha256'],'ir_sha256':manifest['ir_sha256']})
 (OUT/'README.md').write_text(f"# Selective short structure finishes on replay59\n\nOnly target eligibility and short-finish priority change from incumbent29f6d7e6. Source08987348; four color/draft contexts,50games/source/context. Mean score gain{entry['aggregate_gain_percent']:+.2f}%; deployment qualified:{report['deployment_qualified']}.\n\n[Reviewed semantic IR/policy pair](selective-finish/README.md), [all metrics and verdict](evidence/report.json), [mechanism subset](evidence/effects-summary.json). Raw captures remain unchanged.\n")
 subprocess.run([sys.executable,str(pair/'verify.py')],check=True);print(OUT)
if __name__=='__main__':main()

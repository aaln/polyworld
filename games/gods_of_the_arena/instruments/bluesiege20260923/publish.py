"""Seal the full comparison and reflect its decision into unchanged tested BASIC."""
import json,pprint,shutil,subprocess,sys
import publish_local as local
from publish_local import ROOT,STUDY,read,sha,write
OUT=ROOT/'examples/gods_of_the_arena/players/ir/forks/blue-druid-siege20260923-hosted'
def main():
 report=read(STUDY/'trial/report.json');effects=read(STUDY/'trial/effects-summary.json')
 assert report['complete'] and report['games']==400 and len(effects['rows'])==16
 assert not OUT.exists(),'Preserve sealed results'
 prior=local.OUT/'blue-druid-siege';pair=OUT/'blue-druid-siege';shutil.copytree(prior,pair,ignore=shutil.ignore_patterns('__pycache__'))
 ev=OUT/'evidence';ev.mkdir()
 for name in ['plan.json','result.json','report.json','field-changes.json','effects-plan.json','effects-summary.json','score-breakdown.png','score-breakdown.svg']:shutil.copy2(STUDY/'trial'/name,ev/name)
 for label in ['field-before','field-after','field-submit']:
  (ev/label).mkdir()
  for name in ['snapshot.json','game.json','leaderboard.json']:shutil.copy2(STUDY/'trial'/label/name,ev/label/name)
 for arm in read(STUDY/'trial/plan.json')['arms']:
  src=STUDY/'trial'/arm['name']/arm['cell'];dst=ev/arm['name']/arm['cell'];dst.mkdir(parents=True)
  for name in ['arm.json','episodes.json','review.json']:shutil.copy2(src/name,dst/name)
  for part in arm['batches']:
   (dst/part).mkdir()
   for name in ['request.json','episodes.json']:shutil.copy2(src/part/name,dst/part/name)
   shutil.copy2(src/part/'batch/created.json',dst/part/'created.json')
 shutil.copy2(STUDY/'budget/authorization.json',ev/'budget-authorization.json')
 shutil.copy2(STUDY/'transport-amendment.json',ev/'transport-amendment.json')
 shutil.copy2(pair/'evidence/hosted-plan.json',pair/'evidence/initial-hosted-plan.json')
 shutil.copy2(STUDY/'trial/plan.json',pair/'evidence/hosted-plan.json')
 shutil.copy2(STUDY/'transport-amendment.json',pair/'evidence/transport-amendment.json')
 for name in ['report.json','effects-summary.json']:shutil.copy2(STUDY/'trial'/name,pair/'evidence'/('trial-report.json' if name=='report.json' else name))
 b=local.b;b.configure();ir=b.ir;p=read(prior/'policy.ir.json');parent=ir.digest(p);entry=report['candidates'][0]
 p['belief']['claims']['CompetitiveGain'].update(status='supported' if report['deployment_qualified'] else 'contradicted',claim=f"The frozen400-game qualification rule was met: {report['deployment_qualified']}. Pooled mean score change {entry['aggregate_gain_percent']:.3f}%,95%gain interval {entry['gain_ci95_percent']},context changes {entry['per_context_gain_percent']}. Relative score-gap preservation {entry['relative_preservation']},Druid exposure {entry['druid_exposure']}. This result applies to one complete scoped source and a fixed blue later-draft roster. Rejection is failure to qualify, not proof of population harm. It establishes neither a universal ranking nor single-component causality.",evidence=[{'artifact':'evidence/trial-report.json'}])
 totals={k:sum(r['counts'].get(k,0) for r in effects['rows'] if r['name']=='blue-druid-siege') for k in ['selected_covered_tower','submitted_attack_covered_tower','selected_siege_attacker','submitted_attack_siege_attacker']}
 p['belief']['claims']['RichardSourceTransfer']['claim'] += f" Hosted mechanism audit reconstructs all commands and state hashes in16prospectively selected games; candidate totals {totals}. Selections and submitted attacks do not establish landed damage or causal gain. Competitive qualification is recorded separately."
 p['belief']['claims']['RichardSourceTransfer']['evidence'].append({'artifact':'evidence/effects-summary.json'})
 p['update']={'revision':3,'parent':parent,'change':{'origin':'Full hosted result and mechanism evidence reflected into semantic IR; tested BASIC unchanged.','deployment_qualified':report['deployment_qualified']},'needs_review':[],'evidence':[{'artifact':'evidence/trial-report.json'},{'artifact':'evidence/effects-summary.json'}]}
 ir.refresh_grounding(p);source=(prior/'policy.bas').read_text();assert ir.compile_policy(p)==source and ir.extract(source,p)==p
 for name,value in [('policy.ir.json',p),('extracted.ir.json',p),('semantics.json',ir.grounded(p))]:write(pair/name,value)
 (pair/'policy.py').write_text('POLICY = '+pprint.pformat(p,width=110,sort_dicts=False)+'\n')
 manifest=read(prior/'manifest.json');manifest.update(ir_sha256=ir.digest(p),hosted_complete=True,deployment_qualified=report['deployment_qualified'],score_gate_passed=entry['score_gate_passed'])
 manifest['artifacts']={str(f.relative_to(pair)):sha(f) for f in pair.rglob('*') if f.is_file() and f.name!='manifest.json' and '__pycache__' not in f.parts};write(pair/'manifest.json',manifest)
 subprocess.run([sys.executable,str(pair/'verify.py')],check=True)
 write(ev/'artifact-index.json',{'raw_root':str(STUDY),'artifacts':{str(f.relative_to(STUDY)):sha(f) for f in (STUDY/'trial').rglob('*') if f.is_file() and f.suffix not in ['.log','.tmp']}})
 write(OUT/'summary.json',{'trial':entry,'deployment_qualified':report['deployment_qualified'],'source_sha256':manifest['source_sha256'],'ir_sha256':manifest['ir_sha256'],'mechanism_totals':totals})
 print(OUT)
if __name__=='__main__':main()

"""Adaptive component evidence, including the controller being ablated."""
from copy import deepcopy
from policy_ir import HERE,ROOT,read,write,digest,compile_policy,extract,bundle
from hypothesis_study import paired

old=ROOT/'tmp/gota-ir/hit-kite-20260915'
root=ROOT/'tmp/gota-ir/kiting-ablations-20260915'
prior=[read(p) for p in (old/'screen/candidate').glob('*/result.json')]
reports={}
for name in ['no_escape','targeted']:
 d=root/name;r=read(d/'screen-result.json')
 assert r['audited_games']==120 and not r['invalid_games_scored']
 rows=[read(p) for p in (d/'screen/candidate').glob('*/result.json')]
 component=paired(prior,rows)
 result={'component':name,'design':'adaptive discovery on reused40 seeds; not independent confirmation',
  'game_version':'2026.9.15.3','wins':r['comparisons']['parent']['wins'],
  'parent_wins':r['comparisons']['parent']['control_wins'],
  'prior_controller_wins':component['control_wins'],'component_win_gain':component['gain'],
  'metrics':r['metrics'],'gates':r['gates'],'activation':r['activation'],'passed':r['passed'],
  'audited_games':120,'new_games':40,'promotion_eligible':False,
  'component_pairs':component['pairs'],'by_class':r['by_class']}
 reports[name]=result
 path=HERE/f'kiting-component-{name}-20260915.json';write(path,result)
 p=read(d/'candidate/policy.ir.json');source=compile_policy(p);q=deepcopy(p)
 ref={'artifact':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())}
 q['belief']['claims']['B_component']={'claim':f"Completed adaptive component screen: {result['wins']}/40 wins versus prior controller{result['prior_controller_wins']}/40 and exactv2{result['parent_wins']}/40; candidate deaths{r['metrics']['candidate']['deaths']} versusv2{r['metrics']['parent']['deaths']}. Gate {'passed' if r['passed'] else 'failed'}. All120 matching tapes verified;40new games. Fresh confirmation and hosted validation remain required.",'status':'requires_review','evidence':[ref]}
 q['update'].update(parent=digest(p),revision=p['update']['revision']+1,change={'origin':'completed_component_feedback','passed':r['passed']})
 q['update']['evidence'].append(ref)
 assert compile_policy(q)==source and extract(source,q)==q
 bundle(q,d/'evaluated');write(HERE/f'hypotheses/hit_{name}.evaluated.ir.json',q);(HERE/f'hypotheses/hit_{name}.evaluated.bas').write_text(source)
 record=HERE/f'experiments/2026-09-15-hit-{name}.md';s=record.read_text().replace('Status: running','Status: inconclusive')
 s+=f"\nResult: {result['wins']}/40wins vs priorcontroller{result['prior_controller_wins']},v2{result['parent_wins']}; deaths{r['metrics']['candidate']['deaths']}vsv2{r['metrics']['parent']['deaths']}, hits{r['metrics']['candidate']['hits']}vsv2{r['metrics']['parent']['hits']}. Screenpassed={r['passed']}. No promotion.\n";record.write_text(s)
 print({k:v for k,v in result.items() if k not in ['component_pairs','by_class']})
write(root/'result.json',reports)

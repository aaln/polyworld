"""Close the full adaptive range/filter matrix before choosing a candidate."""
from copy import deepcopy
from policy_ir import HERE,ROOT,read,write,digest,compile_policy,extract,bundle
from hypothesis_study import paired

root=ROOT/'tmp/gota-ir/kiting-range-20260915'
prior_root=ROOT/'tmp/gota-ir/kiting-ablations-20260915/no_escape'
prior=[read(p) for p in (prior_root/'screen/candidate').glob('*/result.json')]
reports={}
for name in ['early_all','targeted_only','early_targeted']:
 d=root/name;r=read(d/'screen-result.json');assert r['audited_games']==120 and not r['invalid_games_scored']
 rows=[read(p) for p in (d/'screen/candidate').glob('*/result.json')]
 hs=[g['heroes'][g['candidate_slots'][0]] for g in rows];ticks=sum(g['ticks'] for g in rows)
 comparison=paired(prior,rows)
 result={'cell':name,'design':'adaptive2x2 range/aggro matrix; same40 inspected cases; no independent confirmation',
  'game_version':'2026.9.15.3','wins':r['comparisons']['parent']['wins'],
  'parent_wins':r['comparisons']['parent']['control_wins'],'default_wins':r['comparisons']['baseline']['control_wins'],
  'previous_pure_kite_wins':comparison['control_wins'],'metrics':r['metrics'],
  'deaths_per_game_minute':sum(h['deaths'] for h in hs)/(ticks/1440),
  'hits_per_game_minute':sum(h['basic_hit_events'] for h in hs)/(ticks/1440),
  'mean_glory':sum(h['score']*(h['total_xp']-100*g['ticks']/1440) for g,h in zip(rows,hs))/40,
  'gates':r['gates'],'activation':r['activation'],'passed':r['passed'],
  'audited_games':120,'new_games':40,'promotion_eligible':False,'by_class':r['by_class']}
 reports[name]=result
 path=HERE/f'kiting-{name}-20260915.json';write(path,result)
 p=read(d/'candidate/policy.ir.json');q=deepcopy(p);source=compile_policy(p)
 ref={'artifact':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())}
 q['belief']['claims']['B_range']={'claim':f"Completed adaptive range/filter cell{name}: {result['wins']}/40 wins versusv2{result['parent_wins']} anddefault{result['default_wins']}; deaths{r['metrics']['candidate']['deaths']}vs{r['metrics']['parent']['deaths']},hits{r['metrics']['candidate']['hits']}vs{r['metrics']['parent']['hits']}. Screen {'passed' if r['passed'] else 'failed'}. All120 matched tapes verified;40new cases. This reused-seed result is not independent confirmation.",'status':'requires_review','evidence':[ref]}
 q['update'].update(parent=digest(p),revision=p['update']['revision']+1,change={'origin':'completed_range_matrix_feedback','passed':r['passed']});q['update']['evidence'].append(ref)
 assert compile_policy(q)==source and extract(source,q)==q
 bundle(q,d/'evaluated');write(HERE/f'hypotheses/{name}.evaluated.ir.json',q);(HERE/f'hypotheses/{name}.evaluated.bas').write_text(source)
 print({k:v for k,v in result.items() if k!='by_class'})
passing=[v for v in reports.values() if v['passed']]
selected=sorted(passing,key=lambda r:(-r['wins'],r['deaths_per_game_minute']))[0]['cell'] if passing else None
write(root/'result.json',{'cells':reports,'selected':selected,'independent_confirmation':False})
record=HERE/'experiments/2026-09-15-early-kiting-matrix.md';s=record.read_text().replace('Status: running','Status: inconclusive')
s+='\nCompleted every new game and tape. '+str({n:{'wins':r['wins'],'deaths':r['metrics']['candidate']['deaths'],'hits':r['metrics']['candidate']['hits'],'passed':r['passed']} for n,r in reports.items()})+'\nSelected for fresh confirmation: '+str(selected)+'. No league change.\n';record.write_text(s)
print('Selected:',selected)

"""Complete spell/retreat matrix -> factual IR feedback, no outcome peeking."""
from copy import deepcopy
from policy_ir import HERE,ROOT,read,write,digest,compile_policy,extract,bundle
root=ROOT/'tmp/gota-ir/kiting-spells-20260915'
names=['spell_short','long_bare','spell_long']
completed={n:read(root/n/'screen-result.json') for n in names}
assert read(root/'reference-parity.json')['complete_games']==80
reports={}
for name,r in completed.items():
 assert r['audited_games']==120 and not r['invalid_games_scored']
 d=root/name;rows=[read(p) for p in (d/'screen/candidate').glob('*/result.json')]
 hs=[g['heroes'][g['candidate_slots'][0]] for g in rows];ticks=sum(g['ticks'] for g in rows)
 result={'cell':name,'design':'adaptive spell/duration matrix, same40 inspected cases; fresh confirmation mandatory',
 'game_version':'2026.9.15.3','wins':r['comparisons']['parent']['wins'],
 'parent_wins':r['comparisons']['parent']['control_wins'],'default_wins':r['comparisons']['baseline']['control_wins'],
 'metrics':r['metrics'],'deaths_per_game_minute':sum(h['deaths'] for h in hs)/(ticks/1440),
 'hits_per_game_minute':sum(h['basic_hit_events'] for h in hs)/(ticks/1440),
 'mean_glory':sum(h['score']*(h['total_xp']-100*g['ticks']/1440) for g,h in zip(rows,hs))/40,
 'activation':r['activation'],'gates':r['gates'],'passed':r['passed'],'audited_games':120,
 'promotion_eligible':False,'by_class':r['by_class']}
 reports[name]=result;path=HERE/f'kiting-{name}-20260915.json';write(path,result)
 p=read(d/'candidate/policy.ir.json');q=deepcopy(p);source=compile_policy(p)
 ref={'artifact':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())}
 m=r['metrics'];a=r['activation']
 q['belief']['claims']['B_spell_kite']={'claim':f"Cell{name}: {result['wins']}/40 wins versusv2{result['parent_wins']} anddefault{result['default_wins']}; deaths{m['candidate']['deaths']}vs{m['parent']['deaths']}, XP{m['candidate']['xp']}vs{m['parent']['xp']}, hits{m['candidate']['hits']}vs{m['parent']['hits']}. Accepted explicit casts during movement:{a['spell_casts']} in{a['spell_games']}cases. Gate {'passed' if r['passed'] else 'failed'}. All120 complete tapes verified. Adaptive discovery, not independent confirmation.",'status':'requires_review','evidence':[ref]}
 q['update'].update(revision=p['update']['revision']+1,parent=digest(p),change={'origin':'completed_spell_matrix_feedback','passed':r['passed']});q['update']['evidence'].append(ref)
 assert compile_policy(q)==source and extract(source,q)==q
 bundle(q,d/'evaluated');write(HERE/f'hypotheses/{name}.evaluated.ir.json',q);(HERE/f'hypotheses/{name}.evaluated.bas').write_text(source)
 print({k:v for k,v in result.items() if k!='by_class'})
passing=[r for r in reports.values() if r['passed']]
selected=sorted(passing,key=lambda r:(-r['wins'],r['deaths_per_game_minute']))[0]['cell'] if passing else None
write(root/'result.json',{'cells':reports,'selected':selected,'independent_confirmation':False})
p=HERE/'experiments/2026-09-15-spell-kiting-matrix.md';s=p.read_text().replace('Status: running','Status: inconclusive')
s+='\nCompleted all cells and tape checks. '+str({n:{'wins':r['wins'],'deaths':r['metrics']['candidate']['deaths'],'casts':r['activation']['spell_casts'],'passed':r['passed']} for n,r in reports.items()})+'\nSelected for fresh confirmation: '+str(selected)+'. No league change from this discovery matrix.\n';p.write_text(s)
print('Selected:',selected)

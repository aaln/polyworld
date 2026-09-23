"""Reproduce historical clean controls and paired portal transitions."""
from collections import Counter
from pathlib import Path
import json,statistics
ROOT=Path(__file__).resolve().parents[4]
RAW=ROOT.parent/'polyworld/tmp/gota-khors114-audit-20260923'
read=lambda p:json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
rows=read(RAW/'actor-rows.json');out={}
for name in ['khors','aaron','coach']:
    counts=Counter();starts=0
    for row in [x for x in rows if x['policy']==name]:
        pending=None
        for e in row['portals']:
            if e['kind']=='PortalStarted':
                if pending:counts['replaced_unfinished_start']+=1
                pending=e;starts+=1
            elif pending:
                if e['kind']=='PortalCompleted':counts[('keep' if pending['can_shop'] else 'field')+'_to_'+('keep' if e['can_shop'] else 'field')]+=1
                elif e['kind']=='PortalInterrupted':counts['interrupted']+=1
                pending=None
            else:counts['end_without_start']+=1
        if pending:counts['unfinished_at_game_end']+=1
    out[name]={'starts':starts,'counts':dict(counts)}
save(RAW/'portal-transitions.json',{'scope':'Paired typed start/end events by same actor; keep membership sampled after event tick. Keep-to-keep does not by itself prove identical destination.','policies':out})
base=ROOT.parent/'polyworld/tmp/gota-richard174-source-20260923/trial';plan=read(base/'plan.json');rows=[]
for arm in plan['arms']:
    if arm['name']!='baseline':continue
    folder=base/'baseline'/arm['cell'];cell=read(folder/'result.json')
    for rr in cell['rows']:
        assert rr['valid'] and rr['all_hashes_equal']
        p=folder/'artifacts'/rr['episode'];a=read(p/'audit.json');e=read(p/'economy.json');sp=read(p/'spec.json')
        for name,slot,digest in [('ours',arm['own_slots'][0],'29f6d7e67252a9cc32521e5a906ec33222a5e7e3b5e59b168db5c6b20c9c9e36'),('khors',arm['roster'].index('145c01e0-0cbf-4e1e-8120-11b437175b91'),'e66729cb198ac6a7a398abc529457b24595013d7070210c09e9445ee138ae160')]:
            assert sp['players'][slot]['content_hash']==digest
            h=a['heroes'][slot];q=e['heroes'][slot]
            rows.append({'episode':rr['episode'],'context':arm['cell'],'policy':name,'class':q['class'],'side':h['team'],'score':h['score'],'xp':h['xp'],'hero_xp':q['xp_sources'].get('hero',0),'creep_xp':q['xp_sources'].get('creep',0),'structure_or_god_xp':q['xp_sources'].get('structure_or_other',0),'deaths':h['deaths'],'kills':q['hero_kills'],'minutes':a['ticks']/1440})
summary=[]
for context in ['red-lead','blue-lead','red-late','blue-late']:
    for policy in ['ours','khors']:
        rs=[r for r in rows if r['context']==context and r['policy']==policy];assert len(rs)==50
        summary.append({'context':context,'policy':policy,'games':len(rs),'zero_scores':sum(r['score']==0 for r in rs),'classes':dict(Counter(r['class'] for r in rs)),'mean':{k:statistics.mean(r[k] for r in rs) for k in ['score','xp','hero_xp','creep_xp','structure_or_god_xp','deaths','kills','minutes']}})
save(RAW/'clean-control-comparison.json',{'scope':'Historical clean controlled baseline cohort200games, exact current29f6d7e6 source and khors114, all four fixed contexts. Reused diagnostic evidence, not new candidate qualification or representative current random matchmaking. Colors in context refer to ours; khors opposes it.','games':200,'summary':summary,'rows':rows,'source_plan':str(base/'plan.json')})
print(json.dumps({'league_portal_profiles':len(out),'clean_control_games':200}))

"""Reproduce descriptive khors/own scoring gaps; never fit or qualify a policy."""
from collections import Counter,defaultdict
from pathlib import Path
import json,statistics,hashlib
ROOT=Path(__file__).resolve().parents[4]
RAW=ROOT.parent/'polyworld/tmp/gota-khors114-audit-20260923'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def mean(rs,key):return statistics.mean(r[key] for r in rs) if rs else None

def actor_row(p,name,slot,valid,failed,context):
    a,e,c=[read(p/n) for n in ['audit.json','economy.json','combat.json']]
    s=read(p/'stalls.json') if (p/'stalls.json').exists() else None
    h,eco,combat=a['heroes'][slot],e['heroes'][slot],c['heroes'][slot];t=combat['totals'];ticks=a['ticks'];minutes=ticks/1440
    purchase=[q for q in e['purchases'] if q['slot']==slot]
    row={'episode':p.name,'policy':name,'class':eco['class'],'side':h['team'],'team_draft_ordinal':slot%5+1,'slot':slot,'context':context,'all_vms_clean':valid,
      'score':h['score'],'xp':h['xp'],'minutes':minutes,'draft_seconds':a['draft_ticks']/24,'deaths':h['deaths'],'level':h['level'],'hero_kills':eco['hero_kills'],'creep_last_hits':eco['creep_last_hits'],
      'hero_xp':t.get('xp_hero',0),'creep_xp':t.get('xp_creep',0),'building_xp':t.get('xp_structure',0),'god_xp':t.get('xp_god',0),
      'xp_per_minute':h['xp']/minutes,'hero_xp_per_minute':t.get('xp_hero',0)/minutes,'creep_xp_per_minute':t.get('xp_creep',0)/minutes,
      'xp_from_eventually_failed_players':sum(eco['hero_xp_by_victim_slot'][i] for i in failed),
      'basic_hero_damage':t.get('damage_basic_hero',0),'spell_hero_damage':t.get('damage_spell_hero',0),'basic_creep_damage':t.get('damage_basic_creep',0),'spell_creep_damage':t.get('damage_spell_creep',0),
      'basic_structure_damage':t.get('damage_basic_structure',0),'spell_structure_damage':t.get('damage_spell_structure',0),'spells':sum(combat['spells'].values()),'damage_taken':t.get('damage_taken',0),
      'keep_seconds':t.get('keep_ticks',0)/24,'field_seconds':t.get('field_ticks',0)/24,'dead_seconds':(a['battle_ticks']-t.get('alive_ticks',0))/24,
      'out_of_range_rejections':t.get('rejected_ActionOutOfRange',0),'gold_spent':t.get('gold_spent',0),'final_gold':h['gold'],'final_inventory':h['inventory'],
      'purchases':purchase,'spell_counts':combat['spells'],'spell_damage':combat['spell_damage'],
      'hero_xp_by_victim_slot':eco['hero_xp_by_victim_slot'],'basic_hits':h['hits']}
    assert sum(row[k] for k in ['hero_xp','creep_xp','building_xp','god_xp'])==row['xp']
    row['time_cost_xp']=200*minutes
    row['unclamped_score_margin']=row['xp']-row['time_cost_xp']
    row['xp_deficit_to_break_even']=max(0,-row['unclamped_score_margin'])
    row['net_xp_per_minute']=row['xp_per_minute']-200
    row['low_band']='zero' if row['score']==0 else 'under500' if row['score']<500 else '500plus'
    if s:
        st=s['heroes'][slot];totals=st['totals'];windows=[w for w in st['windows'] if w['full_minute']]
        row.update(draft=next(d for d in s['draft'] if d['slot']==slot),windows=st['windows'],dead_seconds=totals.get('dead_ticks',0)/24,keep_seconds=totals.get('keep_ticks',0)/24,field_seconds=totals.get('field_ticks',0)/24,max_without_xp_seconds=st['max_without_xp_ticks']/24,
          healthy_field_drought_seconds=totals.get('healthy_field_after30s_without_xp_ticks',0)/24,
          keep_drought_seconds=totals.get('keep_after30s_without_xp_ticks',0)/24,
          full_battle_minutes=len(windows),minutes_under200xp=sum(w['values'].get('xp',0)<200 for w in windows),minutes_zero_xp=sum(w['values'].get('xp',0)==0 for w in windows),
          portals=[q for q in s['portals'] if q['slot']==slot])
    return row

FIELDS=['score','xp','minutes','time_cost_xp','unclamped_score_margin','xp_deficit_to_break_even','net_xp_per_minute','draft_seconds','hero_xp','creep_xp','building_xp','god_xp','hero_kills','creep_last_hits','deaths','level','xp_per_minute','hero_xp_per_minute','creep_xp_per_minute','xp_from_eventually_failed_players','basic_hero_damage','spell_hero_damage','spells','basic_structure_damage','keep_seconds','field_seconds','dead_seconds','out_of_range_rejections','gold_spent','final_gold','basic_hits','max_without_xp_seconds','healthy_field_drought_seconds','keep_drought_seconds','full_battle_minutes','minutes_under200xp','minutes_zero_xp']
def summarize(rs):
    return {'appearances':len(rs),'zero_scores':sum(r['score']==0 for r in rs),'under500_including_zero':sum(r['score']<500 for r in rs),
      'classes':dict(Counter(r['class'] for r in rs)),'mean':{k:mean(rs,k) for k in FIELDS if rs and k in rs[0]},
      'median_score':statistics.median(r['score'] for r in rs) if rs else None,
      'score_total':sum(r['score'] for r in rs),'total_hero_xp':sum(r['hero_xp'] for r in rs),
      'total_xp_from_eventually_failed_players':sum(r['xp_from_eventually_failed_players'] for r in rs)}
def groups(rows,keys):
    d=defaultdict(list)
    for r in rows:d[tuple(r[k] for k in keys)].append(r)
    return [{**dict(zip(keys,k)),**summarize(rs)} for k,rs in sorted(d.items())]

def main():
    plan=read(RAW/'plan.json');verified=read(RAW/'verified.json');assert verified['complete'] and len(verified['rows'])==72
    rows=[];index={};failures=Counter();pairs=[]
    for v in verified['rows']:
        p=RAW/'league-artifacts'/v['episode'];ep=read(p/'episode.json');s=read(p/'stalls.json');assert s['hash_mismatches']==0
        for f,h in v['hashes'].items():assert sha(p/f)==h
        for f in v['failed_slots']:failures[ep['policy_version_ids'][f]]+=1
        for name in ['stalls.json','combat.json','economy.json','audit.json','spec.json','episode.json','verified.json','replay.bin']:
            index[str((p/name).relative_to(RAW))]=sha(p/name)
        actual=[]
        for sub in v['subjects']:
            assert sub['slot'] not in v['failed_slots']
            r=actor_row(p,sub['name'],sub['slot'],v['valid'],v['failed_slots'],'league');rows.append(r);actual.append(r)
        kh=next((r for r in actual if r['policy']=='khors'),None)
        if kh:
            for own in [r for r in actual if r['policy']!='khors']:
                pairs.append({'episode':v['episode'],'own_policy':own['policy'],'relation':'allies' if own['side']==kh['side'] else 'opponents','own_class':own['class'],'khors_class':kh['class'],'own_score':own['score'],'khors_score':kh['score'],'gap':own['score']-kh['score'],'khors_hero_xp_from_own':kh['hero_xp_by_victim_slot'][own['slot']],'own_hero_xp_from_khors':own['hero_xp_by_victim_slot'][kh['slot']]})
    draft=[];economy=[]
    for name in plan['ids']:
        rs=[r for r in rows if r['policy']==name];d=Counter();first=Counter();items=Counter();sequences=Counter();portals=Counter();start_hp=[]
        for r in rs:
            available=r['draft']['available_before'];pick=r['class']
            for cl in available:
                d[(cl,'available')]+=1
                if pick==cl:d[(cl,'selected')]+=1
            if r['purchases']:first[str(r['purchases'][0]['item'])]+=1
            items.update(str(x['item']) for x in r['purchases']);sequences['-'.join(str(x['item']) for x in r['purchases'][:5])]+=1
            portals.update(x['kind'] for x in r['portals'])
            start_hp += [x['hp']/x['max_hp'] for x in r['portals'] if x['kind']=='PortalStarted']
        draft.append({'policy':name,'conditional_choices':[{'hero':cl,'available':n,'selected':d[(cl,'selected')]} for (cl,status),n in sorted(d.items()) if status=='available']})
        economy.append({'policy':name,'first_items':dict(first),'accepted_items':dict(items),'first5_sequences':dict(sequences),'portal_events':dict(portals),'portal_start_mean_hp_fraction':statistics.mean(start_hp) if start_hp else None})
    whole=groups(rows,['policy']);byround=[]
    episode_round={e['id']:e['round_id'] for e in plan['episodes']}
    for r in rows:r['round_id']=episode_round[r['episode']]
    byround=groups(rows,['round_id','policy'])
    summary={'scope':'All72 recent completed league games, three frozen rounds. Retrospective descriptive; appearances share games, teammate and opponent strata separated. Other-player VM failures are part of this live field, not clean comparative efficacy. No source, forecast or proxy.',
      'games':72,'all_vm_clean_games':sum(v['valid'] for v in verified['rows']),'other_vm_failure_games':sum(not v['valid'] for v in verified['rows']),
      'subject_vm_failures':0,'failed_versions':dict(failures),'distinct_command_streams':len({v['canonical_commands_sha1'] for v in verified['rows']}),
      'overall':whole,'by_round':byround,'by_class':groups(rows,['policy','class']),'by_color':groups(rows,['policy','side']),
      'by_draft_ordinal':groups(rows,['policy','team_draft_ordinal']),'by_score_band':groups(rows,['policy','low_band']),
      'by_vm_cleanliness':groups(rows,['policy','all_vms_clean']),'draft_choices':draft,'economy_actions':economy,'pairs':pairs,
      'low_cases':sorted([r for r in rows if r['policy']!='khors' and r['score']<500],key=lambda r:(r['score'],r['xp'],r['episode'])),
      'mean_pair_gap':{rel:statistics.mean(p['gap'] for p in pairs if p['relation']==rel) for rel in ['allies','opponents']},
      'limits':['XP from eventually failed player slots cannot be assigned to post-failure periods without exact failure timing.','Conditioning on selected class is not a draft intervention: hero availability, seats, teams and opponents differ.','Drought and no-target counters do not by themselves identify a bad decision or affordable alternative.','No confidence interval treats shared-game hero appearances as independent.']}
    save(RAW/'analysis.json',summary);save(RAW/'actor-rows.json',rows);save(RAW/'artifact-index.json',{'raw_root':str(RAW),'files':index})
    print(json.dumps({'games':72,'other_failure_games':summary['other_vm_failure_games'],'overall':[{k:r[k] for k in ['policy','appearances','zero_scores','under500_including_zero','mean']} for r in whole]},indent=2))
if __name__=='__main__':main()

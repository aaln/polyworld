"""Publish bounded replay evidence and a descriptive seven-layer opponent IR."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib,json,shutil,statistics,subprocess
ROOT=Path(__file__).resolve().parents[4];RAW=ROOT.parent/'polyworld/tmp/gota-khors179-audit-20260923'
OUT=ROOT/'docs/opponents/khors-v179/score-audit-20260923'
read=lambda p:json.loads(p.read_text())
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def one(row):
 f=RAW/'episodes'/row['episode'];p=f/'opportunity.json'
 if not p.exists():
  r=subprocess.run([str(RAW/'opportunity-audit'),'--replay',str(f/'replay.bin')],capture_output=True,text=True,timeout=600);assert r.returncode==0,r.stderr;write(p,json.loads(r.stdout.splitlines()[-1]))
 d=read(p);assert d['hash_mismatches']==0;return d
v=read(RAW/'verified.json')
with ThreadPoolExecutor(3) as pool:details=list(pool.map(one,v['rows']))
rows=[]
for r,d in zip(v['rows'],details):
 f=RAW/'episodes'/r['episode'];i=r['slot'];c=read(f/'combat-audit.json')['heroes'][i];s=read(f/'stalls.json')['heroes'][i]
 rows.append({**{k:r[k] for k in ['episode','slot','score','ticks','failed_slots']},**r['hero'],'effects':c['totals'],'spells':c['spells'],'spell_damage':c['spell_damage'],'state_time':s['totals'],'action_counts':d['heroes'][i]['counts']})
f=RAW/'episodes'/v['plan']['coached_episode'];econ=read(f/'economy.json');combat=read(f/'combat-audit.json');stalls=read(f/'stalls.json');detail=details[0];totalTicks=read(f/'results.json')['ticks']
ours=econ['heroes'][7];andre=econ['heroes'][0]
comparison=[]
for slot,label in [(0,'Andre khors179'),(7,'Our Coach')]:
 e=econ['heroes'][slot];c=combat['heroes'][slot];st=stalls['heroes'][slot];a=detail['heroes'][slot]['counts'];w=st['windows']
 comparison.append({'label':label,'slot':slot,'class':e['class'],'score':read(f/'results.json')['scores'][slot],
 'xp':e['total_xp'],'hero_xp':e['xp_sources'].get('hero',0),'creep_xp':e['xp_sources'].get('creep',0),'building_xp':c['totals'].get('xp_structure',0),'god_xp':c['totals'].get('xp_god',0),
 'hero_kills':e['hero_kills'],'creep_last_hits':e['creep_last_hits'],'deaths':e['deaths'],'level':e['level'],
 'building_target_commands':sum(a.get('attack_target_'+k,0) for k in ['TowerBuilding','BarracksBuilding','god']),'all_attack_target_commands':a.get('command_2',0),
 'structure_damage':c['totals'].get('damage_basic_structure',0)+c['totals'].get('damage_spell_structure',0),'out_of_range_casts':e['rejected'].get('ActionOutOfRange',0),
 'field_minutes':st['totals']['field_ticks']/1440,'dead_minutes':st['totals']['dead_ticks']/1440,'keep_minutes':st['totals']['keep_ticks']/1440,
 'last6_battle_minutes_xp':sum(x['values'].get('xp',0) for x in w if 14<=x['index']<20),'full_minutes_over200xp':sum(x['full_minute'] and x['values'].get('xp',0)>200 for x in w),'full_minutes':sum(x['full_minute'] for x in w)})
byid={b['id']:b for b in detail['initial_buildings']};barrackDeaths=[{**e,'lane':byid[e['target']]['lane']} for e in detail['building_deaths'] if e['kind']=='BarracksBuilding'];comparisonRows=rows[1:]
analysis={'coached_episode':v['plan']['coached_episode'],'game_version':'2026.9.23.1','engine_commit':'d6827a4bd3a55a46cf86f88e921f147137709c64','duration_minutes':totalTicks/1440,'time_penalty':200*totalTicks/1440,'coached_comparison':comparison,'barracks':{'initial_per_team':6,'deaths':barrackDeaths,'remaining_red_lanes':[0,0],'remaining_blue':6},
 'other12':{'n':len(comparisonRows),'mean_score':statistics.mean(r['score'] for r in comparisonRows),'zeroes':sum(r['score']==0 for r in comparisonRows),'nonzero_mean':statistics.mean(r['score'] for r in comparisonRows if r['score']>0),'all_vm_clean_games':sum(not r['failed_slots'] for r in comparisonRows)},
 'all13':{'basic_structure_damage_total':sum(r['effects'].get('damage_basic_structure',0) for r in rows),'zero_basic_structure_damage_games':sum(r['effects'].get('damage_basic_structure',0)==0 for r in rows),'all_vm_clean_games':sum(not r['failed_slots'] for r in rows),'rows':rows},
 'limits':['Coached episode deliberately selected for high score. Other12 selected by recency before decoding, not representative random sampling.','10of12 comparison games and the coached game have other-player VM failures; two all-clean comparison games retained separately. Khors VM clean in all13.','Retrospective complete truth and commands; exact source/internal guards unavailable; no executable proxy or validated forecast.','No causal claim that removing buildings alone achieves7781. Classes, rosters, draft and routing are confounded.'],
 'source_sha256':v['rows'][0]['source_sha256'],'raw_root':str(RAW),'new_hosted_games':0}
write(RAW/'analysis.json',analysis);write(OUT/'evidence/analysis.json',analysis)
for n in ['plan.json','verified.json','opportunity.json','episode.json','results.json','player-status.json']:
 shutil.copy2(RAW/n,OUT/'evidence'/n)
write(OUT/'evidence/coached-economy.json',econ);write(OUT/'evidence/coached-stalls.json',stalls);write(OUT/'evidence/coached-combat.json',combat)
ir={'schema':'gota-opponent-descriptive-ir/2','id':'khors_v179_score_audit_20260923',
 'situation':{'identity':{'owner':'ply_3d22435e-30a2-4f2a-b037-a5c249583788','label':'khors:v179','version':'346416a0-78f9-401f-b0d3-fed3f840af8d','source_sha256_from_host_specs':analysis['source_sha256'],'source_available':False},'game_version':analysis['game_version'],'engine_commit':analysis['engine_commit'],'authority':'Retrospective full replay truth, submitted commands and accepted typed effects. Not a live feature set.','selection':v['plan']['selection'],'features':['visible enemy unit versus structure category','creep wave renewal by surviving barracks','typed XP sources','elapsed time and post-tick keep/dead/field durations'],'unknown':['Target ordering, threshold and memory','Exact route selection and opponent identity inference','Whether game extension is intentional','Ability auto/manual division']},
 'belief':{'claims':[{'id':'K179_UNIT_FOCUS','status':'observed','claim':'Coached game:0/730 explicit attack-target commands addressed buildings;12/13 audited games have zero basic structure damage. One game has170, so never attacks buildings is overbroad.','evidence':['evidence/analysis.json']},{'id':'K179_RENEWABLE_XP','status':'observed_effects','claim':'11892XP=6342creep+5550hero;37hero kills435creep last hits, no objective reward. Continued highXP late while Coach stopped receiving creepXP after minute11.','evidence':['evidence/coached-economy.json','evidence/coached-combat.json']},{'id':'BARRACKS_ECONOMY','status':'source_verified_mechanism_observed_exposure','claim':'Destroyed barracks stop waves. Blue destroyed4of6red barracks, including3byCoach, removing both central and lane2spawns. Six blue barracks survived. This supports, but does not prove, a productive-lane opportunity-cost intervention.','evidence':['evidence/opportunity.json','../../../../games/gods_of_the_arena/experiments/2026-09-23-unit-farming.md']},{'id':'K179_VARIABILITY','status':'observed','claim':'Other12recent games include3zero scores; mean1642.25. The7781episode is not a demonstrated typical outcome.','evidence':['evidence/analysis.json']}],'forecast_validated':False,'counter_validated':False},
 'goal':{'renewable_xp':{'status':'analyst_hypothesis','description':'Maintain recurring hero/creep XP that exceeds200per added minute.'},'preserve_barracks':{'status':'unidentified_intent','description':'Avoiding structures preserves creep sources, but intent/internal goal is unavailable.'}},
 'strategy':[{'id':'UNIT_TARGET_BIAS','status':'descriptive','when':'Engaging enemies in audited games','prefer':'heroes/creeps over deliberate building attacks','unknown':'eligible opportunity counts and exact guard ordering'},{'id':'REPEATED_FARM','status':'descriptive','when':'Later stages of coached Crossbowman episode','prefer':'continued creep farming and repeated hero kills','unknown':'public route-selection rule'}],
 'skill':{'unit_combat':{'status':'observed','effects':'37hero kills435creep last hits in coached game; attacks and spells both contribute'},'resource_return':{'status':'observed','effects':'Portals, potions and5buyback requests occur; inherited own core build already11→16→18→19. Do not copy unvalidated timing or keep-to-keep portal use.'},'cast_range':{'status':'transfer_hypothesis','effects':'50out-of-range rejections versus1328for our Ranger; classes differ. Validate legal ranges before separate transfer.'}},
 'execution':{'kind':'descriptive_non_executable','forecast_status':'not_validated','proxy_usable':False,'may_use_hidden_features_in_live_policy':False},
 'update':{'revision':1,'origin':'User episode and attack-building screenshot September23; separate from preserved khors114 model.','evidence':['evidence/analysis.json','evidence/verified.json'],'counter_candidate':'unit-farming1238ec73; fresh hosted test pending; no counter gain claimed','version_drift':'Andre moved to khors180 during analysis. Descriptive model remainsv179; prospective comparison uses independently resolved current rivals.'}}
write(OUT/'opponent.ir.json',ir)
unit=ROOT.parent/'polyworld/tmp/gota-unit-farming59-20260923/unit-farming/evidence';write(unit/'coaching-analysis.json',analysis)
print(json.dumps({'published':str(OUT),'comparison':comparison,'other12':analysis['other12']}))

"""Current-release mixed-team diagnosis with one complete100episode XP request."""
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
from datetime import datetime,timezone
import shutil,subprocess,sys,time
from hosted_wave import client,create,episodes,fetch,TERMINAL
from hosted_wave_audit import verify
from policy_ir import HERE,read,write,digest
from release_workspace import RUN
from release_field import OWNED_PLAYERS,DIVISION
from release_hosted import summarize
from win_hosted import live

ROOT=RUN/'coached-lanes/r5-current-field'


def run():
    game=live();ROOT.mkdir(exist_ok=True)
    old=read(RUN/'coached-lanes/r5-convoy/hosted/current/plan.json')
    plan={k:old[k] for k in ['target','game_version','game_source','config','policy_version','policy_label']}
    plan.update(design='100sampled current-division mixed-team episodes, one subject and nine random champions excluding both ownedplayers. Diagnostic only, no candidate A/B or automaticpromotion. Every replay and alltenVMs mustverify beforecompetitive claims. Reportclass,color,deaths,gear,glory andcommanddiversity.')
    if game['id']!=plan['target']['coworld_id']:raise ValueError('League game changed')
    if (ROOT/'plan.json').exists() and read(ROOT/'plan.json')!=plan:raise ValueError('Frozen field changed')
    write(ROOT/'plan.json',plan);shutil.copy2(RUN/'r5/audit',ROOT/'audit')
    body={'idempotency_key':'gota-coached-current-field-'+digest(plan)[:20],
          'target':{'division_id':DIVISION},'game_config_overrides':plan['config'],'num_episodes':100,
          'excluded_players':OWNED_PLAYERS,
          'roster':[{'slot':-1,'player':{'policy_ref':plan['policy_version']}}]+[{'slot':-1,'player':{'random':True}} for _ in range(9)],
          'notes':plan['design']}
    with client() as c:request=create(c,body,ROOT/'batch')
    print(request,flush=True)
    log=(ROOT/'audit.log').open('a')
    proc=subprocess.Popen([sys.executable,str(HERE/'watch_hosted_audit.py'),str(ROOT),'--workers','2'],stdout=log,stderr=log)
    try:
        with client() as c:
            while True:
                rows=episodes(c,request);write(ROOT/'batch/episodes.json',rows)
                if any(e['status'] in {'failed','cancelled','error'} for e in rows):raise ValueError('Failed episode retained; no competitive verdict')
                count=0
                for e in rows:
                    if e['status']=='completed':
                        fetch(c,e,ROOT/'artifacts',plan['policy_version']);count+=1
                print('Field fetched',count,'/100',flush=True)
                if count==100:
                    write(ROOT/'collection.json',{'episodes':100,'request_count':1});break
                time.sleep(15)
        if proc.wait()!=0:raise ValueError('Fullaudit failed; retained invalidgames need diagnosis')
    finally:
        if proc.poll() is None:proc.terminate();proc.wait()
        log.close()
    report()


def report():
    plan=read(ROOT/'plan.json');version=plan['policy_version'];folders=[p.parent for p in (ROOT/'artifacts').glob('*/.done')]
    if len(folders)!=100:raise ValueError('Incomplete field collection')
    binary=ROOT/'audit';sha=digest(binary.read_bytes())
    with ThreadPoolExecutor(4) as pool:list(pool.map(lambda f:verify(f,binary,sha),folders))
    rr=[]
    for f in folders:
        ep,r,a=[read(f/n) for n in ['episode.json','results.json','audit.json']]
        roster=ep['policy_version_ids'];config={k:v for k,v in ep['game_config'].items() if k not in {'seed','players','tokens'}}
        if (ep['coworld_id']!=plan['target']['coworld_id'] or ep['coworld_version']!=plan['game_version'] or config!=plan['config'] or roster.count(version)!=1):raise ValueError('Fieldsource/config/subject changed')
        slot=roster.index(version);h=a['heroes'][slot]
        if any(p['player_id'] in OWNED_PLAYERS for p in ep['participants'] if p['position']!=slot):raise ValueError('Ownedplayer sampled')
        if [h['total_xp'] for h in a['heroes']]!=r['total_xp']:raise ValueError('XP mismatch')
        rr.append({'episode':ep['id'],'slot':slot,'seed':r['seed'],'class':h['class'],'win':h['score'],'deaths':h['deaths'],'alive_ticks':h['alive_ticks'],'ticks':r['ticks'],'xp':h['total_xp'],'first_gear_tick':h['first_gear_tick'],'glory':h['score']*(h['total_xp']-100*r['ticks']/1440),'timeout':r['outcome']=='time_limit','roster':roster,'replay_sha256':a['replay_sha256']})
    if len({r['seed'] for r in rr})!=100:raise ValueError('Repeated effective seeds')
    result=summarize([{'rows':rr}]);result.update(design=plan['design'],colors={str(c):{'games':len(ss:=[r for r in rr if r['slot']//5==c]),'wins':sum(r['win'] for r in ss)} for c in [0,1]})
    write(ROOT/'result.json',result);print({k:v for k,v in result.items() if k!='rows'},flush=True)


if __name__=='__main__':run()

"""Frozen local five-copy team comparison on the clean published engine."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
import subprocess

from policy_ir import HERE, ROOT, bundle, digest, read, write
from release_workspace import RUN, SOURCE, VERSION, verify
from rush_candidates import make, VARIANTS

STUDY = RUN / 'rush-study'


def prepare():
    verify()
    root = STUDY / 'local';root.mkdir(parents=True, exist_ok=True)
    if (root / 'plan.json').exists(): return read(root / 'plan.json')
    sources = {'current': str(HERE / 'win_bounded_0916.evaluated.bas')}
    for n in VARIANTS:
        bundle(make(n), root / 'candidates' / n)
        sources[n] = str(root / 'candidates' / n / 'policy.bas')
    config = read(RUN / 'local/config.json');write(root / 'config.json', config)
    paths = [RUN / 'r3/build/episode', RUN / 'r3/build/audit', root / 'config.json', RUN / 'local/default.bas']
    paths += [HERE / n for n in ['rush_contract.py','rush_candidates.py','rush_local.py','binding.py','policy_ir.py']]
    plan = {'created_at': datetime.now(timezone.utc).isoformat(), 'source': SOURCE, 'version': VERSION,
            'sources': sources, 'input_sha256': {str(p): digest(p.read_bytes()) for p in paths},
            'source_sha256': {n: digest(open(p,'rb').read()) for n,p in sources.items()},
            'cases': [{'seed': 740000+i, 'color': i%2, 'opponent': 'default' if i%4<2 else 'current'} for i in range(40)],
            'rule': 'Finish160localgames/allfullaudits. Three shared-rush variants and unchanged bounded control. Fivecopies/team,20games/color,10eachcolor/opponent. Fixedlineups are directional checks only; choose highestwins, then shortestwinningduration, then fewestdeaths. Require >=90%wins vsdefault and >=50%vscurrent plus equipment and VM validity before exactJordan hosted testing. No interim tuning.'}
    write(root / 'plan.json', plan);return plan


def run(plan=None, root=None):
    if plan is None: plan=prepare()
    if root is None: root=STUDY/'local'
    for path,sha in plan['input_sha256'].items():
        if digest(open(path,'rb').read())!=sha:raise ValueError('Frozen local input changed')
    def one(job):
        name,case=job;own=list(range(case['color']*5,case['color']*5+5))
        folder=root/'games'/name/f"{case['seed']}";folder.mkdir(parents=True,exist_ok=True)
        source=plan['sources'][name]
        if digest(open(source,'rb').read())!=plan['source_sha256'][name]:raise ValueError('Policy changed')
        opponent=RUN/'local/default.bas' if case['opponent']=='default' else HERE/'win_bounded_0916.evaluated.bas'
        if not (folder/'result.json').exists():
            cmd=[str(RUN/'r3/build/episode'),'--config',str(root/'config.json'),'--seed',str(case['seed']),'--record',str(folder/'replay.bin')]
            cmd+=['--bot:'+str(source if slot in own else opponent) for slot in range(10)]
            with (folder/'stdout.log').open('w') as out,(folder/'stderr.log').open('w') as err:
                subprocess.run(cmd,cwd=ROOT,stdout=out,stderr=err,check=True,timeout=400)
            r=json.loads((folder/'stdout.log').read_text().splitlines()[-1]);write(folder/'result.json',r)
        r=read(folder/'result.json')
        if not (folder/'audit.json').exists():
            proc=subprocess.run([str(RUN/'r3/build/audit'),'--replay',str(folder/'replay.bin')],cwd=ROOT,capture_output=True,text=True,check=True,timeout=400)
            write(folder/'audit.json',json.loads(proc.stdout.splitlines()[-1]))
        a=read(folder/'audit.json')
        if a['hash_mismatches'] or a['ticks']!=r['ticks'] or a['state_hash']!=r['state_hash'] or a['actions_consumed']!=r['actions']:
            raise ValueError('Replay diverged')
        if 'BASIC error:' in (folder/'stdout.log').read_text():raise ValueError('VM failure')
        heroes=[r['heroes'][s] for s in own]
        if any(h['max_work']>50000 or h['max_instructions']>20000 for h in r['heroes']):raise ValueError('VM budget exceeded')
        return {'name':name,**case,'win':heroes[0]['score'],'ticks':r['ticks'],'deaths':sum(h['deaths'] for h in heroes),
                'gear_heroes':sum(h['equipment_count']>0 for h in heroes),'fort_hp':r['fort_hp'],
                'replay_sha256':digest((folder/'replay.bin').read_bytes())}
    jobs=[(n,c) for c in plan['cases'] for n in plan['sources']];rows=[]
    with ThreadPoolExecutor(8) as pool:
        for future in as_completed([pool.submit(one,j) for j in jobs]):
            rows.append(future.result())
            if len(rows)%10==0:print(f'Local fullgames/audits {len(rows)}/{len(jobs)}',flush=True)
    rows.sort(key=lambda r:(r['name'],r['seed']));metrics={}
    for n in plan['sources']:
        rr=[r for r in rows if r['name']==n];wins=[r for r in rr if r['win']]
        metrics[n]={'games':len(rr),'wins':len(wins),'mean_win_seconds':sum(r['ticks'] for r in wins)/24/max(1,len(wins)),
                    'deaths':sum(r['deaths'] for r in rr),'all_gear':all(r['gear_heroes']==5 for r in rr),
                    'opponents':{o:sum(r['win'] for r in rr if r['opponent']==o) for o in ['default','current']},
                    'colors':{str(c):sum(r['win'] for r in rr if r['color']==c) for c in [0,1]}}
    selected=[n for n in plan.get('variants', VARIANTS) if metrics[n]['opponents']['default']>=18 and metrics[n]['opponents']['current']>=10 and metrics[n]['all_gear']]
    selected.sort(key=lambda n:(-metrics[n]['wins'],metrics[n]['mean_win_seconds'],metrics[n]['deaths'],n))
    write(root/'result.json',{'verified_games':len(rows),'metrics':metrics,'selected':selected,'rows':rows})
    print(metrics,selected,flush=True)


if __name__=='__main__':run()

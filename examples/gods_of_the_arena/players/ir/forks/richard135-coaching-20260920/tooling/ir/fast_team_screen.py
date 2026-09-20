"""Small local tactical screen followed by full40case validation; no promotion."""
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
import json,subprocess
from policy_ir import HERE,ROOT,bundle,digest,read,write
from release_workspace import RUN,verify


def screen(study,variants,factory,count=4,seed=744000,stage='screen'):
    verify();root=study/stage;root.mkdir(parents=True,exist_ok=True)
    binary=RUN/'r5/fast/episode';auditor=RUN/'r5/build/audit'
    if not read(RUN/'r5/fast/calibration/proof.json')['full_replay_bytes_equal']:raise ValueError('Fast evaluator not calibrated')
    if not (root/'plan.json').exists():
        sources={'current':str(HERE/'win_bounded_0916.evaluated.bas')}
        for n in variants:
            bundle(factory(n),root/'candidates'/n);sources[n]=str(root/'candidates'/n/'policy.bas')
        write(root/'config.json',read(RUN/'local/config.json'))
        plan={'sources':sources,'variants':list(variants),'cases':[{'seed':seed+i,'color':i%2,'opponent':'default' if i%4<2 else 'current'} for i in range(count)],
              'inputs':{str(p):digest(p.read_bytes()) for p in [binary,auditor,root/'config.json',RUN/'r5/default.bas']},
              'source_sha256':{n:digest(Path(p).read_bytes()) for n,p in sources.items()},
              'rule':f'Complete{count}cases/arm, allfullaudits. Small directional fixedlineups; notindependentgeneralization. Localqualifier must win>=90%vsdefault and>=50%vsbounded, allgear, VMvalid. No interimtuning; freeze40newcases for selectedsmall-screen qualifier beforehosted.'}
        write(root/'plan.json',plan)
    p=read(root/'plan.json')
    for path,sha in p['inputs'].items():
        if digest(Path(path).read_bytes())!=sha:raise ValueError('Frozen tool/config changed')
    def one(job):
        n,c=job;d=root/'games'/n/str(c['seed']);d.mkdir(parents=True,exist_ok=True)
        src=Path(p['sources'][n]);opp=Path(p['sources']['current']) if c['opponent']=='current' else RUN/'r5/default.bas'
        if digest(src.read_bytes())!=p['source_sha256'][n]:raise ValueError('Frozen policy changed')
        own=list(range(c['color']*5,c['color']*5+5));tape=d/'replay.bin'
        if not (d/'result.json').exists():
            cmd=[str(binary),'--config',str(root/'config.json'),'--seed',str(c['seed']),'--record',str(tape)]
            cmd+=['--bot:'+str(src if s in own else opp) for s in range(10)]
            with (d/'stdout.log').open('w') as out,(d/'stderr.log').open('w') as err:subprocess.run(cmd,cwd=ROOT,stdout=out,stderr=err,check=True,timeout=600)
            write(d/'result.json',json.loads((d/'stdout.log').read_text().splitlines()[-1]))
        r=read(d/'result.json')
        if not (d/'audit.json').exists():
            result=subprocess.run([str(auditor),'--replay',str(tape)],cwd=ROOT,capture_output=True,text=True,check=True,timeout=600)
            write(d/'audit.json',json.loads(result.stdout.splitlines()[-1]))
        a=read(d/'audit.json')
        if a['hash_mismatches'] or a['state_hash']!=r['state_hash'] or a['actions_consumed']!=r['actions'] or a['ticks']!=r['ticks']:raise ValueError('Replay mismatch')
        if any(h['max_work']>50000 or h['max_instructions']>20000 for h in r['heroes']):raise ValueError('VM budget failed')
        hh=[r['heroes'][s] for s in own]
        return {'name':n,**c,'win':hh[0]['score'],'ticks':r['ticks'],'deaths':sum(h['deaths'] for h in hh),'gear_heroes':sum(h['equipment_count']>0 for h in hh),'replay_sha256':digest(tape.read_bytes())}
    rows=[];jobs=[(n,c) for c in p['cases'] for n in p['sources']]
    with ThreadPoolExecutor(4) as pool:
        for f in as_completed([pool.submit(one,j) for j in jobs]):
            rows.append(f.result());print(f'{stage} {len(rows)}/{len(jobs)}',flush=True)
    metrics={}
    for n in p['sources']:
        rr=[r for r in rows if r['name']==n];ww=[r for r in rr if r['win']]
        metrics[n]={'games':len(rr),'wins':len(ww),'mean_win_seconds':sum(r['ticks'] for r in ww)/24/max(1,len(ww)),
                    'deaths':sum(r['deaths'] for r in rr),'all_gear':all(r['gear_heroes']==5 for r in rr),
                    'opponents':{o:sum(r['win'] for r in rr if r['opponent']==o) for o in ['default','current']},
                    'colors':{str(c):sum(r['win'] for r in rr if r['color']==c) for c in [0,1]}}
    selected=[n for n in variants if metrics[n]['opponents']['default']>=count*.45 and metrics[n]['opponents']['current']>=count*.25 and metrics[n]['all_gear']]
    selected.sort(key=lambda n:(-metrics[n]['wins'],metrics[n]['mean_win_seconds'],metrics[n]['deaths'],n))
    write(root/'result.json',{'verified_games':len(rows),'metrics':metrics,'selected':selected,'rows':rows})
    print(metrics,selected,flush=True);return selected

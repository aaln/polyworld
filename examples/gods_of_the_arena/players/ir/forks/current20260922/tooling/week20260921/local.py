"""Run frozen complete matches and resimulate every recorded state hash."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
from build import ROOT, ENGINE, STUDY, digest, write

def run_case(case):
    out=STUDY/'local'/case['name']/str(case['seed'])/str(case['side'])
    out.mkdir(parents=True,exist_ok=True)
    result_path=out/'result.json'
    if result_path.exists(): return json.loads(result_path.read_text())
    binary=STUDY/'bin/episode'; tape=out/'replay.bin'
    cmd=[str(binary),'--config',str(STUDY/'game-config.json'),'--seed',str(case['seed']),'--record',str(tape)]
    cmd += ['--bot:'+case['source']+':5','--bot:'+case['opponent']+':5'] if case['side']==0 else ['--bot:'+case['opponent']+':5','--bot:'+case['source']+':5']
    try:
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=900)
        (out/'stdout.log').write_text(p.stdout);(out/'stderr.log').write_text(p.stderr)
        assert p.returncode==0,(p.returncode,p.stderr[-1500:])
        live=json.loads(p.stdout.splitlines()[-1]);write(out/'live.json',live)
        q=subprocess.run([str(binary),'--replay',str(tape)],capture_output=True,text=True,timeout=900)
        (out/'audit-stderr.log').write_text(q.stderr)
        assert q.returncode==0,(q.returncode,q.stderr[-1500:])
        audit=json.loads(q.stdout.splitlines()[-1]);write(out/'audit.json',audit)
        for key in ('ticks','battle_ticks','draft_ticks','state_hash','actions','winner','fort_hp','commands'):
            assert live[key]==audit[key],key
        assert len(live['heroes'])==10 and len({h['class'] for h in live['heroes']})==10
        assert all(h['drafted'] for h in live['heroes'])
        assert live['draft_ticks']<=2400
        ours=live['heroes'][case['side']*5:case['side']*5+5]
        theirs=live['heroes'][(1-case['side'])*5:(1-case['side'])*5+5]
        result={**case,'valid':True,'win':int(live['winner']==case['side']),
          'loss':int(live['winner']==1-case['side']),'draw':int(live['winner']==-1),
          'ticks':live['ticks'],'draft_ticks':live['draft_ticks'],'xp':sum(h['xp'] for h in ours),
          'enemy_xp':sum(h['xp'] for h in theirs),'deaths':sum(h['deaths'] for h in ours),
          'max_instructions':max(h['max_instructions'] for h in ours),
          'max_work':max(h['max_work'] for h in ours),'all_hashes_equal':True,
          'replay_sha256':digest(tape.read_bytes()),'source_sha256':digest(Path(case['source']).read_bytes())}
    except Exception as exc:
        result={**case,'valid':False,'error':repr(exc)}
    write(result_path,result)
    print(json.dumps(result),flush=True)
    return result

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--name',default='lane');parser.add_argument('--games',type=int,default=8);args=parser.parse_args()
    assert args.games%2==0
    game=json.loads((STUDY/'canonical-game.json').read_text())
    cfg=game['manifest']['variants'][0]['game_config'];write(STUDY/'game-config.json',cfg)
    source=ENGINE/'examples/gods_of_the_arena/players/base.bas' if args.name=='baseline' else STUDY/'candidates'/args.name/'policy.bas'
    opponent=ENGINE/'examples/gods_of_the_arena/players/base.bas'
    cases=[{'name':args.name,'source':str(source),'opponent':str(opponent),'seed':921100+r,'side':side} for r in range(args.games//2) for side in (0,1)]
    plan=STUDY/(args.name+'-local-plan.json')
    frozen={'cases':cases,'source_sha256':digest(source.read_bytes()),'opponent_sha256':digest(opponent.read_bytes()),'config_sha256':digest((STUDY/'game-config.json').read_bytes())}
    if plan.exists():assert json.loads(plan.read_text())==frozen
    else:write(plan,frozen)
    with ThreadPoolExecutor(2) as pool:rows=list(pool.map(run_case,cases))
    write(STUDY/(args.name+'-local-result.json'),{'rows':rows,'complete':len(rows)==args.games,'scope':'Native diagnostic only; no hosted quality qualification.'})

if __name__=='__main__':main()

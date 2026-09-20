"""Run frozen repairs on the seed in the actual replay, not request defaults."""
from concurrent.futures import ThreadPoolExecutor
import json
import subprocess

from jordan254_research import PARENT,STUDY as BASE
from policy_ir import ROOT,digest,read,write
from ranger_guard_hosted import freeze
from release_workspace import RUN,verify
from stale_rally_repair import STUDY,prepare,VARIANTS


def main():
    verify();prepare()
    original=BASE/'user-stall-77d700dd/artifacts/ereq_77d700dd-de3c-4ee6-ab43-965fedf66b7d'
    seed=read(original/'audit.json')['seed']
    out=STUDY/'replay-seed';out.mkdir(exist_ok=True)
    sources={n:STUDY/'candidates'/n/'policy.bas' for n in VARIANTS}
    sources['old_middle_rush']=PARENT/'policy.bas'
    freeze(out/'prospective.json',{'seed':seed,'request_default_seed':2026,
        'correction':'The actual full-replay auditor reads1651318157; request game_config.seed2026 is an overridden default. Preserve the unrelated2026 tests, do not call them a reproduction.',
        'sources':{n:digest(p.read_bytes()) for n,p in sources.items()},
        'source_scope':'Opponent public local default is equivalent only if full old-middle action/hash playback matches the hosted tape.',
        'gate':'Must reproduce exact old loss; then local repair episode is a single diagnostic counterfactual, not competitive qualification.'})
    def one(pair):
        name,src=pair;folder=out/name;folder.mkdir(exist_ok=True)
        if not (folder/'result.json').exists():
            cmd=[str(RUN/'r5/fast/episode'),'--config',str(STUDY/'config.json'),'--seed',str(seed),
                 '--record',str(folder/'replay.bin')]+['--bot:'+str(src if i<5 else RUN/'r5/default.bas') for i in range(10)]
            with (folder/'stdout.log').open('w') as stdout,(folder/'stderr.log').open('w') as stderr:
                subprocess.run(cmd,cwd=ROOT,stdout=stdout,stderr=stderr,check=True,timeout=900)
            write(folder/'result.json',json.loads((folder/'stdout.log').read_text().splitlines()[-1]))
        result=read(folder/'result.json')
        if not (folder/'audit.json').exists():
            audit=subprocess.check_output([str(RUN/'r5/fast/audit-local'),'--replay',str(folder/'replay.bin')],text=True,cwd=ROOT)
            write(folder/'audit.json',json.loads(audit.splitlines()[-1]))
        audit=read(folder/'audit.json')
        assert audit['hash_mismatches']==0 and audit['state_hash']==result['state_hash']
        assert audit['ticks']==result['ticks'] and audit['actions_consumed']==result['actions']
        assert all(h['max_work']<=50000 and h['max_instructions']<=20000 for h in result['heroes'])
        assert all(h['equipment_count']>0 for h in result['heroes'][:5])
        print(name,'ticks',result['ticks'],'score',result['heroes'][0]['score'],flush=True)
        return name,{'ticks':result['ticks'],'red_win':result['heroes'][0]['score'],
                     'red_deaths':sum(h['deaths'] for h in result['heroes'][:5]),'full_audit_passed':True}
    with ThreadPoolExecutor(4) as pool:rows=dict(pool.map(one,sources.items()))
    parity=json.loads(subprocess.check_output([str(RUN/'r5/compare-gameplay'),str(original/'replay.bin'),str(out/'old_middle_rush/replay.bin')],text=True))
    reproduced=all(parity[k] for k in ['all_actions_equal','all_state_hashes_equal','setup_equal','same_seed'])
    write(out/'result.json',{'arms':rows,'original_loss_reproduced':reproduced,'parity':parity,
          'seed':seed,'promotion_qualification':False})
    assert reproduced,'Public local default/config does not reproduce this hosted tape; do not attribute counterfactual wins.'
    print('Exact original gameplay reproduced.',rows,flush=True)


if __name__=='__main__':main()

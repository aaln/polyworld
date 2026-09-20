"""Complete responding native games; competitive claims require hosted arms."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import importlib.util
from pathlib import Path
import subprocess
from build import ROOT, STUDY, read, write, digest

spec=importlib.util.spec_from_file_location('growth_local_reuse',ROOT/'games/gods_of_the_arena/instruments/richard_growth/study.py')
local=importlib.util.module_from_spec(spec);spec.loader.exec_module(local)
local.STUDY=STUDY


def main():
    assert read(STUDY/'vm-proof.json')['passed']
    local.verify()
    sources={n:str(STUDY/('inputs/formation' if n=='formation' else 'candidates/profile_switch')/'policy.bas')
             for n in ('formation','profile_switch')}
    rivals={'richard135':str(ROOT/'docs/opponents/richard-v135/source-audit-20260920/v135.bas'),
            'legacy_reference':str(STUDY/'inputs/legacy/policy.bas'),
            'jordan_specialist_reference':str(STUDY/'inputs/jordan/policy.bas')}
    cases=[{'opponent':r,'side':side,'seed':9990000+4*i+2*rep+side}
           for i,r in enumerate(rivals) for rep in range(2 if i==0 else 1) for side in (0,1)]
    plan={'at':datetime.now(timezone.utc).isoformat(),'sources':sources,'opponents':rivals,'cases':cases,
          'gate':'All16games full runtime/replay valid, <=19000instructions; blue Richard control/candidate complete command equality on2cases. Other local outcomes diagnostic, never Alex/Jordan proxy evidence.',
          'input_hashes':{p:digest(Path(p).read_bytes()) for p in [*sources.values(),*rivals.values(),str(STUDY/'config.json')]}}
    p=STUDY/'local-plan.json'
    if not p.exists():write(p,plan)
    plan=read(p)
    for path,sha in plan['input_hashes'].items():assert digest(Path(path).read_bytes())==sha
    jobs=[(name,case) for case in plan['cases'] for name in plan['sources']]
    def run(job):
        name,case=job
        return local.match(name,case,plan['sources'][name],plan['opponents'][case['opponent']],
                           STUDY/'local'/name/str(case['seed']))
    with ThreadPoolExecutor(2) as pool:rows=list(pool.map(run,jobs))
    write(STUDY/'local-results.json',{'complete':True,'rows':rows})
    valid=all(r['valid'] and r['gear_heroes']==5 and r['max_instructions']<=19000 for r in rows)
    stream=ROOT.parent/'gota-autoresearch/cycles/20260919T101825Z-880d3c/replay-command-stream'
    checks=[]
    for case in plan['cases']:
        if case['opponent']=='richard135' and case['side']==1:
            hashes={}
            for n in plan['sources']:
                tape=STUDY/'local'/n/str(case['seed'])/'replay.bin'
                result=subprocess.run([str(stream),str(tape)],capture_output=True,check=True)
                hashes[n]=digest(result.stdout)
            checks.append({'case':case,'hashes':hashes,'equal':len(set(hashes.values()))==1})
    verdict={'passed':valid and all(c['equal'] for c in checks),'all_games_and_margin_valid':valid,
             'blue_richard_exact_command_parity':checks,'games':len(rows),'source_sha256':digest(Path(sources['profile_switch']).read_bytes())}
    write(STUDY/'local-verdict.json',verdict);print(verdict,flush=True)


if __name__=='__main__':main()

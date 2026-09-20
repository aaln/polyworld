"""Full prospective local confirmation, including exact inactive-blue parity."""
import json
import subprocess
import time
from core_pressure import STUDY, VARIANTS, make
from economy_feedback import record
from policy_ir import read, write
from ranger_guard_hosted import freeze
from ranger_guard_queue import alive
from release_workspace import RUN
from rush_defense_eval import evaluate


def main(study=STUDY,variants=VARIANTS,factory=make,seed=778000):
    plan={'variants':variants,'cases_per_variant':60,'seed':seed,'local_games':(len(variants)+2)*60,
        'primary_control':'pressure_parent',
        'rule':f'Complete all{(len(variants)+2)*60}games; no opponent/color win regression versus pressure_parent, all gear/VM/full replay checks, '
               f'all{30*(len(variants)-2)} inactive-blue full gameplay comparisons exact. Rank wins/deaths/name. '
               'Actual red-kite27 and gota-g002, Jordan/black-kite preservation and mixed-field checks remain required.'}
    freeze(study/'prospective-plan.json',plan)
    other=RUN/'coached-lanes/r5-breach-pressure/local-process.json'
    while alive(read(other)['pid']): time.sleep(15)
    evaluate('local',variants,60,seed,factory,study,RUN/'r5/fast/audit-local')
    result=read(study/'local/result.json'); m=result['metrics']; proofs={}
    for name in variants[2:]:
        rr=[]
        for row in result['rows']:
            if row['name']!=name or row['color']!=1: continue
            root=study/'local/games'
            p=json.loads(subprocess.check_output([str(RUN/'r5/compare-gameplay'),
                str(root/name/str(row['seed'])/'replay.bin'),str(root/'pressure_parent'/str(row['seed'])/'replay.bin')],text=True))
            rr.append({'seed':row['seed'],**p})
        proofs[name]={'games':len(rr),'all_gameplay_equal':len(rr)==30 and all(all(p[k] for k in
            ('all_actions_equal','all_state_hashes_equal','setup_equal','config_equal','same_seed')) for p in rr),'rows':rr}
    write(study/'local/blue-parity.json',proofs)
    b=m['pressure_parent']
    qualified=[n for n in variants[2:] if proofs[n]['all_gameplay_equal'] and m[n]['all_gear'] and
        m[n]['wins']>=b['wins'] and all(m[n]['opponents'][o]>=b['opponents'][o] for o in b['opponents']) and
        all(m[n]['colors'][c]>=b['colors'][c] for c in b['colors'])]
    qualified.sort(key=lambda n:(-m[n]['wins'],m[n]['deaths'],n))
    comparison={'selected':qualified[0] if qualified else None,'qualified':qualified,'metrics':m,
        'verified_games':result['verified_games'],'scope':plan['rule']}
    for n in variants[2:]:
        src=study/'local/candidates'/n;out=study/'local/comparison-feedback'/n
        if not out.exists(): record(src/'policy.ir.json',src/'policy.bas',
            f'Fresh60case core comparison: candidate{m[n]}, pressureparent{b}, deployed{m["deployed"]}. '
            f'Blue30game parity{proofs[n]["all_gameplay_equal"]}; qualification{n in qualified}. Hosted followup untested.',
            study/'local/result.json',out)
    write(study/'local/comparison.json',comparison)
    print('Core confirmation',comparison,flush=True)


if __name__=='__main__': main()

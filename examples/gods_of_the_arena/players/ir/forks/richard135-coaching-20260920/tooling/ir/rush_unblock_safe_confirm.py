"""Keep the failed study; reuse only fully audited unchanged control/spread cases."""
import os
from pathlib import Path
import time

from economy_feedback import record
from policy_ir import digest,read,write
from release_workspace import RUN
from rush_defense_eval import evaluate
from rush_unblock_safe import STUDY,make


def main():
    original=STUDY/'local';target=STUDY/'local-safe'
    target.mkdir(exist_ok=True)
    names=['deployed_parent','fused_core','spread']
    plan={'variants':names,'cases_per_arm':60,'seed':762000,
          'new_games':60,'reused_games':240,
          'reason':'Preserve original300game study with invalid near_core arm. Reuse all60audited '
                   'games from each unchanged parent/spread/legacy arm; run fused_core on every '
                   'same scheduled seed. The budget repair follows an observed failure, so '
                   'these local results are adaptive engineering evidence, not a held-out win claim.',
          'rule':'All gear/VM/full replay checks, default>=18/20, eachotheropponent>=12/20, '
                 'wins>=deployed_parent. Rank by wins, lower deaths, then fused_core.'}
    if (target/'design.json').exists() and read(target/'design.json')!=plan:raise ValueError('Safe confirmation changed')
    write(target/'design.json',plan)
    reused={}
    for name in ['current','blue_parent','deployed_parent','spread']:
        while len(list((original/'games'/name).glob('*/audit.json')))!=60:
            if any(p.stat().st_size for p in (original/'games'/name).glob('*/stderr.log')):
                raise ValueError('Cannot reuse a control with errors')
            time.sleep(10)
        dest=target/'games'/name;dest.parent.mkdir(parents=True,exist_ok=True)
        if not dest.exists():dest.symlink_to(original/'games'/name,target_is_directory=True)
        reused[name]={'source':str(original/'games'/name),'episodes':60}
    failures=[{'artifact':str(p),'sha256':digest(p.read_bytes())} for p in (original/'games/near_core').glob('*/stderr.log') if p.stat().st_size]
    if not failures:raise ValueError('Missing original failure evidence')
    write(target/'reuse-and-quarantine.json',{'reused':reused,'invalid_original_arm':'near_core','failures':failures,
          'policy':'No failed episode discarded or relabeled; original arm is ineligible regardless of score.'})
    evaluate('local-safe',names,60,762000,make,STUDY,RUN/'r5/fast/audit-local')
    result=read(target/'result.json');m=result['metrics']
    qualified=[n for n in names[1:] if m[n]['all_gear'] and m[n]['wins']>=m['deployed_parent']['wins'] and
               m[n]['opponents']['default']>=18 and all(m[n]['opponents'][k]>=12 for k in ('current','center_proxy'))]
    qualified.sort(key=lambda n:(-m[n]['wins'],m[n]['deaths'],0 if n=='fused_core' else 1))
    comparison={'metrics':m,'qualified':qualified,'selected':qualified[0] if qualified else None,
                'primary_control':'deployed_parent','verified_games':result['verified_games'],'scope':plan}
    write(target/'comparison.json',comparison)
    for name in names:
        parent=target/'feedback'/name;out=target/'deployed-comparison-feedback'/name
        if not out.exists():record(parent/'policy.ir.json',parent/'policy.bas',
            f'Complete source-matched60case local comparison. Own{m[name]};deployed{m["deployed_parent"]}. '
            f'Qualified{name in qualified}. '+plan['reason'],target/'comparison.json',out)
    print('Safe confirmation qualified:',qualified,flush=True)


if __name__=='__main__':main()

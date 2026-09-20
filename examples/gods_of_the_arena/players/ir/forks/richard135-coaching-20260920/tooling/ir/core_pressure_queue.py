"""Serial hosted followup for locally qualified red objective defense."""
import time
from core_pressure import STUDY
from core_pressure_hosted import prepare,run
from policy_ir import read,write,digest
from priority_wide_queue import drained_wide
from ranger_guard_hosted import freeze
from ranger_guard_queue import alive
from red_pressure import STUDY as PRESSURE


def main():
    freeze(STUDY/'hosted-prospective-plan.json',{
        'max_candidates':2,'new_games_per_candidate':520,'controls':'Reuse exact promotedG cohorts from existing wide plan',
        'design':'Actual red-kite27 and gota-g002 each80 first; thenblack-kite80/Jordan80; thenmixed200 onlyifprecedinggatespass. '
                 'Stopafterfirstfullypassingcandidate. Full audits/equipment/source checks required. Noautodeploy.',
        'gates':{'each_threat_red_floor':24,'threat_color_loss':2,'red_gain_in_at_least_one_threat':8,
                 'preservation_each_color':38,'allied_floor':112,'allied_loss':4,'roster_loss':4,
                 'class_fraction_loss':.2,'no_added_opposed_draws':True,'all_equipment':True}})
    while not (STUDY/'local/comparison.json').exists():
        if not alive(read(STUDY/'local-process.json')['pid']):raise RuntimeError('Local study stopped without result')
        time.sleep(15)
    choices=read(STUDY/'local/comparison.json')['qualified'][:2]
    if not choices:
        write(STUDY/'hosted-comparison.json',{'selected':None,'reason':'No local qualifier','results':{}});return
    for key in ('promotion-guardrail','g002-guardrail'):
        root=PRESSURE/key
        while alive(read(root/'process.json')['pid']):time.sleep(15)
        if not (root/'result.json').exists() and not (root/'not-run.json').exists():
            raise RuntimeError('Unreconciled pressure queue: '+key)
    freeze(STUDY/'hosted-selection.json',{'choices':choices,'local_sha256':digest((STUDY/'local/comparison.json').read_bytes())})
    prepare(choices[0])
    with drained_wide(STUDY):
        reports={};selected=None
        for name in choices:
            write(STUDY/'queue-state.json',{'stage':'core_threats','candidate':name})
            result=run(name);reports[name]={'passed':result['passed'],'stage':result['stage'],'checks':result['checks']}
            if result['passed']:selected=name;break
        write(STUDY/'hosted-comparison.json',{'selected':selected,'results':reports})


if __name__=='__main__':main()

"""Fresh local confirmation with the actual deployed sentry as primary control."""
from economy_feedback import record
from policy_ir import read,write
from release_workspace import RUN
from rush_defense_eval import evaluate
from rush_unblock import STUDY


def main():
    names=['deployed_parent','near_core','spread']
    plan={'names':names,'cases_per_arm':60,'seed':762000,
          'rule':'Require all equipment, complete replay/VM checks, >=18/20 default wins, '
                 '>=12/20 wins versus each remaining local opponent, and totalwins>=deployed_parent. '
                 'Rank by total wins, fewer deaths, then near_core before spread for its replay-derived '
                 'emergency fix. Legacy controls remain descriptive. Only selected repair proceeds to '
                 'fresh40/color Richard69,relh133,redkite20,khors1. No hosted-improvement claim from local tests.'}
    target=STUDY/'confirmation-plan.json'
    if target.exists() and read(target)!=plan:raise ValueError('Confirmation plan changed')
    write(target,plan)
    factory=lambda n:read(STUDY/'screen-refine/candidates'/n/'policy.ir.json')
    evaluate('local',names,60,762000,factory,STUDY,RUN/'r5/fast/audit-local')
    result=read(STUDY/'local/result.json');metrics=result['metrics']
    qualified=[n for n in names[1:] if metrics[n]['all_gear'] and
               metrics[n]['wins']>=metrics['deployed_parent']['wins'] and
               metrics[n]['opponents']['default']>=18 and
               all(metrics[n]['opponents'][k]>=12 for k in ('current','center_proxy'))]
    qualified.sort(key=lambda n:(-metrics[n]['wins'],metrics[n]['deaths'],0 if n=='near_core' else 1))
    comparison={'metrics':metrics,'qualified':qualified,'selected':qualified[0] if qualified else None,
                'primary_control':'deployed_parent','verified_games':result['verified_games'],'rule':plan['rule']}
    write(STUDY/'local/comparison.json',comparison)
    for name in names:
        parent=STUDY/'local/feedback'/name;out=STUDY/'local/deployed-comparison-feedback'/name
        if not out.exists():
            record(parent/'policy.ir.json',parent/'policy.bas',
                   f'Fresh60case comparison to actual deployed sentry: own {metrics[name]}; '
                   f'current deployed {metrics["deployed_parent"]}. Qualified {name in qualified}. '
                   +plan['rule'],STUDY/'local/comparison.json',out)
    print('Primary-control qualification:',qualified,flush=True)


if __name__=='__main__':main()

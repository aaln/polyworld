"""Frozen screen followed by fresh60cases per qualifying coordinated candidate."""
from economy_feedback import record
from policy_ir import read,write
from release_workspace import RUN
from rush_defense_eval import evaluate
from mixed_isolated import STUDY,VARIANTS,make


def main():
    plan={'question':'Can isolated-attacker defense protect the base without overriding group combat?',
          'variants':VARIANTS,'screen_cases':12,'screen_seed':765000,'confirmation_cases':60,
          'confirmation_seed':766000,'local_rule':'Allgear/VM/fullreplay;default>=18/20,other>=12/20;wins>=deployed. Screen rank wins then deaths; confirm up to two.',
          'hosted_rule':read(RUN/'coached-lanes/r5-mixed-backdoor/prospective-plan.json')['hosted_rule']}
    if (STUDY/'prospective-plan.json').exists() and read(STUDY/'prospective-plan.json')!=plan:raise ValueError('Plan changed')
    write(STUDY/'prospective-plan.json',plan)
    evaluate('screen',VARIANTS,12,765000,make,STUDY,RUN/'r5/fast/audit-local')
    screen=read(STUDY/'screen/result.json');m=screen['metrics']
    candidates=[n for n in screen['selected'] if n.startswith('isolated_') and m[n]['wins']>=m['deployed_parent']['wins']]
    candidates.sort(key=lambda n:(-m[n]['wins'],m[n]['deaths'],n));candidates=candidates[:2]
    if not candidates:raise ValueError('No isolated-defense screen qualifier')
    write(STUDY/'local-choice.json',{'selected_for_confirmation':candidates})
    evaluate('local',['deployed_parent','fused_parent',*candidates],60,766000,make,STUDY,RUN/'r5/fast/audit-local')
    r=read(STUDY/'local/result.json');m=r['metrics']
    qualified=[n for n in candidates if m[n]['all_gear'] and m[n]['wins']>=m['deployed_parent']['wins'] and
               m[n]['opponents']['default']>=18 and all(m[n]['opponents'][k]>=12 for k in ('current','center_proxy'))]
    qualified.sort(key=lambda n:(-m[n]['wins'],m[n]['deaths'],n))
    comparison={'selected':qualified[0] if qualified else None,'qualified':qualified,'metrics':m,'verified_games':r['verified_games'],
                'interpretation':'Adaptive local proxy confirmation. Exact ten-player roster and mixed-team benefit remain untested.'}
    write(STUDY/'local/comparison.json',comparison)
    for name in candidates:
        src=STUDY/'local/feedback'/name;out=STUDY/'local/comparison-feedback'/name
        if not out.exists():record(src/'policy.ir.json',src/'policy.bas',
            f'Complete60case local confirmation: {m[name]}; actualdeployed{m["deployed_parent"]}; fused{m["fused_parent"]}. '
            f'Qualified{name in qualified}. '+comparison['interpretation'],STUDY/'local/comparison.json',out)
    print('Isolated qualification:',qualified,flush=True)


if __name__=='__main__':main()

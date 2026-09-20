"""Frozen multi-hypothesis screen and fresh confirmation of root defense repair."""
from economy_feedback import record
from policy_ir import read,write
from release_workspace import RUN
from rush_defense_eval import evaluate
from jordan_root import STUDY,VARIANTS,make

def main():
    plan={'question':'Does objective-relative interception plus productive defense transitions remove the observed dead zone without losing rush defense?',
          'screen_cases':12,'screen_seed':770000,'variants':VARIANTS,
          'confirmation_cases':60,'confirmation_seed':771000,'max_confirmed_variants':2,
          'screen_rule':'Allgear, >=actualdeployed and blue_assigned totalwins; default>=3/4, eachother>=2/4. Rank wins then deaths; retain at most two coordinated candidates.',
          'confirmation_rule':'All fullreplay/VM/equipment checks; wins>=actualdeployed and blue_assigned; default>=18/20, eachother>=12/20. Rank wins then deaths. Fresh hosted Jordan80 follows only qualified candidate; no automatic league selection.',
          'evidence':'Exact16513tick baseline reconstruction:78022ownedcommands and allstatehashes matched; originalepisode andinputs preserved.'}
    if (STUDY/'prospective-plan.json').exists() and read(STUDY/'prospective-plan.json')!=plan:raise ValueError('Frozen design changed')
    write(STUDY/'prospective-plan.json',plan)
    evaluate('screen',VARIANTS,12,770000,make,STUDY,RUN/'r5/fast/audit-local')
    r=read(STUDY/'screen/result.json');m=r['metrics']
    choices=[n for n in VARIANTS[2:] if m[n]['all_gear'] and m[n]['wins']>=max(m['deployed_parent']['wins'],m['blue_assigned']['wins']) and m[n]['opponents']['default']>=3 and all(m[n]['opponents'][o]>=2 for o in ('current','center_proxy'))]
    choices.sort(key=lambda n:(-m[n]['wins'],m[n]['deaths'],n));choices=choices[:2]
    write(STUDY/'screen/selection.json',{'qualified_for_confirmation':choices,'metrics':m})
    if not choices:
        write(STUDY/'local/comparison.json',{'selected':None,'qualified':[],'reason':'No screen qualifier'});return
    names=['deployed_parent','blue_assigned']+choices
    evaluate('local',names,60,771000,make,STUDY,RUN/'r5/fast/audit-local')
    r=read(STUDY/'local/result.json');m=r['metrics']
    qualified=[n for n in choices if m[n]['all_gear'] and m[n]['wins']>=max(m['deployed_parent']['wins'],m['blue_assigned']['wins']) and m[n]['opponents']['default']>=18 and all(m[n]['opponents'][o]>=12 for o in ('current','center_proxy'))]
    qualified.sort(key=lambda n:(-m[n]['wins'],m[n]['deaths'],n))
    comparison={'selected':qualified[0] if qualified else None,'qualified':qualified,'verified_games':r['verified_games'],'metrics':m,'scope':'Local fixedteam proxies. Actual private Jordan policy is hosted only. New variants require hosted validation; no deployment verdict.'}
    write(STUDY/'local/comparison.json',comparison)
    for n in choices:
        src=STUDY/'local/feedback'/n;out=STUDY/'local/comparison-feedback'/n
        if not out.exists():record(src/'policy.ir.json',src/'policy.bas',f'Root repair fresh60case confirmation: {m[n]}; actualdeployed{m["deployed_parent"]}; prior mixed winner{m["blue_assigned"]}. Qualified{n in qualified}. '+comparison['scope'],STUDY/'local/comparison.json',out)
    print('Root repair confirmation',comparison,flush=True)

if __name__=='__main__':main()

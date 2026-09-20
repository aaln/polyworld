"""Select a coordinated solo-defense candidate, then confirm locally on60cases."""
import os,time,sys
from economy_feedback import record
from policy_ir import read,write
from release_workspace import RUN
from rush_defense_eval import evaluate
from mixed_backdoor import STUDY,make


def main(screen_stage='screen',factory=make,prefix='solo_',seed=764000):
    while not (STUDY/screen_stage/'result.json').exists():
        os.kill(read(STUDY/'screen-process.json')['pid'],0);time.sleep(10)
    screen=read(STUDY/screen_stage/'result.json')
    eligible=[n for n in screen['selected'] if n.startswith(prefix) and
              screen['metrics'][n]['wins']>=screen['metrics']['deployed_parent']['wins']]
    eligible.sort(key=lambda n:(-screen['metrics'][n]['wins'],screen['metrics'][n]['deaths'],n))
    if not eligible:raise ValueError('No solo-defense screen qualifier; preserve failures and revise')
    name=eligible[0];names=['deployed_parent','fused_parent',name]
    write(STUDY/'local-choice.json',{'selected':name,'all_screen_qualifiers':eligible,'names':names})
    evaluate('local',names,60,seed,factory,STUDY,RUN/'r5/fast/audit-local')
    r=read(STUDY/'local/result.json');m=r['metrics'];v=m[name]
    passed=(v['all_gear'] and v['wins']>=m['deployed_parent']['wins'] and
            v['opponents']['default']>=18 and all(v['opponents'][k]>=12 for k in ('current','center_proxy')))
    comparison={'selected':name if passed else None,'qualified':[name] if passed else [],
                'metrics':m,'verified_games':r['verified_games'],'primary_control':'deployed_parent',
                'interpretation':'Local proxy confirmation; exact mixed roster still untested. Also report fused parent; do not infer mixed improvement from local team tests.'}
    write(STUDY/'local/comparison.json',comparison)
    src=STUDY/'local/feedback'/name;out=STUDY/'local/comparison-feedback'/name
    if not out.exists():record(src/'policy.ir.json',src/'policy.bas',
        f'Complete60cases vsactualdeployed: {v}; parent{m["deployed_parent"]}; fused{m["fused_parent"]}. Qualified{passed}. '
        +comparison['interpretation'],STUDY/'local/comparison.json',out)
    print('Mixed backdoor local qualification:',passed,name,flush=True)


if __name__=='__main__':
    if '--protected' in sys.argv:
        from mixed_backdoor_protected import make as protected
        main('screen-protected',protected,'protected_',764200)
    elif '--assigned' in sys.argv:
        from mixed_backdoor_assigned import make as assigned
        main('screen-assigned',assigned,'assigned_',764100)
    else:main()

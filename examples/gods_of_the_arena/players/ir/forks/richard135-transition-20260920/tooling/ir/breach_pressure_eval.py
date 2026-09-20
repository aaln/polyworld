"""Full local comparison against the successful pressure20 parent."""
import json
import subprocess
from breach_pressure import STUDY,VARIANTS,make
from economy_feedback import record
from policy_ir import read,write
from ranger_guard_hosted import freeze
from release_workspace import RUN
from rush_defense_eval import evaluate


def main():
    plan={'variants':VARIANTS,'cases_per_variant':60,'seed':777000,'local_games':420,
        'primary_control':'pressure_parent=exactpressure20with80/80black-kiteand80/80Jordan; deployedGsecondarydiagnostic',
        'rule':'Completeall7variants/controls60eachbeforeselection. Requireallgear/fullruntime/replay, no opponent/colorwinregressionversuspressure_parent. '
        'Everybluegamefornear24/32/40must matchpressure_parent30completeactions/hashes/config/seed each. '
        'Rankqualifierswins/deaths/name; actualredkite27 andbroadtestsrequiredbeforepromotion. Noautomatic hostedlaunch.'}
    freeze(STUDY/'prospective-plan.json',plan)
    evaluate('local',VARIANTS,60,777000,make,STUDY,RUN/'r5/fast/audit-local')
    result=read(STUDY/'local/result.json');m=result['metrics'];proofs={}
    for name in VARIANTS[2:]:
        rr=[]
        for row in result['rows']:
            if row['name']!=name or row['color']!=1:continue
            root=STUDY/'local/games'
            p=json.loads(subprocess.check_output([str(RUN/'r5/compare-gameplay'),
                str(root/name/str(row['seed'])/'replay.bin'),str(root/'pressure_parent'/str(row['seed'])/'replay.bin')],text=True))
            rr.append({'seed':row['seed'],**p})
        proofs[name]={'games':len(rr),'all_gameplay_equal':len(rr)==30 and all(all(p[k] for k in
            ('all_actions_equal','all_state_hashes_equal','setup_equal','config_equal','same_seed')) for p in rr),'rows':rr}
    write(STUDY/'local/blue-parity.json',proofs)
    b=m['pressure_parent']
    qualified=[n for n in VARIANTS[2:] if proofs[n]['all_gameplay_equal'] and m[n]['all_gear'] and
        m[n]['wins']>=b['wins'] and all(m[n]['opponents'][o]>=b['opponents'][o] for o in b['opponents']) and
        all(m[n]['colors'][c]>=b['colors'][c] for c in b['colors'])]
    qualified.sort(key=lambda n:(-m[n]['wins'],m[n]['deaths'],n))
    comparison={'selected':qualified[0] if qualified else None,'qualified':qualified,'metrics':m,
        'verified_games':result['verified_games'],'scope':plan['rule']}
    for n in VARIANTS[2:]:
        src=STUDY/'local/candidates'/n;out=STUDY/'local/comparison-feedback'/n
        if not out.exists():record(src/'policy.ir.json',src/'policy.bas',
            f'Fresh60case breach comparison: candidate{m[n]}, successfulpressureparent{b}, deployedG{m["deployed"]}. '
            f'Blue30gameparity{proofs[n]["all_gameplay_equal"]}; qualification{n in qualified}. Actualhostedfollowupuntested.',
            STUDY/'local/result.json',out)
    write(STUDY/'local/comparison.json',comparison)
    print('Breach confirmation',comparison,flush=True)


if __name__=='__main__':main()

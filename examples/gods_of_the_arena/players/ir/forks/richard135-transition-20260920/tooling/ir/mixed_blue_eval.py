from economy_feedback import record
import json,subprocess
from policy_ir import read,write
from release_workspace import RUN
from rush_defense_eval import evaluate
from mixed_blue import STUDY,make


def main():
    plan={'question':'Does blue assigned solo defense preserve red play and improve mixed base protection?',
          'variants':['deployed_parent','fused_parent','blue_assigned'],'screen_cases':12,'screen_seed':767000,
          'confirmation_cases':60,'confirmation_seed':768000,
          'local_rule':'Allgear/VM/replays;default>=18/20,others>=12/20,wins>=actualdeployed;red full command tape parity with fused parent.',
          'hosted_rule':read(RUN/'coached-lanes/r5-mixed-backdoor/prospective-plan.json')['hosted_rule']}
    if (STUDY/'prospective-plan.json').exists() and read(STUDY/'prospective-plan.json')!=plan:raise ValueError('Plan changed')
    write(STUDY/'prospective-plan.json',plan)
    names=plan['variants'];evaluate('screen',names,12,767000,make,STUDY,RUN/'r5/fast/audit-local')
    r=read(STUDY/'screen/result.json')
    if 'blue_assigned' not in r['selected'] or r['metrics']['blue_assigned']['wins']<r['metrics']['deployed_parent']['wins']:
        raise ValueError('Blue screen did not qualify')
    evaluate('local',names,60,768000,make,STUDY,RUN/'r5/fast/audit-local')
    r=read(STUDY/'local/result.json');m=r['metrics'];v=m['blue_assigned']
    rows={(x['name'],x['seed']):x for x in r['rows']}
    paired=[x for x in r['rows'] if x['name']=='blue_assigned' and x['color']==0]
    proofs=[]
    for x in paired:
        a=STUDY/'local/games/blue_assigned'/str(x['seed'])/'replay.bin'
        b=STUDY/'local/games/fused_parent'/str(x['seed'])/'replay.bin'
        proof=json.loads(subprocess.check_output([str(RUN/'r5/compare-gameplay'),str(a),str(b)],text=True))
        proofs.append({'seed':x['seed'],**proof})
    parity=all(all(p[k] for k in ('all_actions_equal','all_state_hashes_equal','setup_equal','config_equal','same_seed')) for p in proofs)
    write(STUDY/'local/red-parity.json',{'games':len(paired),'all_gameplay_equal':parity,'proofs':proofs,
          'note':'Replay containers include VM metrics. Different instruction/work counts change raw bytes even when every game action and every state hash match.'})
    passed=(parity and v['all_gear'] and v['wins']>=m['deployed_parent']['wins'] and
            v['opponents']['default']>=18 and all(v['opponents'][k]>=12 for k in ('current','center_proxy')))
    comparison={'selected':'blue_assigned' if passed else None,'qualified':['blue_assigned'] if passed else [],'metrics':m,'verified_games':r['verified_games'],
                'red_replay_parity':parity,'interpretation':'Fresh local confirmation after adaptive lineup restriction. Hosted mixed benefit remains untested; red unattended solo attack has no new recall.'}
    write(STUDY/'local/comparison.json',comparison)
    src=STUDY/'local/feedback/blue_assigned';out=STUDY/'local/comparison-feedback/blue_assigned'
    if not out.exists():record(src/'policy.ir.json',src/'policy.bas',
        f'Complete60case blue-response confirmation: {v}; actualdeployed{m["deployed_parent"]}; fused{m["fused_parent"]}. '
        f'Qualified{passed}; redfullreplayparity{parity}. '+comparison['interpretation'],STUDY/'local/comparison.json',out)
    print('Blue assigned qualification:',passed,flush=True)


if __name__=='__main__':main()

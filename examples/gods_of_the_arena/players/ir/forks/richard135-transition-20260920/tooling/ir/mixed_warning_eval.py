"""Fresh local confirmation of warning retention while prior hosted A/B drains."""
import json,subprocess
from economy_feedback import record
from policy_ir import read,write
from release_workspace import RUN
from rush_defense_eval import evaluate
from mixed_warning import STUDY,make


def main():
    names=['deployed_parent','fused_parent','blue_assigned','blue_warning20']
    plan={'question':'Retain intruder warnings across observed target-switch gaps without inventing a current attack.',
          'variants':names,'cases':60,'seed':769000,'rule':'Allfullreplay/VM/gear;default18/20,others12/20;wins>=actualdeployed and blue_assigned;red every action/hash matches blue_assigned. No automatic hosted launch or deployment.',
          'prior_hosted':'r5-mixed-blue160 remains frozen; this is an independent follow-up based on original replay timing.'}
    if (STUDY/'prospective-plan.json').exists() and read(STUDY/'prospective-plan.json')!=plan:raise ValueError('Plan changed')
    write(STUDY/'prospective-plan.json',plan)
    evaluate('local',names,60,769000,make,STUDY,RUN/'r5/fast/audit-local')
    r=read(STUDY/'local/result.json');m=r['metrics'];v=m['blue_warning20'];proofs=[]
    for x in r['rows']:
        if x['name']!='blue_warning20' or x['color']!=0:continue
        base=STUDY/'local/games'
        a=base/'blue_warning20'/str(x['seed'])/'replay.bin';b=base/'blue_assigned'/str(x['seed'])/'replay.bin'
        proofs.append({'seed':x['seed'],**json.loads(subprocess.check_output([str(RUN/'r5/compare-gameplay'),str(a),str(b)],text=True))})
    parity=all(all(p[k] for k in ('all_actions_equal','all_state_hashes_equal','setup_equal','config_equal','same_seed')) for p in proofs)
    write(STUDY/'local/red-parity.json',{'games':len(proofs),'all_gameplay_equal':parity,'proofs':proofs})
    passed=parity and v['all_gear'] and v['wins']>=max(m['deployed_parent']['wins'],m['blue_assigned']['wins']) and v['opponents']['default']>=18 and all(v['opponents'][k]>=12 for k in ('current','center_proxy'))
    comparison={'selected':'blue_warning20' if passed else None,'qualified':['blue_warning20'] if passed else [],'verified_games':r['verified_games'],'metrics':m,'red_gameplay_parity':parity,'interpretation':'Local fixed-team confirmation; longer warning has no established hosted advantage.'}
    write(STUDY/'local/comparison.json',comparison)
    src=STUDY/'local/feedback/blue_warning20';out=STUDY/'local/comparison-feedback/blue_warning20'
    if not out.exists():record(src/'policy.ir.json',src/'policy.bas',f'Complete60case warning confirmation: {v}; deployed{m["deployed_parent"]}; shortwarning{m["blue_assigned"]}. Qualified{passed}; redparity{parity}. '+comparison['interpretation'],STUDY/'local/comparison.json',out)
    print('Warning confirmation qualified:',passed,flush=True)


if __name__=='__main__':main()

"""Drain user-requested Alex diagnostics, then resume frozen repair experiments."""
import os
from alex_next_probe import STUDY as ALEX
from g002_coordination import STUDY as M
from g002_arrival import STUDY as N
import g002_coordination_hosted as runner
from policy_ir import read,write
from ranger_guard_hosted import freeze
from red_pressure_hosted import prepare_head,result as head_result


def main():
    freeze(M/'new-alex-validation-plan.json',{'targets':['gota-me:v166','gota-g003:v1'],
        'when':'After any original full-suite repair winner and before promotion.',
        'cohorts':'40percolor versus each available exact user-named target; original deployedG controls from r5-alex-next reused without double counting.',
        'gates':{'red_floor':32,'blue_floor':38,'max_color_loss_vs_deployed':2},
        'promotion':'None in this runner. Full current-field confirmation still required.'})
    runner.wait_for(ALEX/'result.json',ALEX/'process.json')
    for study in (M,N):
        write(study/'hosted-process.json',{'pid':os.getpid(),'command':'g002_research_queue.py','stage':'frozen_original_suite'})
        runner.STUDY=study
        runner.main(diagnostic_study=M)
        name=read(study/'hosted-comparison.json').get('selected')
        if not name:continue
        root=study/'hosted'/name;version=read(root/'uploaded-version.json');checks={};heads={}
        for label,data in read(ALEX/'result.json')['results'].items():
            if data is None:continue
            key=label.replace(':','-');ref=ALEX/key/'deployed'
            prepare_head(root/'new-alex'/key,version,ref,'User-requested '+label+' versus qualified repair',runner.DESIGN)
            a=head_result(root/'new-alex'/key);b=head_result(ref);heads[key]={'candidate':a,'deployed':b}
            for color in ('red','blue'):
                checks[key+'_'+color]=a['colors'][color]['win']>=max(32 if color=='red' else 38,b['colors'][color]['win']-2)
        write(root/'new-alex-result.json',{'checks':checks,'heads':heads,'passed':bool(heads) and all(checks.values()),'promotion_performed':False})
        if heads and all(checks.values()):
            write(M/'queue-result.json',{'selected_study':str(study),'selected':name,'next':'current_field_followup.py then concrete deployment validation','promotion_performed':False});return
    write(M/'queue-result.json',{'selected':None,'promotion_performed':False,'reason':'No complete original plus new-Alex qualifier; retain evidence for next iteration.'})

if __name__=='__main__':main()

"""Coached base-exit repair: g002 first, then completed preservation and field gates."""
import time
import core_pressure_hosted as field_hosted
from economy_feedback import record
from g002_coordination import STUDY
from g002_activation import activated
from jordan_lineup_wide import WINNER
from policy_ir import read,write,digest
from priority_wide_queue import drained_wide
from ranger_guard_hosted import freeze
from ranger_guard_queue import alive
from red_pressure_hosted import prepare_head,result as head_result
from rush_hosted import upload
from threat_coverage_hosted import control
from win_hosted import live

DESIGN=('User-coached g002 red post-defense stall. Exact release.5, pinned g002v1, '
        '40episodes/color. Compare qualified frozen combined rally/quiet-release variants '
        'to completed deployedG and anchorH controls without double counting. '
        'No interim source changes. Local proxy and complete native execution proof first. '
        'G002 primary floor32red/38blue; preserve Richard78, Jordan186, other frozen '
        'champions and mixed200 before current-version followup. Directional fixed-lineup '
        'evidence; not independent-trial significance. No automatic league mutation.')


def wait_for(path,process):
    while not path.exists():
        if not alive(read(process)['pid']):raise RuntimeError('Worker stopped without result: '+str(path))
        time.sleep(10)


def main(diagnostic_study=None):
    freeze(STUDY/'hosted-prospective-plan.json',{
        'candidates':'All local qualifiers, at most4, ranked wins/deaths/name; stop first full-suite pass.',
        'primary':'gota-g002:v1 UUIDa30542cb-54de-4109-92e6-bcabca7db4d8;40red40blue; G24red40blue and H4red40blue controls reused.',
        'gates':{'g002_red_floor':32,'g002_blue_floor':38,'richard_red_floor':30,'richard_blue_floor':38,
                 'jordan_each_color':38,'other_max_color_loss':2,'red_kite_red_floor':24,
                 'black_extra_losses':2,'mixed_allied_floor':112,'mixed_allied_loss':4,
                 'mixed_roster_loss':4,'mixed_class_fraction_loss':.2,'no_added_opposed_draws':True,
                 'all_equipment_runtime_replays':True},
        'conditional_order':['richard78','jordan186','red-kite27','vanguard','black-kite13','mixed200','separate-current-field-followup'],
        'maximum_new_candidate_games_before_current_followup':2720,'design':DESIGN})
    wait_for(STUDY/'local/comparison.json',STUDY/'local-process.json')
    names=read(STUDY/'local/comparison.json')['qualified'][:4]
    if not names:
        write(STUDY/'hosted-comparison.json',{'selected':None,'stage':'local','promotion_performed':False});return
    wait_for(STUDY/'activation-proof.json',STUDY/'activation-process.json')
    proof=read(STUDY/'activation-proof.json')
    if not proof['passed'] or not read(STUDY/'vm-stress.json')['passed']:raise ValueError('Missing execution proof')
    for name in names:
        source=STUDY/'local/candidates'/name/'policy.bas'
        rr=[r for r in proof['rows'] if r['name']==name and activated(r)]
        if not rr or any(r['source_sha256']!=digest(source.read_bytes()) for r in rr):raise ValueError('Unproven source: '+name)
    diagnostic_study=diagnostic_study or STUDY
    wait_for(diagnostic_study/'diagnostic-result.json',diagnostic_study/'diagnostic-resumed-process-2.json')
    live();reports={};selected=None
    with drained_wide(STUDY):
        for name in names:
            root,version=upload(name,STUDY,'aaron-gota-ir-post-defense',
                'Refresh recalled attacker destinations without extending defense, separate actual-role rally destinations, and resume lane pressure after declared quiet interval while guarding visible near-base threats; preserve blue.',
                feedback_override=STUDY/'activation-feedback'/name,
                validation_note='Local comparison, blue gameplay parity, focused VM tests and full native behavior activation passed. Hosted g002 and field unvalidated; inert experiment.')
            heads={};checks={};stage='g002'
            ref=control('gota-g002:v1');prepare_head(root/stage,version,ref,'g002 coached post-defense repair',DESIGN)
            a=head_result(root/stage);b=head_result(ref);heads[stage]={'candidate':a,'control':b}
            checks.update(g002_red_floor=a['colors']['red']['win']>=32,g002_blue_floor=a['colors']['blue']['win']>=38)
            write(root/'g002-result.json',{'heads':heads,'checks':checks,'passed':all(checks.values())})
            if all(checks.values()):
                for key,ref in [('richard',control('richard-gods-of-the-arena:v78')),('jordan',WINNER/'jordan'),
                                ('red-kite',control('red-kite:v27')),('vanguard',control('gota-vanguard-rally-hold:v1')),
                                ('black-kite',control('black-kite:v13'))]:
                    stage=key;prepare_head(root/key,version,ref,key+' preservation after g002 repair',DESIGN)
                    a=head_result(root/key);b=head_result(ref);heads[key]={'candidate':a,'control':b}
                    for color in ('red','blue'):
                        floor=(30 if color=='red' else 38) if key=='richard' else (38 if key=='jordan' else b['colors'][color]['win']-2)
                        checks[key+'_'+color]=a['colors'][color]['win']>=floor
                    if key=='black-kite':checks['black_losses']=a['losses']<=b['losses']+2
                    if key=='red-kite':checks['red_kite_red_floor']=a['colors']['red']['win']>=24
                    write(root/(key+'-result.json'),{'heads':heads,'checks':checks,'passed':all(checks.values())})
                    if not all(checks.values()):break
            if all(checks.values()):
                stage='field';field_hosted.STUDY=STUDY;field_hosted.DESIGN=DESIGN
                field=field_hosted.field(root,name);checks.update({'field_'+k:v for k,v in field['checks'].items()})
            result={'stage':stage,'heads':heads,'checks':checks,'passed':all(checks.values()),'plan_sha256':digest((STUDY/'hosted-prospective-plan.json').read_bytes())}
            write(root/'final-result.json',result)
            src=STUDY/'activation-feedback'/name
            if not (root/'final-feedback').exists():
                record(src/'policy.ir.json',src/'policy.bas',f'Complete g002-first coached repair reached {stage}; checks {checks}. Full cohorts and replay/runtime/equipment audits. No league promotion; current-field validation remains required.',root/'final-result.json',root/'final-feedback')
            reports[name]=result;write(STUDY/'hosted-progress.json',{'results':reports});print(name,stage,checks,flush=True)
            if result['passed']:selected=name;break
    write(STUDY/'hosted-comparison.json',{'selected':selected,'results':reports,'promotion_performed':False})


if __name__=='__main__':main()

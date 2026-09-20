"""Richard78 on both colors first; preserve opponents and mixed-team performance."""
import time
import core_pressure_hosted as field_hosted
from counterpush import STUDY
from economy_feedback import record
from jordan_lineup_wide import ROOT as WIDE, WINNER
from policy_ir import read, write, digest
from priority_wide_queue import drained_wide
from ranger_guard_hosted import freeze
from ranger_guard_queue import alive
from red_pressure_hosted import prepare_head, result as head_result
from rush_hosted import upload
from threat_coverage_hosted import control
from win_hosted import live

DESIGN = ('Counterpush after a successful red defense. Exact Richard78 and deployed G sources, '
          '40 episodes per color, complete both colors and all command/replay/runtime/equipment '
          'audits. Reuse completed G controls without double counting. Fixed-lineup empirical '
          'evidence; correlated command trajectories preclude independent-trial significance. '
          'Blue alone cannot qualify this candidate. No automatic champion change.')
PREFIX='aaron-gota-ir-counterpush'
CHANGE='Retire destroyed red defense anchors, release quiet defenders into wave pressure, separate rally points; exact blue branch.'
RED_KITE_FLOOR=None
RICHARD_RED_FLOOR=28
MAX_CANDIDATES=2


def main():
    plan={
        'candidates': ('At most first two local relative qualifiers, ranked by wins/deaths/name.' if MAX_CANDIDATES == 2
                       else f'At most first {MAX_CANDIDATES} local relative qualifiers, ranked by wins/deaths/name.'),
        'primary': 'Richard78: 80 per candidate, 40 per color; G red11W24L5D, blue40W reused.',
        'gates': {'richard_red_floor':RICHARD_RED_FLOOR, 'richard_red_gain':10, 'richard_blue_floor':38,
                  'jordan_each_color':38, 'other_opponent_max_color_loss':2,
                  'black_extra_losses':2, 'mixed_allied_floor':112, 'mixed_allied_loss':4,
                  'mixed_roster_loss':4, 'mixed_class_fraction_loss':.2,
                  'no_added_opposed_draws':True, 'all_equipment_runtime_replays':True},
        'conditional_order':['Jordan186','gota-g002:v1','red-kite:v27',
                             'gota-vanguard-rally-hold:v1','black-kite:v13','mixed200'],
        'selection':'Stop at the first candidate passing every stage. Reject on a complete failed stage.',
        'maximum_new_candidate_games':680*MAX_CANDIDATES, 'design':DESIGN}
    if RED_KITE_FLOOR is not None:plan['gates']['red_kite_absolute']=RED_KITE_FLOOR
    freeze(STUDY/'hosted-prospective-plan.json',plan)
    while not (STUDY/'local/comparison.json').exists():
        if not alive(read(STUDY/'local-process.json')['pid']):
            raise RuntimeError('Local study ended without a verdict; reconcile retained artifacts')
        time.sleep(15)
    candidates=read(STUDY/'local/comparison.json')['qualified'][:MAX_CANDIDATES]
    if not candidates:
        write(STUDY/'hosted-comparison.json',{'selected':None,'stage':'local','reason':'No local qualifier'})
        return
    if not read(STUDY/'vm-stress.json')['passed']: raise ValueError('Missing VM qualification')
    live()
    reports={};selected=None
    with drained_wide(STUDY):
        for name in candidates:
            root, version=upload(name,STUDY,PREFIX,CHANGE,
                feedback_override=STUDY/'local/comparison-feedback'/name,
                validation_note='Local full-game relative qualification, blue parity, and focused VM checks passed. Richard and field unvalidated. Inert experiment.')
            checks={};heads={};stage='richard'
            ref=control('richard-gods-of-the-arena:v78')
            prepare_head(root/stage,version,ref,'Richard78 both colors',DESIGN)
            b=head_result(ref);a=head_result(root/stage);heads[stage]={'candidate':a,'control':b}
            checks.update(richard_red_floor=a['colors']['red']['win']>=RICHARD_RED_FLOOR,
                          richard_red_gain=a['colors']['red']['win']>=b['colors']['red']['win']+10,
                          richard_blue=a['colors']['blue']['win']>=38)
            write(root/'richard-result.json',{'heads':heads,'checks':checks,'passed':all(checks.values())})
            if all(checks.values()):
                for key,ref in [('jordan',WINNER/'jordan'),
                    ('g002',control('gota-g002:v1')),('red-kite',control('red-kite:v27')),
                    ('vanguard',control('gota-vanguard-rally-hold:v1')),('black-kite',control('black-kite:v13'))]:
                    stage=key
                    prepare_head(root/key,version,ref,key+' preservation',DESIGN)
                    a=head_result(root/key);b=head_result(ref);heads[key]={'candidate':a,'control':b}
                    for color in ('red','blue'):
                        floor=38 if key=='jordan' else b['colors'][color]['win']-2
                        checks[key+'_'+color]=a['colors'][color]['win']>=floor
                    if key=='black-kite':checks['black_losses']=a['losses']<=b['losses']+2
                    if key=='red-kite' and RED_KITE_FLOOR is not None:
                        checks['red_kite_absolute']=a['colors']['red']['win']>=RED_KITE_FLOOR
                    write(root/(key+'-result.json'),{'checks':checks,'passed':all(checks.values()),'heads':heads})
                    if not all(checks.values()):break
            if all(checks.values()):
                stage='field';field_hosted.STUDY=STUDY;field_hosted.DESIGN=DESIGN
                field=field_hosted.field(root,name)
                checks.update({'field_'+k:v for k,v in field['checks'].items()})
            result={'stage':stage,'heads':heads,'checks':checks,'passed':all(checks.values()),
                    'plan_sha256':digest((STUDY/'hosted-prospective-plan.json').read_bytes())}
            write(root/'final-result.json',result)
            src=STUDY/'local/comparison-feedback'/name
            if not (root/'final-feedback').exists():
                record(src/'policy.ir.json',src/'policy.bas',f'Counterpush completed stage {stage}; checks {checks}. '
                       'Full cohorts and replay/runtime/gear audits. Fixed-lineup evidence. No champion change.',
                       root/'final-result.json',root/'final-feedback')
            reports[name]=result
            write(STUDY/'hosted-progress.json',{'results':reports})
            print(name,stage,checks,flush=True)
            if result['passed']:
                selected=name;break
    write(STUDY/'hosted-comparison.json',{'selected':selected,'results':reports,'promotion_performed':False})


if __name__=='__main__':main()

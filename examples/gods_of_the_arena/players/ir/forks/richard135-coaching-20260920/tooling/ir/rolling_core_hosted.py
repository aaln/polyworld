"""Serial, prospective core-creep league threats, preservation, then mixed field."""
import time
import core_pressure_hosted as field_hosted
from economy_feedback import record
from policy_ir import read,write,digest
from priority_wide_queue import drained_wide
from ranger_guard_hosted import freeze
from ranger_guard_queue import alive
from red_pressure_hosted import prepare_head,result as head_result
from threat_coverage_hosted import control
from jordan_lineup_wide import ROOT as WIDE,WINNER
from rolling_core import STUDY
from rush_hosted import upload
from win_hosted import live

DESIGN=('Independent rotating red core-creep response on exact deployed recall parent; '
        '40episodes percolor, complete both colors and all source/VM/replay/equipment audits. '
        'Fixed-lineup directional evidence, not independent-trial significance. No automatic promotion.')


def main():
    freeze(STUDY/'hosted-prospective-plan.json',{'candidate':'scan8','maximum_new_candidate_games':680,
        'stages':[['gota-vanguard-rally-hold:v1','gota-g002:v1'],['red-kite:v27','richard-gods-of-the-arena:v78'],
                  ['Jordan186','black-kite:v13'],['mixed200']],
        'control':'Reuse exact promoted G wide cohorts; complete any pending planned controls once.',
        'gates':{'threat_red_floor':24,'threat_color_loss':2,'primary_red_gain_one':8,
                 'jordan_each_color':38,'black_color_loss':2,'black_extra_losses':2,
                 'mixed_allied_floor':112,'mixed_allied_loss':4,'mixed_roster_loss':4,
                 'mixed_class_fraction_loss':.2,'no_added_opposed_draws':True,'all_equipment':True},
        'design':DESIGN,'qualification':'Completed local relative nonregression versus deployedG, blue fullgame parity and bounded VM fixtures. Scan16 rejected before local games.'})
    while not (STUDY/'local/comparison.json').exists():
        if not alive(read(STUDY/'local-process.json')['pid']):raise RuntimeError('Local study ended without verdict')
        time.sleep(15)
    if 'scan8' not in read(STUDY/'local/comparison.json')['qualified']:
        write(STUDY/'hosted-comparison.json',{'selected':None,'reason':'Local gate failed'});return
    if not read(STUDY/'vm-stress.json')['passed']:raise ValueError('Runtime proof required')
    game=live();prior=read(WIDE/'plan.json')
    if game['version']!=prior['game_version'] or game['manifest']['game']['runnable']['source_url']!=prior['game_source']:
        raise ValueError('Release changed')
    root,version=upload('scan8',STUDY,'aaron-gota-ir-core-creeps',
        'Nearby red defenders independently react to visible creeps near their god; bounded rotating scan; exact blue branch.',
        feedback_override=STUDY/'local/comparison-feedback/scan8',
        validation_note='Completed local relative nonregression and full blue parity; hosted threats and field unvalidated. Inert registration only.')
    reports={};checks={};stage='primary';passed=False
    with drained_wide(STUDY):
        for group in [('vanguard','g002'),('red-kite','richard')]:
            labels={'vanguard':'gota-vanguard-rally-hold:v1','g002':'gota-g002:v1',
                    'red-kite':'red-kite:v27','richard':'richard-gods-of-the-arena:v78'}
            gains=[]
            for key in group:
                label=labels[key];ref=control(label)
                prepare_head(root/key,version,ref,label,DESIGN)
                b=head_result(ref);a=head_result(root/key);reports[key]={'candidate':a,'control':b}
                checks[key+'_red_floor']=a['colors']['red']['win']>=24
                for color in ('red','blue'):
                    checks[key+'_'+color]=a['colors'][color]['win']>=b['colors'][color]['win']-2
                gains.append(a['colors']['red']['win']-b['colors']['red']['win'])
            if group[0]=='vanguard':checks['primary_gain']=max(gains)>=8
            stage='primary' if group[0]=='vanguard' else 'all_threats'
            write(root/(stage+'-result.json'),{'reports':reports,'checks':checks,'passed':all(checks.values())})
            print(stage,checks,flush=True)
            if not all(checks.values()):break
        if all(checks.values()):
            stage='preservation'
            for key,ref in [('jordan',WINNER/'jordan'),('black-kite',control('black-kite:v13'))]:
                prepare_head(root/key,version,ref,key,DESIGN);a=head_result(root/key);b=head_result(ref)
                reports[key]={'candidate':a,'control':b}
                for color in ('red','blue'):
                    floor=38 if key=='jordan' else b['colors'][color]['win']-2
                    checks[key+'_'+color]=a['colors'][color]['win']>=floor
                if key=='black-kite':checks['black_losses']=a['losses']<=b['losses']+2
            if all(checks.values()):
                stage='field';field_hosted.STUDY=STUDY;f=field_hosted.field(root,'scan8')
                checks.update({'field_'+k:v for k,v in f['checks'].items()})
        passed=all(checks.values())
        result={'stage':stage,'heads':reports,'checks':checks,'passed':passed,
                'plan_sha256':digest((STUDY/'hosted-prospective-plan.json').read_bytes())}
        write(root/'final-result.json',result)
        src=STUDY/'local/comparison-feedback/scan8'
        if not (root/'final-feedback').exists():
            record(src/'policy.ir.json',src/'policy.bas',f'Core creep study finished stage{stage}; checks{checks}. '
                   'Fixed-lineup empirical evidence; no automatic deployment.',root/'final-result.json',root/'final-feedback')
        write(STUDY/'hosted-comparison.json',{'selected':'scan8' if passed else None,'stage':stage,'checks':checks})


if __name__=='__main__':main()

"""Post-win actual red-kite threat and current mixed-field guardrail for pressure."""
import time
from coached_league_live import arm_plan
from economy_feedback import record
from hosted_batch import batch_body
from hosted_queue import run as run_queue
from hosted_wave import client, create
from jordan_lineup_guardrails import mixed_part, pin_auditor
from jordan_lineup_wide import ROOT as WIDE, mixed_summary
from policy_ir import read, write, digest
from priority_wide_queue import drained_wide
from ranger_guard_hosted import freeze
from ranger_guard_queue import alive
from red_pressure import STUDY
from red_pressure_hosted import prepare_head, result as head_result
from release_deploy_pair import clone_for_aaron
from threat_coverage_hosted import control
from win_hosted import live

ROOT = STUDY / 'promotion-guardrail'


def prepare(name):
    prior = read(WIDE/'plan.json'); root = STUDY/'hosted'/name
    if not read(root/'black-kite-result.json')['passed'] or not read(root/'jordan-result.json')['passed']:
        raise ValueError('Black-kite and Jordan must pass before guardrail')
    game = live()
    if game['version'] != prior['game_version'] or game['manifest']['game']['runnable']['source_url'] != prior['game_source']:
        raise ValueError('Release changed')
    v = read(root/'uploaded-version.json'); source = (STUDY/'local/candidates'/name/'policy.bas').read_bytes()
    with client() as c:
        buddy = clone_for_aaron(c,root,read(root/'upload-request.json'),source,
            'Pressure local and black-kite/Jordan passed; actual red-kite and mixed-field guardrail pending. Inert registration only.')
    p = {k:prior[k] for k in ('target','game_version','game_source','config','lineups')}
    p.update(control_versions=prior['candidate_versions'],candidate_versions=[v['id'],buddy['id']],
        candidate=name,design='After black-kite and Jordan checks, test actualred-kite27 threat80 and current13champion mixed200. '
        'Reuse exactblue_repair80head and200mixed from alreadyplannedbroad suite, completing pending controls without duplication. '
        'Bothownedplayers rotateallclasses across2fixed100rosters,160allied+40opposed perarm. '
        'Directionalempiricalguardrails; no formalindependence claim. Noautodeployment.',
        gates={'maximum_allied_loss':4,'minimum_allied_wins':112,'maximum_roster_loss':4,
               'maximum_class_fraction_loss':.2,'maximum_head_color_loss':2,'minimum_red_kite_red_wins':24,
               'no_added_opposed_draws':True,'all_equipment':True})
    freeze(ROOT/'plan.json',p)
    for i in range(2):
        expected = arm_plan(p,'control',i); old = read(WIDE/f'mixed/candidate/part-{i}/plan.json')
        for k in ('target','game_version','game_source','config','policy_version','partner_version','opponents'):
            if old[k] != expected[k]: raise ValueError('Current mixed control differs: '+k)
        out = ROOT/f'candidate/part-{i}';out.mkdir(parents=True,exist_ok=True)
        ap = arm_plan(p,'candidate',i);freeze(out/'plan.json',ap);pin_auditor(out)
        with client() as c:create(c,batch_body(ap,100),out/'batch',dry_run=True)
    prepare_head(ROOT/'red-kite',v,control('red-kite:v27'),'Pressure actualleague threat',p['design'])
    return p


def run(name):
    p=prepare(name)
    with drained_wide(ROOT):
        heads={'control':head_result(control('red-kite:v27')),'candidate':head_result(ROOT/'red-kite')}
        for i in range(2):
            for out in (WIDE/f'mixed/candidate/part-{i}',ROOT/f'candidate/part-{i}'):
                if not (out/'audit-progress.json').exists() or read(out/'audit-progress.json')['verified']!=100:
                    run_queue([out])
        arms={};seeds=set()
        for arm in ('control','candidate'):
            rows=[]
            for i in range(2):
                out=WIDE/f'mixed/candidate/part-{i}' if arm=='control' else ROOT/f'candidate/part-{i}'
                for r in mixed_part(out):
                    if r['seed'] in seeds:raise ValueError('Repeated fieldcomparison seed')
                    seeds.add(r['seed']);r['roster_index']=i;rows.append(r)
            arms[arm]=mixed_summary(rows)
        a,b,g=arms['candidate'],arms['control'],p['gates']
        checks={'allied':a['allied_wins']>=b['allied_wins']-g['maximum_allied_loss'],
            'absolute':a['allied_wins']>=g['minimum_allied_wins'],
            'rosters':all(a['rosters'][str(i)]>=b['rosters'][str(i)]-g['maximum_roster_loss'] for i in range(2)),
            'classes':a['classes'].keys()==b['classes'].keys() and all(v['games']==b['classes'][c]['games'] and
                v['wins']>=b['classes'][c]['wins']-g['maximum_class_fraction_loss']*v['games'] for c,v in a['classes'].items()),
            'opposed_draws':a['opposed_draws']<=b['opposed_draws'],'equipment':a['both_gear']==b['both_gear']==200,
            'red_kite_absolute':heads['candidate']['colors']['red']['win']>=g['minimum_red_kite_red_wins']}
        for color in ('red','blue'):
            checks['red_kite_'+color]=heads['candidate']['colors'][color]['win']>=heads['control']['colors'][color]['win']-g['maximum_head_color_loss']
        result={'candidate':name,'arms':arms,'heads':heads,'checks':checks,'passed':all(checks.values()),
                'plan_sha256':digest((ROOT/'plan.json').read_bytes()),'new_candidate_games':280,
                'reused_deployed_games':280,'scope':p['design']}
        write(ROOT/'result.json',result)
        feedback=STUDY/'hosted'/name/'jordan-feedback'
        if not (ROOT/'feedback').exists():
            record(feedback/'policy.ir.json',feedback/'policy.bas',
                f'Actual red-kite and currentmixedfield guardrail: allied{a["allied_wins"]}/160vs{b["allied_wins"]}/160; checks{checks}. '
                'Black-kite andJordanresults separate; no league rank guarantee.',ROOT/'result.json',ROOT/'feedback')
        print('Pressure field guardrail',checks,'allied',a['allied_wins'],b['allied_wins'],flush=True)


def main():
    ROOT.mkdir(exist_ok=True)
    freeze(ROOT/'prospective-plan.json',{'primary':'selected pressure variant only afterblack-kite+Jordanpass',
        'new_candidate_games':280,'reused_controls':280,'scope':'80actualred-kite27 and200current13champion ten-player matchedfixedrosters',
        'gates':{'allied_loss':4,'roster_loss':4,'class_fraction_loss':.2,'allied_floor':112,'redkite_red_floor':24,'head_color_loss':2,'no_new_opposed_draws':True,'all_equipment':True}})
    while alive(read(STUDY/'hosted-process.json')['pid']):time.sleep(15)
    path=STUDY/'hosted-comparison.json'
    if not path.exists():raise RuntimeError('Pressure challenge stopped without reconciled result')
    name=read(path)['selected']
    if not name:
        write(ROOT/'not-run.json',{'reason':'No pressure candidate passed black-kite/Jordan'});return
    run(name)


if __name__=='__main__':main()

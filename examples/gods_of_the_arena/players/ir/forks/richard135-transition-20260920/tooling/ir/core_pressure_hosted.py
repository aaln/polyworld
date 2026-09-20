"""Prospective actual-threat checks and preservation for red core priority."""
from coached_league_live import arm_plan
from core_pressure import STUDY
from economy_feedback import record
from hosted_batch import batch_body
from hosted_queue import run as run_queue
from hosted_wave import client, create
from jordan_lineup_guardrails import mixed_part, pin_auditor
from jordan_lineup_wide import ROOT as WIDE, WINNER, mixed_summary
from policy_ir import read, write, digest
from ranger_guard_hosted import freeze
from red_pressure_hosted import prepare_head, result as head_result
from release_deploy_pair import clone_for_aaron
from rush_hosted import upload
from threat_coverage_hosted import control
from win_hosted import live

DESIGN = ('Red core-priority followup to observed league losses. Exact pinned release and rivals; '
          '40episodes percolor; complete both colors and all VM/replay/equipment audits. '
          'Reuse already-planned deployed controls without duplicate counting. '
          'Directional fixed-lineup evidence; no independent-trial significance claim.')


def prepare(name):
    if name not in read(STUDY/'local/comparison.json')['qualified']:
        raise ValueError('Local qualification required')
    prior=read(WIDE/'plan.json'); game=live()
    if game['version']!=prior['game_version'] or game['manifest']['game']['runnable']['source_url']!=prior['game_source']:
        raise ValueError('Release changed')
    root,version=upload(name,STUDY,'aaron-gota-ir-core-pressure',
        'Prioritize a visible god attacker during active nearby red defense; exact promoted blue branch.',
        feedback_override=STUDY/'local/comparison-feedback'/name,
        validation_note='Fresh local relative qualification and complete blue gameplay parity passed. Hosted threats and field unvalidated; inert experiment.')
    for key,label in [('red-kite','red-kite:v27'),('gota-g002','gota-g002:v1')]:
        prepare_head(root/key,version,control(label),key+' observed league threat',DESIGN)
    return root


def field(root,name):
    prior=read(WIDE/'plan.json'); version=read(root/'uploaded-version.json')
    with client() as c:
        buddy=clone_for_aaron(c,root,read(root/'upload-request.json'),(STUDY/'local/candidates'/name/'policy.bas').read_bytes(),
            'Threat and preservation checks passed; current mixed-field check pending. Inert only.')
    p={k:prior[k] for k in ('target','game_version','game_source','config','lineups')}
    p.update(control_versions=prior['candidate_versions'],candidate_versions=[version['id'],buddy['id']],
        candidate=name,design=DESIGN+' Two100game ten-player rosters,160allied40opposed; both owned players rotate roles.')
    out=root/'field';out.mkdir(exist_ok=True);freeze(out/'plan.json',p)
    for i in range(2):
        ap=arm_plan(p,'control',i);old=read(WIDE/f'mixed/candidate/part-{i}/plan.json')
        for k in ('target','game_version','game_source','config','policy_version','partner_version','opponents'):
            if ap[k]!=old[k]:raise ValueError('Reused mixed control differs: '+k)
        folder=out/f'candidate/part-{i}';folder.mkdir(parents=True,exist_ok=True)
        plan=arm_plan(p,'candidate',i);freeze(folder/'plan.json',plan);pin_auditor(folder)
        with client() as c:create(c,batch_body(plan,100),folder/'batch',dry_run=True)
    for i in range(2):
        for folder in (WIDE/f'mixed/candidate/part-{i}',out/f'candidate/part-{i}'):
            if not (folder/'audit-progress.json').exists() or read(folder/'audit-progress.json')['verified']!=100:run_queue([folder])
    arms={};seeds=set()
    for arm in ('control','candidate'):
        rows=[]
        for i in range(2):
            folder=WIDE/f'mixed/candidate/part-{i}' if arm=='control' else out/f'candidate/part-{i}'
            for r in mixed_part(folder):
                if r['seed'] in seeds:raise ValueError('Repeated field seed')
                seeds.add(r['seed']);r['roster_index']=i;rows.append(r)
        arms[arm]=mixed_summary(rows)
    a,b=arms['candidate'],arms['control']
    checks={'allied':a['allied_wins']>=b['allied_wins']-4,'absolute':a['allied_wins']>=112,
        'rosters':all(a['rosters'][str(i)]>=b['rosters'][str(i)]-4 for i in range(2)),
        'classes':a['classes'].keys()==b['classes'].keys() and all(v['games']==b['classes'][c]['games'] and
            v['wins']>=b['classes'][c]['wins']-.2*v['games'] for c,v in a['classes'].items()),
        'opposed_draws':a['opposed_draws']<=b['opposed_draws'],'equipment':a['both_gear']==b['both_gear']==200}
    result={'arms':arms,'checks':checks,'passed':all(checks.values())};write(out/'result.json',result)
    return result


def run(name):
    root=prepare(name); reports={};checks={};gains=[]
    for key,label in [('red-kite','red-kite:v27'),('gota-g002','gota-g002:v1')]:
        b=head_result(control(label));a=head_result(root/key)
        reports[key]={'candidate':a,'control':b}
        checks[key+'_red_floor']=a['colors']['red']['win']>=24
        for color in ('red','blue'):
            checks[key+'_'+color]=a['colors'][color]['win']>=b['colors'][color]['win']-2
        gains.append(a['colors']['red']['win']-b['colors']['red']['win'])
    checks['large_gain']=max(gains)>=8
    result={'stage':'threats','heads':reports,'checks':checks,'passed':all(checks.values())}
    write(root/'targeted-result.json',result)
    src=STUDY/'local/comparison-feedback'/name
    if not (root/'targeted-feedback').exists():
        record(src/'policy.ir.json',src/'policy.bas',f'Actual red-kite27/gota-g002 threat checks {checks}; gains {gains}. '
            'Preservation and mixed field remain necessary.',root/'targeted-result.json',root/'targeted-feedback')
    print('Core threats',name,checks,gains,flush=True)
    if result['passed']:
        for key,ref in [('black-kite',control('black-kite:v13')),('jordan',WINNER/'jordan')]:
            prepare_head(root/key,read(root/'uploaded-version.json'),ref,key+' preservation',DESIGN)
            a=head_result(root/key);reports[key]={'candidate':a}
            for color in ('red','blue'):checks[key+'_'+color]=a['colors'][color]['win']>=38
        result={'stage':'preservation','heads':reports,'checks':checks,'passed':all(checks.values())}
        write(root/'preservation-result.json',result)
        if result['passed']:
            f=field(root,name);checks.update({'field_'+k:v for k,v in f['checks'].items()})
            result={'stage':'field','heads':reports,'field':f,'checks':checks,'passed':all(checks.values())}
    result['plan_sha256']=digest((STUDY/'hosted-prospective-plan.json').read_bytes())
    write(root/'final-result.json',result)
    src=root/'targeted-feedback'
    if not (root/'final-feedback').exists():
        record(src/'policy.ir.json',src/'policy.bas',f'Core priority completed stage {result["stage"]}; final checks {checks}. '
            'No automatic deployment; completed fixed-lineup evidence only.',root/'final-result.json',root/'final-feedback')
    return result

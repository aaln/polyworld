"""Broad rotated mixed rosters and fixed-team rush checks for the mixed winner.

Reuse fully audited same-release deployed controls without counting them as
new games. Launch200newmixed and160newheads, serially; no league selection.
"""
from pathlib import Path
import shutil
from campaign_hosted_compare import cohort
from coached_league_live import arm_plan,AARON,OPTIMIZER
from command_diversity import inventory
from direct_matchup import run_prepared
from economy_feedback import record
from hosted_batch import batch_body
from hosted_queue import run as run_queue
from hosted_wave import client,create
from mixed_blue import STUDY
from policy_ir import read,write,digest
from release_workspace import RUN
from rush_sentries import STUDY as BASE
from win_hosted import live

ROOT=STUDY/'hosted/blue_assigned/guardrails'
QUEUE=STUDY/'guardrail-queue'


def pin_auditor(out):
    binary=RUN/'r5/fast/audit-hosted';cal=RUN/'r5/fast/audit-calibration/proof.json';proof=read(cal)
    if digest(binary.read_bytes())!=proof['optimized_binary_sha256'] or not all(r['all_audit_fields_identical'] for r in proof['rows']):
        raise ValueError('Auditor calibration changed')
    if not (out/'audit').exists():shutil.copy2(binary,out/'audit')
    if digest((out/'audit').read_bytes())!=digest(binary.read_bytes()):raise ValueError('Pinned auditor changed')
    write(out/'audit-build.json',{'binary_sha256':digest(binary.read_bytes()),'calibration':str(cal),'calibration_sha256':digest(cal.read_bytes())})


def prepare(_=None):
    game=live();ROOT.mkdir(parents=True,exist_ok=True)
    winner=STUDY/'hosted/blue_assigned'
    if not read(winner/'mixed-result.json')['passed']:raise ValueError('Exact mixed comparison must pass first')
    prior=read(BASE/'paired-guardrail/plan.json');v=read(winner/'mixed-plan.json')['versions']
    plan={k:prior[k] for k in ('target','game_version','game_source','config','lineups')}
    if game['version']!=plan['game_version'] or game['manifest']['game']['runnable']['source_url']!=plan['game_source']:
        raise ValueError('Release drift')
    plan.update(control_versions=prior['candidate_versions'],candidate_versions=[v['optimizer'],v['aaron']],
                design='Broadfixed-roster guardrail:200newcandidate games,100perroster, bothowned '
                'players rotating across allclasses,160allied+40opposed. Compare the200completed '
                'deployed games from the exact same release,config,pinned opponents and rotations. '
                'These controls are reused, not new or simultaneous; new serverseeds are unpaired. '
                'Separately160new fixed-team games versusJordan186andkhors1,40percolor, with '
                'completed same-source deployed80/rival controls. No tuning or league selection.',
                gates={'maximum_allied_loss':8,'maximum_roster_loss':8,'maximum_class_fraction_loss':.30,
                       'minimum_allied_wins':112,'no_added_opposed_draws':True,
                       'maximum_head_color_loss':2,'maximum_head_total_loss':4},
                reused_control=str(BASE/'paired-guardrail'),
                control_result_sha256=digest((BASE/'paired-guardrail/result.json').read_bytes()))
    if (ROOT/'plan.json').exists() and read(ROOT/'plan.json')!=plan:raise ValueError('Guardrail plan changed')
    write(ROOT/'plan.json',plan)
    for i in range(2):
        old=read(BASE/f'paired-guardrail/candidate/part-{i}/plan.json')
        expected=arm_plan(plan,'control',i)
        for k in ('target','game_version','game_source','config','policy_version','partner_version','opponents'):
            if old[k]!=expected[k]:raise ValueError('Reused control is not an exact roster/config match')
        out=ROOT/f'candidate/part-{i}';out.mkdir(parents=True,exist_ok=True);p=arm_plan(plan,'candidate',i)
        if (out/'plan.json').exists() and read(out/'plan.json')!=p:raise ValueError('Frozen mixed arm changed')
        write(out/'plan.json',p);pin_auditor(out)
        with client() as c:create(c,batch_body(p,100),out/'batch',dry_run=True)
    heads=[]
    for oldroot in (BASE/'league-sweep/head-to-head/rival_7d6190c0',BASE/'hosted/long_three/matchups/khors'):
        old=read(oldroot/'plan.json');key=old['rival_key'];outroot=ROOT/'heads'/key;outroot.mkdir(parents=True,exist_ok=True)
        p={k:old[k] for k in ('target','game_version','game_source','config','rival','rival_version','rival_key','episodes_per_color','interpretation')}
        p.update(policy_version=v['optimizer'],policy_label='aaron-gota-ir-backdoor-blue_assigned-0916:v1',
                 design=plan['design'],control=str(oldroot),control_result_sha256=digest((oldroot/'result.json').read_bytes()))
        if (outroot/'plan.json').exists() and read(outroot/'plan.json')!=p:raise ValueError('Head plan changed')
        write(outroot/'plan.json',p)
        for color in ('red','blue'):
            out=outroot/key/color;out.mkdir(parents=True,exist_ok=True);slots=list(range(5)) if color=='red' else list(range(5,10))
            roster=[v['optimizer'] if s in slots else p['rival_version'] for s in range(10)]
            arm=p|{'color':color,'own_slots':slots,'roster':roster}
            if (out/'plan.json').exists() and read(out/'plan.json')!=arm:raise ValueError('Head arm changed')
            write(out/'plan.json',arm);pin_auditor(out)
            body={'idempotency_key':'gota-backdoor-guard-'+digest(arm)[:20],'target':p['target'],
                  'game_config_overrides':p['config'],'num_episodes':40,
                  'roster':[{'slot':s,'player':{'policy_ref':ref}} for s,ref in enumerate(roster)],
                  'notes':plan['design']+' '+p['rival']+' '+color}
            with client() as c:create(c,body,out/'batch',dry_run=True)
        heads.append(str(outroot))
    write(ROOT/'schedule.json',{'new_games':360,'reused_control_games':360,'heads':heads,'mixed':[str(ROOT/f'candidate/part-{i}') for i in range(2)]})
    return ROOT


def mixed_part(folder):
    p=read(folder/'plan.json');part=cohort(folder,2)
    owners={o['id']:o['player_id'] for o in p['opponents']}|{p['policy_version']:OPTIMIZER}
    for r in part['rows']:
        ep=read(folder/'artifacts'/r['episode']/'episode.json');audit=read(folder/'artifacts'/r['episode']/'audit.json')
        if len({x['player_id'] for x in ep['participants']})!=10 or {x['position']:x['player_id'] for x in ep['participants']}!={s:owners[v] for s,v in enumerate(ep['policy_version_ids'])}:
            raise ValueError('Wrong actual owners')
        slot=ep['policy_version_ids'].index(p['partner_version']);buddy=audit['heroes'][slot]
        r.update(partner_slot=slot,allied=slot//5==r['slot']//5,partner_win=buddy['score'],partner_gear=buddy['first_gear_tick']>=0,
                 glory=r['win']*(r['xp']-200*r['ticks']/1440))
    return part['rows']


def report():
    plan=read(ROOT/'plan.json');schedule=read(ROOT/'schedule.json');arms={};seen=set()
    for arm in ('control','candidate'):
        rows=[]
        for i in range(2):
            folder=BASE/f'paired-guardrail/candidate/part-{i}' if arm=='control' else ROOT/f'candidate/part-{i}'
            rr=mixed_part(folder)
            for r in rr:
                if r['seed'] in seen:raise ValueError('Repeated seed across guardrail arms')
                seen.add(r['seed']);r['roster_index']=i
            rows+=rr
        allied=[r for r in rows if r['allied']];opposed=[r for r in rows if not r['allied']]
        if len(allied)!=160 or len(opposed)!=40:raise ValueError('Role coverage mismatch')
        arms[arm]={'games':200,'allied_wins':sum(r['win'] for r in allied),'opposed_draws':sum(not r['win'] and not r['partner_win'] for r in opposed),
                   'both_gear':sum(r['first_gear_tick']>=0 and r['partner_gear'] for r in rows),
                   'rosters':{str(i):sum(r['win'] for r in allied if r['roster_index']==i) for i in range(2)},
                   'classes':{c:{'games':len(cr:=[r for r in allied if r['class']==c]),'wins':sum(r['win'] for r in cr)} for c in {r['class'] for r in rows}},'rows':rows}
    a,b=arms['candidate'],arms['control'];g=plan['gates']
    checks={'allied':a['allied_wins']>=b['allied_wins']-g['maximum_allied_loss'],
            'absolute':a['allied_wins']>=g['minimum_allied_wins'],
            'rosters':all(a['rosters'][str(i)]>=b['rosters'][str(i)]-g['maximum_roster_loss'] for i in range(2)),
            'classes':all(v['games']>=10 and v['games']==b['classes'][c]['games'] and v['wins']>=b['classes'][c]['wins']-g['maximum_class_fraction_loss']*v['games'] for c,v in a['classes'].items()),
            'opposed_draws':a['opposed_draws']<=b['opposed_draws'],'equipment':a['both_gear']==200}
    heads={}
    for folder in map(Path,schedule['heads']):
        p=read(folder/'plan.json');key=p['rival_key'];x=read(folder/'result.json')['rivals'][key];y=read(Path(p['control'])/'result.json')['rivals'][key]
        heads[key]={'candidate':x,'control':y}
        checks[key]=x['wins']>=y['wins']-g['maximum_head_total_loss'] and all(x['colors'][c]['win']>=y['colors'][c]['win']-g['maximum_head_color_loss'] for c in ('red','blue'))
        checks[key+'_gear']=all(r['gear_heroes']==5 for r in x['rows'])
    r={'new_games':360,'reused_control_games':360,'arms':arms,'heads':heads,'checks':checks,'passed':all(checks.values()),'scope':plan['design']}
    write(ROOT/'result.json',r)
    if not (ROOT/'feedback').exists():
        src=STUDY/'hosted/blue_assigned/mixed-feedback'
        record(src/'policy.ir.json',src/'policy.bas',f'Broad guardrail360newgames versus360reused exact-source controls. Allied{a["allied_wins"]}/160 vs{b["allied_wins"]}/160. Checks{checks}. Source/VM/owner/gear/fullreplay checks complete; fixed-role guardrail, not a randomized league-wide estimate.',ROOT/'result.json',ROOT/'feedback')
    print('Backdoor guardrail:',{k:v for k,v in r.items() if k not in ('arms','heads')},flush=True)


def run(_=None):
    prepare();schedule=read(ROOT/'schedule.json')
    for i in range(2):
        folder=Path(schedule['mixed'][i])
        if not (folder/'audit-progress.json').exists() or read(folder/'audit-progress.json')['verified']!=100:run_queue([folder])
        head=Path(schedule['heads'][i])
        if not (head/'result.json').exists():run_prepared(head)
        inventory(head)
    report()


if __name__=='__main__':
    from rush_unblock_queue import main
    main(prepare,run,'backdoor_guardrails360',STUDY/'local',QUEUE)

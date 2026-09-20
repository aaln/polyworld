"""Forty games per color against exact Jordan186; source/VM/replay guarded."""
from pathlib import Path
from backdoor_guardrails import pin_auditor
from command_diversity import inventory
from direct_matchup import run_prepared
from economy_feedback import record
from hosted_wave import client,create
from jordan_root import STUDY
from policy_ir import read,write,digest
from release_workspace import RUN
from rush_hosted import upload
from rush_sentries import STUDY as BASE
from win_hosted import live

CONTROL=BASE/'league-sweep/head-to-head/rival_7d6190c0'


def prepare(name):
    game=live();local=read(STUDY/'local/comparison.json')
    if name not in local['qualified']:raise ValueError('Unqualified candidate')
    root,v=upload(name,STUDY,'aaron-gota-ir-perimeter','Objective-relative defense and productive duty transitions',
                  feedback_override=STUDY/'local/comparison-feedback'/name)
    old=read(CONTROL/'plan.json');key=old['rival_key']
    p={k:old[k] for k in ('target','game_version','game_source','config','rival','rival_version','rival_key','episodes_per_color','interpretation')}
    if game['version']!=p['game_version'] or game['manifest']['game']['runnable']['source_url']!=p['game_source']:raise ValueError('Live source drift')
    p.update(policy_version=v['id'],policy_label=f'{v["name"]}:v{v["version"]}',
             design='Exact Jordan186, fivecopies perteam,40newgames/color. Compare reused fullyaudited deployed80(red40W blue0W) onexactrelease/config. Localwinner frozen. No deployment until replayreview and additional guardrails.',
             control=str(CONTROL),control_result_sha256=digest((CONTROL/'result.json').read_bytes()),
             gates={'blue_min_wins':30,'red_min_wins':38,'all_gear':True,'all_full_replays_and_vm':True})
    outroot=root/'jordan'
    outroot.mkdir(parents=True,exist_ok=True)
    if (outroot/'plan.json').exists() and read(outroot/'plan.json')!=p:raise ValueError('Plan changed')
    write(outroot/'plan.json',p)
    for color in ('red','blue'):
        out=outroot/key/color;out.mkdir(parents=True,exist_ok=True)
        slots=list(range(5)) if color=='red' else list(range(5,10))
        roster=[v['id'] if s in slots else p['rival_version'] for s in range(10)]
        arm=p|{'color':color,'own_slots':slots,'roster':roster}
        if (out/'plan.json').exists() and read(out/'plan.json')!=arm:raise ValueError('Arm changed')
        write(out/'plan.json',arm);pin_auditor(out)
        body={'idempotency_key':'gota-root-'+digest(arm)[:20],'target':p['target'],
              'game_config_overrides':p['config'],'num_episodes':40,
              'roster':[{'slot':s,'player':{'policy_ref':ref}} for s,ref in enumerate(roster)],
              'notes':p['design']+' Own'+color}
        with client() as c:create(c,body,out/'batch',dry_run=True)
    return root


def run(name):
    root=prepare(name);out=root/'jordan'
    if not (out/'result.json').exists():run_prepared(out)
    inventory(out)
    p=read(out/'plan.json');r=read(out/'result.json')['rivals'][p['rival_key']]
    checks={'blue':r['colors']['blue']['win']>=p['gates']['blue_min_wins'],
            'red':r['colors']['red']['win']>=p['gates']['red_min_wins'],
            'gear':all(x['gear_heroes']==5 for x in r['rows']),
            'full_audits':r['all_full_audits_passed']}
    result={'games':80,'wins':r['wins'],'colors':r['colors'],'checks':checks,'passed':all(checks.values()),
            'control':{'red_wins':40,'blue_wins':0},'scope':p['design']}
    write(root/'jordan-result.json',result)
    src=STUDY/'local/comparison-feedback'/name
    if not (root/'jordan-feedback').exists():record(src/'policy.ir.json',src/'policy.bas',f'Full80game Jordan186 comparison: {result}. Fixedroster repeats; mixedteam and otherchampion guardrails remain required.',root/'jordan-result.json',root/'jordan-feedback')
    print('Jordan root verdict',result,flush=True)


def run_candidates(name):
    comparison=read(STUDY/'local/comparison.json')
    names=[name]+[n for n in comparison['qualified'] if n!=name]
    design={'ordered_candidates':names,'condition':'Run primary80; if it fails the fixed Jordan gates, test the next locally qualified frozen candidate80. Same thresholds. No retuning within an arm; no automatic deployment.'}
    path=STUDY/'hosted/conditional-plan.json'
    if path.exists() and read(path)!=design:raise ValueError('Conditional design changed')
    write(path,design)
    results={};winner=None
    for candidate in names:
        run(candidate)
        r=read(STUDY/'hosted'/candidate/'jordan-result.json');results[candidate]=r
        if r['passed']:
            winner=candidate
            break
    write(STUDY/'hosted/comparison.json',{'selected':winner,'results':results,'scope':'Exact Jordan186 fixedteam comparison. Otherchampion/mixed guardrails still required.'})


if __name__=='__main__':
    import os,time
    from rush_unblock_queue import main
    while not (STUDY/'local/comparison.json').exists():
        pid=read(STUDY/'local-process.json')['pid']
        try:os.kill(pid,0)
        except ProcessLookupError:raise RuntimeError('Local study stopped')
        time.sleep(15)
    name=read(STUDY/'local/comparison.json')['selected']
    if not name:print('No qualified local candidate; no hosted request created.',flush=True)
    else:
        completed=BASE/'league-sweep/completed.json'
        if completed.exists():
            if read(completed)['games']!=1320:raise ValueError('Incomplete original suite')
            write(STUDY/'queue-state.json',{'stage':'jordan_root80_after_completed_sweep','candidate':name})
            run_candidates(name)
        else:main(prepare,run_candidates,'jordan_root80',STUDY/'local',STUDY)

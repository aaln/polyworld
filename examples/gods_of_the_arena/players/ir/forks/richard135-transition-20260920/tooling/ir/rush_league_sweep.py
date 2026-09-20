"""User-requested current-champion and ten-player XP sweep; no league selection."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import shutil

import rush_defense_hosted as heads
import rush_pair_guard as mixed
from coached_league_live import AARON, OPTIMIZER, arm_plan
from command_diversity import inventory
from direct_matchup import run_prepared
from economy_feedback import record
from hosted_batch import batch_body
from hosted_queue import run as run_queue
from hosted_wave import client, create
from policy_ir import read, write, digest
from release_workspace import RUN
from win_hosted import live


def setup(study, name):
    heads.STUDY=study
    mixed.STUDY=study;mixed.ROOT=study/'paired-guardrail';mixed.NAME=name;mixed.EXPLORATORY=True
    mixed.DIAGNOSTIC_ONLY=True


def prepare(study, name):
    setup(study,name)
    root=study/'league-sweep';root.mkdir(exist_ok=True)
    ref=RUN/'coached-lanes/r5-rush-defense/hosted/current'
    reference={'directory':str(ref),'result_sha256':digest((ref/'result.json').read_bytes()),
               'reason':'Reuse the completed exact same baseline, rivals, coworld release and config; no new result is claimed for these controls.'}
    path=study/'control-reference.json'
    if path.exists() and read(path)!=reference:raise ValueError('Control changed')
    write(path,reference)
    core_paths=heads.prepare(name)
    pair=mixed.freeze()
    if (root/'plan.json').exists():
        return read(root/'plan.json')
    champions=read(mixed.ROOT/'champions.json')
    active=[{'id':r['policy_version']['id'],'label':r['policy_version']['label'],
             'player_id':r['player']['id']} for r in champions
            if r['status']=='competing' and r['substatus']=='active' and r['player']['id'] not in {AARON,OPTIMIZER}]
    parent=read(study/'hosted-plan.json')
    core=parent['rivals']
    core_ids={r['id'] for r in core}
    others=sorted([r for r in active if r['id'] not in core_ids],key=lambda r:r['label'])
    candidate=read(study/'hosted'/name/'uploaded-version.json')
    paths=list(core_paths)
    for rival in others:
        key='rival_'+rival['id'].split('-')[0]
        path=root/'head-to-head'/key;path.mkdir(parents=True,exist_ok=True)
        p={k:parent[k] for k in ['target','game_version','game_source','config','episodes_per_color','interpretation']}
        p.update(policy_version=candidate['id'],policy_label=f'{candidate["name"]}:v{candidate["version"]}',
                 rival=rival['label'],rival_version=rival['id'],rival_key=key,
                 design='User-requested full current-champion sweep, five copies per team,40freshgames/color. '
                        'Pin exact versions for both colors; complete80before interpretation. No interim policy changes.')
        if (path/'plan.json').exists() and read(path/'plan.json')!=p:raise ValueError('Frozen rival changed')
        write(path/'plan.json',p)
        for color in ['red','blue']:
            out=path/key/color;out.mkdir(parents=True,exist_ok=True)
            slots=list(range(5)) if color=='red' else list(range(5,10))
            roster=[candidate['id'] if s in slots else rival['id'] for s in range(10)]
            write(out/'plan.json',p|{'color':color,'own_slots':slots,'roster':roster})
            shutil.copy2(RUN/'r5/audit',out/'audit')
            body={'idempotency_key':'gota-sentry-sweep-'+digest(p)[:20]+'-'+color,
                  'target':p['target'],'game_config_overrides':p['config'],'num_episodes':40,
                  'roster':[{'slot':s,'player':{'policy_ref':v}} for s,v in enumerate(roster)],
                  'notes':p['design']+' Opponent '+rival['label']+'; own color '+color+'.'}
            with client() as c:create(c,body,out/'batch',dry_run=True)
        paths.append(path)
    for i in range(2):
        for arm in ['candidate']:
            out=mixed.ROOT/arm/f'part-{i}';out.mkdir(parents=True,exist_ok=True)
            p=arm_plan(pair,arm,i);write(out/'plan.json',p)
            shutil.copy2(RUN/'r5/audit',out/'audit')
            with client() as c:create(c,batch_body(p,100),out/'batch',dry_run=True)
    plan={'created_at':datetime.now(timezone.utc).isoformat(),'candidate':name,
          'candidate_version':candidate['id'],'current_champions':active,'regression_rivals':core,
          'head_paths':[str(p) for p in paths],'core_paths':[str(p) for p in core_paths],
          'head_games':80*len(paths),'mixed_games':200,'mixed_plan_sha256':digest((mixed.ROOT/'plan.json').read_bytes()),
          'design':'All active other champion versions at the frozen snapshot, plus exact previously requested rush rivals. '
                   '200ten-playergames: two100rosters with bothlatestownedplayers. '
                   'Pairadjacent placement mirrored to cover everyclass allied;160allied+40opposed total. '
                   'This mixed sweep has no freshmatchedbaseline and cannot establish a win-rate gain. '
                   'User requested both modes concurrently in the research plan; launch arms serially and '
                   'drain server/artifacts/audits. No tuning, auto-promotion or replacement of earlier failed gates.'}
    write(root/'plan.json',plan)
    write(root/'README.md','# Latest iteration XP sweep\n\n'+plan['design']+'\n\n'
          +f'{plan["head_games"]} two-player games and200ten-player games.\n\n'
          +'\n'.join('- '+r['label'] for r in active)+'\n')
    return plan


def mixed_arm(plan, arm, i):
    out=mixed.ROOT/arm/f'part-{i}'
    if (out/'audit-progress.json').exists() and read(out/'audit-progress.json')['verified']==100:
        return
    live()
    run_queue([out])


def run(study,name):
    plan=prepare(study,name)
    # Start each requested mode promptly; every arm drains before the next.
    mixed_arm(plan,'candidate',0)
    priority=study/'league-sweep/priority-heads.json'
    if priority.exists():
        for p in map(Path,read(priority)['paths']):
            if str(p) not in plan['head_paths']:raise ValueError('Priority opponent outside frozen sweep')
            if not (p/'result.json').exists():run_prepared(p)
            inventory(p)
    heads.run(name)
    mixed_arm(plan,'candidate',1)
    mixed.report_diagnostic()
    for p in map(Path,plan['head_paths']):
        if not (p/'result.json').exists():run_prepared(p)
        inventory(p)
    results=[read(Path(p)/'result.json') for p in plan['head_paths']]
    rivals={k:v for result in results for k,v in result['rivals'].items()}
    result={'games':sum(r['games'] for r in rivals.values()),'wins':sum(r['wins'] for r in rivals.values()),
            'rivals':rivals,'mixed_result':str(mixed.ROOT/'result.json'),'design':plan['design']}
    root=study/'league-sweep';write(root/'result.json',result)
    if not (root/'feedback').exists():
        parent=study/'hosted'/name/'feedback'
        record(parent/'policy.ir.json',parent/'policy.bas',
               f'Completed all-champion direct sweep: {result["wins"]}/{result["games"]}. '
               'Per-rival/colors and command diversity retained. These fixed-copy tests do not establish '
               'mixed-team superiority. See separate200game paired diagnostic. No league selection.',
               root/'result.json',root/'feedback')
    paired=read(mixed.ROOT/'result.json')
    if not (root/'final-feedback').exists():
        record(root/'feedback/policy.ir.json',root/'feedback/policy.bas',
               f'Complete requested suite: {result["wins"]}/{result["games"]} fixed-copy wins; '
               f'latestpair allied{paired["allied_wins"]}/160 in200ten-playergames. '
               f'Opposed Optimizer/Aaron wins{paired["opposed_optimizer_wins"]}/{paired["opposed_aaron_wins"]} '
               'across40games. Do not pool teammate wins or claim matched mixed-team improvement. '
               'All evidence references and exact symbolic behavior retained; no league selection.',
               mixed.ROOT/'result.json',root/'final-feedback')
    lines=['# Completed XP sweep','',f'Head-to-head: **{result["wins"]}/{result["games"]} wins**.',
           '', '| Opponent | Red | Blue | Total |','|---|---:|---:|---:|']
    for r in rivals.values():
        lines.append(f'| {r["label"]} | {r["colors"]["red"]["win"]}/40 | '
                     f'{r["colors"]["blue"]["win"]}/40 | {r["wins"]}/80 |')
    lines += ['', f'Ten-player: **{paired["allied_wins"]}/160 allied wins**;40opposedgames reported separately.',
              '', 'These are fixed-roster diagnostics with repeated tactical trajectories. '
              'The mixed sweep has no fresh matched baseline. All full replays, ten VMs, '
              'source, roster and equipment checks completed. League selections remain unchanged.',
              '', 'Final paired IR and unchanged BASIC: `final-feedback/`.']
    (root/'REPORT.md').write_text('\n'.join(lines)+'\n')
    print('Completed both requested modes:',result['games'],'head-to-head and200mixed games.',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('study',type=Path);parser.add_argument('name')
    parser.add_argument('--prepare-only',action='store_true')
    args=parser.parse_args()
    (prepare if args.prepare_only else run)(args.study.resolve(),args.name)

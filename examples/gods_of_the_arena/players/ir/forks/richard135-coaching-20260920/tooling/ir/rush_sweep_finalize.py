"""Finish the requested sweep's local IR/evidence report after its runner drains."""
import argparse
import os
from pathlib import Path
import time

from economy_feedback import record
from policy_ir import HERE,digest,read,write
from release_workspace import RUN


def finish(study):
    root=study/'league-sweep';result=read(root/'result.json')
    paired=read(study/'paired-guardrail/result.json')
    if result['games']!=1120 or paired['games']!=200:
        raise ValueError('Requested suite is incomplete')
    deployment_path=study/'deployment-requested/deployment-verified.json'
    deployed=deployment_path.exists()
    deployment_note=('The exact candidate was deployed to both players at the user’s explicit '
                     'request while this suite ran; deployment was not contingent on its result.'
                     if deployed else 'This sweep made no league selection.')
    if not (root/'final-feedback').exists():
        record(root/'feedback/policy.ir.json',root/'feedback/policy.bas',
               f'Complete requested suite: {result["wins"]}/1120fixed-copywins; '
               f'latestpair allied{paired["allied_wins"]}/160 in200ten-playergames. '
               f'Opposed Optimizer/Aaron wins{paired["opposed_optimizer_wins"]}/{paired["opposed_aaron_wins"]} '
               'across40games. Do not pool teammatewins or claim matchedmixedteam improvement. '
               'All evidence and exactsymbolicbehavior retained. '+deployment_note,
               study/'paired-guardrail/result.json',root/'final-feedback')
    lines=['# Completed XP sweep','',f'Head-to-head: **{result["wins"]}/1120 wins**.','',
           '| Opponent | Red | Blue | Total |','|---|---:|---:|---:|']
    for r in result['rivals'].values():
        lines.append(f'| {r["label"]} | {r["colors"]["red"]["win"]}/40 | '
                     f'{r["colors"]["blue"]["win"]}/40 | {r["wins"]}/80 |')
    lines += ['',f'Ten-player: **{paired["allied_wins"]}/160 allied wins**;40opposedgames reported separately.',
              '', 'These are fixed-roster diagnostics with repeated tactical trajectories. '
              'The mixed sweep has no fresh matched baseline. All full replays, ten VMs, source '
              'and rosters were checked. Equipment results are retained per episode. '+deployment_note,
              '', 'Final paired IR and unchanged BASIC: `final-feedback/`.']
    (root/'REPORT.md').write_text('\n'.join(lines)+'\n')
    write(root/'completed.json',{'games':1320,'report':str(root/'REPORT.md'),
          'ir_policy_pair':str(root/'final-feedback'),'league_changed':deployed,
          'deployment_receipt':str(deployment_path) if deployed else None})
    if deployed:
        receipt=read(deployment_path)
        final=root/'deployment-feedback'
        if not final.exists():
            record(root/'final-feedback/policy.ir.json',root/'final-feedback/policy.bas',
                   deployment_note+' Complete suite results are retained without retroactively '
                   'calling the earlier deployment a validated promotion.',deployment_path,final)
        active=read(HERE/'active_policy.json')
        if {p['player']:p['version'] for p in active['players']}==receipt['versions']:
            if digest((final/'policy.bas').read_bytes())!=receipt['source_sha256']:
                raise ValueError('Final evidence changed the deployed executable')
            active.update(policy=str(final/'policy.bas'),semantic_ir=str(final/'policy.ir.json'),
                          latest_evaluation=str(root/'completed.json'))
            write(HERE/'active_policy.json',active)
    state=read(RUN/'active-state.json')
    if state.get('hosted_study')==str(study):
        state.update(stage='requested_sweep_complete',hosted_session=None,
                     valid_current_hosted_games=2860,new_sweep_games=1320,
                     report=str(root/'REPORT.md'),latest_feedback=str(root/'final-feedback'),
                     warning='Full1120head-to-head+200ten-player suite complete. Mixed result is diagnostic; no freshmatchedbaseline. '+deployment_note)
        write(RUN/'active-state.json',state)
    print('Final IR/policy pair and1320game report saved:',root/'REPORT.md',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('study',type=Path);parser.add_argument('--runner-pid',type=int)
    args=parser.parse_args()
    while not (args.study/'league-sweep/result.json').exists():
        if args.runner_pid:
            try:os.kill(args.runner_pid,0)
            except ProcessLookupError:raise RuntimeError('Runner stopped before complete results; resume it from saved receipts')
        time.sleep(20)
    # result.json precedes the runner's immutable feedback bundle.
    while not (args.study/'league-sweep/feedback/policy.bas').exists():time.sleep(5)
    finish(args.study)

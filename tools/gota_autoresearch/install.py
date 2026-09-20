#!/usr/bin/env python3
"""Install the user-authorized GotA service without editing the dirty game tree."""
import json
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import sys

import researcher as r

ROOT = r.DEFAULT
CODE = Path(__file__).resolve().parent
ENGINE = Path('/Users/aaln/experiments/softmax/polyworld-gota-clean-20260916-r5')
HERE = ENGINE / 'examples/gods_of_the_arena/players/ir'
RUN = Path('/Users/aaln/experiments/softmax/gota-research-20260916')
PARENT = RUN / 'coached-lanes/r5-relh154/scoped-followup/final-feedback'
LAB = Path('/Users/aaln/experiments/softmax/optimizer-seed/games/gods-of-the-arena')


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(HERE))
    from win_hosted import live
    from release_workspace import verify
    from hosted_wave import client, get
    from release_deploy import champions
    game, engine = live(), verify()
    with client() as c:
        rows = champions(c)
        own = {p['player']['id']: p['policy_version']['id'] for p in rows}
        r.require(own == {'ply_594ec24d-d7f3-4370-a000-468354ec41c9':'53f15b12-2198-41d1-bb99-df4bdb1ff7fd',
                          'ply_630a768f-d623-44b2-80fa-36968d6fa75a':'eae99cdd-b2a9-4426-aa20-289d8637fa54'}, 'Live baseline changed; reconcile first')
        metadata = r.read(PARENT.parent/'hosted/legacy/upload-request.json')
        remote_source = r.verify_remote_source(c, metadata, '53f15b12-2198-41d1-bb99-df4bdb1ff7fd')
    r.require(r.sha(PARENT/'policy.bas') == 'b2693715459d0de7283ba6f45440c0084ea5c7781c2305e163976a6572246ca9', 'Wrong baseline BASIC')
    r.require(remote_source['source_sha256'] == r.sha(PARENT/'policy.bas'), 'Hosted incumbent source differs')
    r.write(ROOT/'remote-source-at-install.json', remote_source)
    r.write(ROOT/'champions-at-install.json', rows)
    r.write(ROOT/'engine-at-install.json', engine)
    ref = r.read(RUN/'coached-lanes/r5-coach-split-0918/mobile-followup/discovery/g002/mobile30/red/plan.json')
    field = [{'name':'gota-g002:v1', 'id':'a30542cb-54de-4109-92e6-bcabca7db4d8'}]
    for sub in ['confirmation/relh154/legacy/blue', 'confirmation/black16/legacy/blue',
                'confirmation/macro4/legacy/blue', 'batches/jordan254/legacy/blue']:
        p = r.read(PARENT.parent/sub/'plan.json')
        field.append({'name': p['rival'], 'id': p['rival_version']})
    cfg = {'workspace': str(ENGINE), 'tooling': str(HERE), 'codex': shutil.which('codex'),
           'python': sys.executable, 'dependencies': str(RUN/'deps'),
           'game_version': game['version'], 'engine_commit': engine['game_source'],
           'target': ref['target'], 'game_config': ref['config'],
           'auditor': str(RUN/'r5/fast/audit-hosted'), 'auditor_sha256': r.sha(RUN/'r5/fast/audit-hosted'),
           'cycle_timeout_seconds': 9600, 'between_cycles_seconds': 60,
           'cycle_episode_limit': 400, 'daily_episode_limit': 1600, 'max_parallel_xp': 3,
           'field_opponents': field, 'historical_opponents': [
               {'name':'aaron-gota-ir-perimeter-blue_repair-0916-aaron:v1','id':'b64f1ccb-02e1-4ad5-b75b-f374222e9e9a'},
               {'name':'aaron-gota-ir-coordinated-support-anchor-0916:v1','id':'9cedf3ff-c7ce-4cff-897f-d48b44e049ad'}],
           'league_auto_deploy': False}
    r.require(cfg['codex'], 'Codex CLI missing')
    if not (ROOT/'config.json').exists(): r.write(ROOT/'config.json', cfg)
    if not (ROOT/'state.json').exists():
        name = r.snapshot(ROOT, PARENT, 0, None,
                          {'id':'53f15b12-2198-41d1-bb99-df4bdb1ff7fd','name':'aaron-gota-ir-relh154-legacy-0916:v1'},
                          {'kind':'existing validated incumbent; not a new self-play qualification',
                           'original_bundle':str(PARENT), 'league_source_sha256':r.sha(PARENT/'policy.bas'),
                           'active_policy':r.read(HERE/'active_policy.json')})
        r.write(ROOT/'state.json', {'schema':1,'accepted':name, 'generation':0, 'initialized_at':r.now()})
        r.fork(ROOT, 'Improve general gameplay from the validated incumbent; investigate red defensive commitment and wave-supported counterattack')
    for n in ('PROMPT.md','README.md','HANDOFF.md'):
        if not (ROOT/n).exists(): shutil.copy2(CODE/n, ROOT/n)
    guide = Path('/Users/aaln/Downloads/guide-episode-semantic-ir (1).md')
    if not (ROOT/'episode-semantic-ir-guide.md').exists(): shutil.copy2(guide, ROOT/'episode-semantic-ir-guide.md')
    if not (ROOT/'CHECKPOINT.md').exists():
        (ROOT/'CHECKPOINT.md').write_text('Bootstrap complete. Generation zero is the current deployed relh154-legacy policy.\n'
            'No new candidate has qualified. Read HANDOFF.md, verify game source, resume the initial fork, then run a local self-play screen.\n')
    if not (ROOT/'progress.json').exists():
        r.write(ROOT/'progress.json', {'phase':'initialized','last_result':'Validated incumbent snapshotted; no newly accepted candidate',
                                      'pending_jobs':[], 'next_action':'First autonomous research cycle'})
    preferences = LAB.parent.parent/'user_preferences.md'
    text = preferences.read_text()
    marker = '2026-09-18, persistent GotA autoresearch authorization'
    if marker not in text:
        text += '\n- **'+marker+'.** User: “I want you to setup an autoresearcher which keeps building policies to beat our last policies for gota. Continuously self improve by beating our own policies. Every time you get a newly upgraded policy that passed the beating threshold, save a snapshot of that policy and create a fork of the policy that can beat it. Try to actually improve it in a way which improves gameplay in general across vs only exploiting a weakness in the previous policy. Make all the policies IR and built off one another. You can run xp requests with the policies in this iteration loop to ensure they are generalized. Keep it running and relaunch this every 3 hours in case the agent stops.” Ongoing autonomous coordinated research, testing, snapshots and forks are authorized.\n'
        preferences.write_text(text)
    plist = {'Label':'com.aaron.gota-autoresearch',
             'ProgramArguments':[sys.executable, str(CODE/'researcher.py'), '--root',str(ROOT),'run'],
             'WorkingDirectory': str(ENGINE), 'RunAtLoad':True, 'StartInterval':10800,
             'KeepAlive':{'SuccessfulExit':False}, 'ThrottleInterval':60,
             'ProcessType':'Background',
             'StandardOutPath':str(ROOT/'service.stdout.log'), 'StandardErrorPath':str(ROOT/'service.stderr.log'),
             'EnvironmentVariables':{'PATH':os.environ['PATH'],'POLYWORLD_DEPS':str(RUN/'deps'),'PYTHONUNBUFFERED':'1','LANG':'en_US.UTF-8'}}
    path = Path('/Users/aaln/Library/LaunchAgents/com.aaron.gota-autoresearch.plist')
    if path.exists():
        r.require(plistlib.loads(path.read_bytes()) == plist, 'Existing service differs; reconcile explicitly')
    else:
        path.write_bytes(plistlib.dumps(plist))
    subprocess.run(['plutil','-lint',str(path)],check=True)
    print(json.dumps({'campaign':str(ROOT),'launch_agent':str(path),'installed':True,'started':False},indent=2))


if __name__ == '__main__': main()

"""Inspect the largest blue command group per outcome in each mixed A/B arm."""
import argparse
from pathlib import Path
import subprocess
from inspect_backdoor import inspect
from policy_ir import digest,read,write
from release_workspace import RUN
from review_defense_stalls import inspect as stalls


def review(root):
    plan=read(root/'mixed-plan.json');out=root/'replay-review';out.mkdir(exist_ok=True)
    results=[]
    for path in map(Path,plan['paths']):
        div=read(path/'command-diversity.json')['arms']['mixed_roster']['colors']['blue']
        rows=read(path/'result.json')['rivals']['mixed_roster']['rows']
        outcome={r['episode']:('win' if r['win'] else 'loss' if r['loss'] else 'draw') for r in rows}
        selected={}
        for group in sorted(div['groups'],key=lambda g:(-len(g['members']),g['representative'])):
            selected.setdefault(outcome[group['representative']],group)
        for result,group in selected.items():
            episode=group['representative'];folder=path/'mixed_roster/blue/artifacts'/episode
            capture=out/(path.name+'-'+result);capture.mkdir(exist_ok=True)
            decoded=capture/'replay.jsonl'
            if not decoded.exists():
                temporary=decoded.with_suffix('.pending')
                with temporary.open('w') as stream:
                    subprocess.run([str(RUN/'r5/macro-replay-v5'),'--replay',str(folder/'replay.bin')],
                                   stdout=stream,stderr=subprocess.PIPE,text=True,check=True,timeout=600)
                temporary.replace(decoded)
            arm=read(path/'mixed_roster/blue/plan.json');slots=arm['controlled_slots']
            response=inspect(decoded,1,slots);audit=read(folder/'audit.json')
            if response['ticks']!=audit['ticks']:raise ValueError('Incomplete decoded episode')
            write(capture/'response.json',response)
            stalled=stalls(decoded,1)
            stalled['stationary_repeated_order_windows']=[s for s in stalled['stationary_repeated_order_windows'] if s['slot'] in slots]
            write(capture/'stalls.json',stalled)
            results.append({'arm':path.name,'outcome':result,'episode':episode,'command_group_size':len(group['members']),
                            'ticks':response['ticks'],'sampled_visible_core_attacks':response['visible_structure_attack_samples'],
                            'isolated_samples':response['isolated_samples'],
                            'isolated_samples_with_owned_target_order':response['isolated_samples_with_owned_target_order'],
                            'isolated_samples_all_allies_away':response['isolated_samples_all_allies_away'],
                            'owned_stall_windows':len(stalled['stationary_repeated_order_windows']),
                            'replay_sha256':digest((folder/'replay.bin').read_bytes()),'response':str(capture/'response.json')})
    write(out/'result.json',{'selection':'Largest full-command group per blue outcome in each arm, one representative per group.',
                            'interpretation':'Representative descriptive inspection, not all-episode event rates. Shared orders do not prove identical hidden state. No historical VM beliefs available.',
                            'rows':results})
    return out/'result.json'


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('directory',type=Path)
    print(review(p.parse_args().directory))

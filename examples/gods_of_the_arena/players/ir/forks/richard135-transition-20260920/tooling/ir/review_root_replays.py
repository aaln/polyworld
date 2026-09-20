"""Reconstruct candidate VM decisions in largest blue outcome groups after eval."""
import json,os,subprocess
from pathlib import Path
from policy_ir import read,write,digest,ROOT
from release_workspace import RUN
from jordan_root import STUDY
from review_defense_stalls import inspect


def review(name):
    root=STUDY/'hosted'/name;match=root/'jordan';key=read(match/'plan.json')['rival_key']
    groups=read(match/'command-diversity.json')['arms'][key]['colors']['blue']['groups']
    selected=[]
    for outcome in sorted({g['win'] for g in groups}):
        g=max((g for g in groups if g['win']==outcome),key=lambda x:len(x['members']))
        selected.append(g)
    results=[]
    for g in selected:
        episode=g['representative'];src=match/key/'blue/artifacts'/episode
        out=root/'replay-review'/episode;out.mkdir(parents=True,exist_ok=True)
        replay=out/'replay.jsonl';trace=out/'decisions.jsonl'
        if not replay.exists():
            with replay.open('w') as f:subprocess.run([str(RUN/'r5/macro-replay-v5'),'--replay',str(src/'replay.bin')],cwd=ROOT,stdout=f,check=True)
        if not trace.exists():
            with trace.open('w') as f:subprocess.run([str(RUN/'r5/replay-perimeter-probe'),'--replay',str(src/'replay.bin')],cwd=ROOT,stdout=f,check=True,env=dict(os.environ,PROBE_POLICY=str(STUDY/'local/candidates'/name/'policy.bas')))
        traces=[json.loads(l) for l in trace.open()];summary=traces[-1]
        if summary.get('type')!='summary' or not summary['all_state_hashes_equal'] or not summary['all_actions_consumed']:raise ValueError('Candidate VM reconstruction failed')
        stalls=inspect(replay,1);write(out/'stalls.json',stalls)
        decisions=[r for r in traces if r['type']=='decision']
        results.append({'episode':episode,'wins':g['win'],'group_games':len(g['members']),
                        'summary':summary,'sampled_decisions':len(decisions),
                        'active_target_decisions':sum(r['memory']['defActive']==1 and r['memory']['bestId']!=0 for r in decisions),
                        'quiet_defense_decisions':sum(r['memory']['defActive']==1 and r['memory']['bestId']==0 for r in decisions),
                        'non_sentry_offense_decisions':sum(r['slot'] in (6,9) and r['memory']['defActive']==0 for r in decisions),
                        'stationary_windows':len(stalls['stationary_repeated_order_windows']),
                        'shared_waypoint_windows':len(stalls['shared_destination_windows']),
                        'decoded_sha256':digest(replay.read_bytes()),'trace_sha256':digest(trace.read_bytes())})
    result={'name':name,'representatives':results,'instrument_sha256':digest((RUN/'r5/replay-perimeter-probe').read_bytes()),
            'scope':'Largest blue fullcommandgroup per win/loss outcome. Fullownedcommand/statehash reconstruction; decision samples every5seconds. Samples are not independent game trials; stationary checks do not prove physical collision.'}
    write(root/'replay-review/result.json',result);return result

if __name__=='__main__':
    import sys
    print(json.dumps(review(sys.argv[1]),indent=2))

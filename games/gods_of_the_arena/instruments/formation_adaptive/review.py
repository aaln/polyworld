"""Audit full observed-profile executions and count canonical trajectories."""
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
import json
import os
from pathlib import Path
import subprocess
import sys
from build import ROOT,STUDY,read,write,digest

STREAM=ROOT.parent/'gota-autoresearch/cycles/20260919T101825Z-880d3c/replay-command-stream'


def one(arm):
    d=Path(arm['directory'])
    if not (d/'arm-result.json').exists():return None
    result=read(d/'arm-result.json');assert result['all_full_audits_passed'] and result['games']==40
    path=d/'trajectory-correlation.json'
    if not path.exists():
        rows=[]
        for r in result['rows']:
            p=d/'artifacts'/r['episode'];tape=p/'replay.bin';audit=read(p/'audit.json')
            assert digest(tape.read_bytes())==r['replay_sha256']
            q=subprocess.run([str(STREAM),str(tape)],capture_output=True,check=True);metadata=json.loads(q.stderr)
            assert metadata['ticks']==r['ticks']==audit['ticks']
            assert metadata['actions_consumed']==audit['actions_consumed']==audit['recorded_actions']
            rows.append({'episode':r['episode'],'sha256':digest(q.stdout)})
        counts=Counter(r['sha256'] for r in rows)
        write(path,{'games':40,'distinct_complete_command_streams':len(counts),'counts':dict(counts),'rows':rows,
                    'binary_sha256':digest(STREAM.read_bytes()),'interpretation':'Repeated trajectories are correlated; unique streams are not automatically independent trials.'})
    if arm['name']=='candidate':
        for outcome in ('win','loss','draw'):
            subset=sorted([r for r in result['rows'] if r[outcome]],key=lambda r:(r['ticks'],r['episode']))
            if not subset:continue
            row=subset[len(subset)//2];out=d/('profile-'+outcome+'.json')
            if out.exists():continue
            source=STUDY/'candidates'/read(STUDY/'hosted-plan.json')['candidate']/'policy.bas'
            binary=STUDY/'profile-probe';tape=d/'artifacts'/row['episode']/'replay.bin'
            p=subprocess.run([str(binary),'--replay',str(tape)],env=dict(os.environ,AUDIT_POLICY=str(source),
                AUDIT_SLOTS=','.join(map(str,arm['own_slots']))),capture_output=True,text=True,timeout=900)
            if p.returncode:
                write(d/('profile-'+outcome+'-error.json'),{'code':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
                raise ValueError('Profile reconstruction failed for '+arm['key'])
            audit=json.loads(p.stdout.splitlines()[-1]);assert audit['all_state_hashes_equal'] and audit['all_actions_consumed']
            audit.update(episode=row['episode'],outcome=outcome,source_sha256=digest(source.read_bytes()),
                         binary_sha256=digest(binary.read_bytes()),replay_sha256=digest(tape.read_bytes()))
            write(out,audit)
    return {'key':arm['key'],'games':40,'wins':result['wins'],'losses':result['losses'],'draws':result['draws'],
            'distinct_streams':read(path)['distinct_complete_command_streams']}


def main():
    confirmation='--confirmation' in sys.argv
    plan=read(STUDY/('confirmation-plan.json' if confirmation else 'hosted-plan.json'))
    with ThreadPoolExecutor(2) as pool:rows=list(pool.map(one,plan['arms']))
    rows=[r for r in rows if r]
    write(STUDY/('confirmation-review.json' if confirmation else 'review-progress.json'),
          {'completed_cells':len(rows),'cells':rows,'complete':len(rows)==len(plan['arms'])})
    if confirmation and len(rows)==len(plan['arms']):
        novelty=[]
        for arm in plan['arms']:
            before=read(STUDY/'hosted'/arm['key']/'trajectory-correlation.json')
            after=read(Path(arm['directory'])/'trajectory-correlation.json')
            old=set(before['counts']);new=set(after['counts'])
            novelty.append({'key':arm['key'],'discovery_distinct':len(old),'confirmation_distinct':len(new),
                            'new_complete_streams':len(new-old),'repeated_complete_streams':len(new&old),
                            'confirmation_games_with_new_stream':sum(n for h,n in after['counts'].items() if h not in old)})
        write(STUDY/'confirmation-novelty.json',{'cells':novelty,
              'interpretation':'Fresh requests are prospective replication, not guaranteed novel or independent behavior. Canonical streams contain all ten command sequences; different streams alone do not imply independence.'})
    print(rows,flush=True)


if __name__=='__main__':main()

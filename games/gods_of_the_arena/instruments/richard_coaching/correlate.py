"""Hash every canonical command in each fully audited40game hosted cell."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
from prepare import ROOT, STUDY, CAMPAIGN, read, write, digest

CALIBRATION=CAMPAIGN/'cycles/20260919T101825Z-880d3c'
BINARY=CALIBRATION/'replay-command-stream'


def process(folder):
    dest=folder/'trajectory-correlation.json'
    if dest.exists():return str(folder),read(dest)['distinct_complete_all10_command_streams']
    result=read(folder/'arm-result.json')
    assert result['all_full_audits_passed'] and result['games']==len(result['rows'])==40
    rows=[]
    for row in result['rows']:
        p=folder/'artifacts'/row['episode'];audit=read(p/'audit.json')
        assert audit['hash_mismatches']==0 and digest((p/'replay.bin').read_bytes())==row['replay_sha256']
        proc=subprocess.run([str(BINARY),str(p/'replay.bin')],capture_output=True,check=True)
        info=json.loads(proc.stderr)
        assert len(proc.stdout)==info['bytes']
        assert info['ticks']==audit['ticks']==row['ticks']
        assert info['actions_consumed']==audit['actions_consumed']==audit['recorded_actions']
        rows.append({'episode':row['episode'],'sha256':digest(proc.stdout),
                     'actions':info['actions_consumed'],'ticks':info['ticks']})
    counts=Counter(r['sha256'] for r in rows)
    write(dest,{'dump_binary_sha256':digest(BINARY.read_bytes()),'games':40,
        'distinct_complete_all10_command_streams':len(counts),'counts':dict(counts),'rows':rows,
        'arm_result_sha256':digest((folder/'arm-result.json').read_bytes()),
        'calibration_sha256':digest((CALIBRATION/'command-stream-calibration/proof.json').read_bytes()),
        'interpretation':'Every within-hero command retained; cross-hero serialization normalized. '
            'Repeated command streams are correlated. Different streams/seeds do not prove independence. '
            'Separate full native replay audits remain required and passed for every episode.'})
    return str(folder),len(counts)


if __name__=='__main__':
    proof=read(CALIBRATION/'command-stream-calibration/proof.json')
    assert proof['passed'] and proof['binary_sha256']==digest(BINARY.read_bytes())
    roots=[STUDY,CAMPAIGN/'adaptive-opponent-20260920']
    folders=sorted({p.parent for root in roots for p in root.glob('**/arm-result.json')})
    with ThreadPoolExecutor(2) as pool:
        for folder,n in pool.map(process,folders):print(folder,n,flush=True)

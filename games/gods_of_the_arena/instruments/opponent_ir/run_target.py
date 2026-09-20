"""Resume a frozen target study, respecting the train-before-heldout boundary."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('study',type=Path);a=p.parse_args();d=a.study.resolve()
plan=json.loads((d/'study-plan.json').read_text())
assert all((d/'artifacts'/r['id']/'observer-validation.json').exists() for r in plan['episodes'] if r['split']!='heldout')
commands=[]
if not (d/'model-freeze.json').exists():
    assert not any((d/'artifacts'/r['id']/'observer.jsonl.gz').exists() for r in plan['episodes'] if r['split']=='heldout')
    commands += [('segment.py',[]),('fit.py',[])]
commands += [('decode.py',['--heldout']),('segment.py',['--heldout']),('evaluate_target.py',[])]
for filename,flags in commands:
    print('STAGE',filename,*flags,flush=True)
    with (d/(filename+'.'+('heldout' if flags else 'train')+'.log')).open('w') as log:
        subprocess.run([sys.executable,str(HERE/filename),str(d),*flags],stdout=log,stderr=subprocess.STDOUT,check=True)
print('EVALUATED',plan['target_label'],flush=True)

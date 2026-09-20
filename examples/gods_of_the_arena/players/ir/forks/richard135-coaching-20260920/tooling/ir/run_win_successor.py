"""Advance only complete, passing stages; leave league selection for reviewed results."""
from pathlib import Path
import os
import subprocess
import sys
import time
from policy_ir import HERE,read,write,digest
from win_screen import STUDY

def stage(label,args):
    print('Starting '+label,flush=True)
    write(STUDY/(label+'-tool-provenance.json'),{p.name:digest(p.read_bytes()) for p in HERE.glob('*.py') if not p.name.startswith('test_')})
    subprocess.run([sys.executable,*args],cwd=HERE,check=True)
    print('Completed '+label,flush=True)

path=STUDY/'hosted-discovery/result.json'
while not path.exists():
    try:os.kill(int(sys.argv[1]),0)
    except ProcessLookupError:raise RuntimeError('Discovery ended without a verdict; inspect retained artifacts')
    time.sleep(5)
if not read(path)['passed']:
    print('Discovery failed; no successor XP launched.',flush=True);sys.exit(0)
stage('rivals',[str(HERE/'rival_matchups.py'),str(STUDY),'run'])
stage('confirmation',[str(HERE/'win_hosted.py'),'confirmation'])
if not read(STUDY/'hosted-confirmation/result.json')['passed']:
    print('Fresh confirmation failed; no field or league change.',flush=True);sys.exit(0)
stage('field-launch',[str(HERE/'release_field.py'),str(STUDY),'launch'])
with (STUDY/'field/harvest.log').open('w') as harvest,(STUDY/'field/audit.log').open('w') as audit:
    jobs=[subprocess.Popen([sys.executable,str(HERE/'release_field.py'),str(STUDY),'harvest'],stdout=harvest,stderr=subprocess.STDOUT),
          subprocess.Popen([sys.executable,str(HERE/'watch_hosted_audit.py'),str(STUDY/'field'),'--workers','2'],stdout=audit,stderr=subprocess.STDOUT)]
    statuses=[p.wait() for p in jobs]
    if any(statuses):raise RuntimeError('Field collectors failed: '+str(statuses))
stage('field-report',[str(HERE/'release_field.py'),str(STUDY),'report'])
print('All successor research stages complete; no league mutation.',flush=True)
